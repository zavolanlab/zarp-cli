"""Initialisation routine."""

import os
import git
from zarp.config.models import (
    ExecModes,
    ToolPackaging,
    Run
)


class WorkflowLoader:
    """Obtain external workflows.

    Attributes:
        base_dir (str): path for saving submodules.
        repo (Repo): This repository (zarp-cli).

    Args:
        base_dir (str): path to default save of submodules.

    Example:
        Clone ZARP from github and list all submodules in this repository.
        >>> wfl = WorkflowLoader()
        >>> wfl.clone_repo("zarp", "git@github.com:zavolanlab/zarp.git")
        >>> wfl.get_submodules()
    """

    def __init__(self, base_dir: str = "submodules") -> None:
        self.set_basedir(base_dir)
        self.repo = git.Repo()

    def get_basedir(self) -> str:
        return self.base_dir

    def set_basedir(self, base_dir: str) -> None:
        self.base_dir = base_dir

    def clone_repo(self, repo_name: str, repo_url: str) -> bool:
        """Clone repo from github.

        Args:
            repo_name (str): name of the repo as appearing in base_dir.
            repo_url (str): https url to git repo.

        Returns:
            True if specified repo exists.

        Note:
            Will alter index and .gitmodules file,
            but will not create a new commit.
            If the specified repo is already cloned, no error is raised.
        """
        submodule = git.Submodule.add(repo=self.repo,
                                      name=repo_name,
                                      path=os.path.join(self.get_basedir(),
                                                        repo_name),
                                      url=repo_url)
        return submodule.exists()

    def set_submodule_commit(self, name: str, commit: str) -> None:
        """Checkout submodule at specified commit.

        Args:
            name (str): Name of submodule to apply commit.
            commit (str): Commit string, e.g. branch or tag.

        Note:
            Checkout at given commit detaches HEAD.
            To revert detached HEAD, use commit=<branch>
        """
        sms = self.get_submodules()
        for sm in sms:
            if sm.name == name:
                # Make the submodule a Repo.
                sm_repo = sm.module()
        try:
            # Use git directly.
            sm_repo.git.checkout(commit)
        except git.exec.GitCommandError as git_error:
            print(f"commit string {commit} not valid.")
            raise git_error
        except NameError as name_error:
            print(f"No submodule with {name} found.")
            raise name_error

    def install_dependencies(self) -> bool:
        """Install dependencies from submodule repos."""
        pass

    def get_submodules(self) -> list:
        return self.repo.submodules
