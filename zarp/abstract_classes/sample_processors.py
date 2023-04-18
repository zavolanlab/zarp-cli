"""Abstract sample processor classes."""

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from zarp.config.models import Config
from zarp.config.mappings import columns_model

# pylint: disable=too-few-public-methods


class SampleProcessor(ABC):
    """Abstract sample processor class.

    Defines methods to process ``Sample`` objects.

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
        self.records: pd.DataFrame = records
        self.config: Config = config

    @abstractmethod
    def process(self) -> pd.DataFrame:
        """Process records."""


class SampleFetcher(SampleProcessor):
    """Abstract class for a specialized "fetcher" sample processer.

    Defines methods to fetch samples from remote sources.

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
        super().__init__(config=config, records=records)
        self._select_records()

    @abstractmethod
    def process(  # pylint: disable=arguments-differ
        self, loc: Path = Path.cwd()
    ) -> pd.DataFrame:
        """Fetch and process records.

        Args:
            loc: Path to fetch samples to. Samples may be located within child
                directories. Defaults to current working directory.

        Returns: Dataframe with local path information.
        """

    @abstractmethod
    def _select_records(self) -> None:
        """Select samples to fetch."""
