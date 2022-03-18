"""Module for running snakemake."""

import subprocess
import os

from zarp.config.models import Run


class SnakemakeExecutor:
    """Run snakemake with system calls.
    
    Args:
        run (Run): Run-specific parameters.

    Attributes:
        run_dict (dict): Dictionary with run-specific parameters.
        success (bool): Indicator for successful snakemake run.
        run_list (list): List containing strings for snakemake call.
    
    Example:
        The example below expects a valid `Snakefile` in the current working
        directory. It constructs a run with default values and runs it. 
        >>> mysnk = SnakemakeExecutor(zarp.config.models.Run())
        >>> mysnk.prepare_run(snkfile = "Snakefile", workdir = ".")
        >>> mysnk.run()
        >>> assert mysnk.get_success()

    """

    def __init__(self, run: Run) -> None:
        """Class constructor."""
        self.run_dict = run.dict()
        self.success = None
        self.run_list = []

    def set_run_list(self, run_list: list) -> None:
        """Set run list."""
        self.run_list = run_list

    def get_run_list(self) -> list:
        """Get run list.
        
        Returns:
            run_list (list): list of strings for system call.
        
        """
        return self.run_list

    def prepare_run(self, snkfile: str, workdir: str) -> None:
        """Configure list of strings for execution.

        Args:
            snkfile (str): Path to Snakefile.
            workdir (str): Path to workdir.
        
        Raises:
            KeyError: If `execution_profile` not in run_dict.

        """
        run_list = ["snakemake"]
        # Snakemake config
        run_list.extend(["--snakefile", snkfile])
        run_list.extend(["--cores", str(self.run_dict["cores"])])
        # run_list.extend(["--config", f"workdir={workdir}"])
        # execution profile
        if self.run_dict['execution_profile'] == "local-conda":
            prof = ["--profile", os.path.join("submodules", "zarp", "profiles", "local-conda")]
            run_list.extend(prof)
        self.set_run_list(run_list)

    def validate_run(self) -> bool:
        """Ensure the list of strings is a correct Snakemake call.

        Returns:
            bool: True, if constructed run_list is a valid snakemake call, 
                False otherwise.

        """
        if len(self.run_list) == 0:
            return False
        else:
            # in minimum snakemake command must be called
            if self.run_list[0] == "snakemake":
                return True

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
        except subprocess.CalledProcessError as e:
            self.success = False
            raise e
    
    def get_success(self) -> bool:
        """Obtain whether run successful or not.

        If not yet run, success == None.

        Returns:
            bool: True, if Snakemake exited with code 0, False otherwise.
        """
        return self.success