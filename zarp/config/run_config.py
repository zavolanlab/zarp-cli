"""ZARP run config processing."""

import logging
from pathlib import Path
from typing import (
    Dict,
    Optional,
)

from zarp.config.models import (
    ConfigRun,
    ConfigUser,
)


LOGGER = logging.getLogger(__name__)


class RunConfigFileProcessor:  # pylint: disable=too-few-public-methods
    """Process ZARP run configuration files.

    Args:
        run_config: Run configuration parameters.
        user_config: User configuration parameters.

    Attributes:
        run_config: Run configuration parameters.
        user_config: User configuration parameters.
    """

    def __init__(
        self,
        run_config: ConfigRun,
        user_config: ConfigUser,
    ) -> None:
        """Class constructor."""
        self.run_config: ConfigRun = run_config
        self.user_config: ConfigUser = user_config

    def write_run_config(self) -> Path:
        """Write run configuration file.

        Returns:
            Path to run configuration file.

        Raises:
            ValueError: Cannot write table because run directory is not set.
        """
        if self.run_config.run_directory is None:
            raise ValueError(
                "Cannot write sample table, run directory not set."
            )
        path: Path = self.run_config.run_directory / "config.yml"
        content: str = self._get_file_content()
        with open(path, "w", encoding="utf-8") as _file:
            _file.write(content)
        return path

    def _get_file_content(self) -> str:
        """Get file content.

        Returns:
            Multiline string with file content.
        """
        return f"""---
  # Required fields
  {self._get_required_params()}  # Optional fields
{self._get_optional_params()}...
"""

    def _get_required_params(self) -> str:
        """Get required parameters.

        Returns:
            Multiline string with required parameters.

        Raises:
            ValueError: Cannot generate string because run directory is not
                set.
        """
        run_dir: Optional[Path] = self.run_config.run_directory
        if run_dir is None:
            raise ValueError(
                "Cannot write sample table, run directory not set."
            )
        return f"""samples: "{self.run_config.sample_table}"
  output_dir: "{run_dir / 'results'}"
  log_dir: "{run_dir / 'logs'}"
  cluster_log_dir: "{run_dir / 'logs/cluster'}"
  kallisto_indexes: "{run_dir / 'results/kallisto_indexes'}"
  salmon_indexes: "{run_dir / 'results/salmon_indexes'}"
  star_indexes: "{run_dir / 'results/star_indexes'}"
  alfa_indexes: "{run_dir / 'results/alfa_indexes'}"
"""

    def _get_optional_params(self) -> str:
        """Get optional parameters.

        Returns:
            Multiline string with optional parameters.
        """
        optional: Dict = {
            "rule_config": self.run_config.rule_config,
            "report_description": self.run_config.description,
            "report_logo": self.user_config.logo,
            "report_url": self.user_config.urls,
            "author_name": self.user_config.author,
            "author_email": self.user_config.emails,
        }
        param_str: str = ""
        for key, value in optional.items():
            if value is not None:
                if isinstance(value, list):
                    if len(value) > 0:
                        param_str += f"  {key}: {value[0]}\n"
                else:
                    param_str += f"  {key}: {value}\n"
            else:
                LOGGER.debug(
                    "No value available for optional run config parameter:"
                    f" {key}"
                )
        return param_str
