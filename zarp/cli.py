#!/usr/bin/env python3
"""Command-line interface client."""

import logging
import signal
import sys
from traceback import format_exc
from typing import Dict

from rich.logging import RichHandler

from zarp.config.args import ArgParser
from zarp.config.enums import LogLevels
from zarp.config.init import Initializer
from zarp.config.parser import ConfigParser
from zarp.zarp import ZARP

LOGGER = logging.getLogger(__name__)


def setup_logging(
    verbosity: str = "INFO",
) -> None:
    """Configure logging."""
    level = LogLevels[verbosity].value
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="%m-%d %H:%M:%S",
        handlers=[RichHandler()],
    )


def main() -> None:  # pylint: disable=R0915
    """Entry point for CLI executable."""
    try:
        # create stack for log messages before logging is set up
        messages: Dict = {item.value: [] for item in LogLevels}

        # parse CLI args
        arg_parser = ArgParser()
        arg_parser.set_parser()
        arg_parser.set_arguments()
        arg_parser.parse_arguments()
        arg_parser.process_arguments()
        arg_parser.set_argument_groups()
        args = arg_parser.args_parsed
        messages[logging.DEBUG].append(f"CLI arguments: {args}")

        # set up logging
        messages[logging.DEBUG].append("Setting up logging...")
        setup_logging(verbosity=args.verbosity)
        for lvl, msgs in messages.items():
            for msg in msgs:
                LOGGER.log(lvl, msg)
        LOGGER.debug("Logging set up")

        # run in initialization mode
        if args.init or not args.config_file.is_file():
            if not args.config_file.is_file():
                LOGGER.warning(f"Config file not found: {args.config_file}")
            LOGGER.info("Starting ZARP-cli in mode: initialization")
            initializer = Initializer()
            initializer.set_from_file(config_file=args.config_file)
            initializer.set_from_user_input()
            try:
                initializer.write_yaml(
                    contents=initializer.config,
                    path=args.config_file,
                )
            except (OSError, ValueError):
                args.config_file.unlink()
                raise
            LOGGER.info(
                f"Default configuration written to: {args.config_file}"
            )
            LOGGER.info("Done")
            sys.exit(0)

        # parse config
        LOGGER.info("Starting ZARP-cli in mode: normal")
        LOGGER.debug("Parsing configuration...")
        config_parser = ConfigParser(config_file=args.config_file)
        config_parser.set_from_file()
        config_parser.update_from_mapping(config_mapping=args.grouped)
        config_parser.config.ref = args.sample_references
        LOGGER.info(f"Configuration: {config_parser.config}")

        # run in normal mode
        zarp = ZARP(config=config_parser.config)
        try:
            zarp.set_up_run()
            zarp.process_samples()
            zarp.prepare_run_config()
        except Exception as exc:  # pylint: disable=W0703
            LOGGER.error(f"{exc}")
            LOGGER.debug(format_exc())
            sys.exit(1)

    except KeyboardInterrupt:
        print()
        LOGGER.error("Execution interrupted.")
        sys.exit(128 + signal.SIGINT)

    # conclude execution
    LOGGER.info("Done")
    sys.exit(0)


if __name__ == "__main__":
    main()
