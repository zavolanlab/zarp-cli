"""Unit tests for ``:mod:zarp.config.samples``."""

from pathlib import Path

import pytest

from tests.utils import RaiseError
from zarp.config.enums import SampleReferenceTypes
from zarp.config.samples import SampleProcessor
from zarp.config.models import (
    ConfigSample,
    ConfigRun,
    SampleReference,
)

TEST_FILE_DIR: Path = Path(__file__).parents[1].absolute() / "files"
REF_ID: str = "SRR1234567"
REF_FILE: Path = TEST_FILE_DIR / "config_valid.yaml"
REF_TABLE: Path = TEST_FILE_DIR / "sample_table.tsv"
REF_TABLE_FAULTY: Path = TEST_FILE_DIR / "sample_table_faulty.tsv"
REF_FILE_EMPTY: Path = TEST_FILE_DIR / "empty"
REF_FILE_EMPTY_2: Path = TEST_FILE_DIR / "em@pt:y"
REF_INVALID: Path = Path("path/does/not/exist").absolute()
REF_SRA_TABLE: Path = TEST_FILE_DIR / "sra_table.tsv"
REF_SRA_TABLE_2COLS: Path = TEST_FILE_DIR / "sra_table_2cols.tsv"
REF_SRA_TABLE_NO_FILES: Path = TEST_FILE_DIR / "sra_table_no_files.tsv"
REF_SRA_TABLE_EMPTY: Path = TEST_FILE_DIR / "sra_table_empty.tsv"


class TestSampleTableProcessor:
    """Test ``:cls:zarp.config.samples.SampleProcessor`` class."""

    run_config = ConfigRun(
        zarp_directory=Path(__file__).parents[1] / "files" / "zarp",
        genome_assemblies_map=Path(__file__).parents[1]
        / "files"
        / "genome_assemblies.csv",
    )

    def test_constructor_without_refs(self):
        """Test class constructor.

        Do not provide sample references.
        """
        run_config = self.run_config.copy(deep=True)
        attributes = ["references", "sample_config", "run_config", "samples"]
        processor = SampleProcessor(
            sample_config=ConfigSample(),
            run_config=run_config,
        )
        for attribute in attributes:
            assert hasattr(processor, attribute)
        assert isinstance(processor.references, list)
        assert processor.references == []
        assert isinstance(processor.run_config, ConfigRun)
        assert processor.run_config == self.run_config
        assert isinstance(processor.sample_config, ConfigSample)
        assert processor.sample_config == ConfigSample()
        assert isinstance(processor.samples, list)
        assert processor.samples == []

    def test_constructor_with_refs(self):
        """Test class constructor.

        Use various sample_references.
        """
        run_config = self.run_config.copy(deep=True)
        refs = [
            f"{REF_ID}",
            f"sample@{REF_ID}",
            f"{REF_FILE}",
            f"sample@{REF_FILE}",
            f"{REF_FILE},{REF_FILE}",
            f"sample@{REF_FILE},{REF_FILE}",
            f"table:{REF_TABLE}",
        ]
        processor = SampleProcessor(
            sample_config=ConfigSample(),
            run_config=run_config,
            *refs,
        )
        assert processor.references == refs

    def test_set_samples_no_refs(self):
        """Test method ``.set_samples()``.

        Do not provide sample references.
        """
        run_config = self.run_config.copy(deep=True)
        processor = SampleProcessor(
            sample_config=ConfigSample(),
            run_config=run_config,
        )
        processor.set_samples()
        assert len(processor.samples) == 0

    def test_set_samples_refs(self):
        """Test method ``.set_samples()``.

        Use various sample references.
        """
        run_config = self.run_config.copy(deep=True)
        refs = [
            f"{REF_ID}",
            f"sample@{REF_ID}",
            f"{REF_FILE}",
            f"sample@{REF_FILE}",
            f"{REF_FILE},{REF_FILE}",
            f"sample@{REF_FILE},{REF_FILE}",
            f"table:{REF_TABLE}",
        ]
        processor = SampleProcessor(
            *refs,
            sample_config=ConfigSample(),
            run_config=run_config,
        )
        processor.set_samples()
        assert len(processor.samples) > 5

    def test_set_samples_ref_invalid(self):
        """Test method ``.set_samples()``.

        Use invalid sample references.
        """
        run_config = self.run_config.copy(deep=True)
        processor = SampleProcessor(
            f"{REF_INVALID}",
            sample_config=ConfigSample(),
            run_config=run_config,
        )
        processor.set_samples()
        assert len(processor.samples) == 0

    def test_set_samples_table_ref_empty(self):
        """Test method ``.set_samples()``.

        Use reference to empty table.
        """
        run_config = self.run_config.copy(deep=True)
        processor = SampleProcessor(
            f"table:{REF_FILE_EMPTY}",
            sample_config=ConfigSample(),
            run_config=run_config,
        )
        processor.set_samples()
        assert len(processor.samples) == 0

    def test_set_samples_table_ref_io(self, monkeypatch):
        """Test method ``.set_samples()``.

        Use reference to empty table.
        """
        run_config = self.run_config.copy(deep=True)
        processor = SampleProcessor(
            f"table:{REF_FILE_EMPTY}",
            sample_config=ConfigSample(),
            run_config=run_config,
        )
        monkeypatch.setattr(
            SampleProcessor,
            "_process_sample_table",
            RaiseError(OSError),
        )
        processor.set_samples()
        assert len(processor.samples) == 0

    def test__process_sample_table(self):
        """Test method ``._process_write_sample_table()``.

        Use sample table with entries accounting for all conditions.
        """
        run_config = self.run_config.copy(deep=True)
        ref_str = f"table:{REF_TABLE}"
        processor = SampleProcessor(
            ref_str,
            sample_config=ConfigSample(),
            run_config=run_config,
        )
        ref = processor._resolve_sample_reference(ref=ref_str)
        assert ref.table_path is not None
        processor._process_sample_table(path=ref.table_path)

    def test__process_sample_table_faulty(self):
        """Test method ``._process_write_sample_table()``.

        Sample table contains faulty reference.
        """
        run_config = self.run_config.copy(deep=True)
        ref_str = f"table:{REF_TABLE_FAULTY}"
        processor = SampleProcessor(
            ref_str,
            sample_config=ConfigSample(),
            run_config=run_config,
        )
        ref = processor._resolve_sample_reference(ref=ref_str)
        assert ref.table_path is not None
        processor._process_sample_table(path=ref.table_path)

    def test__set_sample_from_local_lib_single(self):
        """Test method ``._set_sample_from_local_lib()``.

        Use reference for single-ended local library.
        """
        run_config = self.run_config.copy(deep=True)
        ref = str(REF_FILE_EMPTY)
        processor = SampleProcessor(
            ref,
            sample_config=ConfigSample(),
            run_config=run_config,
        )
        assert len(processor.samples) == 0
        deref = processor._resolve_sample_reference(ref=ref)
        processor._set_sample_from_local_lib(ref=deref)
        assert len(processor.samples) == 1
        assert processor.samples[0].paths == (REF_FILE_EMPTY, None)
        assert processor.samples[0].identifier is None

    def test__set_sample_from_local_lib_single_config_update(self):
        """Test method ``._set_sample_from_local_lib()``.

        Use reference for single-ended local library and update configuration.
        """
        run_config = self.run_config.copy(deep=True)
        ref = str(REF_FILE_EMPTY)
        update = ConfigSample(source="test")
        processor = SampleProcessor(
            ref,
            sample_config=ConfigSample(),
            run_config=run_config,
        )
        assert len(processor.samples) == 0
        deref = processor._resolve_sample_reference(ref=ref)
        processor._set_sample_from_local_lib(ref=deref, update=update.dict())
        assert len(processor.samples) == 1
        assert processor.samples[0].paths == (REF_FILE_EMPTY, None)
        assert processor.samples[0].identifier is None
        assert processor.samples[0].source == "test"

    def test__set_sample_from_local_lib_paired(self):
        """Test method ``._set_sample_from_local_lib()``.

        Use reference for paired-ended local library.
        """
        run_config = self.run_config.copy(deep=True)
        ref = f"{REF_FILE_EMPTY},{REF_FILE_EMPTY}"
        processor = SampleProcessor(
            ref,
            sample_config=ConfigSample(),
            run_config=run_config,
        )
        assert len(processor.samples) == 0
        deref = processor._resolve_sample_reference(ref=ref)
        processor._set_sample_from_local_lib(ref=deref)
        assert len(processor.samples) == 1
        assert processor.samples[0].paths == (REF_FILE_EMPTY, REF_FILE_EMPTY)
        assert processor.samples[0].identifier is None

    def test__set_sample_from_local_lib_paired_config_update(self):
        """Test method ``._set_sample_from_local_lib()``.

        Use reference for paired-ended local library and update configuration.
        """
        run_config = self.run_config.copy(deep=True)
        ref = f"{REF_FILE_EMPTY},{REF_FILE_EMPTY}"
        update = ConfigSample(source="test")
        processor = SampleProcessor(
            ref,
            sample_config=ConfigSample(),
            run_config=run_config,
        )
        assert len(processor.samples) == 0
        deref = processor._resolve_sample_reference(ref=ref)
        processor._set_sample_from_local_lib(ref=deref, update=update.dict())
        assert len(processor.samples) == 1
        assert processor.samples[0].paths == (REF_FILE_EMPTY, REF_FILE_EMPTY)
        assert processor.samples[0].identifier is None
        assert processor.samples[0].source == "test"

    def test__set_sample_from_remote_lib(self):
        """Test method ``._set_sample_from_remote_lib()``.

        Use reference for remote library.
        """
        run_config = self.run_config.copy(deep=True)
        ref = REF_ID
        processor = SampleProcessor(
            ref,
            sample_config=ConfigSample(),
            run_config=run_config,
        )
        assert len(processor.samples) == 0
        deref = processor._resolve_sample_reference(ref=ref)
        processor._set_sample_from_remote_lib(ref=deref)
        assert len(processor.samples) == 1
        assert processor.samples[0].paths is None
        assert processor.samples[0].identifier == REF_ID

    def test__set_sample_from_remote_lib_config_update(self):
        """Test method ``._set_sample_from_remote_lib()``.

        Use reference for remote library and update configuration.
        """
        run_config = self.run_config.copy(deep=True)
        ref = REF_ID
        update = ConfigSample(source="test")
        processor = SampleProcessor(
            ref,
            sample_config=ConfigSample(),
            run_config=run_config,
        )
        assert len(processor.samples) == 0
        deref = processor._resolve_sample_reference(ref=ref)
        processor._set_sample_from_remote_lib(ref=deref, update=update.dict())
        assert len(processor.samples) == 1
        assert processor.samples[0].paths is None
        assert processor.samples[0].identifier == REF_ID
        assert processor.samples[0].source == "test"

    def test__set_samples_remote(self):
        """Test method ``._set_samples_remote()``.

        Use references for remote libraries.
        """
        run_config = self.run_config.copy(deep=True)
        refs = [
            f"{REF_ID}",
            f"sample@{REF_ID}",
            f"{REF_FILE}",
            f"sample@{REF_FILE}",
            f"{REF_FILE},{REF_FILE}",
            f"sample@{REF_FILE},{REF_FILE}",
            f"table:{REF_TABLE}",
        ]
        processor = SampleProcessor(
            *refs,
            sample_config=ConfigSample(),
            run_config=run_config,
        )
        processor.set_samples()
        processor.samples_remote = []
        processor._set_samples_remote()
        assert len(processor.samples_remote) == 5
        assert len(processor.samples) == 11

    def test_write_sample_table(self, tmpdir):
        """Test method ``.write_sample_table()``.

        Use various sample references.
        """
        run_config = self.run_config.copy(deep=True)
        refs = [f"{REF_ID}"]
        processor = SampleProcessor(
            *refs,
            sample_config=ConfigSample(),
            run_config=run_config,
        )
        processor.set_samples()
        processor.write_sample_table(
            samples=processor.samples,
            outpath=tmpdir / "samples.tsv",
        )

    def test_write_remote_sample_table(self, tmpdir):
        """Test method ``.write_remote_sample_table()``.

        Use various sample references.
        """
        run_config = self.run_config.copy(deep=True)
        refs = [f"{REF_ID}"]
        processor = SampleProcessor(
            *refs,
            sample_config=ConfigSample(),
            run_config=run_config,
        )
        processor.set_samples()
        processor.write_remote_sample_table(
            samples=processor.samples,
            outpath=tmpdir / "samples_remote.tsv",
        )

    @pytest.mark.parametrize(
        "ref",
        [
            str(REF_FILE_EMPTY),
            str(REF_FILE_EMPTY_2),
        ],
    )
    def test__resolve_sample_reference_unnamed_single(self, ref):
        """Test method ``._resolve_sample_reference()``.

        Use references to unnamed single-ended libaries.
        """
        deref = SampleProcessor._resolve_sample_reference(ref=ref)
        assert isinstance(deref, SampleReference)
        assert deref.type == SampleReferenceTypes.LOCAL_LIB_SINGLE.name
        assert deref.name is None
        assert deref.lib_paths == (Path(ref), None)
        assert deref.identifier is None
        assert deref.table_path is None

    @pytest.mark.parametrize(
        "ref",
        [
            f"{REF_FILE_EMPTY},{REF_FILE_EMPTY}",
            f"{REF_FILE_EMPTY},{REF_FILE_EMPTY_2}",
            f"{REF_FILE_EMPTY_2},{REF_FILE_EMPTY}",
            f"{REF_FILE_EMPTY_2},{REF_FILE_EMPTY_2}",
        ],
    )
    def test__resolve_sample_reference_unnamed_paired(self, ref):
        """Test method ``._resolve_sample_reference()``.

        Use references to unnamed paired-ended libaries.
        """
        deref = SampleProcessor._resolve_sample_reference(ref=ref)
        assert isinstance(deref, SampleReference)
        assert deref.type == SampleReferenceTypes.LOCAL_LIB_PAIRED.name
        assert deref.name is None
        assert deref.lib_paths == tuple(
            [Path(item) for item in ref.split(",", maxsplit=1)]
        )
        assert deref.identifier is None
        assert deref.table_path is None

    @pytest.mark.parametrize(
        "ref",
        [
            "SRR1234567",
            "DRR0000000",
            "ERR7654321",
            "SRR1234567890",
            "DRR0000000000",
            "ERR0987654321",
            "srr1234567",
        ],
    )
    def test__resolve_sample_reference_unnamed_remote(self, ref):
        """Test method ``._resolve_sample_reference()``.

        Use references to unnamed remote libaries.
        """
        deref = SampleProcessor._resolve_sample_reference(ref=ref)
        assert isinstance(deref, SampleReference)
        assert deref.type == SampleReferenceTypes.REMOTE_LIB_SRA.name
        assert deref.name is None
        assert deref.lib_paths is None
        assert deref.identifier == ref.upper()
        assert deref.table_path is None

    @pytest.mark.parametrize(
        "ref",
        [
            f"sample@{REF_FILE_EMPTY}",
            f"sample@{REF_FILE_EMPTY_2}",
        ],
    )
    def test__resolve_sample_reference_named_single(self, ref):
        """Test method ``._resolve_sample_reference()``.

        Use references to named single-ended libaries.
        """
        deref = SampleProcessor._resolve_sample_reference(ref=ref)
        assert isinstance(deref, SampleReference)
        assert deref.type == SampleReferenceTypes.LOCAL_LIB_SINGLE.name
        assert deref.name == "sample"
        assert deref.lib_paths == (
            Path(ref.split("@", maxsplit=1)[1]),
            None,
        )
        assert deref.identifier is None
        assert deref.table_path is None

    @pytest.mark.parametrize(
        "ref",
        [
            f"sample@{REF_FILE_EMPTY},{REF_FILE_EMPTY}",
            f"sample@{REF_FILE_EMPTY},{REF_FILE_EMPTY_2}",
            f"sample@{REF_FILE_EMPTY_2},{REF_FILE_EMPTY}",
            f"sample@{REF_FILE_EMPTY_2},{REF_FILE_EMPTY_2}",
        ],
    )
    def test__resolve_sample_reference_named_paired(self, ref):
        """Test method ``._resolve_sample_reference()``.

        Use references to named paired-ended libaries.
        """
        deref = SampleProcessor._resolve_sample_reference(ref=ref)
        assert isinstance(deref, SampleReference)
        assert deref.type == SampleReferenceTypes.LOCAL_LIB_PAIRED.name
        assert deref.name == "sample"
        paths = ref.split("@", maxsplit=1)[1]
        assert deref.lib_paths == tuple(
            [Path(item) for item in paths.split(",", maxsplit=1)]
        )
        assert deref.identifier is None
        assert deref.table_path is None

    @pytest.mark.parametrize(
        "ref",
        [
            "sample@SRR1234567",
            "sample@SRR1234567890",
            "sample@DRR0000000",
            "sample@ERR7654321",
            "sample@srr1234567",
        ],
    )
    def test__resolve_sample_reference_named_remote(self, ref):
        """Test method ``._resolve_sample_reference()``.

        Use references to named remote libaries.
        """
        deref = SampleProcessor._resolve_sample_reference(ref=ref)
        assert isinstance(deref, SampleReference)
        assert deref.type == SampleReferenceTypes.REMOTE_LIB_SRA.name
        assert deref.name == "sample"
        assert deref.lib_paths is None
        assert deref.identifier == ref.upper()[7:]
        assert deref.table_path is None

    @pytest.mark.parametrize(
        "ref",
        [
            f"table:{REF_FILE_EMPTY}",
            f"table:{REF_FILE_EMPTY_2}",
        ],
    )
    def test__resolve_sample_reference_sample_table(self, ref):
        """Test method ``._resolve_sample_reference()``.

        Use references to sample tables.
        """
        deref = SampleProcessor._resolve_sample_reference(ref=ref)
        assert isinstance(deref, SampleReference)
        assert deref.type == SampleReferenceTypes.TABLE.name
        assert deref.name is None
        assert deref.lib_paths is None
        assert deref.identifier is None
        assert deref.table_path == Path(ref.split(":", maxsplit=1)[1])

    @pytest.mark.parametrize(
        "ref",
        [
            f"{REF_INVALID}",
            f"{REF_FILE_EMPTY},{REF_INVALID}",
            f"{REF_INVALID},{REF_FILE_EMPTY}",
            f"{REF_INVALID,REF_INVALID}",
            f"{REF_FILE_EMPTY},",
            f",{REF_FILE_EMPTY}",
            ",",
            f"{REF_FILE_EMPTY},{REF_FILE_EMPTY},{REF_FILE_EMPTY}",
            f"sample@{REF_INVALID}",
            f"illegal^name@{REF_FILE_EMPTY}",
            f"table:{REF_INVALID}",
            f"tAble:{REF_FILE_EMPTY}",
            f"table:{REF_FILE_EMPTY},{REF_FILE_EMPTY}",
            "SRR1234567A",
            "XRR1234567",
            "SRR123456",
            "S1234567",
            "RR1234567",
            "SR1234567",
            "sample@SRR1234567A",
            "illegal^name@SRR1234567",
        ],
    )
    def test__resolve_sample_reference_invalid(self, ref):
        """Test method ``._resolve_sample_reference()``.

        Use various invalid sample references.
        """
        deref = SampleProcessor._resolve_sample_reference(ref=ref)
        assert isinstance(deref, SampleReference)
        assert deref.type == SampleReferenceTypes.INVALID.name

    @pytest.mark.parametrize(
        "ref",
        [
            str(REF_FILE_EMPTY),
            str(REF_FILE_EMPTY_2),
        ],
    )
    def test_is_unnamed_single_end_true(self, ref):
        """Test method ``._is_unnamed_single_end()``.

        Use references to unnamed single-ended libaries.
        """
        assert SampleProcessor._is_unnamed_single_end(ref=ref) is True

    @pytest.mark.parametrize(
        "ref",
        [
            f"{REF_FILE_EMPTY},{REF_FILE_EMPTY}",
            "SRR1234567",
            f"sample@{REF_FILE_EMPTY}",
            f"sample@{REF_FILE_EMPTY},{REF_FILE_EMPTY}",
            "sample@SRR1234567",
            f"table:{REF_FILE_EMPTY}",
            f"{REF_INVALID}",
        ],
    )
    def test_is_unnamed_single_end_false(self, ref):
        """Test method ``._is_unnamed_single_end()``.

        Use references that do not refer to unnamed single-ended libaries.
        """
        assert SampleProcessor._is_unnamed_single_end(ref=ref) is False

    @pytest.mark.parametrize(
        "ref",
        [
            f"sample@{REF_FILE_EMPTY}",
            f"sample@{REF_FILE_EMPTY_2}",
        ],
    )
    def test_is_named_single_end_true(self, ref):
        """Test method ``._is_named_single_end()``.

        Use references to named single-ended libaries.
        """
        assert SampleProcessor._is_named_single_end(ref=ref) is True

    @pytest.mark.parametrize(
        "ref",
        [
            str(REF_FILE_EMPTY),
            f"{REF_FILE_EMPTY},{REF_FILE_EMPTY}",
            "SRR1234567",
            f"sample@{REF_FILE_EMPTY},{REF_FILE_EMPTY}",
            "sample@SRR1234567",
            f"table:{REF_FILE_EMPTY}",
            f"{REF_INVALID}",
        ],
    )
    def test_is_named_single_end_false(self, ref):
        """Test method ``._is_named_single_end()``.

        Use references that do not refer to named single-ended libaries.
        """
        assert SampleProcessor._is_named_single_end(ref=ref) is False

    @pytest.mark.parametrize(
        "ref",
        [
            f"{REF_FILE_EMPTY},{REF_FILE_EMPTY}",
            f"{REF_FILE_EMPTY},{REF_FILE_EMPTY_2}",
            f"{REF_FILE_EMPTY_2},{REF_FILE_EMPTY}",
            f"{REF_FILE_EMPTY_2},{REF_FILE_EMPTY_2}",
        ],
    )
    def test_is_unnamed_paired_end_true(self, ref):
        """Test method ``._is_unnamed_paired_end()``.

        Use references to unnamed paired-ended libaries.
        """
        assert SampleProcessor._is_unnamed_paired_end(ref=ref) is True

    @pytest.mark.parametrize(
        "ref",
        [
            str(REF_FILE_EMPTY),
            "SRR1234567",
            f"sample@{REF_FILE_EMPTY}",
            f"sample@{REF_FILE_EMPTY},{REF_FILE_EMPTY}",
            "sample@SRR1234567",
            f"table:{REF_FILE_EMPTY}",
            f"{REF_INVALID}",
        ],
    )
    def test_is_unnamed_paired_end_false(self, ref):
        """Test method ``._is_unnamed_paired_end()``.

        Use references that do not refer to unnamed paired-ended libaries.
        """
        assert SampleProcessor._is_unnamed_paired_end(ref=ref) is False

    @pytest.mark.parametrize(
        "ref",
        [
            f"sample@{REF_FILE_EMPTY},{REF_FILE_EMPTY}",
            f"sample@{REF_FILE_EMPTY},{REF_FILE_EMPTY_2}",
            f"sample@{REF_FILE_EMPTY_2},{REF_FILE_EMPTY}",
            f"sample@{REF_FILE_EMPTY_2},{REF_FILE_EMPTY_2}",
        ],
    )
    def test_is_named_paired_end_true(self, ref):
        """Test method ``._is_named_paired_end()``.

        Use references to named paired-ended libaries.
        """
        assert SampleProcessor._is_named_paired_end(ref=ref) is True

    @pytest.mark.parametrize(
        "ref",
        [
            str(REF_FILE_EMPTY),
            f"{REF_FILE_EMPTY},{REF_FILE_EMPTY}",
            "SRR1234567",
            f"sample@{REF_FILE_EMPTY}",
            "sample@SRR1234567",
            f"table:{REF_FILE_EMPTY}",
            f"{REF_INVALID}",
        ],
    )
    def test_is_named_paired_end_false(self, ref):
        """Test method ``._is_named_paired_end()``.

        Use references that do not refer to named paired-ended libaries.
        """
        assert SampleProcessor._is_named_paired_end(ref=ref) is False

    @pytest.mark.parametrize(
        "ref",
        [
            "SRR1234567",
            "DRR0000000",
            "ERR7654321",
            "SRR1234567890",
            "DRR0000000000",
            "ERR0987654321",
            "srr1234567",
        ],
    )
    def test_is_unnamed_seq_identifier_true(self, ref):
        """Test method ``._is_unnamed_seq_identifier()``.

        Use references to unnamed remote libraries.
        """
        assert SampleProcessor._is_unnamed_seq_identifier(ref=ref) is True

    @pytest.mark.parametrize(
        "ref",
        [
            str(REF_FILE_EMPTY),
            f"{REF_FILE_EMPTY},{REF_FILE_EMPTY}",
            f"sample@{REF_FILE_EMPTY}",
            f"sample@{REF_FILE_EMPTY},{REF_FILE_EMPTY}",
            "sample@SRR1234567",
            f"table:{REF_FILE_EMPTY}",
            f"{REF_INVALID}",
        ],
    )
    def test_is_unnamed_seq_identifier_false(self, ref):
        """Test method ``._is_unnamed_seq_identifier()``.

        Use references that do not refer to unnamed remote libraries.
        """
        assert SampleProcessor._is_unnamed_seq_identifier(ref=ref) is False

    @pytest.mark.parametrize(
        "ref",
        [
            "sample@SRR1234567",
            "sample@SRR1234567890",
            "sample@DRR0000000",
            "sample@ERR7654321",
            "sample@srr1234567",
        ],
    )
    def test_is_named_seq_identifier_true(self, ref):
        """Test method ``._is_named_seq_identifier()``.

        Use references to named remote libraries.
        """
        assert SampleProcessor._is_named_seq_identifier(ref=ref) is True

    @pytest.mark.parametrize(
        "ref",
        [
            str(REF_FILE_EMPTY),
            f"{REF_FILE_EMPTY},{REF_FILE_EMPTY}",
            "SRR1234567",
            f"sample@{REF_FILE_EMPTY}",
            f"sample@{REF_FILE_EMPTY},{REF_FILE_EMPTY}",
            f"table:{REF_FILE_EMPTY}",
            f"{REF_INVALID}",
        ],
    )
    def test_is_named_seq_identifier_false(self, ref):
        """Test method ``._is_named_seq_identifier()``.

        Use references that do not refer to named remote libraries.
        """
        assert SampleProcessor._is_named_seq_identifier(ref=ref) is False

    @pytest.mark.parametrize(
        "ref",
        [
            f"table:{REF_FILE_EMPTY}",
            f"table:{REF_FILE_EMPTY_2}",
        ],
    )
    def test_is_sample_table_true(self, ref):
        """Test method ``._is_sample_table()``.

        Use references to sample tables.
        """
        assert SampleProcessor._is_sample_table(ref=ref) is True

    @pytest.mark.parametrize(
        "ref",
        [
            str(REF_FILE_EMPTY),
            f"{REF_FILE_EMPTY},{REF_FILE_EMPTY}",
            "SRR1234567",
            f"sample@{REF_FILE_EMPTY}",
            f"sample@{REF_FILE_EMPTY},{REF_FILE_EMPTY}",
            "sample@SRR1234567",
            f"{REF_INVALID}",
        ],
    )
    def test_is_sample_table_false(self, ref):
        """Test method ``._is_sample_table()``.

        Use references that do not refer to sample tables.
        """
        assert SampleProcessor._is_sample_table(ref=ref) is False

    def test_normalize_path(self):
        """Test method ``._normalize_relative_path()``.

        Use a relative path.
        """
        PATH = "path/to/file"
        assert SampleProcessor._normalize_path(PATH) == str(Path.cwd() / PATH)

    def test_normalize_path_absolute(self):
        """Test method ``._normalize_relative_path()``.

        Use an absolute path.
        """
        PATH = "/path/to/file"
        assert SampleProcessor._normalize_path(PATH) == PATH

    def test_normalize_path_empty(self):
        """Test method ``._normalize_relative_path()``.

        Use an empty path.
        """
        assert SampleProcessor._normalize_path("") == ""
