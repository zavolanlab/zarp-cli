"""Tests for module `zarp.run.snakemake`"""

from zarp.config.models import ExecModes, InitRun, DependencyEmbeddingStrategies
from zarp.run import snakemake
import os
import subprocess
import pytest


def create_test_files():
    # Setup
    example = "example_snakefile.smk"
    with open(example, "w") as f:
        f.write("""
rule example:
    input:
        "infile.txt"
    output:
        "outfile.txt"
    shell:
        "cat {input} > {output}; echo 'added a new line' >> {output}"
""")
    with open("infile.txt", "w") as f:
        f.write("This is an example inputfile.")
    return example


class TestSnakemakeExecutor:
    """Unit tests for executing Snakemake."""

    def test_init(self):
        """Initialise object."""
        myrun = InitRun()
        snke = snakemake.SnakemakeExecutor(myrun)
        assert snke.success is None

    def test_run(self, tmpdir):
        """Prepare a run with a valid Snakefile."""
        myrun = InitRun()
        snke = snakemake.SnakemakeExecutor(myrun)
        os.chdir(tmpdir)
        snkfile = create_test_files()
        snke.prepare_run(snkfile)
        exp_list = ["snakemake", "--snakefile",
                    snkfile, "--cores", "1",
                    "--use-conda"]
        assert snke.get_run_list() == exp_list
        # Run the example Snakemake workflow.
        snke.run()
        assert snke.get_success()
        assert os.path.exists(os.path.join(tmpdir, "outfile.txt"))

    def test_invalid_run(self, tmpdir):
        """Prepare an invalid run."""
        myrun = InitRun()
        snke = snakemake.SnakemakeExecutor(myrun)
        os.chdir(tmpdir)
        snke.prepare_run(snkfile="notASnakefile.smk")
        exp_list = ["snakemake", "--snakefile",
                    "notASnakefile.smk", "--cores", "1",
                    "--use-conda"]
        assert snke.get_run_list() == exp_list
        with pytest.raises(subprocess.CalledProcessError):
            snke.run()
        assert not snke.get_success()

    def test_run_subprocess(self):
        """Trigger Error by subprocess."""
        snke = snakemake.SnakemakeExecutor(InitRun())
        with pytest.raises(IndexError):
            snke.run()
        snke.set_run_list(["snakemake"])
        with pytest.raises(subprocess.CalledProcessError):
            snke.run()
        assert not snke.get_success()

    def test_set_run_list(self):
        """Test setting a new run_list"""
        snke = snakemake.SnakemakeExecutor(InitRun())
        assert snke.get_run_list() == []
        snke.set_run_list(["snakemake"])
        assert snke.get_run_list() == ["snakemake"]
        snke.prepare_run(snkfile="Snakefile", workdir=".")
        assert snke.get_run_list() == ["snakemake", "--snakefile",
                                       "Snakefile", "--cores", "1",
                                       "--directory", ".",
                                       "--use-conda"]

    def test_validate_run(self):
        """Test validation of run."""
        snke = snakemake.SnakemakeExecutor(InitRun())
        assert not snke.validate_run()
        snke.prepare_run(snkfile="Snakefile", workdir=".")
        assert snke.validate_run()

    def test_working_dir(self, tmpdir):
        """Test proper setting of working directory."""
        snke = snakemake.SnakemakeExecutor(InitRun())
        # default working directory: None.
        snke.prepare_run("Snakefile")
        assert snke.get_run_list() == ["snakemake", "--snakefile",
                                       "Snakefile", "--cores", "1",
                                       "--use-conda"]
        # Manually set working directory.
        snke.prepare_run(snkfile="Snakefile", workdir=".")
        assert snke.get_run_list() == ["snakemake", "--snakefile",
                                       "Snakefile", "--cores", "1",
                                       "--directory", ".",
                                       "--use-conda"]
        # Run with "." as working directory.
        os.chdir(tmpdir)
        snkfile = create_test_files()
        snke.prepare_run(snkfile=snkfile, workdir=".")
        snke.run()
        assert snke.get_success()

    def test_execution_profile(self):
        """Prepare run with a profile."""
        non_profile_run = InitRun()
        snke = snakemake.SnakemakeExecutor(non_profile_run)
        snke.prepare_run("Snakefile")
        assert snke.get_run_list() == ["snakemake", "--snakefile",
                                       "Snakefile", "--cores", "1",
                                       "--use-conda"]
        # profile run
        profile_run = InitRun(execution_profile="local-conda")
        snke = snakemake.SnakemakeExecutor(profile_run)
        snke.prepare_run("Snakefile")
        assert snke.get_run_list() == ["snakemake", "--snakefile",
                                       "Snakefile", "--cores", "1",
                                       "--profile", "local-conda"]

    def test_execution_mode(self):
        """Test dry run and prepare run."""
        dryrun = InitRun(execution_mode=ExecModes.DRY_RUN)
        snke = snakemake.SnakemakeExecutor(dryrun)
        snke.prepare_run("Snakefile")
        assert snke.get_run_list() == ["snakemake", "--snakefile",
                                       "Snakefile", "--cores", "1",
                                       "--use-conda",
                                       "--dry-run"]
        # prepare run
        prep_run = InitRun(execution_mode=ExecModes.PREPARE_RUN)
        snke = snakemake.SnakemakeExecutor(prep_run)
        snke.prepare_run("Snakefile")
        assert snke.get_run_list() == ["snakemake", "--snakefile",
                                       "Snakefile", "--cores", "1",
                                       "--use-conda",
                                       "--dry-run"]

    def test_tool_packaging(self):
        """Test supply of conda or singularity."""
        conda_run = InitRun(dependency_embedding=DependencyEmbeddingStrategies.CONDA)
        snke = snakemake.SnakemakeExecutor(conda_run)
        snke.prepare_run("Snakefile")
        assert snke.get_run_list() == ["snakemake", "--snakefile",
                                       "Snakefile", "--cores", "1",
                                       "--use-conda"]
        singularity_run = InitRun(dependency_embedding=DependencyEmbeddingStrategies.SINGULARITY)
        snke = snakemake.SnakemakeExecutor(singularity_run)
        snke.prepare_run("Snakefile")
        assert snke.get_run_list() == ["snakemake", "--snakefile",
                                       "Snakefile", "--cores", "1",
                                       "--use-singularity"]

    def test_configfile(self):
        """Test supply of configfile."""
        configrun = InitRun(snakemake_config="configfile.yaml")
        snke = snakemake.SnakemakeExecutor(configrun)
        snke.prepare_run("Snakefile")
        assert snke.get_run_list() == ["snakemake", "--snakefile",
                                       "Snakefile", "--cores", "1",
                                       "--use-conda",
                                       "--configfile", "configfile.yaml"]
