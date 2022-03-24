"""Test module for `zarp.config.init`"""

import os
from zarp.config.init import WorkflowLoader


class TestWorkflowLoader:
    """Unit tests for cloning other repos."""

    def test_init(self, tmpdir):
        """Initialise WorkflowLoader"""
        wfl = WorkflowLoader(base_dir=tmpdir)
        assert os.path.abspath(wfl.get_basedir()) == tmpdir
        # default initializer
        wfl = WorkflowLoader()
        assert wfl.get_basedir() == "submodules"

    def test_set_basedir(self):
        wfl = WorkflowLoader()
        wfl.set_basedir("new_basedir")
        assert wfl.get_basedir() == "new_basedir"

    def test_get_basedir(self):
        wfl = WorkflowLoader()
        assert wfl.get_basedir() == "submodules"

    def test_clone_repo(self):
        """Mock cloning a repository."""
        pass
