"""Models and enumerators."""

from enum import Enum
from typing import (Optional, List, Tuple)

from pydantic import BaseModel  # pylint: disable=no-name-in-module

# pylint: disable=too-few-public-methods


# Sample-specific enumerators and models
class SampleIds(BaseModel):
    """Sample identifiers and aliases.

    Args:
        name: Human-friendly sample name.
        sra: SRA sample or run identifier.

    Attributes:
        name: Human-friendly sample name.
        sra: SRA sample or run identifier.
    """
    name: Optional[str] = None
    sra: Optional[str] = None


class ReadLayout(BaseModel):
    """Adapters and linkers that may be present in a library's reads.

    Args:
        three: 3'-end adapter, truncated during preprocessing.

    Attributes:
        three: 3'-end adapter, truncated during preprocessing.
    """
    three: Optional[str] = None


class FragLenDist(BaseModel):
    """Fragment length distribution parameters of the sequencing library.

    Required for single-end libraries. If not provided, default values will be
    used. For paired-end libraries any provided values will be ignored, as
    values will be automatically inferred.

    Args:
        mean: Mean of the fragment length distribution.
        sd: Standard deviation of the fragment length distribution.

    Attributes:
        mean: Mean of the fragment length distribution.
        sd: Standard deviation of the fragment length distribution.
    """
    mean: float = 300
    sd: float = 100


class GenomeResources(BaseModel):
    """Genome resources to be used for mapping reads and annotating alignments.

    Args:
        reference_sequences: Path to FASTA file containing reference sequences
            to align reads against, typically chromosome sequences.
        annotations: Path to GTF file containing gene annotations for the
            `reference_sequences`.

    Attributes:
        reference_sequences: Path to FASTA file containing reference sequences
            to align reads against, typically chromosome sequences.
        annotations: Path to GTF file containing gene annotations for the
            `reference_sequences`.
    """
    reference_sequences: Optional[str] = None
    annotations: Optional[str] = None


class Sample(BaseModel):
    """Sample-specific parameters.

    Args:
        file_paths: Paths to FASTQ files of a sequencing library. Either a
            tuple of two paths (paired-end library) or a tuple of one path and
            `None` (for single-end libraries).
        ids: Sample identifiers and aliases.
        read_layout: Adapters and linkers that may be present in a library's
            reads.
        fragment_length_distribution: Fragment length distribution parameters
            of the sequencing library.

    Attributes:
        file_paths: Paths to FASTQ files of a sequencing library.
        ids: Sample identifiers and aliases.
        read_layout: Adapters and linkers that may be present in a library's
            reads.
        fragment_length_distribution: Fragment length distribution parameters
            of the sequencing library.
    """
    file_paths: Optional[Tuple[str, Optional[None]]] = None
    ids: SampleIds = SampleIds()
    read_layout: ReadLayout = ReadLayout()
    fragment_length_distribution: FragLenDist = FragLenDist()


# Run-specific enumerators and models
class ExecModes(Enum):
    """Execution modes.

    Args:
        DRY_RUN: Do not download any files, infer parameters or start the
            analysis workflow.
        PREPARE_RUN: Download files and infer parameters, but do not start the
            analysis workflow.
        RUN:  Download files, infer parameters and start the analysis workflow.

    Attributes:
        DRY_RUN: Do not download any files, infer parameters or start the
            analysis workflow.
        PREPARE_RUN: Download files and infer parameters, but do not start the
            analysis workflow.
        RUN:  Download files, infer parameters and start the analysis workflow.
    """
    DRY_RUN = "dry_run"
    PREPARE_RUN = "prepare_run"
    RUN = "run"


class ToolPackaging(Enum):
    """Supported tool packaging options.

    Args:
        CONDA: Use binaries from Conda.
        SINGULARITY: Use Singularity containers.

    Attributes:
        CONDA: Use binaries from Conda.
        SINGULARITY: Use Singularity containers.
    """
    CONDA = "--use-conda"
    SINGULARITY = "--use-singularity"


class OutputFiles(Enum):
    """Output file types.

    Args:
        CONFIGS: Configuration files.
        LOGS: Log files.
        RESULTS: Result files.
        TEMPORARY: Temporary files.

    Attributes:
        CONFIGS: Configuration files.
        LOGS: Log files.
        RESULTS: Result files.
        TEMPORARY: Temporary files.
    """
    CONFIGS = "configs"
    LOGS = "logs"
    RESULTS = "results"
    TEMPORARY = "temporary"


class RunModes(Enum):
    """Snakemake run modes.

    Args:
        LOCAL: local execution
        SLURM: execution on slurm cluster
    """
    LOCAL = "local"
    SLURM = "slurm"


class SnakemakeConfig(BaseModel):
    """Snakemake-specific parameters for executing zarp.
    Only Snakemake API args allowed.

    Args:
        workdir: Path for working directory (within zarp directory).
        snakefile: Snakefile, relative to workdir.
        configfile: Configuration file for snakemake, relative to workdir.
        local_cores: Number of local cores (only used if in cluster mode).
        profile: Path for profile.
    """
    workdir: Optional[str] = None
    snakefile: str = "Snakefile"
    configfiles: list = ["config.yaml"]
    local_cores: int = 2
    profile: str = "profiles/local-conda"
    printshellcmds: bool = True
    force_incomplete: bool = True
    notemp: bool = False
    no_hooks: bool = False
    verbose: bool = True


class Run(BaseModel):
    """Run-specific parameters.

    Args:
        identifier: Unique identifier for a run.
        description: Run description.
        cores: Cores to use when running the analysis workflow.
        htsinfer_config: Configuration file for parameter inference.
        execution_mode: Execution mode to use.
        run_mode: Snakemake run mode.
        tool_packaging: Tool packaging option to use.
        execution_profile: Configuration options for execution environment.
        keep_files: Types of output files to keep.
        genome_resources: Genome resource description.
        config_file: Configuration file
    """
    identifier: Optional[str] = None
    description: Optional[str] = None
    cores: int = 1
    htsinfer_config: Optional[str] = None
    execution_mode: ExecModes = ExecModes.DRY_RUN
    run_mode: RunModes = RunModes.LOCAL
    tool_packaging: ToolPackaging = ToolPackaging.CONDA
    execution_profile: Optional[str] = None
    keep_files: List[OutputFiles] = [
        OutputFiles.CONFIGS,
        OutputFiles.LOGS,
        OutputFiles.RESULTS,
    ]
    genome_resources: Optional[GenomeResources] = None
    config_file: Optional[str] = None


# User-specific enumerators and models
class User(BaseModel):
    """User-specific parameters.

    Args:
        surname: Surname of the person running the analysis.
        other_names: First/other names of the person running the analysis.
        email: Email address of the person running the analysis.
        affiliations: Affiliations of the person running the analysis.
        url: One or more URLs with additional information about the author or
            their affiliation.
        logo_location: Path or URL pointing to image file to be used as a logo
            in the run report.
    """
    surname: Optional[str] = None
    first_name: Optional[str] = None
    email: Optional[str] = None
    affiliations: Optional[List[str]] = None
    urls: Optional[List[str]] = None
    logo_location: Optional[str] = None


# Unified config model
class Config(BaseModel):
    """ZARP-cli main configuration.

    Args:
        sample: Sample-specific parameters.
        run: Run-specific parameters.
        user: User-specific parameters.

    Attributes:
        sample: Sample-specific parameters.
        run: Run-specific parameters.
        snakemake_config: General
            Snakemake parameters and workflow-specific parameters
        user: User-specific parameters.
    """
    samples: List[Sample] = []
    run: Run = Run()
    snakemake_config: Optional[SnakemakeConfig] = None
    user: User = User()
