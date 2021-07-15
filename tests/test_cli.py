"""Unit tests for module `zarp.cli`."""

import importlib.util
from pathlib import Path
import sys

import pytest

from zarp.config.cli import (
    main,
    parse_args,
    setup_logging,
)

# Test parameters
MAIN_FILE = Path(__file__).parents[1].absolute() / "zarp" / "config" / "cli.py"
OPT_LOG_LEVEL = "DEBUG"
OPT_INVALID = "-+-+-"


def test_main_as_script():
    """Run as script."""
    spec = importlib.util.spec_from_file_location('__main__', MAIN_FILE)
    module = importlib.util.module_from_spec(spec)  # type: ignore
    with pytest.raises(SystemExit):
        spec.loader.exec_module(module)  # type: ignore


class TestMain:
    """Test `main()` function."""

    def test_main(self):
        """Call without args."""
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1

    def test_main_with_args(self, monkeypatch):
        """Call with args."""
        monkeypatch.setattr(
            sys, 'argv', [
                'zarp',
                'path',
            ]
        )
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0

    def test_main_with_args_init(self, monkeypatch):
        """Call with args."""
        monkeypatch.setattr(
            sys, 'argv', [
                'zarp',
                '--init',
            ]
        )
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0

    def test_keyboard_interrupt(self, monkeypatch):
        """Test keyboard interrupt."""

        class RaiseValueError:
            def __init__(self, *args, **kwargs):
                raise ValueError

        monkeypatch.setattr(
            'builtins.KeyboardInterrupt',
            ValueError,
        )
        monkeypatch.setattr(
            'zarp.config.cli.parse_args',
            RaiseValueError,
        )
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code >= 128


class TestParseArgs:
    """Test `parse_args()` function."""

    def test_help_option(self, monkeypatch):
        """Test help option."""
        with pytest.raises(SystemExit) as exc:
            parse_args(["--help"])
        assert exc.value.code == 0

    def test_no_args(self):
        """Call without args."""
        with pytest.raises(SystemExit) as exc:
            parse_args([])
        assert exc.value.code == 1

    def test_invalid_option(self):
        """Test invalid argument."""
        with pytest.raises(SystemExit) as exc:
            parse_args([OPT_INVALID])
        assert exc.value.code == 2

    def test_one_sample(self):
        """Call with one positional arg."""
        args = parse_args(["path1"])
        assert args.samples == [Path("path1"), None]

    def test_two_samples(self):
        """Call with two positional args."""
        args = parse_args(["path1", "path2"])
        assert args.samples == [Path("path1"), Path("path2")]

    def test_too_many_samples(self):
        """Call with too many (2+) positional args."""
        with pytest.raises(SystemExit):
            parse_args(["path1", "path2", "path3"])


class TestSetupLogging:
    """Test `setup_logging()` function."""

    def test_log_level_no_args(self):
        "Call without args."
        setup_logging()

    def test_log_level(self):
        "Manually set log level."
        setup_logging(verbosity=OPT_LOG_LEVEL)
