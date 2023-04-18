"""ZARP-cli utilities."""

from pathlib import Path
from random import choice
import string
from typing import (
    Any,
    Sequence,
)

import pandas as pd

from zarp.config.mappings import columns_zarp_path


def generate_id(length: int = 6) -> str:
    """Generate random string.

    Args:
        length: Length of string to generate.

    Returns:
        Random string of specified length, composed of uppercase ASCII
            characters and digits.
    """
    charset: str = str("".join([string.ascii_uppercase, string.digits]))
    return "".join(choice(charset) for __ in range(length))


def list_get(_list: Sequence[Any], index: int, default: Any = None) -> Any:
    """Get an item from a list by index or return a default value.

    Args:
        _list: List from which to return item.
        index: Index of item to return.
        default: Default value to return if index is out of range.
    """
    try:
        return _list[index]
    except (IndexError, TypeError):
        return default


def resolve_paths(
    df: pd.DataFrame,
    anchor: Path = Path.cwd(),
    path_columns: Sequence = tuple(columns_zarp_path),
) -> pd.DataFrame:
    """Resolve relative sample paths against a defined anchor.

    Absolute paths and non-string or path-like objects are not modified.

    Args:
        df: Pandas ``DataFrame`` object.
        anchor: Path to resolve sample paths relative to.
        columns: Tuple of column names to resolve.

    Returns:
        Pandas ``DataFrame`` object.
    """
    df = df.copy()
    cols = set(path_columns) & set(df.columns)
    for col in cols:
        df[col] = df[col].apply(
            lambda x: (anchor / Path(x)).resolve()
            if isinstance(x, str) and not Path(x).is_absolute()
            else x
        )
    return df
