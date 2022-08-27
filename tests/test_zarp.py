"""Unit tests for ``:mod:zarp.zarp``."""

from pathlib import Path

import pytest

from zarp.config.models import Config
from zarp.zarp import ZARP


class TestZarp:
    """Test ``:cls:zarp.zarp.ZARP` class."""

    def test_constructor_without_args(self):
        """Test class constructor without args."""
        zarp = ZARP()
        assert hasattr(zarp, "config")
        assert isinstance(zarp.config, Config)

    def test_constructor_with_args(self):
        """Test class constructor with args."""
        config = Config()
        zarp = ZARP(config=config)
        assert hasattr(zarp, "config")
        assert isinstance(zarp.config, Config)

    def test_set_up_run_env(self, tmpdir):
        """Test setting up run environment."""
        config = Config()
        config.run.working_directory = tmpdir
        zarp = ZARP(config=config)
        zarp.set_up_run()
        assert hasattr(zarp, "config")
        assert isinstance(zarp.config, Config)
        assert zarp.config.run.working_directory == tmpdir

    def test_set_up_run_env_work_dir_unset(self, monkeypatch, tmpdir):
        """Test setting up run environment when working directory is unset."""
        config = Config()
        config.run.working_directory = None
        monkeypatch.setattr("os.getcwd", lambda: tmpdir)
        zarp = ZARP(config=config)
        zarp.set_up_run()
        assert hasattr(zarp, "config")
        assert isinstance(zarp.config, Config)
        assert zarp.config.run.working_directory == tmpdir

    def test_set_up_run_env_identifier_set(self, tmpdir):
        """Test setting up run environment when run identifier is set."""
        identifier = "test"
        config = Config()
        config.run.working_directory = tmpdir
        config.run.identifier = identifier
        zarp = ZARP(config=config)
        zarp.set_up_run()
        assert hasattr(zarp, "config")
        assert isinstance(zarp.config, Config)
        assert zarp.config.run.identifier == identifier

    def test_set_up_run_env_identifier_unset(self, tmpdir):
        """Test setting up run environment when run identifier is unset."""
        config = Config()
        config.run.working_directory = tmpdir
        config.run.identifier = None
        zarp = ZARP(config=config)
        zarp.set_up_run()
        assert hasattr(zarp, "config")
        assert isinstance(zarp.config, Config)
        assert zarp.config.run.identifier is not None
        assert len(zarp.config.run.identifier) == 6

    def test_set_up_run_env_run_dir_exists(self, tmpdir):
        """Test setting up run environment when run directory exists."""
        config = Config()
        config.run.working_directory = tmpdir
        config.run.identifier = "test"
        tmpdir.mkdir(config.run.identifier)
        zarp = ZARP(config=config)
        with pytest.raises(FileExistsError):
            zarp.set_up_run()

    def test_process_samples_seq_archive_id_ref(self, tmpdir):
        """Test processing samples with sequence archive identifier ref."""
        config = Config()
        config.run.working_directory = tmpdir
        config.run.identifier = "test"
        config.ref = ["SRR1234567"]
        zarp = ZARP(config=config)
        zarp.set_up_run()
        zarp.process_samples()
        assert Path(tmpdir / "test" / "samples.tsv").is_file()

    def test_process_samples_invalid_ref(self, tmpdir):
        """Test processing samples with invalid ref."""
        config = Config()
        config.run.working_directory = tmpdir
        config.run.identifier = "test"
        config.ref = ["invalid&name@/path/does/not/exist"]
        zarp = ZARP(config=config)
        zarp.set_up_run()
        with pytest.raises(ValueError):
            zarp.process_samples()
