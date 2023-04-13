"""Tests for module `zarp.run.snakemake`."""

import os
from pathlib import Path
import subprocess

import pytest

from zarp.config.enums import SnakemakeRunState
from zarp.config.models import (
    ExecModes,
    InitRun,
    DependencyEmbeddingStrategies,
)
from zarp.run.snakemake import SnakemakeExecutor


def create_input_file(dir: Path = Path.cwd()):
    """Create input file.

    Args:
        dir: Path to directory where input file is to be created.

    Returns:
        Path to input file.
    """
    input_file = dir / "input_file.txt"
    with open(input_file, "w") as _file:
        _file.write("This is an example input file.")
    return input_file


def create_snakefile(dir: Path = Path.cwd()):
    """Create Snakefile.

    Args:
        dir: Path to directory where Snakefile is to be created.

    Returns:
        Path to Snakefile.
    """
    snakefile = dir / "Snakefile"
    with open(snakefile, "w") as _file:
        _file.write(
            """rule example:
    input:
        "input_file.txt"
    output:
        "output_file.txt"
    shell:
        "cat {input} > {output}; echo 'some content' >> {output}"
"""
        )
    return snakefile


def create_config_file(dir: Path = Path.cwd()):
    """Create Snakemake config file.

    Args:
        dir: Path to directory where config file is to be created.

    Returns:
        Path to config file.
    """
    config_file = dir / "config.yaml"
    with open(config_file, "w") as _file:
        _file.write("some_param: some_value")
    return config_file


default_run_config = InitRun()
default_cwd = Path.cwd()


class TestSnakemakeExecutor:
    """Unit tests for executing Snakemake."""

    def test_init(self):
        """Initialise object."""
        my_run = SnakemakeExecutor(workflow_config=default_run_config)
        assert my_run.run_state == SnakemakeRunState.UNKNOWN

    def test_set_command(self, tmpdir):
        """Create Snakemake run command."""
        os.chdir(tmpdir)
        snakefile = create_snakefile(dir=tmpdir)
        expected_command = [
            "snakemake",
            "--snakefile",
            str(snakefile),
            "--cores",
            "1",
            "--use-conda",
        ]
        my_run = SnakemakeExecutor(workflow_config=default_run_config)
        my_run.set_command(snakefile=snakefile)
        assert my_run.command == expected_command
        os.chdir(default_cwd)

    def test_set_command_working_directory(self, tmpdir):
        """Execute a run with a manually set working directory."""
        snakefile = create_snakefile(dir=tmpdir)
        run_config = default_run_config.copy()
        run_config.working_directory = tmpdir
        my_run = SnakemakeExecutor(workflow_config=run_config)
        my_run.set_command(snakefile=snakefile)
        assert "--directory" in my_run.command
        assert str(tmpdir) in my_run.command

    @pytest.mark.parametrize(
        "dependency_embedding",
        [
            DependencyEmbeddingStrategies.CONDA,
            DependencyEmbeddingStrategies.SINGULARITY,
        ],
    )
    def test_set_command_dep_embedding(self, dependency_embedding, tmpdir):
        """Execute a run with different dependency embedding strategies."""
        snakefile = create_snakefile(dir=tmpdir)
        run_config = default_run_config.copy()
        run_config.dependency_embedding = dependency_embedding
        my_run = SnakemakeExecutor(workflow_config=run_config)
        my_run.set_command(snakefile=snakefile)
        my_param = f"--use-{dependency_embedding.value.lower()}"
        assert my_param in my_run.command

    @pytest.mark.parametrize(
        "exec_mode", [ExecModes.RUN, ExecModes.DRY_RUN, ExecModes.PREPARE_RUN]
    )
    def test_set_command_exec_modes(self, exec_mode, tmpdir):
        """Execute a run with different execution modes."""
        snakefile = create_snakefile(dir=tmpdir)
        run_config = default_run_config.copy()
        run_config.execution_mode = exec_mode
        my_run = SnakemakeExecutor(workflow_config=run_config)
        my_run.set_command(snakefile=snakefile)
        if exec_mode == ExecModes.RUN:
            assert "--dry-run" not in my_run.command
        else:
            assert "--dry-run" in my_run.command

    def test_set_command_config_file(self, tmpdir):
        """Execute a run with a config file."""
        snakefile = create_snakefile(dir=tmpdir)
        config_file = create_config_file(dir=tmpdir)
        run_config = default_run_config.copy()
        run_config.snakemake_config = config_file
        my_run = SnakemakeExecutor(workflow_config=run_config)
        my_run.set_command(snakefile=snakefile)
        assert "--configfile" in my_run.command
        assert str(config_file) in my_run.command

    def test_run_valid(self, tmpdir):
        """Execute a valid run."""
        os.chdir(tmpdir)
        snakefile = create_snakefile(dir=tmpdir)
        create_input_file(dir=tmpdir)
        my_run = SnakemakeExecutor(workflow_config=default_run_config)
        my_run.set_command(snakefile=snakefile)
        my_run.run()
        assert my_run.run_state == SnakemakeRunState.SUCCESS
        assert (tmpdir / "output_file.txt").exists()
        os.chdir(default_cwd)

    def test_run_invalid_snakefile(self, tmpdir):
        """Execute an invalid run."""
        os.chdir(tmpdir)
        my_run = SnakemakeExecutor(workflow_config=default_run_config)
        my_run.set_command(snakefile=Path("not_a_snakefile"))
        with pytest.raises(subprocess.CalledProcessError):
            my_run.run()
        assert my_run.run_state == SnakemakeRunState.ERROR
        os.chdir(default_cwd)

    def test_run_working_directory(self, tmpdir):
        """Execute a run with a manually set working directory."""
        snakefile = create_snakefile(dir=tmpdir)
        create_input_file(dir=tmpdir)
        run_config = default_run_config.copy()
        run_config.working_directory = tmpdir
        my_run = SnakemakeExecutor(workflow_config=run_config)
        my_run.set_command(snakefile=snakefile)
        my_run.run()
        assert my_run.run_state == SnakemakeRunState.SUCCESS
        assert (tmpdir / "output_file.txt").exists()

    @pytest.mark.parametrize(
        "dependency_embedding",
        [
            DependencyEmbeddingStrategies.CONDA,
            DependencyEmbeddingStrategies.SINGULARITY,
        ],
    )
    def test_run_dep_embedding(self, dependency_embedding, tmpdir):
        """Execute a run with different dependency embedding strategies."""
        os.chdir(tmpdir)
        snakefile = create_snakefile(dir=tmpdir)
        create_input_file(dir=tmpdir)
        run_config = default_run_config.copy()
        run_config.dependency_embedding = dependency_embedding
        my_run = SnakemakeExecutor(workflow_config=run_config)
        my_run.set_command(snakefile=snakefile)
        my_run.run()
        assert my_run.run_state == SnakemakeRunState.SUCCESS
        assert (tmpdir / "output_file.txt").exists()
        my_param = f"--use-{dependency_embedding.value.lower()}"
        assert my_param in my_run.command
        os.chdir(default_cwd)

    @pytest.mark.parametrize(
        "exec_mode", [ExecModes.RUN, ExecModes.DRY_RUN, ExecModes.PREPARE_RUN]
    )
    def test_run_exec_modes(self, exec_mode, tmpdir):
        """Execute a run with different execution modes."""
        os.chdir(tmpdir)
        snakefile = create_snakefile(dir=tmpdir)
        create_input_file(dir=tmpdir)
        run_config = default_run_config.copy()
        run_config.execution_mode = exec_mode
        my_run = SnakemakeExecutor(workflow_config=run_config)
        my_run.set_command(snakefile=snakefile)
        my_run.run()
        assert my_run.run_state == SnakemakeRunState.SUCCESS
        if exec_mode == ExecModes.RUN:
            assert (tmpdir / "output_file.txt").exists()
            assert "--dry-run" not in my_run.command
        else:
            assert not (tmpdir / "output_file.txt").exists()
            assert "--dry-run" in my_run.command
        os.chdir(default_cwd)

    def test_run_config_file(self, tmpdir):
        """Execute a run with a config file."""
        os.chdir(tmpdir)
        snakefile = create_snakefile(dir=tmpdir)
        config_file = create_config_file(dir=tmpdir)
        create_input_file(dir=tmpdir)
        run_config = default_run_config.copy()
        run_config.snakemake_config = config_file
        my_run = SnakemakeExecutor(workflow_config=run_config)
        my_run.set_command(snakefile=snakefile)
        my_run.run()
        assert my_run.run_state == SnakemakeRunState.SUCCESS
        assert (tmpdir / "output_file.txt").exists()
        assert "--configfile" in my_run.command
        assert str(config_file) in my_run.command
        os.chdir(default_cwd)
