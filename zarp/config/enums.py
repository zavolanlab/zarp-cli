"""Configuration enumerators."""

import logging

from enum import Enum


class DependencyEmbeddingStrategies(Enum):
    """Supported dependency embedding strategies.

    Attributes:
        CONDA: Use binaries from Conda.
        SINGULARITY: Use Singularity containers.
    """

    CONDA = "CONDA"
    SINGULARITY = "SINGULARITY"


class ExecModes(Enum):
    """Execution modes.

    Attributes:
        DRY_RUN: Do not download any files, infer parameters or start the
            analysis workflow.
        PREPARE_RUN: Download files and infer parameters, but do not start the
            analysis workflow.
        RUN:  Download files, infer parameters and start the analysis workflow.
    """

    DRY_RUN = "DRY_RUN"
    PREPARE_RUN = "PREPARE_RUN"
    RUN = "RUN"


class LogLevels(Enum):
    """Log level enumerator.

    Attributes:
        DEBUG: Logging level for debug messages.
        INFO: Logging level for info messages.
        WARN: Logging level for warning messages.
        WARNING: Logging level for warning messages.
        ERROR: Logging level for error messages.
        CRITICAL: Logging level for critical error messages.
    """

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARNING
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class FieldNameMappingDirection(Enum):
    """Field name direction enumerator.

    Attributes:
        TO_MODEL_PROPERTIES: Map from ZARP sample table column to model
            property names.
        TO_TABLE_COL_NAMES: Map from model property to ZARP sample table column
            names.
    """

    TO_MODEL_PROPERTIES = "TO_MODEL_PROPERTIES"
    TO_TABLE_COL_NAMES = "TO_TABLE_COL_NAMES"


class OutputFileGroups(Enum):
    """Output file types.

    Attributes:
        CONFIG: Configuration files.
        LOGS: Log files.
        RESULTS: Result files.
        TEMPORARY: Temporary files.
    """

    CONFIG = "CONFIG"
    LOGS = "LOGS"
    RESULTS = "RESULTS"
    TEMPORARY = "TEMPORARY"


class ReadOrientation(Enum):
    """Read orientation types.

    Cf. https://salmon.readthedocs.io/en/latest/library_type.html

    Attributes:
        STRANDED_FORWARD: Reads are stranded and come from the forward strand.
        STRANDED_REVERSE: Reads are stranded and come from the reverse strand.
        UNSTRANDED: Reads are unstranded.
        INWARD_STRANDED_FORWARD: Mates are oriented toward each other, the
            library is stranded, and first mates come from the forward strand.
        INWARD_STRANDED_REVERSE: Mates are oriented toward each other, the
            library is stranded, and first mates come from the reverse strand.
        INWARD_UNSTRANDED: Mates are oriented toward each other and the library
            is unstranded.
    """

    STRANDED_FORWARD = "SF"
    STRANDED_REVERSE = "SR"
    UNSTRANDED = "U"
    INWARD_STRANDED_FORWARD = "ISF"
    INWARD_STRANDED_REVERSE = "ISR"
    INWARD_UNSTRANDED = "IU"


class SampleReferenceTypes(Enum):
    """Types of sample references.

    Attributes:
        LOCAL_LIB_SINGLE: Local single-ended sequencing library.
        LOCAL_LIB_PAIRED: Local paired-ended sequencing library.
        REMOTE_LIB: Sequencing library available at read archive.
        TABLE: ZARP sample table.
        INVALID: Reference type invalid.
    """

    LOCAL_LIB_SINGLE = "LOCAL_LIB_SINGLE"
    LOCAL_LIB_PAIRED = "LOCAL_LIB_PAIRED"
    REMOTE_LIB = "REMOTE_LIB"
    TABLE = "TABLE"
    INVALID = "INVALID"
