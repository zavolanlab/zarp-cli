"""Main class and entry point when imported as a library."""

import logging

import pandas as pd

from zarp.config import models
from zarp.config.samples import SampleProcessor
from zarp.plugins.sample_fetchers.sra import SampleFetcherSRA
from zarp.samples.sample_record_processor import SampleRecordProcessor as SRP

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
        LOGGER.info("Setting up run...")
        self.config.run.working_directory.mkdir(parents=True, exist_ok=True)
        LOGGER.info(
            f"Run '{self.config.run.identifier}' set up in working directory:"
            f" '{self.config.run.working_directory}'"
        )

    def process_samples(self) -> None:
        """Process samples."""
        LOGGER.info("Processing sample references...")
        sample_processor = SampleProcessor(
            *self.config.ref,
            sample_config=self.config.sample,
            run_config=self.config.run,
        )
        sample_processor.set_samples()
        LOGGER.info(f"Samples dereferenced: {len(sample_processor.samples)}")

        srp: SRP = SRP()
        srp.append_from_obj(samples=sample_processor.samples)
        srp.view()

        sample_fetcher = SampleFetcherSRA(
            config=self.config,
            records=srp.records,
        )
        if not sample_fetcher.records.empty:
            df: pd.DataFrame = sample_fetcher.process(
                loc=self.config.run.working_directory
                / "runs"
                / "sra_download",
                workflow=self.config.run.zarp_directory
                / "workflow"
                / "rules"
                / "sra_download.smk",
            )
            srp.update(df=df, by="identifier")
            srp.view()
