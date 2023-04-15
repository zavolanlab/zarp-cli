"""Abstract sample table processor class."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Sequence

import pandas as pd

from zarp.config.models import Sample


class SampleTableProcessor(ABC):
    """Abstract sample table processor class.

    Defines methods to read and write sample tables.

    Attributes:
        samples: Sequence of ``Sample`` objects.
    """

    def __init__(self) -> None:
        """Class constructor method."""
        self.samples: Sequence[Sample] = []

    def set_samples_from_objects(self, samples: Sequence[Sample]) -> None:
        """Set samples from list of sample objects.

        Args:
            samples: Sequence of ``Sample`` objects.
        """
        self.samples = samples

    @abstractmethod
    def read(self, path: Path) -> pd.DataFrame:
        """Set samples from sample table file.

        Args:
            path: Sample table path.

        Returns: Pandas ``DataFrame`` object.
        """

    @abstractmethod
    def set_samples_from_dataframe(self, data: pd.DataFrame) -> None:
        """Set samples from Pandas dataframe.

        Args:
            data: Pandas ``DataFrame`` object.
        """

    @abstractmethod
    def write(
        self,
        path: Path = Path.cwd() / "sample_table.tsv",
    ) -> None:
        """Write sample table.

        Args:
            path: Path to write sample table to.
        """

    @abstractmethod
    def _validate(self) -> None:
        """Validate samples.

        Ensures that the current state of ``self.samples`` is sufficient to
        produce a valid sample table.

        Raises:
            Exception: The state of ``self.samples`` is insufficient to produce
                a valid sample table. All issues should be listed.
        """
