"""Models and enumerators."""

from enum import Enum
from typing import (Optional, List, Tuple)

from pydantic import BaseModel


# Sample-specific enumerators and models
class StarAlignEndsTypes(Enum):
    # TODO: docstring
    end_to_end = "EndToEnd"
    local = "Local"


class StarTwoPassModes(Enum):
    # TODO: docstring
    basic = "Basic"
    none = "None"


class SampleIds(BaseModel):
    # TODO: docstring
    name: Optional[str] = None
    sra: Optional[str] = None


class Adapters(BaseModel):
    # TODO: docstring
    three: Optional[str] = None


class FragLenDist(BaseModel):
    # TODO: docstring
    mean: Optional[float] = None
    sd: Optional[float] = None
    # TODO: set different defaults for single-end libs


class GenomeResources(BaseModel):
    # TODO: docstring
    reference_sequences: Optional[str] = None
    annotations: Optional[str] = None


class ToolParams(BaseModel):
    # TODO: this might change if non-default, mutable tool parameters are to
    # be read from a config file
    # TODO: docstring
    trim_polyA: bool = True
    # TODO: using default STAR params now; discuss whether to change
    n_multimappers: int = 10
    align_ends: StarAlignEndsTypes = StarAlignEndsTypes.local
    two_pass_mode: StarTwoPassModes = StarTwoPassModes.none


class Sample(BaseModel):
    # TODO: docstring
    file_paths: Optional[Tuple[str, Optional[None]]] = None
    ids: SampleIds = SampleIds()
    adapters: Adapters = Adapters()
    fragment_length_distribution: FragLenDist = FragLenDist()
    tool_parameters: ToolParams = ToolParams()


# Run-specific enumerators and models
class ExecModes(Enum):
    # TODO: docstring
    dry_run = "dry_run"
    prepare_run = "prepare_run"
    run = "run"


class ToolPackaging(Enum):
    # TODO: docstring
    conda = "--use-conda"
    singularity = "--use-singularity"


class OutputFiles(Enum):
    # TODO: docstring
    configs = "configs"
    logs = "logs"
    results = "results"
    temporary = "temporary"


class Run(BaseModel):
    # TODO: docstring
    identifier: Optional[str] = None
    description: Optional[str] = None
    cores: int = 1
    htsinfer_config: Optional[str] = None
    execution_mode: ExecModes = ExecModes.run
    tool_packaging: ToolPackaging = ToolPackaging.conda
    execution_profile: Optional[str] = None
    snakemake_config: Optional[str] = None
    keep_files: List[OutputFiles] = [
        OutputFiles.configs,
        OutputFiles.logs,
        OutputFiles.results
    ]


# User-specific enumerators and models
class User(BaseModel):
    # TODO: docstring
    # TODO: discuss whether to require name & email to enforce good practices
    name: Optional[str] = None
    email: Optional[str] = None
    url: Optional[str] = None
    # TODO: allow URLs and local file paths or only one of the two?
    logo_location: Optional[str] = None


# Unified config model
class Config(BaseModel):
    # TODO: docstring
    sample: Sample
    run: Run = Run()
    user: User = User()
