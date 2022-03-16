"""Module for running snakemake."""

import subprocess
import os

from zarp.config.models import Run


class SnakemakeExecutor:
    """Run snakemake with system calls."""

    def __init__(self, run: Run) -> None:
        self.run_dict = run.dict()
        self.success = None

    def prepare_run(self, snkfile: str, workdir: str) -> None:
        """Configure list of strings for execution.
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
        self.run_list = run_list

    def validate_run(self) -> bool:
        """Ensure the list of strings is a correct Snakemake call.
        """
        pass

    def run(self) -> None:
        """Execute Snakemake with system call."""
        try:
            completed = subprocess.run(self.run_list)
            if completed.returncode == 0:
                print("Successfully finished!")
                self.success = True
            else:
                print(f"Snakemake not finished: {completed}")
                self.success = False
        except subprocess.CalledProcessError as e:
            print(e)
    
    def get_success(self) -> bool:
        return self.success