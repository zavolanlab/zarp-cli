"""Module for executing Snakemake workflows."""

from pathlib import Path
import subprocess
from typing import List

from zarp.config.enums import SnakemakeRunState
from zarp.config.models import (
    ExecModes,
    InitRun,
    DependencyEmbeddingStrategies,
)


class SnakemakeExecutor:
    """Run snakemake with system calls.

    Args:
        run_params: Run-specific parameters.

    Attributes:
        run_params: Run-specific parameters.
        success: Indicator for successful snakemake run.
        run_list: Command used to to trigger Snakemake run.  Initially, i.e.,
            before the command was assembled, an empty list.

    Example:
        The example below expects a valid `Snakefile` (e.g. `touch Snakefile`)
        in the current working directory.
        It constructs a run with default values and runs it.
        >>> my_run = SnakemakeExecutor(run_params=InitRun())
        >>> my_run.prepare_run(snakefile="Snakefile")
        >>> my_run.run()
        >>> assert my_run.success == SnakemakeRunState.SUCCESS
    """

    def __init__(self, run_params: InitRun) -> None:
        """Class constructor."""
        self.run_params: InitRun = run_params
        self.success: SnakemakeRunState = SnakemakeRunState.UNKNOWN
        self.command: List[str] = []

    def set_command(self, snakefile: Path) -> None:
        """Compile Snakemake command as list of strings.

        Args:
            snkfile (str): Path to Snakefile.
        """
        cmd_ls = ["snakemake"]
        cmd_ls.extend(["--snakefile", str(snakefile)])
        cmd_ls.extend(["--cores", str(self.run_params.cores)])
        if self.run_params.working_directory is not None:
            cmd_ls.extend(
                ["--directory", str(self.run_params.working_directory)]
            )
        if (
            self.run_params.dependency_embedding
            == DependencyEmbeddingStrategies.CONDA
        ):
            cmd_ls.extend(["--use-conda"])
        elif (
            self.run_params.dependency_embedding
            == DependencyEmbeddingStrategies.SINGULARITY
        ):
            cmd_ls.extend(["--use-singularity"])
        if self.run_params.execution_mode in [
            ExecModes.DRY_RUN,
            ExecModes.PREPARE_RUN,
        ]:
            cmd_ls.extend(["--dry-run"])
        if self.run_params.snakemake_config is not None:
            cmd_ls.extend(["--configfile", self.run_params.snakemake_config])
        self.command = cmd_ls

    def run(self) -> None:
        """Execute Snakemake with system call.

        Run Snakemake with a system call, errors there are not handed over.

        Raises:
            CalledProcessError: If Snakemake or by `subprocess.run()`
        """
        try:
            subprocess.run(self.command, check=True)
            self.success = SnakemakeRunState.SUCCESS
        except subprocess.CalledProcessError as process_error:
            self.success = SnakemakeRunState.ERROR
            raise process_error
