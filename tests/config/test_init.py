"""Test module for `zarp.config.init`"""

import os
from zarp.config import init

class TestWorkflowLoader:
    """Unit tests for cloning other repos."""

    def test_init(self, tmpdir):
        """Initialise WorkflowLoader"""
        wfl = init.WorkflowLoader(base_dir=tmpdir)
        assert os.path.abspath(wfl.base_dir) == tmpdir
        wfl = init.WorkflowLoader()
        assert os.path.abspath(wfl.base_dir) == os.path.abspath("submodules")