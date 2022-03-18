"""Tests for module `zarp.run.snakemake`"""

from zarp.config.models import Run
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
        "sed 'a added a new line' {input} > {output}"
""")
    with open("infile.txt", "w") as f:
        f.write("This is an example inputfile.")
    return example

class TestSnakemakeExecutor:
    """Unit tests for executing Snakemake."""

    def test_init(self):
        """Initialise object."""
        myrun = Run()
        snke = snakemake.SnakemakeExecutor(myrun)
        assert snke.success == None

    def test_run(self, tmpdir):
        """Prepare a run with a valid Snakefile."""
        myrun = Run()
        snke = snakemake.SnakemakeExecutor(myrun)
        os.chdir(tmpdir)
        snkfile = create_test_files()
        workdir = os.getcwd()
        snke.prepare_run(snkfile, workdir)
        exp_list = ["snakemake", "--snakefile", 
            snkfile, "--cores", "1"]
        assert snke.run_list == exp_list
        # Run the example Snakemake workflow.
        snke.run()
        assert snke.get_success()
        assert os.path.exists(os.path.join(tmpdir, "outfile.txt"))

    def test_invalid_run(self, tmpdir):
        """Prepare an invalid run."""
        myrun = Run()
        snke = snakemake.SnakemakeExecutor(myrun)
        os.chdir(tmpdir)
        snkfile = create_test_files()
        workdir = os.getcwd()
        snke.prepare_run(snkfile = "notASnakefile.smk", workdir = workdir)
        exp_list = ["snakemake", "--snakefile", 
            "notASnakefile.smk", "--cores", "1"]
        assert snke.run_list == exp_list
        with pytest.raises(subprocess.CalledProcessError):
            snke.run()
        assert not snke.get_success()

    def test_run_subprocess(self):
        """Trigger Error by subprocess."""
        snke = snakemake.SnakemakeExecutor(Run())
        with pytest.raises(IndexError):
            snke.run()
        snke.set_run_list(["snakemake"])
        with pytest.raises(subprocess.CalledProcessError):
            snke.run()
        assert not snke.get_success()

    def test_set_run_list(self):
        """Test setting a new run_list"""
        snke = snakemake.SnakemakeExecutor(Run())
        assert snke.get_run_list() == []
        snke.set_run_list(["snakemake"])
        assert snke.get_run_list() == ["snakemake"]
        snke.prepare_run(snkfile= "Snakefile", workdir = ".")
        assert snke.get_run_list() == ["snakemake", "--snakefile", 
            "Snakefile", "--cores", "1"]

    def test_validate_run(self):
        """Test validation of run."""
        snke = snakemake.SnakemakeExecutor(Run())
        assert not snke.validate_run()
        snke.prepare_run(snkfile = "Snakefile", workdir = ".")
        assert snke.validate_run()