"""Unit tests for ``:mod:zarp.plugins.sample_processors.defaults``."""

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from zarp.config.models import Config, ConfigRun, ConfigSample, ConfigUser
from zarp.samples.sample_record_processor import SampleRecordProcessor as SRP
from zarp.plugins.sample_processors.defaults import (
    SampleProcessorDefaults as SRD,
)

LOGGER = logging.getLogger(__name__)


class TestSampleProcessorDefaults:
    """Test ``cls:zarp.plugins.sample_processors.SampleProcessorDefaults``."""

    config = Config(
        run=ConfigRun(zarp_directory=Path(__file__).parent / "files" / "zarp"),
        sample=ConfigSample(fragment_length_distribution_mean=1000),
        user=ConfigUser(),
    )
    data = pd.DataFrame(
        data={
            "identifier": ["sample1", "sample2"],
            "type": ["LOCAL_LIB_SINGLE", "LOCAL_LIB_SINGLE"],
            "orientation": ["SF", "SF"],
        }
    )

    def test_init(self):
        """Test constructor."""
        config = self.config.copy()
        df = self.data.copy()
        srp = SRP()
        srp.append(df)
        srd = SRD(config=config, records=srp.records)
        assert hasattr(srd, "records")
        assert len(srd.records.index) == 2
        assert np.isnan(srd.records["salmon_kmer_size"].iloc[0])

    def test_process(self):
        """Test `.process()` method."""
        config = self.config.copy()
        df = self.data.copy()
        srp = SRP()
        srp.append(df)
        srd = SRD(config=config, records=srp.records)
        df_out = srd.process()
        assert len(df_out.index) == 2
        assert not np.isnan(df_out["salmon_kmer_size"].iloc[0])
        assert df_out["fragment_length_distribution_mean"].iloc[0] == 1000

    def test_process_empty(self, caplog):
        """Test `.process()` method with no records."""
        config = self.config.copy()
        srp = SRP()
        srd = SRD(config=config, records=srp.records)
        assert len(srd.records.index) == 0
        with caplog.at_level(logging.DEBUG):
            df_out = srd.process()
        assert len(df_out.index) == 0
        assert "No defaults to set" in caplog.text
