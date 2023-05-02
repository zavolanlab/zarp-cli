"""Unit tests for ``:mod:zarp.plugins.sample_processors.defaults``."""

import logging
from pathlib import Path

import pytest
import pandas as pd

from zarp.config.models import Config, ConfigRun, ConfigSample, ConfigUser
from zarp.samples.sample_record_processor import SampleRecordProcessor as SRP
from zarp.plugins.sample_processors.defaults import SampleProcessorDefaults as SRD

LOGGER = logging.getLogger(__name__)

class TestSampleProcessorDefaults:
    """ Test ``cls:zarp.plugins.sample_processors.SampleProcessorDefaults`` class."""

    config = Config(run=ConfigRun(zarp_directory=Path(__file__).parent / "files" / "zarp"),
                    sample=ConfigSample(),
        user=ConfigUser(),
    )                                                                                 
    data = pd.DataFrame(                                                              
        data={                                                                        
            "identifier": ["sample1", "sample2"],
            "type": ["LOCAL_LIB_SINGLE", "LOCAL_LIB_SINGLE"],
            "orientation": ["SF", "SF"],
        }                                                                             
    )

    def test_no_initial_sample_table(self):
        """Test adding defaults without creating a sample table first."""
        config = self.config.copy()
        df = pd.DataFrame()
        srd = SRD()
        with pytest(ValueError):
            srd.process(df)

    def test_process_no_update(self) -> pd.DataFrame:
        """Test not overwriting existing values."""
        config = self.config.copy()
        df = self.data.copy()
        set_val = 250
        df["fragment_length_distribution_mean"] = [set_val, set_val]
        srp = SRP()
        srp.append(df)
        srd = SRD()
        records = srd.process(srp)
        assert(records["sample1"]["fragment_length_distribution_mean"] == set_val)

    def test_process_update(self) -> pd.DataFrame:
        """Test adding defaults."""
        config = self.config.copy()
        df = self.data.copy()
        srp = SRP()                                                                   
        srp.append(df)                                                                
        srd = SRD()
        records = srd.process(srp)
        assert(records["sample1"]["fragment_length_distribution_mean"] \
               == Config.sample.fragment_length_distribution_mean)
        
