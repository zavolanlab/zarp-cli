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
    DirectoryPath,
    EmailStr,
    FilePath,
    HttpUrl,
    validator,
)

from zarp.config.enums import (
    DependencyEmbeddingStrategies,
    ExecModes,
    ReadOrientation,
    SampleReferenceTypes,
)
from zarp.utils import generate_id

# pylint: disable=too-few-public-methods


class CustomBaseModel(BaseModel):
    """Base model that all other models derive from."""

    class Config:
        """Configuration class."""

        use_enum_values = True
        validate_all = True
        validate_assignment = True


class InitUser(CustomBaseModel):
    """User-specific parameters for initialization.

    Args:
        author: Name of the person running the analysis.
        email: Email address of the person running the analysis.
        logo: Path or URL pointing to image file to be used as a logo
            in the run report.
        url: A URL with additional information about the author or their
            affiliation.

    Attributes:
        author: Name of the person running the analysis.
        email: Email address of the person running the analysis.
        logo: Path or URL pointing to image file to be used as a logo
            in the run report.
        url: A URL with additional information about the author or their
            affiliation.
    """

    author: Optional[str] = None
    email: Optional[EmailStr] = None
    url: Optional[HttpUrl] = None
    logo: Optional[Union[HttpUrl, FilePath]] = None


class InitRun(CustomBaseModel):
    """Run-specific parameters for initialization.

    Args:
        cores: Cores to be used by the workflow engine.
        dependency_embedding: Dependency embedding strategy to use.
        execution_mode: Execution mode to use.
        genome_assemblies_map: Genome assemblies mapping file.
        profile: Snakemake profile for ZARP workflow.
        resources_version: Version of Ensembl genome resources to use when
            resources are not provided.
        rule_config: ZARP rule configuration.
        working_directory: Root directory for all runs.
        zarp_directory: Root directory of the ZARP repository.

    Attributes:
        cores: Cores to be used by the workflow engine.
        dependency_embedding: Dependency embedding strategy to use.
        execution_mode: Execution mode to use.
        genome_assemblies_map: Genome assemblies mapping file.
        profile: Snakemake profile for ZARP workflow.
        resources_version: Version of Ensembl genome resources to use when
            resources are not provided.
        rule_config: ZARP rule configuration.
        working_directory: Root directory for all runs.
        zarp_directory: Root directory of the ZARP repository.
    """

    working_directory: Path = Path.home() / ".zarp"
    zarp_directory: Optional[Path] = Path(__file__).parents[3] / "zarp"
    execution_mode: Optional[ExecModes] = ExecModes.RUN
    cores: Optional[int] = 1
    dependency_embedding: Optional[
        DependencyEmbeddingStrategies
    ] = DependencyEmbeddingStrategies.CONDA
    genome_assemblies_map: Optional[FilePath] = (
        Path(__file__).parents[2] / "data" / "genome_assemblies.csv"
    )
    resources_version: Optional[int] = None
    rule_config: Optional[Path] = None
    profile: Optional[Path] = None


class InitSample(CustomBaseModel):
    """Sample-specific parameters for initialization.

    Args:
        fragment_length_distribution_mean: Mean of the fragment length
            distribution.
        fragment_length_distribution_sd: Standard deviation of the fragment
            length distribution.

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
        sample: Sample-specific parameters.
        user: User-specific parameters.

    Attributes:
        run: Run-specific parameters.
        sample: Sample-specific parameters.
        user: User-specific parameters.
    """

    run: InitRun = InitRun()
    sample: InitSample = InitSample()
    user: InitUser = InitUser()


class ConfigUser(InitUser):
    """User-specific parameters."""


class ConfigRun(InitRun):
    """Run-specific parameters.

    Args:
        description: Run description.
        genome_assemblies_map: Genome assemblies mapping file.
        identifier: Unique identifier for a run.
        zarp_directory: Root directory of the ZARP repository.

    Attributes:
        description: Run description.
        genome_assemblies_map: Genome assemblies mapping file.
        identifier: Unique identifier for a run.
        zarp_directory: Root directory of the ZARP repository.
    """

    description: Optional[str] = None
    genome_assemblies_map: Path
    identifier: str = ""
    zarp_directory: DirectoryPath

    # pylint: disable=no-self-argument
    @validator("identifier")
    def get_identifier(
        cls,
        identifier: str,
    ) -> str:
        """Get default identifier."""
        if identifier == "":
            return generate_id()
        return identifier


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
    salmon_kmer_size: Optional[int] = 31


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
    run: ConfigRun
    sample: ConfigSample
    user: ConfigUser


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


class ConfigFileContent(CustomBaseModel):
    """Snakemake configuration file content."""


class ConfigFileSRA(ConfigFileContent):
    """SRA download workflow configuration file content.

    Args:
        cluster_log_dir: Path to cluster log directory.
        log_dir: Path to log directory.
        outdir: Path to output directory.
        samples: Path to sample table.
        samples_out: Path to output sample table.

    Attributes:
        cluster_log_dir: Path to cluster log directory.
        log_dir: Path to log directory.
        outdir: Path to output directory.
        samples: Path to sample table.
        samples_out: Path to output sample table.
    """

    cluster_log_dir: str
    log_dir: str
    outdir: str
    samples: str
    samples_out: str


class ConfigFileHTSinfer(ConfigFileContent):
    """HTSinfer workflow configuration file content.

    Args:
        cluster_log_dir: Path to cluster log directory.
        log_dir: Path to log directory.
        samples: Path to sample table.
        outdir: Path to output directory.
        samples_out: Path to output sample table.

    Attributes:
        cluster_log_dir: Path to cluster log directory.
        log_dir: Path to log directory.
        samples: Path to sample table.
        outdir: Path to output directory.
        samples_out: Path to output sample table.
    """

    cluster_log_dir: str
    log_dir: str
    samples: str
    outdir: str
    samples_out: str


class ConfigFileZARP(ConfigFileContent):
    """ZARP workflow configuration file content.

    Args:
        samples: Path to sample table.
        output_dir: Path to output directory.
        log_dir: Path to log directory.
        cluster_log_dir: Path to cluster log directory.
        kallisto_indexes: Path to kallisto indexes.
        salmon_indexes: Path to Salmon indexes.
        star_indexes: Path to STAR indexes.
        alfa_indexes: Path to ALFA indexes.
        rule_config: Path to ZARP rule configuration.
        report_description: Run report description.
        report_logo: Path or URL pointing to image file to be used as a logo
            for the run report.
        report_url: URL to link to from the run report.
        author_name: Name of the person running the analysis.
        author_email: Email address of the person running the analysis.

    Attributes:
        samples: Path to sample table.
        output_dir: Path to output directory.
        log_dir: Path to log directory.
        cluster_log_dir: Path to cluster log directory.
        kallisto_indexes: Path to kallisto indexes.
        salmon_indexes: Path to Salmon indexes.
        star_indexes: Path to STAR indexes.
        alfa_indexes: Path to ALFA indexes.
        report_description: Run report description.
        report_logo: Path or URL pointing to image file to be used as a logo
            for the run report.
        report_url: URL to link to from the run report.
        author_name: Name of the person running the analysis.
        author_email: Email address of the person running the analysis.
    """

    samples: str
    output_dir: str
    log_dir: str
    cluster_log_dir: str
    kallisto_indexes: str
    salmon_indexes: str
    star_indexes: str
    alfa_indexes: str
    rule_config: Optional[str]
    report_description: Optional[str]
    report_logo: Optional[str]
    report_url: Optional[str]
    author_name: Optional[str]
    author_email: Optional[str]
