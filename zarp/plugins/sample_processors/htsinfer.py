"""Infer missing sample metadata with HTSinfer."""

import logging
from pathlib import Path

import pandas as pd

from zarp.abstract_classes.sample_processor import SampleProcessor

LOGGER = logging.getLogger(__name__)


class SampleProcessorHTSinfer(
    SampleProcessor
):  # pylint: disable=too-few-public-methods
    """Infer metadata with HTSinfer.

    Args:
        records: Pandas ``DataFrame`` object.
        config: ``Config`` object.

    Attributes:
        records: Pandas ``DataFrame`` object.
        config: ``Config`` object.
    """

    # pylint: disable=unused-argument
    def process(  # pylint: disable=arguments-differ
        self,
        loc: Path = Path.cwd(),
        workflow: Path = Path.cwd() / "Snakefile",
    ) -> pd.DataFrame:
        """Infer metadata with HTSinfer.

        Args:
            loc: Working directory. Data may be located within child
                directories. Defaults to current working directory.
            workflow: Path to Snakemake workflow for running HTSinfer.
                Defaults to ``Snakefile`` in current working directory.

        Returns: Dataframe with inferred sample metadata.
        """
        # TODO: Uncomment when records selector and tests are implemented.
        # if self.records.empty:
        #     LOGGER.debug("No metadata to infer.")
        #     return self.records
        LOGGER.info("Inferring missing metadata...")
        LOGGER.warning("Plugin not implemented!")
        LOGGER.info("Metadata inferred: DESCRIBE WHAT WAS SET")
        return self.records

    def _select_records(self) -> None:
        """Select records to process."""
