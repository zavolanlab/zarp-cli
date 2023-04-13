"""Tests for module `zarp.run.snakemake`."""

import filecmp
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


default_run_config = ConfigRun(identifier="test_run")
default_cwd = Path.cwd()


class TestSnakemakeExecutor:
    """Unit tests for executing Snakemake."""

    def test_init(self):
        """Initialise object."""
        my_run = SnakemakeExecutor(run_config=default_run_config)
        assert my_run.run_state == SnakemakeRunState.UNKNOWN

    def test_setup(self):
        """Set up Snakemake run."""
        my_run = SnakemakeExecutor(run_config=default_run_config)
        my_run.setup()
        assert my_run.run_dir.exists()
        assert my_run.exec_dir.exists()

    def test_setup_run_identifier_unset(self):
        """Set up Snakemake run without run identifier."""
        run_config = default_run_config.copy()
        my_run = SnakemakeExecutor(run_config=run_config)
        my_run.run_config.identifier = None
        with pytest.raises(ValueError):
            my_run.setup()

    def test_set_configuration_file(self, tmpdir):
        """Set configuration file."""
        os.chdir(tmpdir)
        config_file = create_config_file(dir=tmpdir)
        run_config = default_run_config.copy()
        run_config.working_directory = tmpdir
        my_run = SnakemakeExecutor(run_config=run_config)
        assert my_run.config_file == Path() / "config.yaml"
        my_run.setup()
        my_run.set_configuration_file(config=Path(config_file))
        assert filecmp.cmp(my_run.config_file, config_file, shallow=True)
        os.chdir(default_cwd)

    def test_set_configuration_file_no_config(self, tmpdir):
        """Set configuration file without explicit config."""
        os.chdir(tmpdir)
        run_config = default_run_config.copy()
        run_config.working_directory = tmpdir
        my_run = SnakemakeExecutor(run_config=run_config)
        assert my_run.config_file == Path() / "config.yaml"
        my_run.setup()
        my_run.set_configuration_file()
        assert my_run.config_file.stat().st_size == 3
        os.chdir(default_cwd)

    def test_set_configuration_file_config_object(self, tmpdir):
        """Set configuration file without explicit config."""
        os.chdir(tmpdir)
        config = {"some_param": "some_value"}
        run_config = default_run_config.copy()
        run_config.working_directory = tmpdir
        my_run = SnakemakeExecutor(run_config=run_config)
        assert my_run.config_file == Path() / "config.yaml"
        my_run.setup()
        my_run.set_configuration_file(config=config)
        with open(my_run.config_file, "r") as _file:
            assert _file.read() == "some_param: some_value\n"
        os.chdir(default_cwd)

    def test_set_command(self, tmpdir):
        """Create Snakemake run command."""
        os.chdir(tmpdir)
        snakefile = create_snakefile(dir=tmpdir)
        my_run = SnakemakeExecutor(run_config=default_run_config)
        my_run.setup()
        expected_command = [
            "snakemake",
            "--snakefile",
            str(snakefile),
            "--cores",
            "1",
            "--configfile",
            str(my_run.config_file),
            "--directory",
            str(my_run.exec_dir),
            "--use-conda",
        ]
        my_run.set_command(snakefile=snakefile)
        assert my_run.command == expected_command
        os.chdir(default_cwd)

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
        my_run = SnakemakeExecutor(run_config=run_config)
        my_run.set_command(snakefile=snakefile)
        my_param = f"--use-{dependency_embedding.value.lower()}"
        assert my_param in my_run.command

    def test_set_command_dep_embedding_sra_exception(self, tmpdir):
        """Execute a run with different dependency embedding strategies."""
        snakefile = create_snakefile(dir=tmpdir)
        run_config = default_run_config.copy()
        run_config.dependency_embedding = (
            DependencyEmbeddingStrategies.SINGULARITY
        )
        my_run = SnakemakeExecutor(run_config=run_config)
        my_run.workflow_id = "sra_download"
        my_run.set_command(snakefile=snakefile)
        assert "--use-singularity" not in my_run.command

    @pytest.mark.parametrize(
        "exec_mode", [ExecModes.RUN, ExecModes.DRY_RUN, ExecModes.PREPARE_RUN]
    )
    def test_set_command_exec_modes(self, exec_mode, tmpdir):
        """Execute a run with different execution modes."""
        snakefile = create_snakefile(dir=tmpdir)
        run_config = default_run_config.copy()
        run_config.execution_mode = exec_mode
        my_run = SnakemakeExecutor(run_config=run_config)
        my_run.set_command(snakefile=snakefile)
        if exec_mode == ExecModes.DRY_RUN:
            assert "--dry-run" in my_run.command
        else:
            assert "--dry-run" not in my_run.command

    def test_run_valid(self, tmpdir):
        """Execute a valid run."""
        os.chdir(tmpdir)
        snakefile = create_snakefile(dir=tmpdir)
        run_config = default_run_config.copy()
        run_config.working_directory = tmpdir
        my_run = SnakemakeExecutor(run_config=run_config)
        my_run.setup()
        create_input_file(dir=my_run.exec_dir)
        my_run.set_configuration_file()
        my_run.set_command(snakefile=snakefile)
        my_run.run()
        assert my_run.run_state == SnakemakeRunState.SUCCESS
        assert (my_run.exec_dir / "output_file.txt").exists()
        os.chdir(default_cwd)

    def test_run_valid_dry(self, tmpdir):
        """Execute a valid dry run."""
        os.chdir(tmpdir)
        snakefile = create_snakefile(dir=tmpdir)
        run_config = default_run_config.copy()
        run_config.working_directory = tmpdir
        run_config.execution_mode = ExecModes.DRY_RUN
        my_run = SnakemakeExecutor(run_config=run_config)
        my_run.setup()
        create_input_file(dir=my_run.exec_dir)
        my_run.set_configuration_file()
        my_run.set_command(snakefile=snakefile)
        my_run.run()
        assert my_run.run_state == SnakemakeRunState.SUCCESS
        os.chdir(default_cwd)

    def test_run_invalid(self, tmpdir):
        """Execute a valid dry run."""
        os.chdir(tmpdir)
        run_config = default_run_config.copy()
        run_config.working_directory = tmpdir
        my_run = SnakemakeExecutor(run_config=run_config)
        my_run.setup()
        my_run.set_configuration_file()
        my_run.set_command(snakefile=Path("not_a_snakefile"))
        with pytest.raises(subprocess.CalledProcessError):
            my_run.run()
        assert my_run.run_state == SnakemakeRunState.ERROR
        os.chdir(default_cwd)

    def test__set_config_file(self, tmpdir):
        """Set a config file."""
        os.chdir(tmpdir)
        config_file = create_config_file(dir=tmpdir)
        run_config = default_run_config.copy()
        run_config.working_directory = tmpdir
        my_run = SnakemakeExecutor(run_config=run_config)
        assert my_run.config_file == Path() / "config.yaml"
        my_run.setup()
        my_run._set_config_file(config=Path(config_file))
        assert filecmp.cmp(my_run.config_file, config_file, shallow=True)
        os.chdir(default_cwd)

    def test__set_config_file_config_object(self, tmpdir):
        """Set configuration file without explicit config."""
        os.chdir(tmpdir)
        config = {"some_param": "some_value"}
        run_config = default_run_config.copy()
        run_config.working_directory = tmpdir
        my_run = SnakemakeExecutor(run_config=run_config)
        assert my_run.config_file == Path() / "config.yaml"
        my_run.setup()
        my_run._set_config_file(config=config)
        with open(my_run.config_file, "r") as _file:
            assert _file.read() == "some_param: some_value\n"
        os.chdir(default_cwd)

    def test__set_config_file_config_object_wrong_type(self, tmpdir):
        """Set configuration file with a config object of the wrong type."""
        os.chdir(tmpdir)
        config = ["some_param", "some_value"]
        run_config = default_run_config.copy()
        run_config.working_directory = tmpdir
        my_run = SnakemakeExecutor(run_config=run_config)
        assert my_run.config_file == Path() / "config.yaml"
        my_run.setup()
        with pytest.raises(TypeError):
            my_run._set_config_file(config=config)  # type: ignore
        os.chdir(default_cwd)
