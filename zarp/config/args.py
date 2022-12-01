"""Command-line argument parser class."""

import argparse
from typing import (
    Dict,
    List,
    Optional,
    Sequence,
)
from pathlib import Path
import sys

from zarp.config.enums import (
    DependencyEmbeddingStrategies,
    ExecModes,
    LogLevels,
    OutputFileGroups,
)
from zarp.version import __version__


class ArgParser:
    """ZARP-cli argument parser class."""

    ARGUMENT_GROUPS: Dict[str, List[str]] = {
        "sample": [
            "adapter_3p",
            "adapter_5p",
            "adapter_poly_3p",
            "adapter_poly_5p",
            "annotations",
            "fragment_length_distribution_mean",
            "fragment_length_distribution_sd",
            "read_orientation",
            "reference_seqs",
            "source",
        ],
        "run": [
            "cleanup_strategy",
            "cores",
            "dependency_embedding",
            "description",
            "execution_mode",
            "htsinfer_config",
            "identifier",
            "resources_version",
            "rule_config",
            "snakemake_config",
            "working_directory",
        ],
        "user": [
            "affiliations",
            "author",
            "emails",
            "logo",
            "urls",
        ],
    }
    DESCRIPTION = f"{sys.modules[__name__].__doc__}\n\n"
    EPILOG = (
        f"%(prog)s v{__version__}, (c) 2021 by Zavolab "
        "(zavolab-biozentrum@unibas.ch)"
    )

    def __init__(self, args: Optional[Sequence[str]] = None):
        """Class constructor.

        Args:
            args: Command-line arguments.

        Attributes:
            args: Command-line arguments.
            args_parsed: Parsed command-line arguments.
            parser: Argument parser object.
        """
        self.args: Optional[Sequence[str]] = args
        self.args_parsed: argparse.Namespace
        self.parser: argparse.ArgumentParser

    def set_parser(self) -> None:
        """Instantiate argument parser."""
        self.parser = argparse.ArgumentParser(
            description=self.DESCRIPTION,
            epilog=self.EPILOG,
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

    def set_arguments(self) -> None:
        """Add arguments."""
        self._set_general_arguments(
            argument_group=self.parser.add_argument_group(
                title="general parameters",
            )
        )
        self._set_mode_arguments(
            argument_group=self.parser.add_argument_group(
                title="run modes",
                description=(
                    "When specifying any of the options in this group,"
                    " ZARP-cli will ignore all other parameters and will not"
                    " start a ZARP run."
                ),
            )
        )
        self._set_sample_arguments(
            argument_group=self.parser.add_argument_group(
                title="sample-related options",
                description=(
                    "Specify the arguments for any sample-related parameters."
                    " If provided via the command line, the same values will"
                    " applied to all samples. When analyzing multiple samples,"
                    " and samples either originate different sources and/or"
                    " shall be  processed with different genome resources,"
                    " these values  should be specified in a sample table"
                    " instead.  Alternatively, you can make use of the"
                    " inference  functionality to infer the sample source and"
                    " use or retrieve  the corresponding genome resources as"
                    " per your ZARP-cli  configuration. In that case, do not"
                    " specify any arguments to  the parameters in this section"
                    " and/or leave the  corresponding sample table fields"
                    " empty."
                ),
            )
        )
        self._set_run_arguments(
            argument_group=self.parser.add_argument_group(
                title="run-specific parameters",
                description=(
                    "Options in this group influence how the ZARP workflow is"
                    " executed. When specified on the command line, they will"
                    " override the defaults set during initialization. If you"
                    " find yourself specifying any of these options"
                    " repeatedly, consider updating defaults by running `zarp"
                    " --init`."
                ),
            )
        )
        self._set_user_arguments(
            argument_group=self.parser.add_argument_group(
                title="user-specific parameters",
                description=(
                    "Options in this group will be used by ZARP to generate"
                    " reports. When specified on the command line, they will"
                    " override the defaults set during initialization. If you"
                    " find yourself specifying any of these options"
                    " repeatedly, consider updating defaults by running `zarp"
                    " --init`."
                ),
            )
        )

    @staticmethod
    def _set_general_arguments(
        argument_group: argparse._ArgumentGroup,  # pylint: disable=W0212
    ) -> None:
        """Add general arguments.

        Args:
            argument_group: Argument group object.
        """
        argument_group.add_argument(
            "sample_references",
            nargs="*",
            type=str,
            metavar="REF",
            help=(
                "references to individual sequencing libraries by local file"
                " path or read archive identifiers OR paths to ZARP sample"
                " tables; seedocumentation for details"
            ),
        )
        argument_group.add_argument(
            "--config-file",
            default=Path.home() / ".zarp" / "user.yaml",
            type=lambda p: Path(p).absolute(),
            metavar="PATH",
            help="override user-specific default configuration file",
        )
        argument_group.add_argument(
            "--verbosity",
            choices=[e.name for e in LogLevels],
            default="INFO",
            type=str,
            help="logging verbosity level",
        )

    def _set_mode_arguments(
        self,
        argument_group: argparse._ArgumentGroup,  # pylint: disable=W0212
    ) -> None:
        """Add run mode arguments.

        Args:
            argument_group: Argument group object.
        """
        argument_group.add_argument(
            "--init",
            default=False,
            action="store_true",
            help="add or edit user-specific default configuration and exit",
        )
        argument_group.add_argument(
            "-h",
            "--help",
            action="help",
            help="show this help message and exit",
        )
        argument_group.add_argument(
            "--version",
            action="version",
            version=self.EPILOG,
            help="show version information and exit",
        )

    @staticmethod
    def _set_sample_arguments(
        argument_group: argparse._ArgumentGroup,  # pylint: disable=W0212
    ) -> None:
        """Add sample arguments.

        Args:
            argument_group: Argument group object.
        """
        argument_group.add_argument(
            "--adapter-3p",
            default=None,
            type=str,
            metavar="STR",
            help=(
                "adapter sequence to be truncated from the 3'-ends of reads;"
                " for paired-end libraries, two sequences can be specified,"
                " separated by a comma; these are used to truncate the the"
                " 3'-ends of first and second mates, respectively"
            ),
        )
        argument_group.add_argument(
            "--adapter-5p",
            default=None,
            type=str,
            metavar="STR",
            help=(
                "adapter sequence to be truncated from the 5'-ends of reads;"
                " for paired-end libraries, two sequences can be specified,"
                " separated by a comma; these are used to truncate the the"
                " 5'-ends of first and second mates, respectively"
            ),
        )
        argument_group.add_argument(
            "--adapter-poly-3p",
            default=None,
            type=str,
            metavar="STR",
            help=(
                "polynucleotide sequence to be truncated from the 3'-ends of"
                " reads, e.g. a stretch of A's; for paired-end libraries, two"
                " sequences can be specified, separated by a comma; these are"
                " used to truncate the the 3'-ends of first and second mates,"
                " respectively"
            ),
        )
        argument_group.add_argument(
            "--adapter-poly-5p",
            default=None,
            type=str,
            metavar="STR",
            help=(
                "polynucleotide sequence to be truncated from the 3'-ends of"
                " reads, e.g. a stretch of A's; for paired-end libraries, two"
                " sequences can be specified, separated by a comma; these are"
                " used to truncate the the 5'-ends of first and second mates,"
                " respectively"
            ),
        )
        argument_group.add_argument(
            "--annotations",
            default=None,
            type=lambda p: Path(p).absolute(),
            metavar="PATH",
            help=(
                "path to file annotating genes of the sample source; in GTF"
                " format"
            ),
        )
        argument_group.add_argument(
            "--fragment-length-distribution-mean",
            type=float,
            default=None,
            metavar="FLOAT",
            help="mean of fragment length distribution",
        )
        argument_group.add_argument(
            "--fragment-length-distribution-sd",
            type=float,
            default=None,
            metavar="FLOAT",
            help="standard deviation of fragment length distribution",
        )
        argument_group.add_argument(
            "--read-orientation",
            type=str,
            default=None,
            metavar="STR",
            help=(
                "orientation of reads in sequencing library; one of"
                " 'stranded_forward', 'stranded_reverse', 'unstranded',"
                " 'inward_stranded_forward', 'inward_stranded_reverse',"
                " 'inward_unstranded'; cf."
                " https://salmon.readthedocs.io/en/latest/library_type.html"
            ),
        )
        argument_group.add_argument(
            "--reference-seqs",
            type=lambda p: Path(p).absolute(),
            default=None,
            metavar="PATH",
            help=(
                "path to file containing reference sequences of the sample"
                " source; in FASTA format"
            ),
        )
        argument_group.add_argument(
            "--source",
            type=str,
            default=None,
            metavar="INT|STR",
            help=(
                "origin of the sample as either a NCBI taxonomy database"
                " identifier, e.g, 9606 for humans, or the corresponding full"
                " name, e.g., 'Homo sapiens'."
            ),
        )
        argument_group.add_argument(
            "--trim-polya",
            action="store_true",
            default=None,
            help="remove poly-A tails from reads",
        )
        argument_group.add_argument(
            "--star-sjdb-overhang",
            type=int,
            default=None,
            metavar="INT",
            help=(
                "overhang length for splice junctions in STAR (parameter"
                " `sjdbOverhang`); ideally the maximum read length minus 1."
                " Lower values may result in decreased mapping accuracy, while"
                " higher values may result in longer processing times. Cf. "
                "https://github.com/alexdobin/STAR/blob/"
                "3ae0966bc604a944b1993f49aaeb597e809eb5c9/doc/STARmanual.pdf"
            ),
        )
        argument_group.add_argument(
            "--salmon-kmer-size",
            type=int,
            default=31,
            metavar="INT",
            help=(
                "size of k-mers for building the Salmon index; the default"
                " value typically works fine for reads of 75 bp or longer;"
                " consider using lower values if dealing with shorter reads;"
                " Cf. https://salmon.readthedocs.io/en/latest/salmon.html"
                "#preparing-transcriptome-indices-mapping-based-mode"
            ),
        )

    @staticmethod
    def _set_run_arguments(
        argument_group: argparse._ArgumentGroup,  # pylint: disable=W0212
    ) -> None:
        """Add run arguments.

        Args:
            argument_group: Argument group object.
        """
        argument_group.add_argument(
            "--cleanup-strategy",
            choices=[item.value for item in OutputFileGroups]
            + ["NONE", "ALL"],
            default=None,
            type=str,
            action="append",
            help=(
                "class of files to keep after the workflow run; when not"
                " choosing 'NONE' or 'ALL', parameter can be specified"
                " multiple times to provide more than one class of files"
            ),
        )
        argument_group.add_argument(
            "--cores",
            default=None,
            type=int,
            metavar="INT",
            help=(
                "maximum number of cores that Snakemake is allowed to use;"
                " note that this is different from the number of cores that"
                " may be used for each individual workflow step/rule"
            ),
        )
        argument_group.add_argument(
            "--dependency-embedding",
            choices=[item.value for item in DependencyEmbeddingStrategies],
            default=None,
            type=str,
            help=(
                "strategy for embedding dependencies for the execution of"
                " individual workflow steps/rules"
            ),
        )
        argument_group.add_argument(
            "--description",
            default=None,
            type=str,
            metavar="STR",
            help="brief description of the workflow run",
        )
        argument_group.add_argument(
            "--execution-mode",
            choices=[item.value for item in ExecModes],
            default=None,
            type=str,
            help=(
                "run identifier; if not provided a random string will be"
                " generated"
            ),
        )
        argument_group.add_argument(
            "--htsinfer-config",
            default=None,
            type=str,
            metavar="STR",
            help=(
                "command-line options for metadata inference; will be"
                " interpolated into the HTSinfer call"
            ),
        )
        argument_group.add_argument(
            "--identifier",
            default=None,
            type=str,
            metavar="STR",
            help=(
                "run identifier; if not provided a random string will be"
                " generated"
            ),
        )
        argument_group.add_argument(
            "--resources-version",
            default=None,
            type=int,
            metavar="INT",
            help=(
                "version of Ensembl genome resources to use when resources are"
                " not explicitly provided; uses latest version by default"
            ),
        )
        argument_group.add_argument(
            "--rule-config",
            default=None,
            type=lambda p: Path(p).absolute(),
            metavar="PATH",
            help=(
                "ZARP rule configuration; refer to ZARP documentation for"
                " details"
            ),
        )
        argument_group.add_argument(
            "--snakemake-config",
            default=None,
            type=str,
            metavar="STR",
            help=(
                "command-line options for Snakemake; will be interpolated into"
                " the Snakemake calls"
            ),
        )
        argument_group.add_argument(
            "--working-directory",
            default=None,
            type=lambda p: Path(p).absolute(),
            metavar="PATH",
            help="directory in which the ZARP run is executed",
        )

    @staticmethod
    def _set_user_arguments(
        argument_group: argparse._ArgumentGroup,  # pylint: disable=W0212
    ) -> None:
        """Add user arguments.

        Args:
            argument_group: Argument group object.
        """
        argument_group.add_argument(
            "--affiliations",
            action="append",
            default=None,
            type=str,
            metavar="STR",
            help=(
                "your affiliation; parameter can be specified multiple times"
                " to provide more than one affiliation"
            ),
        )
        argument_group.add_argument(
            "--author",
            default=None,
            type=str,
            metavar="STR",
            help="your name",
        )
        argument_group.add_argument(
            "--emails",
            action="append",
            default=None,
            type=str,
            metavar="STR",
            help=(
                "your email address; parameter can be specified multiple times"
                " to provide more than one email address"
            ),
        )
        argument_group.add_argument(
            "--logo",
            default=None,
            type=str,
            metavar="STR",
            help="path or URL pointing to your organization's logo",
        )
        argument_group.add_argument(
            "--urls",
            action="append",
            default=None,
            type=str,
            metavar="STR",
            help=(
                "one or more relevant URLs, pointing to, e.g., your personal"
                " or organization's websites; parameter can be specified"
                " multiple times to provide more than one affiliation"
            ),
        )

    def parse_arguments(self) -> None:
        """Parse arguments."""
        self.args_parsed = self.parser.parse_args(self.args)

    def process_arguments(self) -> None:  # pylint: disable=R0912
        """Process arguments."""
        # check for required arguments
        if (
            len(self.args_parsed.sample_references) == 0
            and self.args_parsed.init is False
        ):
            self.parser.print_usage(file=sys.stderr)
            print(
                "zarp-cli: error: at least one of the following arguments "
                "required if not in initialization mode: REF, --sample-table"
            )
            sys.exit(1)

        # set special cases for keeping files
        if self.args_parsed.cleanup_strategy is not None:
            for singleton in ["NONE", "ALL"]:
                if (
                    singleton in self.args_parsed.cleanup_strategy
                    and len(self.args_parsed.cleanup_strategy) != 1
                ):
                    self.parser.print_usage(file=sys.stderr)
                    sys.stderr.write(
                        "zarp: error: argument --cleanup-strategy: invalid "
                        "choices: multiple arguments not allowed if "
                        f"'{singleton}' included\n"
                    )
                    sys.exit(1)
            if "NONE" in self.args_parsed.cleanup_strategy:
                setattr(self.args_parsed, "cleanup_strategy", [])
            elif "ALL" in self.args_parsed.cleanup_strategy:
                setattr(
                    self.args_parsed,
                    "cleanup_strategy",
                    [
                        "CONFIG",
                        "LOGS",
                        "RESULTS",
                        "TEMPORARY",
                    ],
                )
            setattr(
                self.args_parsed,
                "cleanup_strategy",
                [
                    OutputFileGroups[item]
                    for item in self.args_parsed.cleanup_strategy
                ],
            )

        # set enum choices to values
        if self.args_parsed.execution_mode is not None:
            setattr(
                self.args_parsed,
                "execution_mode",
                ExecModes[self.args_parsed.execution_mode],
            )
        if self.args_parsed.dependency_embedding is not None:
            setattr(
                self.args_parsed,
                "dependency_embedding",
                DependencyEmbeddingStrategies[
                    self.args_parsed.dependency_embedding
                ],
            )

        # set type for source
        if self.args_parsed.source is not None:
            try:
                setattr(
                    self.args_parsed, "source", int(self.args_parsed.source)
                )
            except ValueError:
                pass

        # check for multiple values
        if self.args_parsed.adapter_3p is not None:
            adapters_3p = self.args_parsed.adapter_3p.split(",")
            adapter_3p = tuple(
                None if item == "" else item
                for item in (
                    (adapters_3p[0], adapters_3p[1])
                    if len(adapters_3p) == 2
                    else (adapters_3p[0], None)
                )
            )
            setattr(self.args_parsed, "adapter_3p", adapter_3p)
        if self.args_parsed.adapter_5p is not None:
            adapters_5p = self.args_parsed.adapter_5p.split(",")
            adapter_5p = tuple(
                None if item == "" else item
                for item in (
                    (adapters_5p[0], adapters_5p[1])
                    if len(adapters_5p) == 2
                    else (adapters_5p[0], None)
                )
            )
            setattr(self.args_parsed, "adapter_5p", adapter_5p)
        if self.args_parsed.adapter_poly_3p is not None:
            adapters_poly_3p = self.args_parsed.adapter_poly_3p.split(",")
            adapter_poly_3p = tuple(
                None if item == "" else item
                for item in (
                    (adapters_poly_3p[0], adapters_poly_3p[1])
                    if len(adapters_poly_3p) == 2
                    else (adapters_poly_3p[0], None)
                )
            )
            setattr(self.args_parsed, "adapter_poly_3p", adapter_poly_3p)
        if self.args_parsed.adapter_poly_5p is not None:
            adapters_poly_5p = self.args_parsed.adapter_poly_5p.split(",")
            adapter_poly_5p = tuple(
                None if item == "" else item
                for item in (
                    (adapters_poly_5p[0], adapters_poly_5p[1])
                    if len(adapters_poly_5p) == 2
                    else (adapters_poly_5p[0], None)
                )
            )
            setattr(self.args_parsed, "adapter_poly_5p", adapter_poly_5p)

    def set_argument_groups(self, attr: str = "grouped") -> None:
        """
        Parse command line (CLI) arguments.

        Returns:
            Parsed CLI arguments
        """
        # create dictionary of arg groups
        setattr(self.args_parsed, attr, {})
        for arg_group, arg_names in self.ARGUMENT_GROUPS.items():
            getattr(self.args_parsed, attr)[arg_group] = {
                key: val
                for key, val in vars(self.args_parsed).items()
                if key in arg_names
            }
