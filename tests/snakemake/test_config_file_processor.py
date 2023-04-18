"""Unit tests for ``:mod:zarp.snakemake.config_file_processor``."""

from pathlib import Path

from zarp.config.models import ConfigFileSRA
from zarp.snakemake.config_file_processor import ConfigFileProcessor


class TestConfigFileProcessor:
    """Test for class ``:cls:zarp.snakemake.config_file_processor.ConfigFileProcessor`` class."""  # noqa: E501

    content = ConfigFileSRA(
        cluster_log_dir="cluster_log_dir",
        log_dir="log_dir",
        outdir="outdir",
        samples="samples",
        samples_out="samples_out",
    )

    def test_init(self):
        """Test constructor."""
        cfp = ConfigFileProcessor()
        assert hasattr(cfp, "content")
        assert cfp.content.dict() == {}

    def test_set_content(self):
        """Test `set_content()` function."""
        content = self.content.copy()
        cfp = ConfigFileProcessor()
        assert hasattr(cfp, "content")
        assert cfp.content == {}
        cfp.set_content(content=content)
        assert cfp.content == content

    def test_write(self, tmpdir):
        """Test `write()` function."""
        cfp = ConfigFileProcessor()
        cfp.write(Path(tmpdir) / "config.yaml")
        assert (Path(tmpdir) / "config.yaml").is_file()

    def test_write_content(self, tmpdir):
        """Test `write()` function with content."""
        content = self.content.copy()
        cfp = ConfigFileProcessor()
        content = ConfigFileSRA(
            cluster_log_dir="cluster_log_dir",
            log_dir="log_dir",
            outdir="outdir",
            samples="samples",
            samples_out="samples_out",
        )
        cfp.set_content(content=content)
        assert cfp.content == content
        print(cfp.content.dict())
        cfp.write(Path(tmpdir) / "config.yaml")
        assert (Path(tmpdir) / "config.yaml").is_file()
        print(Path(tmpdir) / "config.yaml")
        print(cfp.content.dict())
        with open(Path(tmpdir) / "config.yaml", "r") as _file:
            assert (
                _file.read()
                == """cluster_log_dir: cluster_log_dir
log_dir: log_dir
outdir: outdir
samples: samples
samples_out: samples_out
"""
            )
