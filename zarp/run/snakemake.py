"""Run zarp with snakemake call."""

import os
import snakemake

from zarp.config.models import (
    ExecModes,
    RunModes,
    ToolPackaging,
)

def run_snakemake(config):
    if config.run.tool_packaging == ToolPackaging.SINGULARITY:
        exec_mode = config.run.execution_mode
        if  exec_mode == ExecModes.DRY_RUN:
            run_successful = snakemake.snakemake(
                config.run.snakemake_config.snakefile,
                workdir = config.run.snakemake_config.workdir,
                cores = config.run.cores,
                configfiles = [config.run.snakemake_config.configfile],
                printshellcmds = config.run.snakemake_config.printshellcmds,
                force_incomplete = config.run.snakemake_config.force_incomplete,
                use_singularity = True,
                singularity_args = config.run.execution_profile,
                notemp = config.run.snakemake_config.notemp,
                no_hooks = config.run.snakemake_config.no_hooks,
                verbose = config.run.snakemake_config.verbose,
                dryrun = True)
        elif exec_mode == ExecModes.RUN:
            run_mode = config.run.snakemake_config.run_mode
            if  run_mode == RunModes.LOCAL:
                run_successful = snakemake.snakemake(
                    config.run.snakemake_config.snakefile,
                    workdir = config.run.snakemake_config.workdir,
                    cores = config.run.cores,
                    configfiles = [config.run.snakemake_config.configfile],
                    printshellcmds = config.run.snakemake_config.printshellcmds,
                    force_incomplete = config.run.snakemake_config.force_incomplete,
                    use_singularity = True,
                    singularity_args = config.run.execution_profile,
                    notemp = config.run.snakemake_config.notemp,
                    no_hooks = config.run.snakemake_config.no_hooks,
                    verbose = config.run.snakemake_config.verbose)
            elif run_mode == RunModes.SLURM:
                pass
        elif exec_mode == ExecModes.PREPARE_RUN:
            pass
    elif config.run.tool_packaging == ToolPackaging.CONDA:
        pass
    return(run_successful)

def generate_report():
    pass