"""Unit tests for ``:mod:zarp.samples.sample_table_processor``."""

from pathlib import Path

import numpy as np

from zarp.samples import sample_table_processor as stp


class TestRead:
    """Tests for function ``:func:zarp.samples.sample_table_processor.read``."""  # noqa: E501

    def test_read(self):
        """Test `read()` function without defaults."""
        df = stp.read(
            path=Path(__file__).parents[1] / "files" / "sample_table.tsv"
        )
        assert len(df.index) > 0
        assert df.iloc[0, 0] == "paired"

    def test_read_with_index_col(self):
        """Test `read()` function with index column."""
        df = stp.read(
            path=Path(__file__).parents[1] / "files" / "sample_table.tsv",
            index_col=0,
        )
        assert len(df.index) > 0
        assert df.iloc[0, 0] is np.nan
        assert "sample" not in df.columns

    def test_read_with_mapping(self):
        """Test `read()` function with mapping."""
        df = stp.read(
            path=Path(__file__).parents[1] / "files" / "sample_table.tsv",
            mapping={"sample": "sample_id"},
        )
        assert len(df.index) > 0
        assert df.iloc[0, 0] == "paired"
        assert "sample" not in df.columns
        assert "sample_id" in df.columns

    def test_read_with_columns(self):
        """Test `read()` function with columns."""
        columns = ["sample", "fq1"]
        df = stp.read(
            path=Path(__file__).parents[1] / "files" / "sample_table.tsv",
            columns=columns,
        )
        assert len(df.index) > 0
        assert len(df.columns) == len(columns)
        assert list(df.columns) == columns
        assert df.iloc[0, 0] == "paired"

    def test_read_with_mapping_and_columns(self):
        """Test `read()` function with mapping and columns."""
        columns = ["sample", "fq1"]
        df = stp.read(
            path=Path(__file__).parents[1] / "files" / "sample_table.tsv",
            columns=columns,
            mapping={"sample": "sample_id"},
        )
        assert len(df.index) > 0
        assert len(df.columns) == len(columns)
        assert list(df.columns) != columns
        assert df.iloc[0, 0] == "paired"


class TestWrite:
    """Tests for function ``:func:zarp.samples.sample_table_processor.write``."""  # noqa: E501

    def test_write(self, tmp_path):
        """Test `write()` function without defaults."""
        df_to_write = stp.read(
            path=Path(__file__).parents[1] / "files" / "sample_table.tsv"
        )
        stp.write(
            df=df_to_write,
            path=tmp_path / "sample_table.tsv",
        )
        df_read_again = stp.read(path=tmp_path / "sample_table.tsv")
        assert len(df_read_again.index) == len(df_to_write.index)
        assert df_read_again.iloc[0, 0] == df_to_write.iloc[0, 0]

    def test_write_with_mapping(self, tmp_path):
        """Test `write()` function with mapping."""
        df_to_write = stp.read(
            path=Path(__file__).parents[1] / "files" / "sample_table.tsv"
        )
        stp.write(
            df=df_to_write,
            path=tmp_path / "sample_table.tsv",
            mapping={"sample": "sample_id"},
        )
        df_read_again = stp.read(path=tmp_path / "sample_table.tsv")
        assert len(df_read_again.index) == len(df_to_write.index)
        assert df_read_again.iloc[0, 0] == df_to_write.iloc[0, 0]
        assert "sample" not in df_read_again.columns
        assert "sample_id" in df_read_again.columns

    def test_write_with_columns(self, tmp_path):
        """Test `write()` function with columns."""
        columns = ["sample", "fq1"]
        df_to_write = stp.read(
            path=Path(__file__).parents[1] / "files" / "sample_table.tsv"
        )
        stp.write(
            df=df_to_write,
            path=tmp_path / "sample_table.tsv",
            columns=columns,
        )
        df_read_again = stp.read(path=tmp_path / "sample_table.tsv")
        assert len(df_read_again.index) == len(df_to_write.index)
        assert len(df_read_again.columns) == len(columns)
        assert len(df_read_again.columns) < len(df_to_write.columns)
        assert list(df_read_again.columns) == columns
        assert df_read_again.iloc[0, 0] == df_to_write.iloc[0, 0]

    def test_write_with_mapping_and_columns(self, tmp_path):
        """Test `write()` function with mapping and columns."""
        columns = ["sample_id", "fq1"]
        df_to_write = stp.read(
            path=Path(__file__).parents[1] / "files" / "sample_table.tsv"
        )
        stp.write(
            df=df_to_write,
            path=tmp_path / "sample_table.tsv",
            mapping={"sample": "sample_id"},
            columns=columns,
        )
        df_read_again = stp.read(path=tmp_path / "sample_table.tsv")
        assert len(df_read_again.index) == len(df_to_write.index)
        assert len(df_read_again.columns) == len(columns)
        assert len(df_read_again.columns) < len(df_to_write.columns)
        assert list(df_read_again.columns) == columns
        assert df_read_again.iloc[0, 0] == df_to_write.iloc[0, 0]

    def test_write_with_missing_columns(self, tmp_path):
        """Test `write()` function with missing columns."""
        new_column = "new_column"
        columns = ["sample", "fq1", new_column]
        df_to_write = stp.read(
            path=Path(__file__).parents[1] / "files" / "sample_table.tsv"
        )
        stp.write(
            df=df_to_write,
            path=tmp_path / "sample_table.tsv",
            columns=columns,
        )
        df_read_again = stp.read(path=tmp_path / "sample_table.tsv")
        assert len(df_read_again.index) == len(df_to_write.index)
        assert len(df_read_again.columns) == len(columns)
        assert list(df_read_again.columns) == columns
        assert df_read_again.iloc[0, 0] == df_to_write.iloc[0, 0]
        assert new_column in df_read_again.columns
        assert new_column not in df_to_write.columns
