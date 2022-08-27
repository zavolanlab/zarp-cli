"""ZARP-cli utilities."""

from random import choice
import string
from typing import (
    Any,
    Sequence,
)


def generate_id(length: int = 6) -> str:
    """Generate random string composed of specified character set.

    Args:
        length: Length of string to generate.

    Returns:
        Random string of specified length, composed of uppercase ASCII
            characters and digits.
    """
    charset: str = str(''.join([string.ascii_uppercase, string.digits]))
    return ''.join(choice(charset) for __ in range(length))


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
