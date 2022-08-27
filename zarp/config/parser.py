"""Configuration parser."""

import logging
from pathlib import Path
from typing import (
    Dict,
    Mapping,
    Union,
)

from addict import Dict as Addict  # type: ignore
from pydantic import ValidationError
from yaml import (
    safe_load,
    YAMLError,
)

from zarp.config.models import Config

LOGGER = logging.getLogger(__name__)


class ConfigParser:
    """Configuration parser for ZARP-cli.

    Args:
        config_file: Path to ZARP-cli configuration file.

    Attributes:
        config_file: Path to ZARP-cli configuration file.
        config: ZARP-cli configuration.
    """

    def __init__(
        self,
        config_file: Union[Path, str],
    ):
        """Class constructor."""
        self.config_file: Path = Path(config_file)
        self.config: Config = Config()

    def set_from_file(self) -> None:
        """Set configuration based on configuration file.

        Raises:
            ValueError: Configuration file contains invalid arguments.
        """
        config_dict = self.parse_yaml(path=self.config_file)
        try:
            self.config = Config(**config_dict)
        except (TypeError, ValidationError) as exc:
            raise ValueError(
                "configuration file contains invalid arguments: "
                f"{self.config_file}"
            ) from exc

    def update_from_mapping(
        self,
        config_mapping: Mapping,
    ) -> None:
        """Update ZARP-cli configuration from dictionary.

        Only parameters will be updated for whom arguments are available and
        which are not ``None``.

        Args:
            config_mapping: Mapping of ZARP-cli configuration items.

        Raises:
            ValueError: Configuration could not be updated because either the
                currently set configuration or the configuration dictionary
                are invalid.
        """
        try:
            override = Config(**config_mapping).dict(exclude_none=True)
            config = Addict(self.config.dict())
            config.update(override)
            self.config = Config(**config)
        except (TypeError, ValidationError) as exc:
            raise ValueError(
                "configuration could not be updated; configuration before "
                f"updating: {self.config}; mapping to update the "
                f"configuration with: {config_mapping}"
            ) from exc

    @staticmethod
    def parse_yaml(path: Path) -> Dict:
        """Serialize YAML file contents into a dictionary.

        Args:
            path: Path to YAML file.

        Returns:
            Serialized YAML file contents.

        Raises:
            FileNotFoundError: File does not exist.
            OSError: File could not be read.
            ValueError: File is not valid YAML.
        """
        try:
            with open(path, encoding="utf-8") as _file:
                try:
                    return safe_load(_file)
                except YAMLError as exc:
                    raise ValueError(
                        f"file is not valid YAML: {path}"
                    ) from exc
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"file does not exist: {path}") from exc
        except OSError as exc:
            raise OSError(f"file could not be read: {path}") from exc
