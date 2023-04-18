"""Snakemake config file processor."""

import logging

import yaml

from zarp.config.models import ConfigFileContent

LOGGER = logging.getLogger(__name__)


class ConfigFileProcessor:
    """Write Snakemake configuration files.

    Args:
        content: Configuration file contents.

    Attributes:
        content: Configuration file contents.
    """

    def __init__(self) -> None:
        """Class constructor method."""
        self.content: ConfigFileContent = ConfigFileContent()

    def set_content(self, content: ConfigFileContent) -> None:
        """Set content from object.

        Args:
            content: ``ConfigFileContent`` object.
        """
        self.content = content

    def write(self, path) -> None:
        """Write Snakemake configuration file in YAML format.

        Args:
            path: Path to run configuration file.
        """
        with open(path, "w", encoding="utf-8") as _file:
            yaml.dump(self.content.dict(), _file)
