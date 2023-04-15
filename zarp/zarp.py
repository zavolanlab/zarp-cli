"""Main class and entry point when imported as a library."""

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

from zarp.config import models
from zarp.config.samples import SampleProcessor
from zarp.plugins.sample_fetchers.sra import SampleFetcherSRA
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
        config: models.Config,
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

        sample_fetcher = SampleFetcherSRA(
            samples=sample_processor.samples,
            config=self.config,
        )
        if sample_fetcher.samples:
            local_paths: Dict[str, Tuple[Path, Optional[Path]]]
            local_paths = sample_fetcher.fetch(
                loc=self.config.run.working_directory
                / "runs"
                / "sra_download",
                workflow=self.config.run.zarp_directory
                / "workflow"
                / "rules"
                / "sra_download",
            )
            sample_fetcher.update(local_paths)
