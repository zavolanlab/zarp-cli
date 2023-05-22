"""Unit tests for ``:mod:zarp.utils``."""

from pathlib import Path
import string

import numpy as np
import pandas as pd
import pytest

from zarp.utils import (
    generate_id,
    list_get,
    remove_none,
    resolve_paths,
    sanitize_strings,
)


class TestGenerateId:
    """Tests for function ``:func:zarp.utils.generate_id``."""

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
    """Tests for function ``:func:zarp.utils.list_get``."""

    def test_with_implicit_default(self):
        """Call without providing explicit default."""
        assert list_get([1, 2, 3], 1) == 2
        assert list_get([1, 2, 3], -1) == 3
        assert list_get([1, None, "a"], 0) == 1
        assert list_get([1, None, "a"], 4) is None

    def test_with_explicit_default(self):
        """Call with providing default."""
        assert list_get([1, 2, 3], 4, "default") == "default"


class TestRemoveNone:
    """Tests for function ``:func:zarp.utils.remove_none``."""

    def test_with_dict(self):
        """Call with dictionary."""
        assert remove_none({"a": 1, "b": None, "c": {"d": None}}) == {
            "a": 1,
            "c": {},
        }

    def test_with_no_dict(self):
        """Call with list."""
        obj = [1, 2, None]
        assert remove_none(obj) is obj


class TestResolvePaths:
    """Tests for function ``:func:zarp.utils.resolve_paths``."""

    def test_with_relative_paths(self, tmpdir):
        """Call with relative paths."""
        df = resolve_paths(
            df=pd.DataFrame(
                {
                    "sample": ["sample1", "sample2"],
                    "path": ["sample1.fastq", "sample2.fastq"],
                }
            ),
            anchor=Path(tmpdir),
            path_columns=("path",),
        )
        assert df["path"].tolist() == [
            Path(tmpdir) / "sample1.fastq",
            Path(tmpdir) / "sample2.fastq",
        ]

    def test_with_absolute_paths(self, tmpdir):
        """Call with absolute paths."""
        df = resolve_paths(
            df=pd.DataFrame(
                {
                    "sample": ["sample1", "sample2"],
                    "path": [
                        Path(tmpdir) / "sample1.fastq",
                        Path(tmpdir) / "sample2.fastq",
                    ],
                }
            ),
            anchor=Path(tmpdir),
            path_columns=("path",),
        )
        assert df["path"].tolist() == [
            Path(tmpdir) / "sample1.fastq",
            Path(tmpdir) / "sample2.fastq",
        ]

    def test_with_mixed_paths(self, tmpdir):
        """Call with mixed paths."""
        df = resolve_paths(
            df=pd.DataFrame(
                {
                    "sample": ["sample1", "sample2"],
                    "path": [
                        "sample1.fastq",
                        Path(tmpdir) / "sample2.fastq",
                    ],
                }
            ),
            anchor=Path(tmpdir),
            path_columns=("path",),
        )
        assert df["path"].tolist() == [
            Path(tmpdir) / "sample1.fastq",
            Path(tmpdir) / "sample2.fastq",
        ]

    def test_with_non_path_like_objects(self, tmpdir):
        """Call with non-path-like objects."""
        df = resolve_paths(
            df=pd.DataFrame(
                {
                    "sample": ["sample1", "sample2"],
                    "path": [1, 2],
                }
            ),
            anchor=Path(tmpdir),
            path_columns=("path",),
        )
        assert df["path"].tolist() == [1, 2]


class TestSanitizeStrings:
    """Tests for function ``:func:zarp.utils.sanitize_strings``."""

    def test_with_strings(self):
        """Call with string."""
        assert sanitize_strings("a") == "a"
        assert sanitize_strings("A B C") == "a_b_c"

    def test_with_numerical(self):
        """Call with numerical values."""
        assert sanitize_strings(1) == "1"
        assert sanitize_strings(1.0) == "1.0"
        assert sanitize_strings(np.nan) == "nan"

    def test_with_illegal_values(self):
        """Call with illegal values."""
        with pytest.raises(TypeError):
            assert sanitize_strings(None)  # type: ignore
        with pytest.raises(TypeError):
            assert sanitize_strings([1, 2, 3])  # type: ignore
        with pytest.raises(TypeError):
            assert sanitize_strings({"a": 1})  # type: ignore
