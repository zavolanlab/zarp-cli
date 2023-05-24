"""Unit tests for ``:mod:zarp.snakemake.run``."""

import os
from pathlib import Path
import subprocess

import pytest

from zarp.config.enums import SnakemakeRunState
from zarp.config.models import (
    ConfigRun,
    ExecModes,
    DependencyEmbeddingStrategies,
)
from zarp.snakemake.run import SnakemakeExecutor

from tests.utils import create_input_file, create_snakefile, create_config_file


default_run_config = ConfigRun(
    identifier="test_run",
    zarp_directory=Path(__file__).parents[1] / "files" / "zarp",
    genome_assemblies_map=Path(__file__).parents[1]
    / "files"
    / "genome_assemblies.csv",
)
default_cwd = Path.cwd()


class TestSnakemakeExecutor:
    """Test for class ``:cls:zarp.snakemake.run.SnakemakeExecutor`` class."""

    def test_init(self):
        """Initialise object."""
        my_run = SnakemakeExecutor(run_config=default_run_config)
        assert my_run.run_state == SnakemakeRunState.UNKNOWN

    def test_compile_command(self, tmpdir):
        """Create Snakemake run command."""
        os.chdir(tmpdir)
        snakefile = create_snakefile(dir=Path(tmpdir))
        my_run = SnakemakeExecutor(
            run_config=default_run_config,
            exec_dir=tmpdir,
        )
        expected_command = [
            "snakemake",
            "--snakefile",
            str(snakefile),
            "--cores",
            "1",
            "--directory",
            str(my_run.exec_dir),
            "--use-conda",
        ]
        cmd = my_run.compile_command(snakefile=snakefile)
        assert all(item in cmd for item in expected_command)
        os.chdir(default_cwd)

    def test_compile_command_config_file(self, tmpdir):
        """Execute a run with a config file."""
        snakefile = create_snakefile(dir=Path(tmpdir), name="sra_download.smk")
        config_file = create_config_file(dir=Path(tmpdir))
        run_config = default_run_config.copy()
        run_config.dependency_embedding = (
            DependencyEmbeddingStrategies.SINGULARITY
        )
        my_run = SnakemakeExecutor(
            run_config=run_config,
            config_file=config_file,
            exec_dir=tmpdir,
        )
        cmd = my_run.compile_command(snakefile=snakefile)
        assert "--configfile" in cmd

    @pytest.mark.parametrize(
        "dependency_embedding",
        [
            DependencyEmbeddingStrategies.CONDA,
            DependencyEmbeddingStrategies.SINGULARITY,
        ],
    )
    def test_compile_command_dep_embedding(self, dependency_embedding, tmpdir):
        """Execute a run with different dependency embedding strategies."""
        snakefile = create_snakefile(dir=Path(tmpdir))
        run_config = default_run_config.copy()
        run_config.dependency_embedding = dependency_embedding
        my_run = SnakemakeExecutor(run_config=run_config, exec_dir=tmpdir)
        cmd = my_run.compile_command(snakefile=snakefile)
        my_param = f"--use-{dependency_embedding.value.lower()}"
        assert my_param in cmd

    def test_compile_command_dep_embedding_sra_exception(self, tmpdir):
        """Execute a run with different dependency embedding strategies."""
        snakefile = create_snakefile(dir=Path(tmpdir), name="sra_download.smk")
        run_config = default_run_config.copy()
        run_config.dependency_embedding = (
            DependencyEmbeddingStrategies.SINGULARITY
        )
        my_run = SnakemakeExecutor(run_config=run_config, exec_dir=tmpdir)
        cmd = my_run.compile_command(snakefile=snakefile)
        assert "--use-singularity" not in cmd

    @pytest.mark.parametrize(
        "exec_mode", [ExecModes.RUN, ExecModes.DRY_RUN, ExecModes.PREPARE_RUN]
    )
    def test_compile_command_exec_modes(self, exec_mode, tmpdir):
        """Execute a run with different execution modes."""
        snakefile = create_snakefile(dir=Path(tmpdir))
        run_config = default_run_config.copy()
        run_config.execution_mode = exec_mode
        my_run = SnakemakeExecutor(run_config=run_config, exec_dir=tmpdir)
        cmd = my_run.compile_command(snakefile=snakefile)
        if exec_mode == ExecModes.DRY_RUN:
            assert "--dry-run" in cmd
        else:
            assert "--dry-run" not in cmd

    def test_run_valid(self, tmpdir):
        """Execute a valid run."""
        os.chdir(tmpdir)
        snakefile = create_snakefile(dir=Path(tmpdir))
        run_config = default_run_config.copy()
        run_config.working_directory = tmpdir
        my_run = SnakemakeExecutor(run_config=run_config, exec_dir=tmpdir)
        create_input_file(dir=my_run.exec_dir)
        cmd = my_run.compile_command(snakefile=snakefile)
        my_run.run(cmd=cmd)
        assert my_run.run_state == SnakemakeRunState.SUCCESS
        os.chdir(default_cwd)

    def test_run_valid_dry(self, tmpdir):
        """Execute a valid dry run."""
        os.chdir(tmpdir)
        snakefile = create_snakefile(dir=Path(tmpdir))
        run_config = default_run_config.copy()
        run_config.working_directory = tmpdir
        run_config.execution_mode = ExecModes.DRY_RUN
        my_run = SnakemakeExecutor(run_config=run_config, exec_dir=tmpdir)
        create_input_file(dir=my_run.exec_dir)
        cmd = my_run.compile_command(snakefile=snakefile)
        my_run.run(cmd=cmd)
        assert my_run.run_state == SnakemakeRunState.SUCCESS
        os.chdir(default_cwd)

    def test_run_invalid(self, tmpdir):
        """Execute a valid dry run."""
        os.chdir(tmpdir)
        run_config = default_run_config.copy()
        run_config.working_directory = tmpdir
        my_run = SnakemakeExecutor(run_config=run_config, exec_dir=tmpdir)
        cmd = my_run.compile_command(snakefile=Path("not_a_snakefile"))
        with pytest.raises(subprocess.CalledProcessError):
            my_run.run(cmd=cmd)
        assert my_run.run_state == SnakemakeRunState.ERROR
        os.chdir(default_cwd)
