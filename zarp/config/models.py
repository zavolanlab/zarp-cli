"""Configuration models."""

from pathlib import Path
from typing import (
    List,
    Optional,
    Tuple,
    Union,
)

from pydantic import (  # pylint: disable=no-name-in-module
    BaseModel,
    EmailStr,
    FilePath,
    HttpUrl,
)
from pydantic_collections import BaseCollectionModel  # type: ignore

from zarp.config.enums import (
    DependencyEmbeddingStrategies,
    ExecModes,
    OutputFileGroups,
    ReadOrientation,
    SampleReferenceTypes,
)

# pylint: disable=too-few-public-methods


class CustomBaseModel(BaseModel):
    """Base model that all other models derive from."""

    class Config:
        """Configuration class."""

        use_enum_values = True
        validate_assignment = True


class InitUser(CustomBaseModel):
    """User-specific parameters for initialization.

    Args:
        affiliations: Affiliations of the person running the analysis.
        author: Name of the person running the analysis.
        emails: Email addresses of the person running the analysis.
        logo: Path or URL pointing to image file to be used as a logo
            in the run report.
        urls: One or more URLs with additional information about the author or
            their affiliation.

    Attributes:
        affiliations: Affiliations of the person running the analysis.
        author: Name of the person running the analysis.
        emails: Email addresses of the person running the analysis.
        logo: Path or URL pointing to image file to be used as a logo
            in the run report.
        urls: One or more URLs with additional information about the author or
            their affiliation.
    """

    author: Optional[str] = None
    emails: Optional[List[EmailStr]] = None
    affiliations: Optional[List[str]] = None
    urls: Optional[List[HttpUrl]] = None
    logo: Optional[Union[HttpUrl, FilePath]] = None


class InitRun(CustomBaseModel):
    """Run-specific parameters for initialization.

    Args:
        cleanup_strategy: Types of output files to keep.
        cores: Cores to be used by the workflow engine.
        dependency_embedding: Dependency embedding strategy to use.
        execution_mode: Execution mode to use.
        htsinfer_config: Configuration options for parameter inference.
        resources_version: Version of Ensembl genome resources to use when
            resources are not provided
        rule_config: ZARP rule configuration.
        snakemake_config: Configuration options for execution environment.
        working_directory: Root directory for all runs.

    Attributes:
        cleanup_strategy: Types of output files to keep.
        cores: Cores to be used by the workflow engine.
        dependency_embedding: Dependency embedding strategy to use.
        execution_mode: Execution mode to use.
        htsinfer_config: Configuration options for parameter inference.
        resources_version: Version of Ensembl genome resources to use when
            resources are not provided.
        rule_config: ZARP rule configuration.
        snakemake_config: Configuration options for execution environment.
        working_directory: Root directory for all runs.
    """

    working_directory: Optional[Path] = None
    cleanup_strategy: Optional[List[OutputFileGroups]] = [
        OutputFileGroups.CONFIG,
        OutputFileGroups.LOGS,
        OutputFileGroups.RESULTS,
    ]
    execution_mode: Optional[ExecModes] = ExecModes.RUN
    dependency_embedding: Optional[
        DependencyEmbeddingStrategies
    ] = DependencyEmbeddingStrategies.CONDA
    cores: Optional[int] = 1
    resources_version: Optional[int] = None
    htsinfer_config: Optional[str] = None
    snakemake_config: Optional[str] = None
    rule_config: Optional[Path] = None


class InitSample(CustomBaseModel):
    """Sample-specific parameters for initialization.

    Args:
        fragment_length_distribution_mean: Mean of the fragment length
            distribution.
        fragment_length_distribution_sd: Standard deviation of the fragment
            length distribution.
        trim_poly_a: Whether to remove poly-A tails from reads.

    Attributes:
        fragment_length_distribution_mean: Mean of the fragment length
            distribution.
        fragment_length_distribution_sd: Standard deviation of the fragment
            length distribution.
    """

    fragment_length_distribution_mean: Optional[float] = 300
    fragment_length_distribution_sd: Optional[float] = 100


class InitConfig(CustomBaseModel):
    """ZARP-cli user default configuration set during initialization.

    Args:
        run: Run-specific parameters.
        user: User-specific parameters.
        sample: Sample-specific parameters.

    Attributes:
        run: Run-specific parameters.
        user: User-specific parameters.
        sample: Sample-specific parameters.
    """

    user: InitUser = InitUser()
    run: InitRun = InitRun(
        cleanup_strategy=[
            OutputFileGroups.CONFIG,
            OutputFileGroups.LOGS,
            OutputFileGroups.RESULTS,
        ]
    )
    sample: InitSample = InitSample()


class ConfigRun(InitRun):
    """Run-specific parameters.

    Args:
        description: Run description.
        identifier: Unique identifier for a run.
        run_directory: Directory where files for the current run will be
            stored.
        sample_table: Path to ZARP sample table.

    Attributes:
        description: Run description.
        identifier: Unique identifier for a run.
        run_directory: Directory where files for the current run will be
            stored.
        sample_table: Path to ZARP sample table.
    """

    description: Optional[str] = None
    identifier: Optional[str] = None
    run_directory: Optional[Path] = None
    sample_table: Optional[Path] = None
    run_config: Optional[Path] = None


class ConfigSample(InitSample):
    """Sample-specific parameters.

    Args:
        adapter_3p: Tuple of adapter sequences to truncate from the 3'-ends of
            single-end/first and second mate libraries, respectively.
        adapter_5p: Tuple of adapter sequences to truncate from the 5'-ends of
            single-end/first and second mate libraries, respectively.
        adapter_poly_3p: Tuple of polynucleotide stretch sequences to truncate
            from the 3'-ends of single-end/first and second mate libraries,
            respectively.
        adapter_poly_5p: Tuple of polynucleotide stretch sequences to truncate
            from the 3'-ends of single-end/first and second mate libraries,
            respectively.
        annotations: Path to GTF file containing gene annotations for the
            `reference_sequences`.
        read_orientation: Orientation of reads in sequencing library. Cf.
            https://salmon.readthedocs.io/en/latest/library_type.html.
        reference_sequences: Path to FASTA file containing reference sequences
            to align reads against, typically chromosome sequences.
        source: Origin of the sample as either a NCBI taxonomy database
            identifier, e.g, `9606` for humans, or the corresponding full name,
            e.g., "Homo sapiens".
        star_sjdb_overhang: Overhang length for splice junctions in STAR (
            parameter `sjdbOverhang`). Ideally the maximum read length minus 1.
            Lower values may result in decreased mapping accuracy, while higher
            values may result in longer processing times. Cf.
            https://github.com/alexdobin/STAR/blob/3ae0966bc604a944b1993f49aaeb597e809eb5c9/doc/STARmanual.pdf
        salmon_kmer_size: Size of k-mers for building the Salmon index. The
            default value typically works fine for reads of 75 bp or longer.
            Consider using lower values if dealing with shorter reads. Cf.
            https://salmon.readthedocs.io/en/latest/salmon.html#preparing-transcriptome-indices-mapping-based-mode
    Attributes:
        adapter_3p: Tuple of adapter sequences to truncate from the 3'-ends of
            single-end/first and second mate libraries, respectively.
        adapter_5p: Tuple of adapter sequences to truncate from the 5'-ends of
            single-end/first and second mate libraries, respectively.
        adapter_poly_3p: Tuple of polynucleotide stretch sequences to truncate
            from the 3'-ends of single-end/first and second mate libraries,
            respectively.
        adapter_poly_5p: Tuple of polynucleotide stretch sequences to truncate
            from the 3'-ends of single-end/first and second mate libraries,
            respectively.
        annotations: Path to GTF file containing gene annotations for the
            `reference_sequences`.
        read_orientation: Orientation of reads in sequencing library. Cf.
            https://salmon.readthedocs.io/en/latest/library_type.html.
        reference_sequences: Path to FASTA file containing reference sequences
            to align reads against, typically chromosome sequences.
        source: Origin of the sample as either a NCBI taxonomy database
            identifier, e.g, `9606` for humans, or the corresponding full name,
            e.g., "Homo sapiens".
        star_sjdb_overhang: Overhang length for splice junctions in STAR (
            parameter `sjdbOverhang`). Ideally the maximum read length minus 1.
            Lower values may result in decreased mapping accuracy, while higher
            values may result in longer processing times. Cf.
            https://github.com/alexdobin/STAR/blob/3ae0966bc604a944b1993f49aaeb597e809eb5c9/doc/STARmanual.pdf
        salmon_kmer_size: Size of k-mers for building the Salmon index. The
            default value typically works fine for reads of 75 bp or longer.
            Consider using lower values if dealing with shorter reads. Cf.
            https://salmon.readthedocs.io/en/latest/salmon.html#preparing-transcriptome-indices-mapping-based-mode
    """

    adapter_3p: Optional[Tuple[Optional[str], Optional[str]]] = None
    adapter_5p: Optional[Tuple[Optional[str], Optional[str]]] = None
    adapter_poly_3p: Optional[Tuple[Optional[str], Optional[str]]] = None
    adapter_poly_5p: Optional[Tuple[Optional[str], Optional[str]]] = None
    annotations: Optional[Path] = None
    read_orientation: Optional[ReadOrientation] = None
    reference_sequences: Optional[Path] = None
    source: Optional[Union[int, str]] = None
    star_sjdb_overhang: Optional[int] = None
    salmon_kmer_size: int = 31


class ConfigUser(InitUser):
    """User-specific parameters."""


class Config(CustomBaseModel):
    """ZARP-cli main configuration.

    Args:
        ref: References to individual sequencing libraries by local file path
            or read archive identifiers OR paths to ZARP sample tables; see
            documentation for details.
        run: Run-specific parameters.
        sample: Sample-specific parameters.
        user: User-specific parameters.

    Attributes:
        ref: References to individual sequencing libraries by local file path
            or read archive identifiers OR paths to ZARP sample tables; see
            documentation for details.
        run: Run-specific parameters.
        sample: Sample-specific parameters.
        user: User-specific parameters.
    """

    ref: List[str] = []
    run: ConfigRun = ConfigRun()
    sample: ConfigSample = ConfigSample()
    user: ConfigUser = ConfigUser()


class SampleReference(CustomBaseModel):
    """Sample reference information.

    Args:
        identifier: Read archive identifier.
        lib_paths: Path (single-ended) or paths (paired-ended) to files
            containing sequencing reads.
        name: Sample name.
        ref: References to individual sequencing libraries by local file path
            or read archive identifiers OR paths to ZARP sample tables; see
            documentation for details.
        table_path: Path to ZARP sample table.
        type: Type of sample reference.

    Attributes:
        identifier: Read archive identifier.
        lib_paths: Path (single-ended) or paths (paired-ended) to files
            containing sequencing reads.
        name: Sample name.
        ref: References to individual sequencing libraries by local file path
            or read archive identifiers OR paths to ZARP sample tables; see
            documentation for details.
        table_path: Path to ZARP sample table.
        type: Type of sample reference.
    """

    identifier: Optional[str] = None
    lib_paths: Optional[Tuple[FilePath, Optional[FilePath]]] = None
    name: Optional[str] = None
    ref: Optional[str] = None
    table_path: Optional[FilePath] = None
    type: SampleReferenceTypes = SampleReferenceTypes.INVALID


class Sample(ConfigSample):
    """Sample-specific parameters.

    Args:
        type: Type of sample, local (single/paired) or remote.
        identifier: Read archive identifier.
        name: Sample name; if not provided, a sample name will be set based on
            the input file name or read archive identifier.
        paths: Path (single-ended) or paths (paired-ended) to files containing
            sequencing reads.

    Attributes:
        type: Type of sample, local (single/paired) or remote.
        identifier: Read archive identifier.
        name: Sample name; if not provided, a sample name will be set based on
            the input file name or read archive identifier.
        paths: Path (single-ended) or paths (paired-ended) to files containing
            sequencing reads.
    """

    type: Optional[SampleReferenceTypes] = None
    identifier: Optional[str] = None
    name: Optional[str] = None
    paths: Optional[Tuple[FilePath, Optional[FilePath]]] = None


class SampleCollection(BaseCollectionModel[Sample]):
    """Collection of samples."""
