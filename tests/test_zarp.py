"""Unit tests for module `zarp.zarp`."""

import importlib.util
from pathlib import Path
import sys

import pytest

from zarp.zarp import (
    main,
    parse_args,
    setup_logging,
)

# Test parameters
MAIN_FILE = Path(__file__).parents[1].absolute() / "zarp" / "zarp.py"
OPT_LOG_LEVEL = "DEBUG"
OPT_INVALID = "-+-+-"


def test_main_as_script():
    """Run as script."""
    spec = importlib.util.spec_from_file_location('__main__', MAIN_FILE)
    module = importlib.util.module_from_spec(spec)
    with pytest.raises(SystemExit):
        spec.loader.exec_module(module)


class TestMain:
    """Test `main()` function."""

    def test_main(self):
        """Call without args."""
        with pytest.raises(SystemExit):
            main()

    def test_main_with_args(self, monkeypatch):
        """Call with args."""
        monkeypatch.setattr(
            sys, 'argv', [
                'zarp',
                '--init',
            ]
        )
        assert main() is None


class TestParseArgs:
    """Test `parse_args()` function."""

    def test_help_option(self):
        """Test help option."""
        with pytest.raises(SystemExit):
            assert parse_args(["--help"])

    def test_no_args(self):
        """Call without args."""
        with pytest.raises(SystemExit):
            parse_args([])

    def test_invalid_option(self):
        """Test invalid argument."""
        with pytest.raises(SystemExit):
            assert parse_args([OPT_INVALID])


class TestSetupLogging:
    """Test `setup_logging()` function."""

    def test_log_level_no_args(self):
        "Call without args."
        setup_logging()

    def test_log_level(self):
        "Manually set log level."
        setup_logging(verbosity=OPT_LOG_LEVEL)
        setup_logging(verbosity="INFO")
