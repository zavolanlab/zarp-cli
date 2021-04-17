"""Unit tests for module zarp.run.snakemake"""

import os
import snakemake
import sys
sys.path.insert(0, '../')

import pytest

import zarp.config.models as models
import zarp.run.snakemake as snakemake

@pytest.fixture
def set_params():
    """Set parameters
    The test assumes that zarp is cloned into a directory on the same level as zarp-cli
    """
    workdir = os.path.join(os.path.expanduser("~"), 
        "zavolab_projects", "zarp", 
        "tests", "test_integration_workflow") # .snakemake will be saved in this dir
    snakefile = "../../Snakefile"
    configfile = "../input_files/config.yaml"
    cores = 4 # corresponds to local_cores in cluster mode
    singularity_args = "--bind ${PWD}/../input_files,${PWD}/../../images"
    # report = "snakemake_report.html"

    # cluster parameters
    # cluster_config = "../input_files/cluster.json"
    # cluster = "sbatch --cpus-per-task={cluster.threads} \
    #     --mem={cluster.mem} --qos={cluster.queue} \
    #     --time={cluster.time} --job-name={cluster.name} \
    #     -o {cluster.out} -p scicore"
    # cluster_cores = 256

    # make file paths absolute (still needed with workdir specified)
    snakefile = os.path.realpath(os.path.join(workdir, snakefile))
    configfile = os.path.realpath(os.path.join(workdir, configfile))
    # cluster_config = os.path.join(workdir, cluster_config)
    singularity_args = singularity_args.replace("${PWD}", workdir)
    return(workdir, snakefile, configfile, cores, singularity_args)


@pytest.fixture
def construct_dry_run(set_params):
    workdir, snakefile, configfile, cores, singularity_args = set_params
    # initialise model with user name
    myconfig = models.Config(user = models.User(surname = "Burri", 
        first_name = "Dominik"))

    snake_config = models.SnakemakeConfig(workdir = workdir,
        snakefile = snakefile,
        configfile = configfile,
        notemp = True,
        no_hooks = True)

    myrun = models.Run(identifier = "test-dry-run",
        description = "test config model and snakemake api",
        cores = cores,
        execution_mode = models.ExecModes.DRY_RUN,
        tool_packaging = models.ToolPackaging.SINGULARITY,
        execution_profile = singularity_args,
        snakemake_config = snake_config)
    myconfig.run = myrun
    return(myconfig)


@pytest.fixture
def construct_local_run(set_params):
    workdir, snakefile, configfile, cores, singularity_args = set_params
    # initialise model with user name
    myconfig = models.Config(user = models.User(surname = "Burri", 
        first_name = "Dominik"))

    snake_config = models.SnakemakeConfig(workdir = workdir,
        snakefile = snakefile,
        configfile = configfile,
        notemp = True,
        no_hooks = True)

    myrun = models.Run(identifier = "test-local-run",
        description = "test config model and snakemake api",
        cores = cores,
        execution_mode = models.ExecModes.RUN,
        tool_packaging = models.ToolPackaging.SINGULARITY,
        execution_profile = singularity_args,
        snakemake_config = snake_config)
    myconfig.run = myrun
    return(myconfig)


class TestSnakemake:
    """Test snakemake execution"""
    def test_user(set_params, construct_dry_run):
        config = construct_dry_run
        assert config.user.surname == "Burri"

    def test_snakefile(set_params, construct_dry_run):
        config = construct_dry_run
        actual_file = config.run.snakemake_config.snakefile
        exp_file = os.path.join(os.path.expanduser("~"), "zavolab_projects", "zarp", "Snakefile")
        assert actual_file == exp_file

    def test_dry_run(set_params, construct_dry_run):
        config = construct_dry_run
        run_successful = snakemake.run_snakemake(config)
        assert run_successful
