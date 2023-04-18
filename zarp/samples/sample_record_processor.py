"""Interact with ZARP sample records."""

import logging
from typing import Any, Optional, Sequence

import numpy as np
import pandas as pd

from zarp.config.models import Sample
from zarp.config.mappings import (
    columns_model,
)
from zarp.utils import resolve_paths

LOGGER = logging.getLogger(__name__)


class SampleRecordProcessor:
    """ZARP sample record processor class.

    Defines methods to append and update sample records.

    Attributes:
        samples: Sequence of ``Sample`` objects.
    """

    def __init__(self) -> None:
        """Class constructor method."""
        self.records: pd.DataFrame = pd.DataFrame(
            columns=np.array(columns_model),
        )

    def append(
        self,
        df: pd.DataFrame,
        **kwargs: Any,
    ) -> None:
        """Append dataframe to records.

        Duplicate records and extra columns will be dropped.

        Args:
            df: Pandas ``DataFrame`` object.
            **kwargs: Keyword arguments to pass to ``_sanitize_df()``.
        """
        LOGGER.debug("Appending sample records...")
        df = self._sanitize_df(df=df, **kwargs)
        self.records = self.records.append(df, verify_integrity=True)[
            self.records.columns
        ]
        LOGGER.debug(f"Sample records appended: {len(df.index)}")

    def append_from_obj(
        self,
        samples: Sequence[Sample],
        **kwargs: Any,
    ) -> None:
        """Append samples to records.

        Duplicate records and extra fields will be dropped.

        Args:
            samples: Sequence of ``Sample`` objects.
            **kwargs: Keyword arguments to pass to ``append()``.
        """
        df = self._objects_to_df(samples=samples)
        self.append(df=df, **kwargs)

    def update(
        self,
        df: pd.DataFrame,
        by: str,
        overwrite: bool = False,
        **kwargs: Any,
    ) -> None:
        """Update records with dataframe.

        Args:
            df: Pandas ``DataFrame`` object.
            by: Column to use as index for update. If ``None``, a hash of the
                records will be used.
            **kwargs: Keyword arguments to pass to ``_sanitize_df()``.

        Raises:
            KeyError: If ``by`` column is not found in dataframe.
        """
        LOGGER.debug("Updating sample records...")
        if not (by in self.records.columns and by in df.columns):
            raise KeyError(
                f"Column '{by}' not found in dataframe. Cannot update records."
            )
        df = self._sanitize_df(df=df, **kwargs)
        self.records.set_index(keys=by, drop=False, inplace=True)
        df.set_index(keys=by, drop=False, inplace=True)
        self.records.update(df, overwrite=overwrite, **kwargs)
        self.records = self._sanitize_df(df=self.records, **kwargs)
        LOGGER.debug(f"Sample records updated: {len(df.index)}")

    def view(
        self,
        level: int = logging.DEBUG,
        rows: Optional[int] = None,
        columns: Optional[int] = None,
        width: Optional[int] = None,
    ) -> None:
        """Show records.

        Args:
            level: Logging level to use.
            rows: Number of rows to show.
            columns: Number of columns to show.
            width: Maximum column width.
        """
        LOGGER.log(level=level, msg="Sample records:")
        with pd.option_context(
            "display.max_rows",
            rows,
            "display.max_columns",
            columns,
            "display.max_colwidth",
            width,
        ):
            LOGGER.log(level=level, msg=self.records)

    def _sanitize_df(self, df: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
        """Sanitize dataframe.

        Remove columns not available in records, resolve relative paths,
        fill missing values with ``np.nan``, set row index to hash of row
        contents and remove records that are already in ``self.record``.

        Args:
            df: Pandas ``DataFrame`` object.
            **kwargs: Keyword arguments to pass to ``resolve_paths()``.

        Returns:
            Pandas ``DataFrame`` object.
        """
        df = df[[col for col in self.records.columns if col in df.columns]]
        df = resolve_paths(df=df, **kwargs)
        df.fillna(value=np.nan, inplace=True)
        df.set_index(pd.util.hash_pandas_object(df), drop=False, inplace=True)
        df = self._remove_duplicates(df=df)
        return df

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove rows from dataframe that are already on record.

        Args:
            df: Pandas ``DataFrame`` object.

        Returns:
            Pandas ``DataFrame`` object with rows removed that are already
            on record.
        """
        duplicates = [
            idx
            for idx, item in enumerate(df.index)
            if item in self.records.index
        ]
        if duplicates:
            LOGGER.warning(
                "Duplicate records found in sample table at index positions"
                f" '{duplicates}'. Dropping."
            )
            LOGGER.debug(f"Dropped records: {df.iloc[duplicates]}")
            df = df.drop(df.index[duplicates])
        return df

    @staticmethod
    def _objects_to_df(samples: Sequence[Sample]) -> pd.DataFrame:
        """Convert sample objects to Pandas dataframe.

        Returns:
            Pandas ``DataFrame`` object.
        """
        df = pd.DataFrame([sample.dict() for sample in samples])
        df = SampleRecordProcessor._expand_tuple_columns(df=df)
        return df

    @staticmethod
    def _expand_tuple_columns(df: pd.DataFrame):
        """Expand tuple columns in sample table.

        For each column in the sample table, if at least one of the values in
        the column is a tuple, expands the column into multiple columns, one
        for each element of the largest tuple. Missing values are filled up
        with `None`. New column names are generated by appending ``.1``,
        ``.2``, etc. to the original column name. Original tuple columns are
        dropped.

        Args:
            df: Pandas ``DataFrame`` object.

        Returns:
            Pandas ``DataFrame`` object with expanded tuple columns and
            original tuple columns removed.
        """
        max_size: int
        for name, vals in df.iteritems():
            if any(isinstance(val, tuple) for val in vals):
                max_size = max(len(x) for x in vals if isinstance(x, tuple))
                n_new = [f"{name}_{i}" for i in range(1, max_size + 1)]
                v_filled = vals.apply(
                    lambda x: list(x) + [None] * (max_size - len(x))
                    if isinstance(x, tuple)
                    else tuple([None] * max_size)
                )
                v_new = pd.DataFrame(
                    {col_name: [None] * len(df) for col_name in n_new}
                )
                v_new[n_new] = pd.DataFrame(v_filled.tolist(), index=df.index)
                df.drop([name], axis=1, inplace=True)
                df[n_new] = v_new[n_new]
        return df
