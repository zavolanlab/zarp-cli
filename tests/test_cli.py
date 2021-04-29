"""Unit tests for module `zarp.cli`."""

import importlib.util
from pathlib import Path
import sys

import pytest

from zarp.config.cli import (
    main,
    parse_args,
)

# Test parameters
MAIN_FILE = Path(__file__).parents[1].absolute() / "zarp" / "config" / "cli.py"
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


class TestParseArgs:
    """Test `parse_args()` function."""

    def test_help_option(self, monkeypatch):
        """Test help option."""
        monkeypatch.setattr(
            sys, 'argv', [
                'cli',
                '--help',
            ]
        )
        with pytest.raises(SystemExit) as exc:
            assert parse_args()
        assert exc.value.code == 0


