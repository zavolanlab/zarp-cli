"""Unit tests for ``:mod:zarp.samples.sample_record_processor``."""

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from zarp.config.models import Sample
from zarp.samples.sample_record_processor import SampleRecordProcessor as SRP

LOGGER = logging.getLogger(__name__)


class TestSampleRecordProcessor:
    """Test for class ``:cls:zarp.samples.sample_record_processor.SampleRecordProcessor`` class."""  # noqa: E501

    def test_init(self):
        """Test constructor."""
        srp = SRP()
        assert hasattr(srp, "records")
        assert isinstance(srp.records, pd.DataFrame)

    def test_append(self):
        """Test `append()` function."""
        srp = SRP()
        df = pd.DataFrame(
            data={
                "name": ["sample1", "sample2"],
                "paths_1": ["library1", "library2"],
                "not_available": ["run1", "run2"],
            }
        )
        srp.append(df, path_columns=["paths_1"])
        assert len(srp.records.index) == 2
        assert "name" in srp.records.columns
        assert "identifier" in srp.records.columns
        assert "not_available" not in srp.records.columns
        assert srp.records.iloc[0, 0] == "sample1"
        assert srp.records.iloc[1, 0] == "sample2"
        assert all(
            [
                Path(item).is_absolute()
                for item in srp.records["paths_1"].tolist()
            ]
        )
        assert not any(
            [Path(item).is_absolute() for item in srp.records["name"].tolist()]
        )

    def test_append_from_obj(self):
        """Test `append_from_obj()` function."""
        srp = SRP()
        srp.append_from_obj(
            samples=[
                Sample(
                    name="sample_pe",
                    paths=(Path(__file__), Path(__file__)),
                ),
                Sample(
                    name="sample_se",
                    paths=(Path(__file__), None),
                ),
            ],
            path_columns=["paths_1"],
        )
        assert len(srp.records.index) == 2
        assert "name" in srp.records.columns
        assert srp.records.iloc[0, 0] == "sample_pe"
        assert srp.records.iloc[1, 0] == "sample_se"
        assert all(
            [
                Path(item).is_absolute()
                for item in srp.records["paths_1"].tolist()
            ]
        )
        assert not any(
            [Path(item).is_absolute() for item in srp.records["name"].tolist()]
        )

    def test_update(self):
        """Test `update()` function."""
        srp = SRP()
        df = pd.DataFrame(
            data={
                "name": ["sample1", "sample2"],
                "paths_1": ["path1", np.nan],
                "not_available": [np.nan, np.nan],
            }
        )
        srp.append(df)
        df_short = pd.DataFrame(
            data={
                "name": ["sample1"],
                "paths_1": ["path1_new"],
                "not_available": ["na2"],
            }
        )
        df_new = pd.DataFrame(
            data={
                "name": ["sample1", "sample2"],
                "paths_1": ["path1_new", "path2"],
                "not_available": ["na2", "na2"],
            }
        )
        with pytest.raises(ValueError):
            srp.update(df_short)
        srp.update(df_new, overwrite=False)
        assert len(srp.records.index) == 2
        assert "name" in srp.records.columns
        assert "paths_1" in srp.records.columns
        assert "not_available" not in srp.records.columns
        assert srp.records["paths_1"].to_list()[0] == "path1"
        # assert srp.records["paths_1"].to_list()[1] == "path2"
        srp.update(df_new, overwrite=True)
        # assert srp.records["paths_1"].to_list()[0] == "path1_new"
        # assert srp.records["paths_1"].to_list()[1] == "path2"

    def test_update_by_column(self):
        """Test `update()` function; merge by specific column."""
        srp = SRP()
        df = pd.DataFrame(
            data={
                "name": ["sample1", "sample2"],
                "paths_1": ["path1", np.nan],
                "not_available": [np.nan, np.nan],
            }
        )
        srp.append(df)
        df_new = pd.DataFrame(
            data={
                "name": ["sample1", "sample2"],
                "paths_1": ["path1_new", "path2"],
                "not_available": ["na2", "na2"],
            }
        )
        srp.update(df_new, by="name", overwrite=False)
        assert len(srp.records.index) == 2
        assert "name" in srp.records.columns
        assert "paths_1" in srp.records.columns
        assert "not_available" not in srp.records.columns
        assert srp.records["paths_1"].to_list()[0] == "path1"
        assert srp.records["paths_1"].to_list()[1] == "path2"
        srp.update(df_new, by="name", overwrite=True)
        assert srp.records["paths_1"].to_list()[0] == "path1_new"
        assert srp.records["paths_1"].to_list()[1] == "path2"
        with pytest.raises(KeyError):
            srp.update(df_new, by="not_available")

    def test_view(self, caplog):
        """Test `view()` function."""
        srp = SRP()
        df = pd.DataFrame(
            data={
                "name": ["sample1", "sample2"],
                "paths_1": ["path1", "path2"],
                "not_available": ["na1", "na2"],
            }
        )
        srp.append(df)
        with caplog.at_level(logging.DEBUG):
            srp.view()
        assert "sample1" in caplog.text

    def test__sanitize_df(self):
        """Test `_sanitize_df()` function."""
        srp = SRP()
        df = pd.DataFrame(
            data={
                "name": ["sample1"],
                "paths_1": ["path1"],
                "identifier": ["id1"],
            }
        )
        srp.records = srp._sanitize_df(df=df, path_columns=["paths_1"])
        assert Path(srp.records["paths_1"].to_list()[0]).is_absolute()
        assert srp.records["identifier"].to_list()[0] == "id1"
        assert len(srp.records.index) == 1
        df_new = pd.DataFrame(
            data={
                "name": ["sample1", "sample2"],
                "paths_1": ["path1", "path2"],
                "not_available": ["na1", "na2"],
                "identifier": ["id1", None],
            }
        )
        df_sanitized = srp._sanitize_df(df=df_new, path_columns=["paths_1"])
        assert "not_available" not in df_sanitized.columns
        assert Path(df_sanitized["paths_1"].to_list()[0]).is_absolute()
        assert df_sanitized["identifier"].to_list()[0] is np.nan
        assert len(df_sanitized.index) == 1

    def test__remove_duplicates(self, caplog):
        """Test `_remove_duplicates()` function."""
        srp = SRP()
        df = pd.DataFrame(
            data={
                "name": ["sample1", "sample2"],
                "paths_1": ["path1", "path2"],
            }
        )
        srp.append(df)
        df_same = df.copy(deep=True)
        df_same = srp._sanitize_df(df=df_same)
        with caplog.at_level(logging.WARNING):
            df_trunc = srp._remove_duplicates(df=df_same)
        assert len(df_trunc.index) == 0
        assert "Duplicate records found" in caplog.text
        caplog.clear()
        df_new = pd.DataFrame(
            data={
                "name": ["sample1", "sample3"],
                "paths_1": ["path1", "path3"],
            }
        )
        df_new = srp._sanitize_df(df=df_new)
        with caplog.at_level(logging.WARNING):
            df_new_trunc = srp._remove_duplicates(df=df_new)
        assert len(df_new_trunc.index) == 1
        assert "Duplicate records found" in caplog.text

    def test__objects_to_df(self):
        """Test `_objects_to_df()` function."""
        srp = SRP()
        df = pd.DataFrame(
            data={
                "name": ["sample1", "sample2"],
                "paths_1": ["path1", "path2"],
            }
        )
        df = srp._sanitize_df(df=df, path_columns=["paths_1"])
        df_new = srp._objects_to_df(
            samples=[Sample(identifier="id1", paths=(Path(__file__), None))],
        )
        assert len(df_new.index) == 1
        assert "identifier" in df_new.columns
        assert "paths_1" in df_new.columns
        assert "paths_2" in df_new.columns
        assert df_new["identifier"].to_list()[0] == "id1"
        assert Path(df_new["paths_1"].to_list()[0]).is_absolute()
        assert df_new["paths_1"].to_list()[0] == Path(__file__).absolute()
        assert df_new["paths_2"].to_list()[0] is None

    def test__expand_tuple_columns(self):
        """Test `_expand_tuple_columns()` function."""
        df = pd.DataFrame(
            data={
                "one": ["sample1", None, "sample3"],
                "two": [("path1", "path2"), "path1", ("path1", None)],
                "three": [("path1", "path2", None), None, (None, "path2")],
            }
        )
        print(df)
        df_new = SRP._expand_tuple_columns(df=df)
        print(df_new)
        assert len(df_new.columns) == 6
        assert "one" in df_new.columns
        assert "two_1" in df_new.columns
        assert "two_2" in df_new.columns
        assert "three_1" in df_new.columns
        assert "three_2" in df_new.columns
        assert "three_3" in df_new.columns
