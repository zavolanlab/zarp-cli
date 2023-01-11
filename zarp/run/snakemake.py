"""Module for executing Snakemake workflows."""

import subprocess
from typing import List, Optional

from zarp.config.models import (ExecModes, InitRun,
                                DependencyEmbeddingStrategies)


class SnakemakeExecutor:
    """Run snakemake with system calls.

    Args:
        run (InitRun): Run-specific parameters.

    Attributes:
        run_dict (dict): Dictionary with run-specific parameters.
        success (bool): Indicator for successful snakemake run.
        run_list (list[str]): List containing strings for snakemake call.

    Example:
        The example below expects a valid `Snakefile` (e.g. `touch Snakefile`)
        in the current working directory.
        It constructs a run with default values and runs it.
        >>> mysnk = SnakemakeExecutor(InitRun())
        >>> mysnk.prepare_run(snkfile = "Snakefile")
        >>> mysnk.run()
        >>> assert mysnk.get_success()

    """

    def __init__(self, run: InitRun) -> None:
        """Class constructor."""
        self.run_dict = run.dict()
        self.success: Optional[bool] = None
        self.run_list: List[str] = []

    def set_run_list(self, run_list: list) -> None:
        """Set run list."""
        self.run_list = run_list

    def get_run_list(self) -> list:
        """Get run list.

        Returns:
            run_list (list): list of strings for system call.

        """
        return self.run_list

    def prepare_run(self, snkfile: str, workdir: str = None) -> None:
        """Configure list of strings for execution.

        Args:
            snkfile (str): Path to Snakefile.
            workdir (str): Optional path to working directory. (default None).

        """
        run_list = ["snakemake"]
        # Snakemake config
        run_list.extend(["--snakefile", snkfile])
        run_list.extend(["--cores", str(self.run_dict["cores"])])
        if workdir is not None:
            run_list.extend(["--directory", workdir])
        # execution profile
        if "execution_profile" in self.run_dict:
            prof = ["--profile", self.run_dict['execution_profile']]
            run_list.extend(prof)
        else:
            # tool packaging (conda or singularity)
            # only applies if execution_profile not defined.
            if (self.run_dict["dependency_embedding"] ==
                    DependencyEmbeddingStrategies.CONDA.value):
                run_list.extend(["--use-conda"])
            if (self.run_dict["dependency_embedding"] ==
                    DependencyEmbeddingStrategies.SINGULARITY.value):
                run_list.extend(["--use-singularity"])
        # execution mode (e.g. dry-run)
        if self.run_dict["execution_mode"] in [ExecModes.DRY_RUN.value,
                                               ExecModes.PREPARE_RUN.value]:
            run_list.extend(["--dry-run"])
        # configfile
        if not self.run_dict["snakemake_config"] is None:
            conf = ["--configfile", self.run_dict["snakemake_config"]]
            run_list.extend(conf)
        self.set_run_list(run_list)

    def validate_run(self) -> bool:
        """Ensure the list of strings is a correct Snakemake call.

        Returns:
            bool: True, if constructed run_list is a valid snakemake call,
                False otherwise.

        """
        valid_run = False
        # in minimum snakemake command must be called
        if len(self.run_list) > 0 and self.run_list[0] == "snakemake":
            valid_run = True
        return valid_run

    def run(self) -> None:
        """Execute Snakemake with system call.

        Run Snakemake with a system call, errors there are not handed over.

        Raises:
            CalledProcessError: by `subprocess.run()`

        """
        try:
            subprocess.run(self.run_list, check=True)
            print("Successfully finished!")
            self.success = True
        except subprocess.CalledProcessError as process_error:
            self.success = False
            raise process_error

    def get_success(self) -> Optional[bool]:
        """Obtain whether run successful or not.

        If not yet run, success == None.

        Returns:
            bool: True, if Snakemake exited with code 0, False otherwise.
        """
        return self.success
