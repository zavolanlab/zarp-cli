"""Read and write ZARP sample tables."""

import logging
from pathlib import Path
from typing import List, Optional, Sequence

import pandas as pd

from zarp.abstract_classes.sample_table_processor import SampleTableProcessor
from zarp.config.models import Sample

LOGGER = logging.getLogger(__name__)


class SampleTableProcessorZARP(SampleTableProcessor):
    """ZARP sample table processor class.

    Defines methods to read and write ZARP sample tables.

    Attributes:
        samples: Sequence of ``Sample`` objects.
    """

    def read(  # pylint: disable=arguments-differ
        self,
        path: Path,
        index_col: Optional[int] = None,
    ) -> pd.DataFrame:
        """Set samples from sample table file.

        Args:
            path: Sample table path.
            index_col: Optional index column.

        Returns: Pandas ``DataFrame`` object.
        """
        LOGGER.debug(f"Reading sample table: {path}")
        data: pd.DataFrame = pd.read_csv(
            path,
            comment="#",
            sep="\t",
            keep_default_na=False,
            dtype=str,
            index_col=index_col,
        )
        LOGGER.debug(f"Records found: {len(data.index)}")
        return data

    def set_samples_from_dataframe(  # pylint: disable=arguments-differ
        self,
        data: pd.DataFrame,
        anchor: Path = Path.cwd(),
    ) -> None:
        """Set samples from Pandas dataframe.

        Args:
            data: Pandas ``DataFrame`` object.
            anchor: Path to resolve sample paths relative to.
        """
        self.samples = self._df_to_objects(data=data)
        self.samples = self._resolve_paths(anchor=anchor)

    def write(  # pylint: disable=arguments-differ
        self,
        path: Path = Path.cwd() / "sample_table.tsv",
        columns: Optional[Sequence] = None,
    ) -> None:
        """Write sample table.

        Args:
            path: Path to write sample table to.
            columns: Optional list of sample table columns to write. Columns
                will be written in the specified order. Missing columns will
                be created with empty strings.
        """
        LOGGER.debug(f"Writing sample table: {path}")
        data: pd.DataFrame = self._objects_to_df()
        if columns is not None:
            for col in columns:
                if col not in data.columns:
                    data[col] = ""
            data = pd.DataFrame(data[columns])
        data.to_csv(path, sep="\t", index=False)
        LOGGER.debug(f"Records written: {len(data.index)}")

    def _validate(self) -> None:
        """Validate samples.

        Ensures that the current state of ``self.samples`` is sufficient to
        produce a valid sample table.

        Raises:
            Exception: The state of ``self.samples`` is insufficient to produce
                a valid sample table. All issues should be listed.
        """

    def _df_to_objects(  # pylint: disable=no-self-use
        self,
        data: pd.DataFrame,  # pylint: disable=unused-argument
    ) -> List[Sample]:
        """Convert sample table records to sample objects.

        Args:
            data: Pandas ``DataFrame`` object.

        Returns:
            Sequence of ``Sample`` objects.
        """
        return []

    def _objects_to_df(self) -> pd.DataFrame:  # pylint: disable=no-self-use
        """Convert sample objects to Pandas dataframe.

        Returns:
            Pandas ``DataFrame`` object.
        """
        return pd.DataFrame()

    def _resolve_paths(  # pylint: disable=no-self-use
        self,
        anchor: Path,  # pylint: disable=unused-argument
    ) -> List[Sample]:
        """Resolve sample paths.

        Args:
            anchor: Path to resolve sample paths relative to.

        Returns:
            Sequence of ``Sample`` objects.
        """
        return []
