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
        """Set up run."""
        if self.config.run.working_directory is None:
            self.config.run.working_directory = Path.cwd()
        self.config.run.working_directory.mkdir(parents=True, exist_ok=True)
        LOGGER.info("Setting up run...")
        if self.config.run.identifier is None:
            self.config.run.identifier = generate_id()
        LOGGER.info(f"Run identifier: {self.config.run.identifier}")
        self.config.run.working_directory.mkdir(
            parents=True,
            exist_ok=True,
        )
        LOGGER.info(f"Working directory: {self.config.run.working_directory}")
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
        if len(sample_processor.samples_remote) > 0:
            LOGGER.info("Fetching remote libraries...")
            sample_table = sample_processor.fetch_remote_libraries()
            LOGGER.info("Remote libraries fetched")
            LOGGER.info("Updating paths of fetched libraries...")
            sample_processor.update_sample_paths(sample_table=sample_table)
            LOGGER.info("Paths updated...")
        if self.config.run.working_directory is None:
            self.config.run.working_directory = Path.cwd() / "runs"
            self.config.run.working_directory.mkdir(
                parents=True,
                exist_ok=True,
            )
            LOGGER.warning(
                "Working directory not set. Using:"
                f" {self.config.run.working_directory}"
            )
        self.config.run.sample_table = sample_processor.write_sample_table(
            samples=sample_processor.samples
        )
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
