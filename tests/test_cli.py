"""Unit tests for ``:mod:zarp.cli``."""

import importlib.util
from pathlib import Path
from shutil import copyfile
import sys

import pytest

from tests.utils import RaiseError
from zarp.cli import (
    main,
    setup_logging,
)
from zarp.config.init import Initializer
from zarp.config.parser import ConfigParser
from zarp.zarp import ZARP

TEST_FILE_DIR: Path = Path(__file__).parent.absolute() / "files"
CONFIG_FILE: Path = TEST_FILE_DIR / "config_valid.yaml"


def test_main_as_script():
    """Run as script."""
    MAIN_FILE = Path(__file__).parents[1].absolute() / "zarp" / "cli.py"
    spec = importlib.util.spec_from_file_location("__main__", MAIN_FILE)
    module = importlib.util.module_from_spec(spec)  # type: ignore
    with pytest.raises(SystemExit):
        spec.loader.exec_module(module)  # type: ignore


class TestMain:
    """Test `main()` function."""

    def test_normal_mode_without_args(self):
        """Call without args."""
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1

    def test_normal_mode_with_args(self, monkeypatch, tmpdir):
        """Call with args."""
        TMP_CONFIG_FILE = Path(tmpdir / "config.yaml")
        copyfile(CONFIG_FILE, TMP_CONFIG_FILE)
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "zarp",
                "SRR1234567",
                "--config-file",
                str(TMP_CONFIG_FILE),
                "--working-directory",
                str(tmpdir),
            ],
        )
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0

    def test_normal_mode_with_runtime_error(self, monkeypatch, tmpdir):
        """Call with runtime error being raised."""
        TMP_CONFIG_FILE = Path(tmpdir / "config.yaml")
        copyfile(CONFIG_FILE, TMP_CONFIG_FILE)
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "zarp",
                "SRR1234567",
                "--config-file",
                str(TMP_CONFIG_FILE),
            ],
        )
        monkeypatch.setattr(ZARP, "set_up_run", RaiseError(exc=ValueError))
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1

    def test_init_mode(self, monkeypatch, tmpdir):
        """Test init mode."""

        def patched_set_from_user_input(self):
            pass

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "zarp",
                "--init",
                "--config-file",
                str(tmpdir / "config.yaml"),
            ],
        )
        monkeypatch.setattr(
            Initializer,
            "set_from_user_input",
            patched_set_from_user_input,
        )
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0

    def test_init_mode_no_default_config(self, monkeypatch, tmpdir):
        """Test init mode when no default config file is available."""

        def patched_set_from_user_input(self):
            pass

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "zarp",
                "SRR1234567",
                "--config-file",
                str(tmpdir / "config.yaml"),
            ],
        )
        monkeypatch.setattr(
            Initializer,
            "set_from_user_input",
            patched_set_from_user_input,
        )
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0

    def test_init_mode_write_error(self, monkeypatch, tmpdir):
        """Test init mode with write error."""

        def patched_set_from_user_input(self):
            pass

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "zarp",
                "--init",
                "--config-file",
                str(tmpdir / "config.yaml"),
            ],
        )
        open(tmpdir / "config.yaml", "w", encoding="utf-8").close()
        monkeypatch.setattr(
            Initializer,
            "set_from_user_input",
            patched_set_from_user_input,
        )
        monkeypatch.setattr(
            Initializer,
            "write_yaml",
            RaiseError(exc=OSError),
        )
        monkeypatch.setattr(ConfigParser, "parse_yaml", lambda path: {})
        with pytest.raises(OSError):
            main()

    def test_help_mode(self, monkeypatch):
        """Test help mode."""
        monkeypatch.setattr(sys, "argv", ["zarp", "--help"])
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0

    def test_version_mode(self, monkeypatch):
        """Test version mode."""
        monkeypatch.setattr(sys, "argv", ["zarp", "--version"])
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0

    def test_keyboard_interrupt(self, monkeypatch):
        """Test keyboard interrupt."""
        monkeypatch.setattr(sys, "argv", ["zarp", "SRR1234567"])
        monkeypatch.setattr(
            "zarp.cli.setup_logging", RaiseError(exc=KeyboardInterrupt)
        )
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code >= 128


class TestSetupLogging:
    """Test `setup_logging()` function."""

    def test_log_level_no_args(self):
        """Call without args."""
        setup_logging()

    def test_log_level(self):
        """Manually set log level."""
        setup_logging(verbosity="DEBUG")
