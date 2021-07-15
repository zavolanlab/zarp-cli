#!/usr/bin/env python3
"""Command-line interface client."""

import argparse
from enum import Enum
import logging
from pathlib import Path
import signal
import sys
from typing import (Optional, Sequence)

from zarp import __version__
from zarp.zarp import ZARP

LOGGER = logging.getLogger(__name__)


class LogLevels(Enum):
    """Log level enumerator."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARNING
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


def parse_args(
    args: Optional[Sequence[str]] = None
) -> argparse.Namespace:
    """
    Parse command line (CLI) arguments.

    Returns:
        Parsed CLI arguments
    """
    # set metadata
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
                    "zarp-cli: error: not more than two of the following "
                    "arguments are allowed: PATH\n"
                )
                parser.exit(2)
            elif len(values) == 1:
                values.append(None)
            elif len(values) == 0:
                values += [None, None]
            setattr(namespace, self.dest, values)

    # Instantiate parser
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Positional parameters
    parser.add_argument(
        "--name",
        required=False,
        help=(
            "name of each sample "
            "if not specified, the sample name "
            "is the sample id (or the concatenation in case of "
            "multiple lanes or paired-end library)"
        ),
    )
    parser.add_argument(
        "-o", "--output-directory",
        default=Path.cwd(),
        type=lambda p: Path(p).absolute(),
        metavar="PATH",
        help="directory where output shall be written",
    )

    run_modes = parser.add_argument_group(
        title="run modes",
        description=(
            "Specifying any of the options in this group will cause ZARP-cli "
            "to behave differently then the default mode. Generally, most "
            "other parameters are not required and will be ignored in these "
            "cases."
        )
    )
    run_modes.add_argument(
        "--init",
        default=False,
        action="store_true",
        help="edit user-level default parameters and exit",
    )
    run_modes.add_argument(
        "-h", "--help",
        action="help",
        help="show this help message and exit",
    )
    run_modes.add_argument(
        "--version",
        action="version",
        version=epilog,
        help="show version information and exit",
    )

    # Sample-specific parameters
    sample = parser.add_argument_group(
        title="sample-related options",
        description=(
            "Specify the values for any sample-related parameters. If "
            "provided via the command line, the same values will be applied "
            "to all samples. When analyzing multiple samples and samples "
            "either originate different sources and/or shall be processed "
            "with different genome resources, these values should be "
            "specified in a sample table instead. Alternatively, you can make "
            "use of the inference functionality to infer the sample source "
            "and use or retrieve the corresponding genome resources as per "
            "your ZARP-cli configuration."
        )
    )
    # TODO: ids, read layout
    sample.add_argument(
        'samples',
        nargs="*",
        type=Path,
        action=PathsAction,
        metavar="PATH",
        help=(
            "paths to individual samples, ZARP sample tables and/or "
            "SRA identifiers; see online documentation for details"
        ),
    )
    sample.add_argument(
        "--fragment-length-mean",
        default=100,
        type=int,
        metavar="INT",
        help=(
            "mean of the fragment length distribution"
        ),
    )
    sample.add_argument(
        "--fragment-length-sd",
        default=10,
        type=int,
        metavar="INT",
        help=(
            "standard deviation of the fragment length distribution"
        ),
    )
    sample.add_argument(
        "--sample-source",
        help=(
            "origin of the sample as either a NCBI taxonomy database "
            "identifier, e.g, 9606 for humans, or the corresponding full "
            "name, e.g., 'Homo sapiens'."
        )
    )
    sample.add_argument(
        "--annotations",
        type=str,
        metavar="STR",
        help=(
            "gene annotation file matching the `--organism`, in GTF format"
        ),
    )
    sample.add_argument(
        "--reference-sequences",
        type=str,
        metavar="STR",
        help=(
            "file containing reference/chromosome sequences matching the "
            "`--organism`, in FASTA format"
        ),
    )

    processing = parser.add_argument_group("ZARP processing options")
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
        help="3'-end adapter, truncated during preprocessing",
    )
    processing.add_argument(
        "--trim-polya",
        type=bool,
        default=False,
        metavar="BOOL",
        help=(
            "remove poly-A tails from reads"
        ),
    )

    # to be moved to the rule-specific config
    processing.add_argument(
        "--multimappers",
        type=int,
        metavar="INT",
        default=40,
        help=(
            "STAR related choice of multimappers"
        )
    )
    # to be moved to the rule-specific config
    processing.add_argument(
        "--soft-clip",
        choices=['Local', 'EndtoEnd'],
        default='EndtoEnd',
        help=(
            "STAR related choice of multimappers "
            "choices: {%(choices)s}"
        )
    )

    # Parameters related to the inference of missing sample metadata
    htsinfer = parser.add_argument_group(
        title="metadata inference options",
        description=(
            "Specify if and how sample metadata sniffing shall be performed "
            "via HTSinfer."
        )
    )
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
            "choices: {%(choices)s}"
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
            "choices: {%(choices)s}"
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
            "choices: {%(choices)s}"
        ),
    )

    verbosity = parser.add_argument_group("verbosity related options")
    verbosity.add_argument(
         "--verbosity",
         choices=[e.name for e in LogLevels],
         default="INFO",
         type=str,
         help="logging verbosity level",
     )
    verbosity.add_argument(
        "--no-report",
        default=False,
        type=bool,
        metavar="BOOL",
        help=(
            "this option disables the reports of ZARP"
            "(multiqc and snakemake)"
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
            "choices: {%(choices)s}"
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
            "make sure this is unique"
        )
    )
    report.add_argument(
        "--logo",
        default=None,
        type=str,
        metavar="STR",
        help=(
            "logo that will appear in the multiqc report"
        )
    )
    report.add_argument(
        "--url",
        default=None,
        type=str,
        metavar="STR",
        help=(
            "url that will appear in the multiqc report"
        )
    )
    report.add_argument(
        "--author",
        default=None,
        type=str,
        metavar="STR",
        help=(
            "user information that will appear in the multiqc report"
        )
    )
    report.add_argument(
        "--author-email",
        default=None,
        type=str,
        metavar="STR",
        help=(
            "user email that will appear in the multiqc report"
        )
    )

    # parse CLI args
    args_parsed = parser.parse_args(args)

    # fix faulty usage string for nargs={1,2}
    parser.usage = parser.format_usage()
    parser.usage = parser.usage.replace("PATH [PATH ...]", "PATH [PATH]")

    # check for required arguments
    if all(e is None for e in args_parsed.samples) and not args_parsed.init:
        parser.print_usage(file=sys.stderr)
        print(
            "zarp-cli: error: at least one of the following arguments "
            "required if not in init mode: PATH"
        )
        sys.exit(1)

    return args_parsed


def setup_logging(
    verbosity: str = 'INFO',
) -> None:
    """Configure logging."""
    level = LogLevels[verbosity].value
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] %(message)s",
        datefmt='%m-%d %H:%M:%S',
    )


def main() -> None:
    """Entry point for CLI executable."""
    try:
        # handle CLI args
        args = parse_args()

        # set up logging
        setup_logging(verbosity=args.verbosity)
        messages = {e.value: [] for e in LogLevels}
        messages[logging.DEBUG].append('Logging set up')

        # log startup messages
        if not args.init:
            LOGGER.info("Starting ZARP-cli...")
        else:
            LOGGER.info("Starting ZARP-cli in init mode...")
        for lvl, msgs in messages.items():
            for msg in msgs:
                LOGGER.log(lvl, msg)

        # initialize ZARP-cli
        LOGGER.debug(f"CLI arguments: {args}")
        zarp = ZARP(
            sample_1=args.samples[0],
            sample_2=args.samples[1],
            name=args.name,
            output_directory=args.output_directory,
            organism=args.organism,
            gtf=args.gtf,
            genome=args.genome,
            init=args.init,
            read_orientation=args.read_orientation,
            adapter_3p=args.adapter_3p,
            trim_polya=args.trim_polya,
            fragment_length_mean=args.fragment_length_mean,
            fragment_length_sd=args.fragment_length_sd,
            multimappers=args.multimappers,
            soft_clip=args.soft_clip,
            no_inference=args.no_inference,
            htsinfer_config=args.htsinfer_config,
            tool_packaging=args.tool_packaging,
            profile=args.profile,
            execution_mode=args.execution_mode,
            no_report=args.no_report,
            delete_files=args.delete_files,
            run_description=args.run_description,
            run_identifier=args.run_identifier,
            logo=args.logo,
            url=args.url,
            author=args.author,
            author_email=args.author_email,
        )
        zarp.evaluate()

    except KeyboardInterrupt:
        LOGGER.error('Execution interrupted.')
        sys.exit(128 + signal.SIGINT)

    # conclude execution
    LOGGER.info("Done")
    sys.exit(0)


if __name__ == '__main__':
    main()
