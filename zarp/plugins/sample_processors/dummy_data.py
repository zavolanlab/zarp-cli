"""Fill in missing metadata with dummy data."""

import logging
from typing import Dict, List

import pandas as pd

from zarp.abstract_classes.sample_processor import SampleProcessor
from zarp.samples.sample_record_processor import SampleRecordProcessor as SRP

LOGGER = logging.getLogger(__name__)


class SampleProcessorDummyData(
    SampleProcessor
):  # pylint: disable=too-few-public-methods
    """Set dummy data for missing sample metadata, as required by ZARP.

    Args:
        records: Pandas ``DataFrame`` object.
        config: ``Config`` object.

    Attributes:
        records: Pandas ``DataFrame`` object.
        config: ``Config`` object.
    """

    columns = [
        "name",
        "paths_2",
        "adapter_3p_1",
        "adapter_3p_2",
        "adapter_5p_1",
        "adapter_5p_2",
        "adapter_poly_3p_1",
        "adapter_poly_3p_2",
        "adapter_poly_5p_1",
        "adapter_poly_5p_2",
    ]
    dummy_data = "X" * 15

    def process(self) -> pd.DataFrame:
        """Set dummy data for missing sample metadata.

        Returns: Dataframe with dummy data set.
        """
        if self.records.empty:
            LOGGER.debug("No dummy data to set.")
            return self.records

        LOGGER.info("Setting dummy data...")

        default_data: Dict[str, List[str]] = {}
        sample_index: pd.Index = self.records.index
        for key in self.columns:
            default_data[key] = [
                self.dummy_data for _ in range(len(sample_index))
            ]
        default_df: pd.DataFrame = pd.DataFrame(default_data)

        srp: SRP = SRP()
        srp.append(self.records)
        srp.update(
            df=default_df,
            anchor=self.config.run.working_directory,
            path_columns=["annotations", "reference_sequences"],
        )

        LOGGER.info("Dummy data set.")

        return srp.records

    def _select_records(self) -> None:
        """Select records to process."""
