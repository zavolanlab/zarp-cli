"""Initialisation routine."""

import os
from git import Repo, Submodule
from typing import Optional

from zarp.config.models import (
    ExecModes,
    ToolPackaging,
    Run
)

class WorkflowLoader:
    """Obtain external workflows.

    Args:
        base_dir: path to default save of submodules.
    """

    def __init__(self, base_dir = "submodules") -> None:
        self.base_dir = base_dir

    def clone_repo(self, repo_name: str, repo_url: str, repo_commit: str) -> bool:
        """Clone repo from github.

        Args:
            repo_name: name of the repo as appearing in base_dir
            repo_url: https url to git repo
        """
        repo = Repo(os.getcwd())
        submodule = Submodule.add(repo = repo,
            name = "zarp",
            path = os.path.join(self.base_dir, repo_name),
            url = repo_url)
        # submodule.set_parent_commit(repo_commit) # TODO: replace by text entry
        return True

    def install_dependencies(self) -> bool:
        """Install dependencies from submodule repos."""
        pass