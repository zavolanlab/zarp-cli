"""Unit tests for module zarp.run.snakemake"""

import pytest

from zarp.config.models import (
    SnakemakeConfig,
    Run
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
