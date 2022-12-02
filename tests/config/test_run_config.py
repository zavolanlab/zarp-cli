"""Unit tests for ``:mod:zarp.config.run_config``."""

from pathlib import Path

import pytest

from zarp.config.run_config import RunConfigFileProcessor
from zarp.config.models import (
    ConfigRun,
    ConfigUser,
)

TEST_FILE_DIR: Path = Path(__file__).parents[1].absolute() / "files"
SAMPLE_TABLE: Path = TEST_FILE_DIR / "sample_table.tsv"


class TestRunConfigFileProcessor:
    """Test ``:cls:zarp.config.run_config.RunConfigFileProcessor`` class."""

    def test_constructor(self):
        """Test class constructor."""
        processor = RunConfigFileProcessor(
            run_config=ConfigRun(),
            user_config=ConfigUser(),
        )
        assert hasattr(processor, "run_config")
        assert hasattr(processor, "user_config")

    def test_write_run_config(self, tmp_path):
        """Test write run configuration file."""
        processor = RunConfigFileProcessor(
            run_config=ConfigRun(run_directory=tmp_path),
            user_config=ConfigUser(),
        )
        path = processor.write_run_config()
        assert path.exists()

    def test_write_run_config_no_run_directory(self):
        """Test write run configuration file with no run directory."""
        processor = RunConfigFileProcessor(
            run_config=ConfigRun(run_directory=None),
            user_config=ConfigUser(),
        )
        with pytest.raises(ValueError):
            processor.write_run_config()

    def test_get_file_content(self, tmp_path):
        """Test get file content."""
        processor = RunConfigFileProcessor(
            run_config=ConfigRun(run_directory=tmp_path),
            user_config=ConfigUser(),
        )
        content = processor._get_file_content()
        assert isinstance(content, str)
        assert content.startswith("---\n")
        assert content.endswith("...\n")

    def test_get_required_params(self, tmp_path):
        """Test get required parameters."""
        processor = RunConfigFileProcessor(
            run_config=ConfigRun(run_directory=tmp_path),
            user_config=ConfigUser(),
        )
        params = processor._get_required_params()
        assert isinstance(params, str)
        assert params.startswith("samples: ")
        assert params.endswith("\n")

    def test_get_required_params_no_run_directory(self):
        """Test get required parameters with no run directory."""
        processor = RunConfigFileProcessor(
            run_config=ConfigRun(run_directory=None),
            user_config=ConfigUser(),
        )
        with pytest.raises(ValueError):
            processor._get_required_params()

    def test_get_optional_params_all_none(self, tmp_path):
        """Test get optional parameters with no params."""
        processor = RunConfigFileProcessor(
            run_config=ConfigRun(run_directory=tmp_path),
            user_config=ConfigUser(),
        )
        params = processor._get_optional_params()
        assert isinstance(params, str)
        assert params == ""

    def test_get_optional_params_with_atomic(self, tmp_path):
        """Test get optional parameters with atomic parameter."""
        processor = RunConfigFileProcessor(
            run_config=ConfigRun(
                run_directory=tmp_path,
                description="Test description",
            ),
            user_config=ConfigUser(),
        )
        params = processor._get_optional_params()
        assert isinstance(params, str)
        assert params == "  report_description: Test description\n"

    def test_get_optional_params_with_empty_list(self, tmp_path):
        """Test get optional parameters with empty list parameter."""
        processor = RunConfigFileProcessor(
            run_config=ConfigRun(run_directory=tmp_path),
            user_config=ConfigUser(emails=[]),
        )
        params = processor._get_optional_params()
        assert isinstance(params, str)
        assert params == ""

    def test_get_optional_params_with_list(self, tmp_path):
        """Test get optional parameters with list parameter."""
        processor = RunConfigFileProcessor(
            run_config=ConfigRun(run_directory=tmp_path),
            user_config=ConfigUser(emails=["abc@de.fg"]),  # type: ignore
        )
        params = processor._get_optional_params()
        assert isinstance(params, str)
        assert params == "  author_email: abc@de.fg\n"
