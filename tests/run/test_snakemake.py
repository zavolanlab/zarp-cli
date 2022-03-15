"""Unit tests for module zarp.run.snakemake"""

import pytest

from zarp.config.models import (
    ExecModes,
    SnakemakeConfig,
    Run,
    RunModes,
    ToolPackaging
)
import zarp.run.snakemake as snk

@pytest.fixture
def snakemake_with_default_args():
    mysnk = snk.Snakemake(Run(), SnakemakeConfig())
    return mysnk

class TestSnakemake:
    """Test Snakemake class"""
    def test_init_without_args(self):
        """Class init without arguments"""
        with pytest.raises(TypeError):
            snk.Snakemake()
    
    def test_init_with_default_args(self, snakemake_with_default_args):
        """Class init with default arguments"""
        mysnk = snakemake_with_default_args
        assert type(mysnk) == snk.Snakemake
        assert type(mysnk.config_dict['configfiles']) == list

    def test_default_run(self, snakemake_with_default_args):
        """Prepare run with default args and run. 
        Snakemake will not successfully finish, as files are not found.
        """
        mysnk = snakemake_with_default_args
        assert mysnk.success is None
        assert mysnk.prepare_run()
        assert mysnk.success is None
        mysnk.run()
        assert not mysnk.success
    
    def test_snakemake_config(self):
        """Init SnakemakeConfig with non-existent attribute.
        This will not affect snakemake run.
        """
        mycnfg = SnakemakeConfig(wrong_key = 10)
        with pytest.raises(AttributeError):
            mycnfg.wrong_key
        mysnk = snk.Snakemake(Run(), mycnfg)
        mysnk.prepare_run()
        mysnk.run()
        assert not mysnk.success

    def test_execution_mode(self, snakemake_with_default_args):
        """Change default ExecMode and check the change.
        """
        # default run: dry run
        mysnk_default = snakemake_with_default_args
        mysnk_default.prepare_run()
        assert mysnk_default.config_dict['dryrun']
        # Normal run
        myrun = Run(execution_mode = ExecModes.RUN)
        mysnk = snk.Snakemake(myrun, SnakemakeConfig())
        mysnk.prepare_run()
        assert not mysnk.config_dict['dryrun']
    
    def test_snakemake_profile(self):
        """Initialise Run with non-default profile.
        Check whether profile is correctly added.
        """
        myrun = Run(run_mode = RunModes.SLURM,
            tool_packaging = ToolPackaging.SINGULARITY,
            cores = 4)
        assert myrun.run_mode == RunModes.SLURM
        assert myrun.cores == 4
        mysnk = snk.Snakemake(myrun, SnakemakeConfig())
        with pytest.raises(KeyError):
            mysnk.config_dict['cores']
        assert mysnk.config_dict['profile'] == "profiles/local-conda"
        
        mysnk.prepare_run()
        assert mysnk.config_dict['cores'] == 4
        assert mysnk.run_dict['run_mode'] == RunModes.SLURM
        assert mysnk.run_dict['tool_packaging'] == ToolPackaging.SINGULARITY
        assert mysnk.config_dict['profile'] == "profiles/slurm-singularity"
