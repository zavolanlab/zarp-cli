"""Main class and entry point when imported as a library."""

import logging
from pathlib import Path

from zarp.config import models
from zarp.config.run_config import RunConfigFileProcessor
from zarp.config.samples import SampleProcessor
from zarp.utils import generate_id

LOGGER = logging.getLogger(__name__)


class ZARP:
    """Handle ZARP workflow execution.

    Args:
        config: ZARP-cli configuration.

    Attributes:
        config: ZARP-cli configuration.
    """

    def __init__(
        self,
        config: models.Config = models.Config(),
    ):
        """Class constructor."""
        self.config: models.Config = config

    def set_up_run(self) -> None:
        """Set up run.

        Raises:
            FileExistsError: The run directory exists already.
        """
        if self.config.run.working_directory is None:
            self.config.run.working_directory = Path.cwd()
        self.config.run.working_directory.mkdir(parents=True, exist_ok=True)
        LOGGER.info("Setting up run...")
        if self.config.run.identifier is None:
            self.config.run.identifier = generate_id()
        LOGGER.info(f"Run identifier: {self.config.run.identifier}")
        self.config.run.run_directory = (
            self.config.run.working_directory / self.config.run.identifier
        )
        try:
            self.config.run.run_directory.mkdir(parents=False, exist_ok=False)
        except FileExistsError as exc:
            raise FileExistsError(
                f"Run directory '{self.config.run.run_directory}' already "
                "exists. Please choose a different run identifier or "
                "working directory."
            ) from exc
        LOGGER.info(f"Run directory: {self.config.run.run_directory}")
        LOGGER.info("Run set up")

    def process_samples(self) -> None:
        """Process samples."""
        LOGGER.info("Processing sample references...")
        sample_processor = SampleProcessor(
            *self.config.ref,
            sample_config=self.config.sample,
            run_config=self.config.run,
        )
        sample_processor.set_samples()
        LOGGER.info(f"Samples found: {len(sample_processor.samples)}")
        if len(sample_processor.samples) == 0:
            raise ValueError("No samples found. Aborting.")
        self.config.run.sample_table = sample_processor.write_sample_table()
        LOGGER.info(f"Sample table: {self.config.run.sample_table}")
        LOGGER.info("Samples processed")

    def prepare_run_config(self) -> None:
        """Prepare run configuration."""
        LOGGER.info("Preparing run configuration file...")
        run_config_processor = RunConfigFileProcessor(
            run_config=self.config.run,
            user_config=self.config.user,
        )
        self.config.run.run_config = run_config_processor.write_run_config()
        LOGGER.info(
            f"Run configuration file prepared: {self.config.run.run_config}"
        )
