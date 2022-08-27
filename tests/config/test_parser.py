"""Unit tests for ``:mod:zarp.config.parser``."""

from pathlib import Path
from typing import (
    Dict,
    List,
)

import pytest

from tests.utils import (
    RaiseError,
)
from zarp.config.parser import ConfigParser

TEST_FILES_DIR: Path = Path(__file__).parents[1].absolute() / "files"


class TestConfigParser:
    """Test ``cls:zarp.config.init.ConfigParser`` class."""

    def test_init_str(self):
        """Test class initialization with string argument."""
        config_file: str = str(TEST_FILES_DIR / "config_valid.yaml")
        parser: ConfigParser = ConfigParser(config_file=config_file)
        assert hasattr(parser, "config")
        assert parser.config_file == Path(config_file)

    def test_init_path(self):
        """Test class initialization with string argument."""
        config_file: Path = TEST_FILES_DIR / "config_valid.yaml"
        parser: ConfigParser = ConfigParser(config_file=config_file)
        assert hasattr(parser, "config")
        assert parser.config_file == config_file

    def test_set_from_file_valid(self):
        """Test method `.set_from_file()` with valid file."""
        config_file: Path = TEST_FILES_DIR / "config_valid.yaml"
        parser: ConfigParser = ConfigParser(config_file=config_file)
        assert parser.config.user.author is None
        parser.set_from_file()
        assert parser.config.user.author == "test_author"

    def test_set_from_file_invalid(self, monkeypatch):
        """Test method `.set_from_file()` with invalid file."""
        config_file: Path = TEST_FILES_DIR / "config_invalid.yaml"
        parser: ConfigParser = ConfigParser(config_file=config_file)
        monkeypatch.setattr(
            "zarp.config.parser.ConfigParser.parse_yaml",
            lambda *args, **kwargs: None,
        )
        with pytest.raises(ValueError):
            parser.set_from_file()

    def test_update_from_mapping_valid(self):
        """Test method `.update_from_mapping()` with valid mapping."""
        config_file: Path = TEST_FILES_DIR / "config_valid.yaml"
        parser: ConfigParser = ConfigParser(config_file=config_file)
        config_mapping: Dict = {"user": {"author": "test_author"}}
        assert parser.config.user.author is None
        parser.update_from_mapping(config_mapping=config_mapping)
        assert parser.config.user.author == "test_author"

    def test_update_from_mapping_invalid(self):
        """Test method `.update_from_mapping()` with invalid mapping."""
        config_file: Path = TEST_FILES_DIR / "config_valid.yaml"
        parser: ConfigParser = ConfigParser(config_file=config_file)
        config_mapping: List = ["NOT_A_MAPPING"]
        with pytest.raises(ValueError):
            parser.update_from_mapping(
                config_mapping=config_mapping  # type: ignore
            )

    def test_parse_yaml_valid_yaml(self):
        """Test method `.parse_yaml()` with valid YAML contents."""
        config_file: Path = TEST_FILES_DIR / "config_valid.yaml"
        ret = ConfigParser.parse_yaml(path=config_file)
        assert isinstance(ret, dict)
        assert ret["user"]["author"] == "test_author"

    def test_parse_yaml_invalid_yaml(self):
        """Test method `.parse_yaml()` with invalid YAML contents."""
        config_file: Path = TEST_FILES_DIR / "config_invalid.yaml"
        with pytest.raises(ValueError):
            ConfigParser.parse_yaml(path=config_file)

    def test_parse_yaml_not_found(self, monkeypatch):
        """Test method `.parse_yaml()` when input file is not readable."""
        config_file: Path = TEST_FILES_DIR / "config_valid.yaml"
        monkeypatch.setattr("builtins.open", RaiseError(exc=FileNotFoundError))
        with pytest.raises(OSError):
            ConfigParser.parse_yaml(path=config_file)

    def test_parse_yaml_not_readable(self, monkeypatch):
        """Test method `.parse_yaml()` when input file is not readable."""
        config_file: Path = TEST_FILES_DIR / "config_valid.yaml"
        monkeypatch.setattr("builtins.open", RaiseError(exc=OSError))
        with pytest.raises(OSError):
            ConfigParser.parse_yaml(path=config_file)
