"""Unit tests for ``:mod:zarp.runner.zarp_runner``."""

import logging
from pathlib import Path
import shutil

import numpy as np

from zarp.config.mappings import map_zarp_to_model
from zarp.config.models import (
    Config,
    ConfigRun,
    ConfigSample,
    ConfigUser,
    ExecModes,
)
from zarp.runner.zarp_runner import SampleRunnerZARP as SRZ
from zarp.samples.sample_record_processor import SampleRecordProcessor as SRP
from zarp.samples import sample_table_processor as STP
from zarp.snakemake.run import SnakemakeExecutor

from tests.utils import create_snakefile

LOGGER = logging.getLogger(__name__)


class TestSampleRunnerZARP:
    """Test ``:cls:zarp.runner.zarp_runner.SampleRunnerZARP`` class."""

    config = Config(
        run=ConfigRun(
            zarp_directory=Path(__file__).parents[1] / "files" / "zarp",
            genome_assemblies_map=Path(__file__).parents[1]
            / "files"
            / "genome_assemblies.csv",
        ),
        sample=ConfigSample(),
        user=ConfigUser(),
    )
    data = STP.read(
        path=Path(__file__).parents[1]
        / "files"
        / "complete_test_set"
        / "sample_table_complete.tsv",
        mapping=map_zarp_to_model,
    )
    data_incomplete = STP.read(
        path=Path(__file__).parents[1] / "files" / "sample_table_short.tsv",
        mapping=map_zarp_to_model,
    )
    data_incomplete.replace(to_replace="", value=np.nan, inplace=True)

    def test_init(self):
        """Test constructor."""
        config = self.config.copy(deep=True)
        df = self.data.copy(deep=True)
        srp = SRP()
        srp.append(df)
        srz = SRZ(config=config, records=srp.records)
        assert hasattr(srz, "records")
        assert len(srz.records.index) == 2

    def test__configure_run(self, tmpdir):
        """Test `._configure_run()` method."""
        config = self.config.copy(deep=True)
        config.run.identifier = "ABCDE"
        df = self.data.copy(deep=True)
        run_dir = Path(tmpdir) / "runs" / config.run.identifier
        out_dir = Path(tmpdir) / "results"
        cluster_log_dir = Path(tmpdir) / "logs" / "cluster"
        config_file = Path(run_dir) / "config.yaml"
        sample_table = Path(run_dir) / "samples_zarp.tsv"
        index_dir = Path(tmpdir) / "indexes"
        srp = SRP()
        srp.append(df)
        srz = SRZ(config=config, records=srp.records)
        conf_file, content = srz._configure_run(root_dir=Path(tmpdir))
        assert conf_file.exists()
        assert Path(run_dir).exists()
        assert Path(out_dir).exists()
        assert Path(cluster_log_dir).exists()
        assert Path(config_file).exists()
        assert Path(sample_table).exists()
        assert Path(index_dir).exists()
        assert content.rule_config == str(
            config.run.zarp_directory
            / "tests"
            / "input_files"
            / "rule_config.yaml"
        )
        config.run.rule_config = Path(__file__)
        _, content = srz._configure_run(root_dir=Path(tmpdir))
        assert content.rule_config == str(Path(__file__))

    def test__prepare_sample_table(self, tmpdir):
        """Test `._prepare_sample_table()` method."""
        config = self.config.copy(deep=True)
        df = self.data.copy(deep=True)
        sample_table = Path(tmpdir) / "samples_zarp.tsv"
        srp = SRP()
        srp.append(df)
        srz = SRZ(config=config, records=srp.records)
        srz._prepare_sample_table(sample_table=sample_table)
        assert sample_table.exists()

    def test__select_records(self):
        """Test `._select_records()` method."""
        config = self.config.copy(deep=True)
        df = self.data_incomplete.copy(deep=True)
        srp = SRP()
        srp.append(df)
        srz = SRZ(config=config, records=srp.records)
        assert len(srz.records.index) == 0
        srz.records = srp.records
        assert len(srz.records.index) == 2
        srz._select_records()
        assert len(srz.records.index) == 0

    def test_process_empty(self, tmpdir, caplog):
        """Test `.process()` method with no records."""
        config = self.config.copy(deep=True)
        outdir = Path(tmpdir)
        workflow = create_snakefile(dir=outdir, name="Snakefile")
        df = self.data_incomplete.copy(deep=True)
        srp = SRP()
        srp.append(df)
        srz = SRZ(config=config, records=srp.records)
        assert len(srz.records.index) == 0
        with caplog.at_level(logging.DEBUG):
            df_out = srz.process(loc=outdir, workflow=workflow)
        assert len(df_out.index) == 0
        assert "No samples to run" in caplog.text

    def test_process(self, tmpdir, monkeypatch):
        """Test `.process()` method."""
        config = self.config.copy(deep=True)
        df = self.data.copy(deep=True)
        outdir = Path(tmpdir)
        workflow = create_snakefile(dir=outdir, name="Snakefile")
        srp = SRP()
        srp.append(df)
        srz = SRZ(config=config, records=srp.records)

        def patched_run(self, cmd) -> None:
            """Patch `run()` method."""
            run_dir = Path(tmpdir) / "runs" / config.run.identifier
            src = Path(__file__).parents[1] / "files" / "sra_table.tsv"
            dst_in = run_dir / "samples_local.tsv"
            dst_out = run_dir / "samples_remote.tsv"
            shutil.copyfile(src, dst_in)
            shutil.copyfile(src, dst_out)

        monkeypatch.setattr(SnakemakeExecutor, "run", patched_run)
        df_out = srz.process(loc=outdir, workflow=workflow)
        assert len(df_out.index) == 2

    def test_process_dry_run(self, tmpdir, monkeypatch):
        """Test `.process()` method with dry run."""
        config = self.config.copy(deep=True)
        config.run.execution_mode = ExecModes.PREPARE_RUN
        df = self.data.copy(deep=True)
        outdir = Path(tmpdir)
        workflow = create_snakefile(dir=outdir, name="Snakefile")
        srp = SRP()
        srp.append(df)
        srz = SRZ(config=config, records=srp.records)
        df_out = srz.process(loc=outdir, workflow=workflow)
        assert len(df_out.index) == 2
