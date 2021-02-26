#!/usr/bin/env python
"""CLI runner for the ZARP RNA-Seq analysis pipeline."""

import argparse
from enum import Enum
import logging
import sys
from typing import (Optional, Sequence)

from zarp import __version__

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
    """Parse CLI arguments."""
    description = (
        f"{sys.modules[__name__].__doc__}\n\n"
        ""
    )
    epilog = (
        f"%(prog)s v{__version__}, (c) 2021 by Zavolab "
        "(zavolab-biozentrum@unibas.ch)"
    )
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    samples = parser.add_argument_group(
        title="Positional arguments",
    )
    samples.add_argument(
        "samples",
        metavar="PATH/ID",
        nargs="*",
        type=str,
        help=(
            "paths to individual samples, ZARP sample tables and/or SRA "
            "identifiers; see online documentation for details"
        ),
    )
#    runs = parser.add_argument_group(
#        title="Run-specific arguments",
#        description=(
#            "Use these arguments to overwrite defaults set up during "
#            "initiation; see online documentation for details"
#        ),
#    )
    misc = parser.add_argument_group(
        title="ZARP-CLI arguments",
        description="Arguments not passed on to the analysis pipeline",
    )
    misc.add_argument(
        "-h", "--help",
        action="help",
        help="show this help message and exit",
    )
    misc.add_argument(
        "--init",
        action="store_true",
        help="edit user-level default parameters and exit",
    )
    misc.add_argument(
        "--verbosity",
        choices=[e.name for e in LogLevels],
        default="INFO",
        type=str,
        help="logging verbosity level",
    )
    misc.add_argument(
        "--version",
        action="version",
        version=epilog,
        help="show version information and exit",
    )

    args_parsed = parser.parse_args(args)
    if not args_parsed.init and not args_parsed.samples:
        print("Error: no samples supplied\n")
        parser.print_help(sys.stderr)
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
    """Main function.

    Args:
        args: Command-line arguments and their values.
    """

    # Initialize
    args = parse_args()
    setup_logging(
        verbosity=args.verbosity,
    )
    LOGGER.debug("Logging set up")

    # Do stuff

    # Clean up
    LOGGER.info("Done")


if __name__ == "__main__":
    main()
