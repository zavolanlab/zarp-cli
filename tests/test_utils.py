"""Unit tests for ``:mod:zarp.utils``."""

import string

from zarp.utils import (
    generate_id,
    list_get,
)


class TestGenerateId:
    """Test `generate_id()` function."""

    def test_without_args(self):
        """Call without args."""
        identifier = generate_id()
        assert len(identifier) == 6
        assert all(
            char in string.ascii_uppercase + string.digits
            for char in identifier
        )

    def test_with_length_arg(self):
        """Call without args."""
        identifier = generate_id(length=12)
        assert len(identifier) == 12


class TestListGet:
    """Test `list_get()` function."""

    def test_with_implicit_default(self):
        """Call without providing explicit default."""
        assert list_get([1, 2, 3], 1) == 2
        assert list_get([1, 2, 3], -1) == 3
        assert list_get([1, None, "a"], 0) == 1
        assert list_get([1, None, "a"], 4) is None

    def test_with_explicit_default(self):
        """Call with providing default."""
        assert list_get([1, 2, 3], 4, "default") == "default"
