"""Set missing metadata defaults."""

import logging

import pandas as pd

from zarp.abstract_classes.sample_processor import SampleProcessor

LOGGER = logging.getLogger(__name__)


class SampleProcessorDefaults(
    SampleProcessor
):  # pylint: disable=too-few-public-methods
    """Set available defaults for missing sample metadata.

    Args:
        records: Pandas ``DataFrame`` object.
        config: ``Config`` object.

    Attributes:
        records: Pandas ``DataFrame`` object.
        config: ``Config`` object.
    """

    def process(self) -> pd.DataFrame:
        """Set available defaults for missing sample metadata.

        Returns: Dataframe with set defaults.
        """
        # TODO: Uncomment when records selector and tests are implemented.
        # if self.records.empty:
        #     LOGGER.debug("No defaults to set.")
        #     return self.records
        LOGGER.info("Setting defaults...")
        LOGGER.warning("Plugin not implemented!")
        LOGGER.info("Defaults set: DESCRIBE WHAT WAS SET")

        sample_index = self.records.index

        defaults = self.config.dict()
        default_data = {}
        for key, val in defaults:
            default_data[key] = [val for _ in range(len(sample_index))]
        defaults_df: pd.DataFrame(default_data)
        default_df.index = sample_index

        common_cols = default_df.columns.intersection(self.records.columns)
        self.records = default_df.drop(common_cols, axis=1).join(self.records, how="right")
        
        return self.records
