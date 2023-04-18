"""Unit tests for ``:mod:zarp.config.run_config``."""

from pathlib import Path

from zarp.config.run_config import RunConfigFileProcessor
from zarp.config.models import (
    ConfigRun,
    ConfigUser,
)

TEST_FILE_DIR: Path = Path(__file__).parents[1].absolute() / "files"
SAMPLE_TABLE: Path = TEST_FILE_DIR / "sample_table.tsv"


class TestRunConfigFileProcessor:
    """Test ``:cls:zarp.config.run_config.RunConfigFileProcessor`` class."""

    run_config = ConfigRun(
        zarp_directory=Path(__file__).parent / "files" / "zarp"
    )

    def test_constructor(self):
        """Test class constructor."""
        processor = RunConfigFileProcessor(
            run_config=self.run_config,
            user_config=ConfigUser(),
        )
        assert hasattr(processor, "run_config")
        assert hasattr(processor, "user_config")

    def test_write_run_config(self, tmpdir):
        """Test write run configuration file."""
        run_config = self.run_config.copy()
        processor = RunConfigFileProcessor(
            run_config=run_config,
            user_config=ConfigUser(),
        )
        processor.run_config.working_directory = tmpdir
        path = processor.write_run_config()
        assert path.exists()

    def test_get_file_content(self, tmpdir):
        """Test get file content."""
        run_config = self.run_config.copy()
        processor = RunConfigFileProcessor(
            run_config=run_config,
            user_config=ConfigUser(),
        )
        processor.run_config.working_directory = tmpdir
        content = processor._get_file_content()
        assert isinstance(content, str)
        assert content.startswith("---\n")
        assert content.endswith("...\n")

    def test_get_required_params(self, tmpdir):
        """Test get required parameters."""
        run_config = self.run_config.copy()
        processor = RunConfigFileProcessor(
            run_config=run_config,
            user_config=ConfigUser(),
        )
        processor.run_config.working_directory = tmpdir
        params = processor._get_required_params()
        assert isinstance(params, str)
        assert params.startswith("samples: ")
        assert params.endswith("\n")

    def test_get_optional_params_all_none(self, tmpdir):
        """Test get optional parameters with no params."""
        run_config = self.run_config.copy()
        processor = RunConfigFileProcessor(
            run_config=run_config,
            user_config=ConfigUser(),
        )
        processor.run_config.working_directory = tmpdir
        params = processor._get_optional_params()
        assert isinstance(params, str)
        assert params == ""

    def test_get_optional_params_with_atomic(self, tmpdir):
        """Test get optional parameters with atomic parameter."""
        run_config = self.run_config.copy()
        processor = RunConfigFileProcessor(
            run_config=run_config,
            user_config=ConfigUser(),
        )
        processor.run_config.working_directory = tmpdir
        processor.run_config.description = "Test description"
        params = processor._get_optional_params()
        assert isinstance(params, str)
        assert params == "  report_description: Test description\n"

    def test_get_optional_params_with_empty_list(self, tmpdir):
        """Test get optional parameters with empty list parameter."""
        run_config = self.run_config.copy()
        processor = RunConfigFileProcessor(
            run_config=run_config,
            user_config=ConfigUser(emails=[]),
        )
        processor.run_config.working_directory = tmpdir
        params = processor._get_optional_params()
        assert isinstance(params, str)
        assert params == ""

    def test_get_optional_params_with_list(self, tmpdir):
        """Test get optional parameters with list parameter."""
        run_config = self.run_config.copy()
        processor = RunConfigFileProcessor(
            run_config=run_config,
            user_config=ConfigUser(emails=["abc@de.fg"]),  # type: ignore
        )
        processor.run_config.working_directory = tmpdir
        params = processor._get_optional_params()
        assert isinstance(params, str)
        assert params == "  author_email: abc@de.fg\n"
