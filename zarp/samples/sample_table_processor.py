"""Read and write ZARP sample tables."""

import logging
from pathlib import Path
from typing import Optional, Mapping, Sequence

import pandas as pd
from numpy.typing import ArrayLike

LOGGER = logging.getLogger(__name__)


def read(
    path: Path,
    index_col: Optional[int] = None,
    mapping: Optional[Mapping] = None,
    columns: Optional[ArrayLike] = None,
) -> pd.DataFrame:
    """Set records from sample table file.

    Args:
        path: Sample table path.
        index_col: Optional index column.
        columns: Optional list of sample table columns to select. If not
            provided, all columns will be selected. Column selection will
            occur _before_ column renaming.
        mapping: Optional mapping of column names to rename columns.

    Returns: Pandas ``DataFrame`` object.
    """
    LOGGER.debug(f"Reading sample table from '{path}'...")
    df: pd.DataFrame = pd.read_csv(
        path,
        comment="#",
        sep="\t",
        keep_default_na=False,
        dtype=str,
        index_col=index_col,
        usecols=columns,  # type: ignore
    )
    if mapping is not None:
        df = df.rename(columns=mapping)
    LOGGER.debug(f"Records read: {len(df.index)}")
    return df


def write(
    df: pd.DataFrame,
    path: Path = Path.cwd() / "sample_table.tsv",
    mapping: Optional[Mapping] = None,
    columns: Optional[Sequence] = None,
) -> None:
    """Write sample table.

    Args:
        df: Pandas ``DataFrame`` object to write.
        path: Path to write sample table to.
        mapping: Optional mapping of column names to rename columns.
        columns: Optional list of sample table columns to write. Columns
            will be written in the specified order. Missing columns will
            be created with empty strings. If not provided, all columns
            will be written. Column selection will occur _after_ column
            renaming.
    """
    LOGGER.debug(f"Writing sample table to '{path}'...")
    df = df.copy()
    if mapping is not None:
        df = df.rename(columns=mapping)
    if columns is not None:
        missing_columns = set(columns) - set(df.columns)
        if missing_columns:
            LOGGER.warning(
                f"Missing columns in dataframe: {missing_columns}. Will be"
                " added and filled with empty strings."
            )
            for col in missing_columns:
                df[col] = ""
        df = pd.DataFrame(df[columns])
    df.to_csv(path, sep="\t", index=False)
    LOGGER.debug(f"Records written: {len(df.index)}")
