"""Test fixtures and utilities."""

from pathlib import Path
from typing import Any, List, Type


def create_config_file(dir: Path):
    """Create Snakemake config file.

    Args:
        dir: Path to directory where config file is to be created.

    Returns:
        Path to config file.
    """
    config_file = dir / "config.yaml"
    with open(config_file, "w") as _file:
        _file.write("some_param: some_value")
    return config_file


def create_input_file(dir: Path):
    """Create input file.

    Args:
        dir: Path to directory where input file is to be created.

    Returns:
        Path to input file.
    """
    input_file = dir / "input_file.txt"
    with open(input_file, "w") as _file:
        _file.write("This is an example input file.")
    return input_file


def create_snakefile(dir: Path, name: str = "Snakefile"):
    """Create Snakefile.

    Args:
        dir: Path to directory where Snakefile is to be created.

    Returns:
        Path to Snakefile.
    """
    snakefile = dir / name
    with open(snakefile, "w") as _file:
        _file.write(
            """rule example:
    input:
        "input_file.txt"
    output:
        temp("output_file.txt")
    shell:
        "cat {input} > {output}; echo 'some content' >> {output}"
"""
        )
    return snakefile


class RaiseError:
    """Raise exception when called."""

    exception: Type[BaseException] = BaseException

    def __init__(self, exc: Type[BaseException]) -> None:
        """Class constructor."""
        RaiseError.exception = exc

    def __call__(self, *args, **kwargs) -> None:
        """Class instance call method."""
        raise RaiseError.exception


class MultiMocker:
    """Return different list element every time an instance is called."""

    counter: int = -1
    responses: List[Any] = []

    def __init__(self, responses: List[Any]) -> None:
        """Class constructor."""
        MultiMocker.responses = responses
        MultiMocker.counter = -1

    def __call__(self) -> Any:
        """Class instance call method."""
        MultiMocker.counter += 1
        return MultiMocker.responses[MultiMocker.counter]
