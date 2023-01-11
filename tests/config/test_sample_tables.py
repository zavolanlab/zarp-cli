"""Unit tests for ``:mod:zarp.config.sample_tables``."""

from pathlib import Path

import pytest

from zarp.config.enums import FieldNameMappingDirection

from zarp.config.sample_tables import SampleTableProcessor

TEST_FILE_DIR: Path = Path(__file__).parents[1].absolute() / "files"
SAMPLE_TABLE: Path = TEST_FILE_DIR / "sample_table.tsv"


class TestSampleTableProcessor:
    """Test ``:cls:zarp.config.sample_tables.SampleTableProcessor`` class."""

    def test_constructor_without_args(self):
        """Test class constructor without args."""
        processor = SampleTableProcessor()
        assert hasattr(processor, "records")
        assert isinstance(processor.records, list)
        assert processor.records == []

    def test_constructor_with_args(self):
        """Test class constructor with args."""
        records = [
            {"field1": "value1A", "field2": "value2A"},
            {"field1": "value1B", "field2": "value2B"},
        ]
        processor = SampleTableProcessor(records=records)
        assert hasattr(processor, "records")
        assert isinstance(processor.records, list)
        assert processor.records == records

    def test_read(self):
        """Test ``.read()`` method with valid ZARP sample table."""
        processor = SampleTableProcessor()
        processor.read(path=SAMPLE_TABLE)
        assert len(processor.records) == 5

    def test_write(self, tmpdir):
        """Test ``.write()`` method with valid ZARP sample table as input."""
        outfile = Path(tmpdir) / "sample_table.tsv"
        processor = SampleTableProcessor()
        processor.read(path=SAMPLE_TABLE)
        processor.write(path=outfile)
        new_processor = SampleTableProcessor()
        new_processor.read(path=outfile)
        assert len(new_processor.records) == 5

    def test_to_model_records(self):
        """Test ``._to_model_records()`` method."""
        DELETED = [
            "fq1",
            "fq2",
            "fq1_3p",
            "fq2_3p",
            "fq1_5p",
            "fq2_5p",
            "fq1_polya_3p",
            "fq2_polya_3p",
            "fq1_polya_5p",
            "fq2_polya_5p",
            "seqmode",
        ]
        NEW = [
            "adapter_3p",
            "adapter_5p",
            "adapter_poly_3p",
            "adapter_poly_5p",
            "paths",
        ]
        processor = SampleTableProcessor()
        processor.read(path=SAMPLE_TABLE)
        processor._to_sample_table_records()
        new_processor = SampleTableProcessor(records=processor.records)
        new_processor._to_model_records(table_dir=SAMPLE_TABLE.parent)
        record = new_processor.records[0]
        assert all(item not in record for item in DELETED)
        assert all(item in record for item in NEW)

    def test_to_sample_table_records(self):
        """Test ``._to_sample_table_records()`` method."""
        NEW = [
            "fq1",
            "fq2",
            "fq1_3p",
            "fq2_3p",
            "fq1_5p",
            "fq2_5p",
            "fq1_polya_3p",
            "fq2_polya_3p",
            "fq1_polya_5p",
            "fq2_polya_5p",
        ]
        DELETED = [
            "adapter_3p",
            "adapter_5p",
            "adapter_poly_3p",
            "adapter_poly_5p",
            "paths",
        ]
        processor = SampleTableProcessor()
        processor.read(path=SAMPLE_TABLE)
        processor._to_sample_table_records()
        record = processor.records[0]
        print(record)
        assert all(item not in record for item in DELETED)
        assert all(item in record for item in NEW)

    def test_translate_field_names(self):
        """Test ``._translate_field_names()`` method."""
        from bidict import frozenbidict

        records = [
            {"a": "value_a1", "b": "value_b1"},
            {"a": "value_a2", "b": "value_b2"},
        ]
        processor = SampleTableProcessor(records)
        for record in processor.records:
            assert "a" in record
            assert "b" in record
            assert "A" not in record
            assert "B" not in record
        processor.key_mapping = frozenbidict({"a": "A", "b": "B"})
        processor._translate_field_names(
            direction=FieldNameMappingDirection.TO_MODEL_PROPERTIES
        )
        for record in processor.records:
            assert "A" in record
            assert "B" in record
            assert "a" not in record
            assert "b" not in record
        processor._translate_field_names(
            direction=FieldNameMappingDirection.TO_TABLE_COL_NAMES
        )
        for record in processor.records:
            assert "a" in record
            assert "b" in record
            assert "A" not in record
            assert "B" not in record

    @pytest.mark.parametrize(
        "anchor,path,expected",
        [
            (Path.cwd(), "test", str(Path.cwd() / "test")),
            (Path.cwd(), Path.cwd(), str(Path.cwd())),
            (Path.cwd(), "./test", str(Path.cwd() / "test")),
        ],
    )
    def test_resolve_path(self, anchor, path, expected):
        """Test method ``.resolve_path()`` with various anchors and paths."""
        path = SampleTableProcessor.resolve_path(anchor=anchor, path=path)
        assert isinstance(path, Path)
        assert str(path) == expected
