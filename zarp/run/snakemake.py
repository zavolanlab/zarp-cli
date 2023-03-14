"""Module for executing Snakemake workflows."""

from pathlib import Path
import subprocess
from typing import Dict, List, Optional

from zarp.config.enums import SnakemakeRunState
from zarp.config.models import InitRun


class SnakemakeExecutor:
    """Run snakemake with system calls.

    Args:
        run_config: Run-specific parameters.

    Attributes:
        run_config: Run-specific parameters.
        success: Indicator for successful snakemake run.
        run_list: Command used to to trigger Snakemake run.  Initially, i.e.,
            before the command was assembled, an empty list.

    Example:
        The example below expects a valid `Snakefile` (e.g. `touch Snakefile`)
        in the current working directory.
        It constructs a run with default values and runs it.
        >>> my_run = SnakemakeExecutor(run_config=InitRun())
        >>> my_run.prepare_run(snakefile="Snakefile")
        >>> my_run.run()
        >>> assert my_run.success == SnakemakeRunState.SUCCESS
    """

    def __init__(self, run_config: InitRun) -> None:
        """Class constructor."""
        self.run_config: InitRun = run_config
        self.run_state: SnakemakeRunState = SnakemakeRunState.UNKNOWN
        self.command: List[str] = []

    def set_command(
        self,
        snakefile: Path,
        config_file: Path,
        config: Optional[Dict] = None,
    ) -> None:
        """Compile Snakemake command as list of strings.

        Args:
            snakefile: Path to Snakemake workflow file.
            config_file: Either the path to the configuration file for the
                Snakemake workflow (if `config` is `None`), or the path suffix,
                relative to the run directory, where the configuration file is
                to be written, based on the contents of `config`). file is to be stored (if `config`)
            config: Configuration for Snakemake workflow.
        """
        cmd_ls = ["snakemake"]
        cmd_ls.extend(["--snakefile", str(snakefile)])
        cmd_ls.extend(["--cores", str(self.run_config.cores)])
        if self.run_config.working_directory is not None:
            cmd_ls.extend(
                ["--directory", str(self.run_config.working_directory)]
            )
        if self.run_config.dependency_embedding == "CONDA":
            cmd_ls.extend(["--use-conda"])
        elif self.run_config.dependency_embedding == "SINGULARITY":
            cmd_ls.extend(["--use-singularity"])
        if self.run_config.execution_mode in [
            "DRY_RUN",
            "PREPARE_RUN",
        ]:
            cmd_ls.extend(["--dry-run"])
        if self.run_config.snakemake_config is not None:
            cmd_ls.extend(
                ["--configfile", str(self.run_config.snakemake_config)]
            )
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
