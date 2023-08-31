"""Abstract sample processor classes."""

from abc import ABC, abstractmethod

import pandas as pd

from zarp.config.models import Config
from zarp.config.mappings import columns_model


class SampleProcessor(ABC):  # pylint: disable=too-few-public-methods
    """Abstract sample processor class.

    Defines methods to process sample records.

    Args:
        records: Pandas ``DataFrame`` object.
        config: ``Config`` object.

    Attributes:
        records: Pandas ``DataFrame`` object.
        config: ``Config`` object.
    """

    def __init__(
        self,
        config: Config,
        records: pd.DataFrame = pd.DataFrame(columns=columns_model),
    ) -> None:
        """Class constructor method."""
        self.records: pd.DataFrame = records.copy(deep=True)
        self.config: Config = config
        self._select_records()

    @abstractmethod
    def process(self) -> pd.DataFrame:
        """Process records."""

    @abstractmethod
    def _select_records(self) -> None:
        """Select records to process."""
