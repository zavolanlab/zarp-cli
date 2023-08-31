"""Unit tests for ``:mod:zarp.plugins.sample_processors.dummy_data``."""

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from zarp.config.models import Config, ConfigRun, ConfigSample, ConfigUser
from zarp.samples.sample_record_processor import SampleRecordProcessor as SRP
from zarp.plugins.sample_processors.dummy_data import (
    SampleProcessorDummyData as SPDD,
)

LOGGER = logging.getLogger(__name__)


class TestSampleProcessorDefaults:
    """Test ``cls:zarp.plugins.sample_processors.SampleProcessorDummyData``."""

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
        }
    )

    def test_init(self):
        """Test constructor."""
        config = self.config.copy(deep=True)
        df = self.data.copy(deep=True)
        srp = SRP()
        srp.append(df)
        srdd = SPDD(config=config, records=srp.records)
        assert hasattr(srdd, "records")
        assert len(srdd.records.index) == 2

    def test_process(self):
        """Test `.process()` method."""
        config = self.config.copy(deep=True)
        df = self.data.copy(deep=True)
        srp = SRP()
        srp.append(df)
        srdd = SPDD(config=config, records=srp.records)
        df_out = srdd.process()
        assert len(df_out.index) == 2
        assert np.isnan(srdd.records["paths_2"].iloc[0])
        assert df_out["paths_2"].iloc[0] == "X" * 15

    def test_process_empty(self, caplog):
        """Test `.process()` method with no records."""
        config = self.config.copy(deep=True)
        srp = SRP()
        srdd = SPDD(config=config, records=srp.records)
        assert len(srdd.records.index) == 0
        with caplog.at_level(logging.DEBUG):
            df_out = srdd.process()
        assert len(df_out.index) == 0
        assert "No dummy data to set" in caplog.text
