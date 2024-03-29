"""ZARP CLI package definition."""

from pathlib import Path

from setuptools import (setup, find_packages)

ROOT_DIR: Path = Path(__file__).parent.resolve()

exec(open(ROOT_DIR / "zarp" / "version.py", encoding="utf-8").read())

# Read long description from file
FILE_NAME: Path = ROOT_DIR / "README.md"
with open(FILE_NAME, encoding="utf-8") as _f:
    LONG_DESCRIPTION: str = _f.read()

setup(
    name="zarp",
    version=__version__,  # noqa: F821
    description=(
        "User-friendly command-line interface for the ZARP RNA-Seq analysis "
        "pipeline"
    ),
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://git.scicore.unibas.ch/zavolan_group/tools/zarp-cli",
    author="Zavolan Lab",
    author_email="zavolab-biozentrum@unibas.ch",
    maintainer="Zavolan Lab",
    maintainer_email="zavolab-biozentrum@unibas.ch",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Utilities",
    ],
    entry_points={
        "console_scripts": [
            "zarp = zarp.cli:main",
        ],
    },
    keywords=[
        "bioinformatics",
        "workflow",
        "ngs",
        "high-throughput sequencing",
        "rna-seq",
    ],
    project_urls={
        "Documentation": "https://zavolanlab.github.io/zarp-cli",
        "Repository": "https://github.com/zavolanlab/zarp-cli",
        "Tracker": "https://github.com/zavolanlab/zarp-cli/issues",
    },
    packages=find_packages(),
    include_package_data=True,
    setup_requires=[
        "setuptools_git == 1.2",
    ],
)
