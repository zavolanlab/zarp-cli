"""Main class and entry point when imported as a library."""

import logging

import pandas as pd

from zarp.config import models
from zarp.config.enums import ExecModes
from zarp.config.samples import SampleProcessor
from zarp.plugins.sample_fetchers.sra import SampleFetcherSRA
from zarp.plugins.sample_processors.genomepy import SampleProcessorGenomePy
from zarp.plugins.sample_processors.htsinfer import SampleProcessorHTSinfer
from zarp.plugins.sample_processors.defaults import SampleProcessorDefaults
from zarp.plugins.sample_processors.dummy_data import SampleProcessorDummyData
from zarp.runner.zarp_runner import SampleRunnerZARP
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
        """Set up run.

        Raises:
            FileNotFoundError: If genome assemblies map file is not found.
        """
        if self.config.run.execution_mode != ExecModes.RUN.value:
            LOGGER.warning(
                f"Execution mode: '{self.config.run.execution_mode}'"
            )
        LOGGER.info("Setting up run...")
        self.config.run.working_directory.mkdir(parents=True, exist_ok=True)
        if not self.config.run.genome_assemblies_map.is_file():
            raise FileNotFoundError(
                "Genome assemblies map file not found: "
                f"'{self.config.run.genome_assemblies_map}'"
            )
        LOGGER.info(
            f"Run '{self.config.run.identifier}' set up in working directory:"
            f" '{self.config.run.working_directory}'"
        )

    def process_samples(self) -> SRP:
        """Process samples.

        Returns:
            Sample record processor instance.
        """
        df: pd.DataFrame

        # dereference sample references
        # TODO: integrate with SampleProcessor
        LOGGER.info("Dereferencing sample references...")
        sample_processor = SampleProcessor(
            *self.config.ref,
            sample_config=self.config.sample,
            run_config=self.config.run,
        )
        sample_processor.set_samples()
        LOGGER.info(
            f"Sample references dereferenced: {len(sample_processor.samples)}"
        )

        # instantiate sample record processor
        srp: SRP = SRP()
        srp.append_from_obj(samples=sample_processor.samples)
        srp.view()

        # fill defaults
        processor_defaults = SampleProcessorDefaults(
            config=self.config,
            records=srp.records,
        )
        df = processor_defaults.process()
        srp.update(df=df)
        srp.view()

        # fetch remote samples from SRA
        fetcher_sra = SampleFetcherSRA(
            config=self.config,
            records=srp.records,
        )
        df = fetcher_sra.process(
            loc=self.config.run.working_directory / "sra_download",
            workflow=self.config.run.zarp_directory
            / "workflow"
            / "rules"
            / "sra_download.smk",
        )
        srp.update(df=df, by="identifier")
        srp.view()

        # infer sample metadata with HTSinfer
        processor_htsinfer = SampleProcessorHTSinfer(
            config=self.config,
            records=srp.records,
        )
        df = processor_htsinfer.process(
            loc=self.config.run.working_directory / "htsinfer",
            workflow=self.config.run.zarp_directory
            / "workflow"
            / "rules"
            / "htsinfer.smk",
        )
        srp.update(df=df)
        srp.view()

        # fetch genome resources with genomepy
        fetcher_genomepy = SampleProcessorGenomePy(
            config=self.config,
            records=srp.records,
        )
        df = fetcher_genomepy.process(
            loc=self.config.run.working_directory / "genomes",
        )
        srp.update(df=df, overwrite=True)
        srp.view()

        # fill with dummy data
        processor_dummy_data = SampleProcessorDummyData(
            config=self.config,
            records=srp.records,
        )
        df = processor_dummy_data.process()
        srp.update(df=df)
        srp.view()

        return srp

    def execute_run(self, samples: SRP) -> None:
        """Execute run.

        Args:
            samples: Sample record processor instance.
        """
        runner_zarp = SampleRunnerZARP(
            config=self.config,
            records=samples.records,
        )
        runner_zarp.process(
            loc=self.config.run.working_directory / "zarp",
            workflow=self.config.run.zarp_directory / "workflow" / "Snakefile",
        )
