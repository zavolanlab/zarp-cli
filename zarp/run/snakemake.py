"""Module for executing Snakemake workflows."""

import logging
from pathlib import Path
import shutil
import subprocess
from typing import Dict, List, Optional, Union

import yaml

from zarp.config.enums import SnakemakeRunState
from zarp.config.models import ConfigRun
from zarp.utils import generate_id

LOGGER = logging.getLogger(__name__)


class SnakemakeExecutor:
    """Run snakemake with system calls.

    Args:
        run_config: Run-specific parameters.
        workflow_id: Identifier for the workflow.

    Attributes:
        run_config: Run-specific parameters.
        workflow_id: Identifier for the workflow.
        command: Command used to trigger the Snakemake run.
        exec_dir: Directory in which the run is executed.
        run_dir: Directory in which run-specific files are stored.
        config_file: Path to Snakemake configuration file.
        run_state: State of the run.

    Example:
        The example below expects a valid `Snakefile` and a valid YAML
        configuration file for that workflow in the current working directory.
        It constructs a run with default values and runs it.
        >>> my_run = SnakemakeExecutor(run_config=ConfigRun())
        >>> my_run.set_configuration(config="config.yaml")
        >>> my_run.set_command(snakefile=Snakefile")
        >>> my_run.run()
        >>> assert my_run.success == SnakemakeRunState.SUCCESS
    """

    def __init__(
        self,
        run_config: ConfigRun,
        workflow_id: str = generate_id(),
    ) -> None:
        """Class constructor."""
        self.run_config: ConfigRun = run_config
        self.workflow_id: str = workflow_id
        self.command: List[str] = []
        self.exec_dir: Path = Path()
        self.run_dir: Path = Path()
        self.config_file: Path = Path() / "config.yaml"
        self.run_state: SnakemakeRunState = SnakemakeRunState.UNKNOWN

    def setup(self) -> None:
        """Set up Snakemake run."""
        if self.run_config.working_directory is None:
            self.run_config.working_directory = Path.cwd() / "runs"
            self.run_config.working_directory.mkdir(
                parents=True,
                exist_ok=True,
            )
            LOGGER.warning(
                "Working directory not set. Using:"
                f" {self.run_config.working_directory}"
            )
        self.exec_dir = self.run_config.working_directory / self.workflow_id
        if self.run_config.identifier is None:
            raise ValueError("Run identifier not set.")
        self.run_dir = self.exec_dir / "runs" / self.run_config.identifier
        LOGGER.info(f"Run-specific directory: {self.run_dir}")
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.run_dir / "config.yaml"

    def set_configuration_file(
        self,
        config: Optional[Union[Path, Dict]] = None,
    ) -> None:
        """Set configuration file.

        Args:
            config: Either the path to the configuration file for the Snakemake
                workflow, or a dictionary with configuration parameters.
        """
        if config is None:
            config = {}
        self._set_config_file(config=config)

    def set_command(self, snakefile: Path) -> None:
        """Compile Snakemake command as list of strings.

        Args:
            snakefile: Path to Snakemake workflow file.
        """
        cmd_ls = ["snakemake"]
        cmd_ls.extend(["--snakefile", str(snakefile)])
        cmd_ls.extend(["--cores", str(self.run_config.cores)])
        cmd_ls.extend(["--configfile", str(self.config_file)])
        cmd_ls.extend(["--directory", str(self.exec_dir)])
        if self.run_config.execution_mode == "DRY_RUN":
            cmd_ls.append("--dry-run")
        if self.run_config.dependency_embedding == "CONDA":
            cmd_ls.append("--use-conda")
        # Singularity is currently not supported for SRA download workflow
        # Reason: https://github.com/snakemake/snakemake/issues/1521
        elif self.workflow_id == "sra_download":
            cmd_ls.append("--use-conda")
        elif self.run_config.dependency_embedding == "SINGULARITY":
            cmd_ls.append("--use-singularity")
        self.command = cmd_ls

    def run(self) -> None:
        """Execute Snakemake with system call.

        Run Snakemake with a system call, errors there are not handed over.

        Raises:
            CalledProcessError: If Snakemake or by `subprocess.run()`
        """
        try:
            subprocess.run(self.command, check=True)
            self.run_state = SnakemakeRunState.SUCCESS
        except subprocess.CalledProcessError as process_error:
            self.run_state = SnakemakeRunState.ERROR
            raise process_error

    def _set_config_file(self, config: Union[Path, Dict]) -> None:
        """Populate Snakemake configuration file.

        If `config` is a path, the file is copied to the working directory.
        Otherwise the file is created from the configuration parameters.

        Args:
            config: Either the path to a Snakemake configuration file, or a
                dictionary with configuration parameters.

        Raises:
            TypeError: If `config` is neither a path nor a dictionary.
        """
        if isinstance(config, Path):
            shutil.copyfile(config, self.config_file)
        elif isinstance(config, dict):
            with open(self.config_file, "w", encoding="utf-8") as _file:
                yaml.dump(config, _file)
        else:
            raise TypeError(
                "Value of config must be either a path to a configuration "
                " file, or a dictionary with configuration parameters, but is:"
                f" {type(config)}"
            )
