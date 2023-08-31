"""Unit tests for ``:mod:zarp.plugins.sample_processors.genomepy``."""

import logging
from pathlib import Path
import shutil
from unittest.mock import Mock

from genomepy.genome import Genome
import numpy as np
import pandas as pd

from zarp.config.models import Config, ConfigRun, ConfigSample, ConfigUser
from zarp.samples.sample_record_processor import SampleRecordProcessor as SRP
from zarp.plugins.sample_processors.genomepy import (
    SampleProcessorGenomePy as SPG,
)

LOGGER = logging.getLogger(__name__)


class TestSampleProcessorGenomePy:
    """Test ``cls:zarp.plugins.sample_processors.SampleProcessorGenomePy``."""

    config = Config(
        run=ConfigRun(
            zarp_directory=Path(__file__).parents[2] / "files" / "zarp",
            genome_assemblies_map=Path(__file__).parents[2]
            / "files"
            / "genome_assemblies.csv",
        ),
        sample=ConfigSample(fragment_length_distribution_mean=1000),
        user=ConfigUser(),
    )
    data = pd.DataFrame(
        data={
            "identifier": ["sample1", "sample2"],
            "type": ["LOCAL_LIB_SINGLE", "LOCAL_LIB_SINGLE"],
            "orientation": ["SF", "SF"],
            "source": ["Schizosaccharomyces pombe", 4932],
        }
    )
    assemblies = ["ASM294v2", "R64-1-1"]

    def test_init(self):
        """Test constructor."""
        config = self.config.copy(deep=True)
        df = self.data.copy(deep=True)
        srp = SRP()
        srp.append(df)
        spg = SPG(config=config, records=srp.records)
        assert hasattr(spg, "records")
        assert len(spg.records.index) == 2

    def test_process(self, monkeypatch, tmpdir):
        """Test `.process()` method."""
        config = self.config.copy(deep=True)
        df = self.data.copy(deep=True)
        srp = SRP()
        srp.append(df)
        spg = SPG(config=config, records=srp.records)
        genomes_dir_root = Path(tmpdir)
        return_data = []
        for assembly in self.assemblies:
            genomes_dir = genomes_dir_root / "latest" / assembly
            genomes_dir.mkdir(parents=True, exist_ok=False)
            shutil.copyfile(
                Path(__file__).parents[2] / "files" / "fasta",
                genomes_dir / f"{assembly}.fa",
            )
            shutil.copyfile(
                Path(__file__).parents[2] / "files" / "gtf",
                genomes_dir / f"{assembly}.annotation.gtf",
            )
            obj = Genome(assembly, genomes_dir=genomes_dir_root / "latest")
            obj.annotation_gtf_file = (
                genomes_dir / f"{assembly}.annotation.gtf"
            )
            return_data.append(obj)
        monkeypatch.setattr(
            "genomepy.install_genome",
            Mock(side_effect=return_data),
        )
        df_out = spg.process()
        assert len(df_out.index) == 2
        assert (
            df_out["reference_sequences"].iloc[0]
            == genomes_dir_root
            / "latest"
            / self.assemblies[0]
            / f"{self.assemblies[0]}.fa"
        )
        assert (
            df_out["annotations"].iloc[0]
            == genomes_dir_root
            / "latest"
            / self.assemblies[0]
            / f"{self.assemblies[0]}.annotation.gtf"
        )
        assert (
            df_out["reference_sequences"].iloc[1]
            == genomes_dir_root
            / "latest"
            / self.assemblies[1]
            / f"{self.assemblies[1]}.fa"
        )
        assert (
            df_out["annotations"].iloc[1]
            == genomes_dir_root
            / "latest"
            / self.assemblies[1]
            / f"{self.assemblies[1]}.annotation.gtf"
        )

    def test_process_empty(self, caplog):
        """Test `.process()` method with no records."""
        config = self.config.copy(deep=True)
        srp = SRP()
        srdd = SPG(config=config, records=srp.records)
        assert len(srdd.records.index) == 0
        with caplog.at_level(logging.DEBUG):
            df_out = srdd.process()
        assert len(df_out.index) == 0
        assert "No genome resources to fetch" in caplog.text

    def test_set_assemblies(self):
        """Test `.set_assemblies()` method."""
        config = self.config.copy(deep=True)
        df = self.data.copy(deep=True)
        srp = SRP()
        srp.append(df)
        spg = SPG(config=config, records=srp.records)
        spg.set_assemblies()
        assert "assembly" in spg.records.columns
        assert len(spg.records["assembly"]) == 2
        assert list(spg.records["assembly"]) == ["ASM294v2", "R64-1-1"]

    def test_fetch_resources(self, monkeypatch, tmpdir):
        """Test `.fetch_resources()` method."""
        config = self.config.copy(deep=True)
        config.run.resources_version = 50
        df = self.data.copy(deep=True)
        srp = SRP()
        srp.append(df)
        spg = SPG(config=config, records=srp.records)
        spg.set_assemblies()
        genomes_dir_root = Path(tmpdir)
        return_data = []
        for assembly in self.assemblies:
            genomes_dir = (
                genomes_dir_root / str(config.run.resources_version) / assembly
            )
            genomes_dir.mkdir(parents=True, exist_ok=False)
            shutil.copyfile(
                Path(__file__).parents[2] / "files" / "fasta",
                genomes_dir / f"{assembly}.fa",
            )
            shutil.copyfile(
                Path(__file__).parents[2] / "files" / "gtf",
                genomes_dir / f"{assembly}.annotation.gtf",
            )
            obj = Genome(
                assembly,
                genomes_dir=genomes_dir_root
                / str(config.run.resources_version),
            )
            obj.annotation_gtf_file = (
                genomes_dir / f"{assembly}.annotation.gtf"
            )
            return_data.append(obj)
        # test with genome files and annotation files available
        monkeypatch.setattr(
            "genomepy.install_genome",
            Mock(side_effect=return_data),
        )
        paths = spg.fetch_resources(genomes_dir_root=genomes_dir_root)
        assert len(paths) == 2
        # test with one genome file and one annotation file missing
        Path(paths[self.assemblies[0]][0]).unlink()
        Path(paths[self.assemblies[1]][1]).unlink()
        monkeypatch.setattr(
            "genomepy.install_genome",
            Mock(side_effect=return_data),
        )
        paths = spg.fetch_resources(genomes_dir_root=genomes_dir_root)
        assert len(paths) == 0

    def test_set_resource_paths(self):
        """Test `.set_resource_paths()` method."""
        config = self.config.copy(deep=True)
        df = self.data.copy(deep=True)
        srp = SRP()
        srp.append(df)
        spg = SPG(config=config, records=srp.records)
        spg.set_assemblies()
        resource_paths = dict(
            zip(self.assemblies, [(Path(), Path()), (Path(), Path())])
        )
        # test when for all records, assemblies are available
        spg.set_resource_paths(resource_paths=resource_paths)
        assert spg.records["reference_sequences"].iloc[0] == Path()
        assert spg.records["annotations"].iloc[0] == Path()
        assert spg.records["reference_sequences"].iloc[1] == Path()
        assert spg.records["annotations"].iloc[1] == Path()
        # test when for one record, assembly is not available
        spg.records["assembly"].iloc[0] = None
        spg.set_resource_paths(resource_paths=resource_paths)
        assert np.isnan(spg.records["reference_sequences"].iloc[0])
        assert np.isnan(spg.records["annotations"].iloc[0])
        assert spg.records["reference_sequences"].iloc[1] == Path()
        assert spg.records["annotations"].iloc[1] == Path()
