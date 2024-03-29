"""Unit tests for ``:mod:zarp.zarp``."""

from pathlib import Path

import pytest

from zarp.config.enums import ExecModes
from zarp.config.models import Config, ConfigRun, ConfigSample, ConfigUser
from zarp.zarp import ZARP


class TestZarp:
    """Test ``:cls:zarp.zarp.ZARP` class."""

    config = Config(
        run=ConfigRun(
            zarp_directory=Path(__file__).parent / "files" / "zarp",
            genome_assemblies_map=Path(__file__).parent
            / "files"
            / "genome_assemblies.csv",
        ),
        sample=ConfigSample(),
        user=ConfigUser(),
    )

    def test_constructor_without_args(self):
        """Test class constructor without args."""
        with pytest.raises(TypeError):
            zarp = ZARP()  # type: ignore  # noqa: F841

    def test_constructor_with_args(self):
        """Test class constructor with args."""
        config = self.config.copy(deep=True)
        zarp = ZARP(config=config)
        assert hasattr(zarp, "config")
        assert isinstance(zarp.config, Config)

    def test_set_up_run_env(self, tmpdir):
        """Test setting up run environment."""
        config = self.config.copy(deep=True)
        config.run.working_directory = tmpdir
        zarp = ZARP(config=config)
        zarp.set_up_run()
        assert hasattr(zarp, "config")
        assert isinstance(zarp.config, Config)
        assert zarp.config.run.working_directory == tmpdir

    def test_set_up_run_genome_assemblies_map_file_not_exists(self, tmpdir):
        """Test setting up run environment.

        Genome assemblies map file does not exist at specified location.
        """
        config = self.config.copy(deep=True)
        config.run.working_directory = tmpdir
        config.run.genome_assemblies_map = tmpdir / "genome_assemblies.csv"
        zarp = ZARP(config=config)
        with pytest.raises(FileNotFoundError):
            zarp.set_up_run()

    def test_set_up_run_env_identifier_set(self, tmpdir):
        """Test setting up run environment when run identifier is set."""
        identifier = "ABCDE"
        config = self.config.copy(deep=True)
        config.run.working_directory = tmpdir
        config.run.identifier = identifier
        zarp = ZARP(config=config)
        zarp.set_up_run()
        assert hasattr(zarp, "config")
        assert isinstance(zarp.config, Config)
        assert zarp.config.run.identifier == identifier

    def test_set_up_run_dry_run(self, tmpdir):
        """Test setting up run environment for dry run."""
        config = self.config.copy(deep=True)
        config.run.working_directory = tmpdir
        config.run.execution_mode = ExecModes.DRY_RUN
        zarp = ZARP(config=config)
        zarp.set_up_run()
        assert hasattr(zarp, "config")
        assert isinstance(zarp.config, Config)
        assert zarp.config.run.execution_mode == ExecModes.DRY_RUN.value

    def test_process_samples_abs_file_ref(self, monkeypatch, tmpdir):
        """Test processing samples with absolute local file ref."""
        config = self.config.copy(deep=True)
        config.run.zarp_directory = Path(__file__).parent / "files" / "zarp"
        config.run.identifier = "test"
        config.ref = [str(Path(__file__).parent / "files" / "empty")]
        zarp = ZARP(config=config)
        zarp.set_up_run()
        monkeypatch.setattr("pathlib.Path.cwd", lambda: tmpdir)
        zarp.process_samples()

    def test_process_samples_seq_archive_id_ref(self, tmpdir):
        """Test processing samples with sequence archive identifier ref."""
        config = self.config.copy(deep=True)
        config.run.working_directory = tmpdir
        config.run.zarp_directory = Path(__file__).parent / "files" / "zarp"
        config.run.identifier = "test"
        config.ref = ["SRR1234567"]
        zarp = ZARP(config=config)
        zarp.set_up_run()
        zarp.process_samples()

    def test_process_samples_invalid_ref(self, tmpdir):
        """Test processing samples with invalid ref."""
        config = self.config.copy(deep=True)
        config.run.working_directory = tmpdir
        config.run.identifier = "test"
        config.ref = ["invalid&name@/path/does/not/exist"]
        zarp = ZARP(config=config)
        zarp.set_up_run()

    def test_execute_run(self, tmpdir):
        """Test run execution."""
        config = self.config.copy(deep=True)
        config.run.working_directory = tmpdir
        config.run.zarp_directory = Path(__file__).parent / "files" / "zarp"
        config.run.identifier = "test"
        config.ref = ["SRR1234567"]
        zarp = ZARP(config=config)
        zarp.set_up_run()
        samples = zarp.process_samples()
        zarp.execute_run(samples=samples)
