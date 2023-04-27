"""Fetch genome resources with ``mod:genomepy``."""

import logging
from pathlib import Path

import pandas as pd

from zarp.abstract_classes.sample_processor import SampleProcessor

LOGGER = logging.getLogger(__name__)


class SampleFetcherGenomePy(
    SampleProcessor
):  # pylint: disable=too-few-public-methods
    """Fetch genome resources with ``mod:genomepy``.

    Args:
        records: Pandas ``DataFrame`` object.
        config: ``Config`` object.

    Attributes:
        records: Pandas ``DataFrame`` object.
        config: ``Config`` object.
    """

    def process(  # pylint: disable=arguments-differ
        self,
        loc: Path = Path.cwd(),  # pylint: disable=unused-argument
    ) -> pd.DataFrame:
        """Fetch genome resources with ``mod:genomepy``.

        Args:
            loc: Path to fetch resources to. Resources may be located within
                child directories. Defaults to current working directory.

        Returns: Dataframe with local path information for genome resources.
        """
        # TODO: Uncomment when records selector and tests are implemented.
        # if self.records.empty:
        #     LOGGER.debug("No genome resources to fetch.")
        #     return self.records
        LOGGER.info("Fetching genome resources...")
        LOGGER.warning("Plugin not implemented!")
        LOGGER.info("Fetched: DESCRIBE WHAT WAS FETCHED")
        return self.records

    def _select_records(self) -> None:
        """Select records to process."""
