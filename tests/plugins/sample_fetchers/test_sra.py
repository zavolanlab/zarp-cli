"""Unit tests for ``:mod:zarp.plugins.sample_fetchers.sra``."""

import logging
from pathlib import Path
import shutil

import pandas as pd

from zarp.config.models import Config, ConfigRun, ConfigSample, ConfigUser
from zarp.plugins.sample_fetchers.sra import SampleFetcherSRA as SRA
from zarp.samples.sample_record_processor import SampleRecordProcessor as SRP
from zarp.snakemake.run import SnakemakeExecutor

from tests.utils import create_snakefile

LOGGER = logging.getLogger(__name__)


class TestSampleFetcherSRA:
    """Test ``:cls:zarp.plugins.sample_fetchers.SampleFetcherSRA`` class."""

    config = Config(
        run=ConfigRun(zarp_directory=Path(__file__).parent / "files" / "zarp"),
        sample=ConfigSample(),
        user=ConfigUser(),
    )
    data = pd.DataFrame(
        data={
            "identifier": ["SRR9004891", "ERR2248142", "no_sra"],
            "type": [
                "REMOTE_LIB_SRA",
                "REMOTE_LIB_SRA",
                "INVALID",
            ],
        }
    )

    def test_init(self):
        """Test constructor."""
        config = self.config.copy()
        df = self.data.copy()
        srp = SRP()
        srp.append(df)
        sra = SRA(config=config, records=srp.records)
        assert hasattr(sra, "records")
        assert len(sra.records.index) == 2

    def test_process(self, tmpdir, monkeypatch):
        """Test `.process()` method."""
        config = self.config.copy()
        df = self.data.copy()
        outdir = Path(tmpdir)
        workflow = create_snakefile(dir=outdir, name="Snakefile")
        srp = SRP()
        srp.append(df)
        sra = SRA(config=config, records=srp.records)

        def patched_run(self, cmd) -> None:
            """Patch `run()` method."""
            run_dir = Path(tmpdir) / "runs" / config.run.identifier
            src = Path(__file__).parents[2] / "files" / "sra_table.tsv"
            dst_in = run_dir / "samples_local.tsv"
            dst_out = run_dir / "samples_remote.tsv"
            shutil.copyfile(src, dst_in)
            shutil.copyfile(src, dst_out)

        monkeypatch.setattr(SnakemakeExecutor, "run", patched_run)
        df_out = sra.process(loc=outdir, workflow=workflow)
        assert len(df_out.index) == 4
        assert df_out.loc[0, "identifier"] == "SRR1234567"

    def test_process_empty(self, tmpdir, caplog):
        """Test `.process()` method with no records."""
        config = self.config.copy()
        outdir = Path(tmpdir)
        workflow = create_snakefile(dir=outdir, name="Snakefile")
        df = pd.DataFrame(data={"identifier": ["no_sra"], "type": ["INVALID"]})
        sra = SRA(config=config, records=df)
        assert len(sra.records.index) == 0
        with caplog.at_level(logging.DEBUG):
            df_out = sra.process(loc=outdir, workflow=workflow)
        assert len(df_out.index) == 0
        assert "No remote libraries to fetch" in caplog.text

    def test__select_records(self):
        """Test `._select_records()` method."""
        config = self.config.copy()
        df = self.data.copy()
        df_set = self.data.copy()
        srp = SRP()
        srp.append(df)
        sra = SRA(config=config, records=srp.records)
        sra.records = df_set
        assert len(sra.records.index) == 3
        sra._select_records()
        assert len(sra.records.index) == 2

    def test__configure_run(self, tmpdir):
        """Test `._configure_run()` method."""
        config = self.config.copy()
        df = self.data.copy()
        run_dir = Path(tmpdir) / "runs" / config.run.identifier
        out_dir = Path(tmpdir) / "sra"
        cluster_log_dir = Path(tmpdir) / "logs" / "cluster"
        config_file = Path(run_dir) / "config.yaml"
        sample_table = Path(run_dir) / "samples_remote.tsv"
        srp = SRP()
        srp.append(df)
        sra = SRA(config=config, records=srp.records)
        sra._configure_run(root_dir=Path(tmpdir))
        assert Path(run_dir).exists()
        assert Path(out_dir).exists()
        assert Path(cluster_log_dir).exists()
        assert Path(config_file).exists()
        assert Path(sample_table).exists()

    def test__prepare_sample_table(self, tmpdir):
        """Test `._prepare_sample_table()` method."""
        config = self.config.copy()
        df = self.data.copy()
        sample_table = Path(tmpdir) / "samples_remote.tsv"
        srp = SRP()
        srp.append(df)
        sra = SRA(config=config, records=srp.records)
        sra._prepare_sample_table(sample_table=sample_table)
        assert (Path(tmpdir) / "samples_remote.tsv").exists()

    def test__process_sample_table(self, tmpdir, caplog):
        """Test `._process_sample_table()` method."""
        config = self.config.copy()
        df = self.data.copy()
        sample_table = Path(tmpdir) / "samples_remote.tsv"
        srp = SRP()
        srp.append(df)
        sra = SRA(config=config, records=srp.records)
        sra._prepare_sample_table(sample_table=sample_table)
        with caplog.at_level(logging.DEBUG):
            df_proc = sra._process_sample_table(sample_table=sample_table)
        assert len(df_proc.index) == 0
        assert "No FASTQ paths available" in caplog.text
