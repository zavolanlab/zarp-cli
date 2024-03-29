"""Set missing metadata defaults."""

import logging
from typing import Any, Dict, List

import pandas as pd

from zarp.abstract_classes.sample_processor import SampleProcessor
from zarp.samples.sample_record_processor import SampleRecordProcessor as SRP

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
        if self.records.empty:
            LOGGER.debug("No defaults to set.")
            return self.records
        defaults: Dict[str, Any] = self.config.sample.dict()
        default_data: Dict[str, List[Any]] = {}
        sample_index: pd.Index = self.records.index
        for key, val in defaults.items():
            default_data[key] = [val for _ in range(len(sample_index))]
        default_df: pd.DataFrame = pd.DataFrame(default_data)
        srp: SRP = SRP()
        srp.append(self.records)
        srp.update(
            df=default_df,
            anchor=self.config.run.working_directory,
            path_columns=["annotations", "reference_sequences"],
        )
        return srp.records

    def _select_records(self) -> None:
        """Select records to process."""
