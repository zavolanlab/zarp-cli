#!/usr/bin/env python3
import argparse
import logging
import sys
from pathlib import Path
from zarp import __version__
# from pydantic import BaseModel
# from pydantic_cli import run_and_exit
LOGGER = logging.getLogger(__name__)

def parse_cli_args() -> argparse.Namespace:
    """
    Parse command line (CLI) arguments.

    Returns:
        Parsed CLI arguments
    """
    # set metadata
    __doc__ = "ZARP-cli argument parser"


    description = (
        f"{sys.modules[__name__].__doc__}\n\n"
        ""
    )
    epilog = (
        f"%(prog)s v{__version__}, (c) 2021 by Zavolab "
        "(zavolab-biozentrum@unibas.ch)"
    )

    # custom actions
    # need to recognise in this step if the input provided
    # correpsonds to sra entries
    class PathsAction(argparse.Action):
        """Sanitize ``paths`` parsing in positional args."""
        def __call__(
            self,
            parser,
            namespace,
            values,
            option_string=None,
        ) -> None:
            if len(values) > 2:
                parser.print_usage(file=sys.stderr)
                sys.stderr.write(
                    "zarp-cli: error: only one or two of the following "
                    "arguments are allowed: PATH\n"
                )
                parser.exit(2)
            if len(values) == 1:
                values.append(None)
            setattr(namespace, self.dest, values)

    # instantiate parser
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        'samples',
        nargs="+",
        type=Path,
        action=PathsAction,
        metavar="PATH",
        help=(
            "paths to individual samples, ZARP sample tables and/or"
            "SRA identifiers; see online documentation for details"
        ),
    )
    parser.add_argument(
        "-h", "--help",
        action="help",
        help="show this help message and exit",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=epilog,
        help="show version information and exit",
    )
    parser.add_argument(
        "--name",
        required=False,
        help=(
            "name of each sample "
            "if not specified, the sample name "
            "is the sample id (or the concatenation in case of "
            "multiple lanes or paired-end library) "
        ),
    )
    parser.add_argument(
        "--output-directory",
        default=Path.cwd(),
        type=lambda p: Path(p).absolute(),
        metavar="PATH",
        help="output directory",
    )
    annotation = parser.add_argument_group("organism annotation")
    annotation.add_argument(
        "--organism",
        help=(
            "organism that the sample originates from "
        ),
    )
    annotation.add_argument(
        "--gtf",
        type=str,
        metavar="STR",
        help=(
            "gtf annotation file containing the transcript information"
        ),
    )
    annotation.add_argument(
        "--genome",
        type=str,
        metavar="STR",
        help=(
            "fasta file containing the chromosome sequences"
        ),
    )
    processing = parser.add_argument_group("ZARP processing options")
    processing.add_argument(
        "--init",
        required=True,
        type=bool,
        metavar="BOOL",
        help=(
            "config file containing ZARP rule-specific parameters" 
        )
    )
    processing.add_argument(
        "--read-orientation",
        required=False,
        type=str,
        metavar="STR",
        help=(
            "fragment library type (salmon compatible abbreviations) "
            "if not provided it will be inferred by htsinfer"
        ),
    )
    processing.add_argument(
        "--adapter-3p",
        default="XXX",
        type=str,
        metavar="STR",
        help=(
            "3 prime end adapter used in the protocol "
            "if not provided it will be inferred by htsinfer "
        ),
    )
    processing.add_argument(
        "--trim-polya",
        type=bool,
        default=False,
        metavar="BOOL",
        help=(
            "remove poly-A tails from reads "
        ),
    )
     
    processing.add_argument(
        "--fragment-length-mean",
        default=100,
        type=int,
        metavar="INT",
        help=(
            "mean fragment size "
        ),
    )
    processing.add_argument(
        "--fragment-length-sd",
        default=10,
        type=int,
        metavar="INT",
        help=(
            "standard deviation of fragment sizes "
        ),
    )
    # to be moved to the rule-specific config
    processing.add_argument(
        "--multimappers",
        type=int,
        metavar="INT",
        default=40,
        help=(
            "STAR related choice of multimappers "
        )
    )
    # to be moved to the rule-specific config
    processing.add_argument(
        "--soft-clip",
        choices=['Local', 'EndtoEnd'],
        default='EndtoEnd',
        help=(
            "STAR related choice of multimappers "
            "choices: {%(choices)s} "
        )
    ) 
    htsinfer = parser.add_argument_group("htsinfer options")
    htsinfer.add_argument(
        "--no-inference",
        default=False,
        type=bool,
        metavar="BOOL",
        help=(
            "this option disables htsinfer inferences "
            "if htsinfer is disabled, library type"
            "has to be specified by the user"
        ),
    )
    htsinfer.add_argument(
        "--htsinfer-config",
        default=None,
        type=Path,
        metavar="PATH",
        help=(
            "htsinfer specific config"
        ),
    )
    system = parser.add_argument_group("containers and system related options")
    system.add_argument(
        "--tool-packaging",
        choices=["use-conda", "use-singularity"],
        default="use-singularity",
        type=str,
        metavar="STR",
        help=(
            "choose container environment, "
            "choices: {%(choices)s} "
        ),
    ) 
    system.add_argument(
        "--profile",
        choices=["slurm", "local"],
        default="local",
        type=str,
        metavar="STR",
        help=(
            "choose cluster environment "
            "choices: {%(choices)s} "
        ),
    )
    system.add_argument(
        "--execution-mode",
        choices=["dry-run", "prepare-run", "run"],
        default="dry-run",
        type=str,
        metavar="STR",
        help=(
            "mode of execution only the option `run` "
            "will create the final results "
            "choices: {%(choices)s} "
        ),
    )
    verbosity = parser.add_argument_group("verbosity related options")
    verbosity.add_argument(
        "--no-report",
        default=False,
        type=bool,
        metavar="BOOL",
        help=(
            "this option disables the reports of ZARP"
            "(multiqc and snakemake) "
        ),
    )
    verbosity.add_argument(
        "--delete-files",
        choices=["results", "temporary", "logs", "all"],
        default="temporary",
        type=str,
        metavar="STR",
        help=(
            "remove files after ZARP has finished "
            "choices: {%(choices)s} "
        ),
    )

    report = parser.add_argument_group("report")
        
    report.add_argument(
        "--run-description",
        default="",
        type=str,
        metavar="STR",
        help=(
            "text description about the samples included"
        )
    )
    report.add_argument(
        "--run-identifier",
        default=None,
        type=str,
        metavar="STR",
        help=(
            "identifier specific to the run "
            "make sure this is unique "
        )
    )
    report.add_argument(
        "--logo",
        default=None,
        type=str,
        metavar="STR",
        help=(
            "logo that will appear in the multiqc report "    
        )
    )
    report.add_argument(
        "--url",
        default=None,
        type=str,
        metavar="STR",
        help=(
            "url that will appear in the multiqc report "    
        )
    )
    report.add_argument(
        "--author",
        default=None,
        type=str,
        metavar="STR",
        help=(
            "user information that will appear in the multiqc report "    
        )
    )
    report.add_argument(
        "--author-email",
        default=None,
        type=str,
        metavar="STR",
        help=(
            "user email that will appear in the multiqc report "    
        )
    )
    args = parser.parse_args()

    return args


def main() -> None:
    """Entry point for CLI executable."""
    try:
        # handle CLI args
        args = parse_cli_args()
    except KeyboardInterrupt:
        LOGGER.error('Execution interrupted.')
        sys.exit(128 + signal.SIGINT)

    # conclude execution
    LOGGER.info("Done")
    sys.exit(hts_infer.state.value)



if __name__ == '__main__':
    main()