"""Unit tests for ``:mod:zarp.plugins.sample_processors.htsinfer``."""

import logging
from pathlib import Path
import shutil

import pandas as pd

from zarp.config.models import (
    Config,
    ConfigRun,
    ConfigSample,
    ConfigUser,
    ExecModes,
)
from zarp.plugins.sample_processors.htsinfer import (
    SampleProcessorHTSinfer as HTS,
)
from zarp.samples.sample_record_processor import SampleRecordProcessor as SRP
from zarp.snakemake.run import SnakemakeExecutor

from tests.utils import create_snakefile

LOGGER = logging.getLogger(__name__)


class TestSampleProcessorHTSinfer:
    """Test ``:cls:zarp.plugins.sample_processors.htsinfer`` class."""

    config = Config(
        run=ConfigRun(
            zarp_directory=Path(__file__).parents[2] / "files" / "zarp",
            genome_assemblies_map=Path(__file__).parents[2]
            / "files"
            / "genome_assemblies.csv",
        ),
        sample=ConfigSample(),
        user=ConfigUser(),
    )
    data = pd.DataFrame(
        data={
            "sample": ["SRR1", "SRR2"],
            "fq1": [Path("path"), Path("path1")],
            "fq2": ["", Path("path2")],
        }
    )

    def test_init(self):
        """Test constructor."""
        config = self.config.copy(deep=True)
        df = self.data.copy(deep=True)
        srp = SRP()
        srp.append(df)
        hts = HTS(config=config, records=srp.records)
        assert hasattr(hts, "records")
        assert len(hts.records.index) == 2

    def test_process(self, tmpdir, monkeypatch):
        """Test `.process()` method."""
        config = self.config.copy(deep=True)
        df = self.data.copy(deep=True)
        outdir = Path(tmpdir)
        workflow = create_snakefile(dir=outdir, name="Snakefile")
        srp = SRP()
        srp.append(df)
        hts = HTS(config=config, records=srp.records)

        def patched_run(self, cmd) -> None:
            """Patch `run()` method."""
            run_dir = Path(tmpdir) / "runs" / config.run.identifier
            src = Path(__file__).parents[2] / "files" / "sample_table.tsv"
            dst_in = run_dir / "samples_htsinfer.tsv"
            dst_out = run_dir / "samples_result.tsv"
            print(dst_out)
            shutil.copyfile(src, dst_in)
            shutil.copyfile(src, dst_out)

        monkeypatch.setattr(SnakemakeExecutor, "run", patched_run)
        df_out = hts.process(loc=outdir, workflow=workflow)
        assert len(df_out.index) == 5

    def test_process_empty(self, tmpdir, caplog):
        """Test `.process()` method with no records."""
        config = self.config.copy(deep=True)
        outdir = Path(tmpdir)
        workflow = create_snakefile(dir=outdir, name="Snakefile")
        df = pd.DataFrame(data={"sample": [], "fq1": [], "fq2": []})
        hts = HTS(config=config, records=df)
        assert len(hts.records.index) == 0
        with caplog.at_level(logging.DEBUG):
            df_out = hts.process(loc=outdir, workflow=workflow)
        assert len(df_out.index) == 0
        assert "No metadata to infer." in caplog.text

    def test_process_dry_run(self, tmpdir, monkeypatch):
        """Test `.process()` method with dry run."""
        config = self.config.copy(deep=True)
        config.run.execution_mode = ExecModes.DRY_RUN
        df = self.data.copy(deep=True)
        outdir = Path(tmpdir)
        workflow = create_snakefile(dir=outdir, name="Snakefile")
        srp = SRP()
        srp.append(df)
        hts = HTS(config=config, records=srp.records)

        def patched_run(self, cmd) -> None:
            """Patch `run()` method."""
            run_dir = Path(tmpdir) / "runs" / config.run.identifier
            src = Path(__file__).parents[2] / "files" / "sample_table.tsv"
            dst_in = run_dir / "samples_htsinfer.tsv"
            dst_out = run_dir / "samples_result.tsv"
            shutil.copyfile(src, dst_in)
            shutil.copyfile(src, dst_out)

        monkeypatch.setattr(SnakemakeExecutor, "run", patched_run)
        df_out = hts.process(loc=outdir, workflow=workflow)
        assert len(df_out.index) == 5

    def test__configure_run(self, tmpdir):
        """Test `._configure_run()` method."""
        config = self.config.copy(deep=True)
        config.run.identifier = "ABCDE"
        df = self.data.copy(deep=True)
        run_dir = Path(tmpdir) / "runs" / config.run.identifier
        out_dir = Path(tmpdir) / "results"
        sample_table = Path(run_dir) / "samples_htsinfer.tsv"
        srp = SRP()
        srp.append(df)
        hts = HTS(config=config, records=srp.records)
        hts._configure_run(root_dir=Path(tmpdir))
        assert Path(run_dir).exists()
        assert Path(out_dir).exists()
        assert Path(sample_table).exists()

    def test__prepare_sample_table(self, tmpdir):
        """Test `._prepare_sample_table()` method."""
        config = self.config.copy(deep=True)
        df = self.data.copy(deep=True)
        sample_table = Path(tmpdir) / "samples_htsinfer.tsv"
        srp = SRP()
        srp.append(df)
        hts = HTS(config=config, records=srp.records)
        hts._prepare_sample_table(sample_table=sample_table)
        assert (Path(tmpdir) / "samples_htsinfer.tsv").exists()
