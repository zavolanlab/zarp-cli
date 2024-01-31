"""Module for executing Snakemake workflows."""

import logging
import os
from pathlib import Path
import subprocess
from typing import List, Optional, Union

from zarp.config.enums import SnakemakeRunState
from zarp.config.models import ConfigRun

LOGGER = logging.getLogger(__name__)


class SnakemakeExecutor:
    """Run snakemake with system calls.

    Args:
        run_config: Run-specific parameters.
        exec_dir: Directory in which the run is executed.
        config_file: Path to Snakemake configuration file.
        bind_paths: Paths to bind to Singularity container.

    Attributes:
        run_config: Run-specific parameters.
        exec_dir: Directory in which the run is executed.
        config_file: Path to Snakemake configuration file.
        bind_paths: Paths to bind to Singularity container.
        run_state: State of the run.
    """

    def __init__(
        self,
        run_config: ConfigRun,
        exec_dir: Path = Path.cwd(),
        config_file: Optional[Path] = None,
        bind_paths: Optional[List[Path]] = None,
    ) -> None:
        """Class constructor."""
        self.run_config: ConfigRun = run_config
        self.exec_dir: Path = exec_dir
        self.config_file: Optional[Path] = config_file
        self.bind_paths: Optional[List[Path]] = bind_paths
        self.run_state: SnakemakeRunState = SnakemakeRunState.UNKNOWN

    def compile_command(self, snakefile: Path) -> List[str]:
        """Compile Snakemake command as list of strings.

        Args:
            snakefile: Path to Snakemake descriptor file.
        """
        bind_paths: List[Optional[Union[Path, str]]] = [
            self.exec_dir,
            self.run_config.working_directory,
            self.run_config.zarp_directory,
            os.environ.get("TMP"),
            os.environ.get("TMPDIR"),
        ]
        bind_paths_str: List[str] = [
            str(item) for item in bind_paths if item is not None
        ]
        if self.bind_paths is not None:
            bind_paths_str.extend([str(path) for path in self.bind_paths])
        bind_paths_arg: str = ",".join(bind_paths_str)
        cmd_ls = ["snakemake"]
        cmd_ls.extend(["--snakefile", str(snakefile)])
        cmd_ls.extend(["--cores", str(self.run_config.cores)])
        cmd_ls.extend(["--singularity-args", f"--bind {bind_paths_arg}"])
        cmd_ls.extend(["--directory", str(self.exec_dir)])
        if self.config_file is not None:
            cmd_ls.extend(["--configfile", str(self.config_file)])
        if self.run_config.profile is not None:
            if snakefile.name == "Snakefile":
                cmd_ls.extend(["--profile", str(self.run_config.profile)])
        if self.run_config.execution_mode == "DRY_RUN":
            cmd_ls.append("--dry-run")
        if self.run_config.dependency_embedding == "CONDA":
            if snakefile.name == "htsinfer.smk":
                cmd_ls.append("--use-singularity")
                # Conda is currently not supported for the HTSinfer
                # workflow
                LOGGER.warning(
                    "Conda not supported for HTSinfer workflow."
                    " Using Singularity instead."
                )
            else:
                cmd_ls.append("--use-conda")
        elif self.run_config.dependency_embedding == "SINGULARITY":
            if snakefile.name == "sra_download.smk":
                cmd_ls.append("--use-conda")
                # Singularity is currently not supported for the SRA download
                # workflow; reason:
                # https://github.com/snakemake/snakemake/issues/1521
                LOGGER.warning(
                    "Singularity not supported for SRA download workflow."
                    " Using Conda instead."
                )
            else:
                cmd_ls.append("--use-singularity")
        return cmd_ls

    def run(self, cmd) -> None:
        """Run Snakemake command.

        Run Snakemake workflow with a system call. The run state is set to
        ``SUCCESS`` if the run was successful, and to ``ERROR`` if the run
        failed.

        Args:
            cmd: Snakemake command as list of strings.

        Raises:
            CalledProcessError: If the Snakemake run failed.
        """
        try:
            subprocess.run(cmd, check=True)
            self.run_state = SnakemakeRunState.SUCCESS
        except subprocess.CalledProcessError as exc:
            self.run_state = SnakemakeRunState.ERROR
            raise exc
