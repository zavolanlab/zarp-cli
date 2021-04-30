"""Run zarp with snakemake call."""

from typing import Optional
import snakemake

from zarp.config.models import (
    ExecModes,
    RunModes,
    SnakemakeConfig,
    ToolPackaging,
    Run
)

class Snakemake:
    """Output file types.

    Args:
        run: Run specific configuration.
        snakemake_config: Snakemake configuration.
    
    Attributes:
        run_dict: Dictionary from Run specific configuration.
        config_dict: Dictionary from Snakemake configuration.
        success (bool): True if snakemake run successful, False if not.
    """

    def __init__(self, run: Run, snakemake_config: SnakemakeConfig) -> None:
        self.run_dict = run.dict()
        self.config_dict = snakemake_config.dict()
        self.success: Optional[bool] = None

    def prepare_run(self) -> bool:
        """ Prepare Snakemake run.
        
        Translate Run entries to Snakemake API keywords.
        This will add or adjust config_dict based on values in run_dict.

        Returns:
            True if success, False otherwise.
        """
        try:
            # Define cores
            self.config_dict['cores'] = self.run_dict['cores']
            # Singularity
            if self.run_dict['tool_packaging'] == ToolPackaging.SINGULARITY:
                self.config_dict['use_singularity'] = True
                self.config_dict['singularity_args'] = self.run_dict['execution_profile']
            # Conda
            if self.run_dict['tool_packaging'] == ToolPackaging.CONDA:
                self.config_dict['use_conda'] = True
                # additional args to conda
            self.config_dict['dryrun'] = (True if 
                self.run_dict['execution_mode'] == ExecModes.DRY_RUN else False)
            return True
        except KeyError:
            return False
        
    def run(self) -> None:
        """Run snakemake command with supplied dictionary.

        The attribute config_dict is passed to snakemake.
        The attribute success is set according to snakemake return value.
        """
        try:
            self.success = snakemake.snakemake(**self.config_dict)
        except (TypeError, Exception):
            # TypeError: unexpected keyword arguments
            pass
