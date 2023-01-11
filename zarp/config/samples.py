"""ZARP sample processing."""

import logging
from os.path import commonprefix
from pathlib import Path
from re import search
from typing import (
    Dict,
    List,
    Optional,
)

from pandas.errors import EmptyDataError  # type: ignore

from zarp.config.enums import SampleReferenceTypes
from zarp.config.models import (
    ConfigRun,
    ConfigSample,
    Sample,
    SampleCollection,
    SampleReference,
)
from zarp.config.sample_tables import SampleTableProcessor


LOGGER = logging.getLogger(__name__)


class SampleProcessor:
    """Process ZARP samples.

    Resolve sample references, set sample configuration, download remote
    samples, validate samples and produce a ZARP sample table.

    Args:
        *args: References to individual sequencing libraries by local file path
            or read archive identifiers OR paths to ZARP sample tables; see
            documentation for details.
        sample_config: Sample configuration parameters.
        run_config: Run configuration parameters.

    Attributes:
        references: References to individual sequencing libraries by local file
            path or read archive identifiers OR paths to ZARP sample tables;
            see documentation for details.
        sample_config: Sample configuration parameters.
        run_config: Run configuration parameters.
        samples: List of sample objects.
    """

    def __init__(
        self,
        *args: str,
        sample_config: ConfigSample,
        run_config: ConfigRun,
    ) -> None:
        """Class constructor."""
        self.references: List[str] = list(args)
        self.sample_config: ConfigSample = sample_config
        self.run_config: ConfigRun = run_config
        self.samples: List[Sample] = []

    def set_samples(self) -> None:
        """Resolve sample references and set sample configuration."""
        for ref_str in self.references:
            ref = self.resolve_sample_reference(ref=ref_str)
            LOGGER.debug(f"Type of sample reference '{ref_str}': {ref.type}")
            if (
                ref.type == SampleReferenceTypes.TABLE.name
                and ref.table_path is not None
            ):
                try:
                    self._process_sample_table(path=ref.table_path)
                except IOError as exc:
                    LOGGER.warning(
                        f"Cannot read table at '{ref.table_path}'. Skipping. "
                        f"Original error: {exc}"
                    )
                except EmptyDataError:
                    LOGGER.warning(
                        f"Table at '{ref.table_path}' is empty. Skipping."
                    )
            elif ref.type in [
                SampleReferenceTypes.LOCAL_LIB_SINGLE.name,
                SampleReferenceTypes.LOCAL_LIB_PAIRED.name,
            ]:
                self._set_sample_from_local_lib(ref=ref)
            elif ref.type == SampleReferenceTypes.REMOTE_LIB.name:
                self._set_sample_from_remote_lib(ref=ref)
            elif ref.type == SampleReferenceTypes.INVALID.name:
                LOGGER.warning(
                    f"Cannot determine type of sample reference '{ref_str}'. "
                    "Check spelling and refer to documentation for supported "
                    "syntax. Skipping."
                )
        LOGGER.debug(self.samples)

    def fetch_remote_libraries(self, dry_run: bool = False) -> None:
        """Fetch remote sequencing libraries.

        Args:
            dry_run: If ``True``, do not actually download any files.
        """
        samples_to_fetch = [
            sample.identifier
            for sample in self.samples
            if sample.type == SampleReferenceTypes.REMOTE_LIB.name
        ]
        LOGGER.debug(
            "Attempting to fetch sequencing libraries for records: "
            f"{samples_to_fetch}"
        )
        if dry_run:
            LOGGER.info(
                "Dry run: not actually fetching any sequencing libraries"
            )
        else:
            LOGGER.info("Fetching any sequencing libraries...")

    def write_sample_table(self) -> Path:
        """Write table of samples to file.

        Returns:
            Path to sample table.

        Raises:
            ValueError: Cannot write table because run directory is not set.
        """
        if self.run_config.run_directory is None:
            raise ValueError(
                "Cannot write sample table, run directory not set."
            )
        # take care of adapter_3p etc. / remove trim_poly_a & adapt_three
        path: Path = self.run_config.run_directory / "samples.tsv"
        records = SampleCollection(  # pylint: disable=E1101
            self.samples
        ).dict()
        table = SampleTableProcessor(records=records)
        table.write(path=path)
        return path

    def _process_sample_table(self, path: Path) -> None:
        """Set sample configuration for all samples in a sample table.

        Args:
            path: Path to sample table.
        """
        table = SampleTableProcessor()
        table.read(path=path)
        LOGGER.warning(table.records)
        for index, record in enumerate(table.records):
            deref = SampleReference()
            # sequence archive identifier
            if record["paths"][0] is None and self._is_unnamed_seq_identifier(
                ref=record["name"]
            ):
                deref.type = SampleReferenceTypes.REMOTE_LIB
                deref.identifier = record["name"].upper()
                self._set_sample_from_remote_lib(
                    ref=deref,
                    update=record,
                )
            # single-ended local library
            elif (
                record["paths"][1] is None
                and isinstance(record["paths"][0], Path)
                and self._is_unnamed_single_end(ref=str(record["paths"][0]))
            ):
                deref.type = SampleReferenceTypes.LOCAL_LIB_SINGLE
                deref.lib_paths = record["paths"]
                self._set_sample_from_local_lib(
                    ref=deref,
                    update=record,
                )
            # paired-ended local library
            elif all(
                isinstance(item, Path) for item in record["paths"]
            ) and self._is_unnamed_paired_end(
                ref=",".join(
                    [
                        str(record["paths"][0]),
                        str(record["paths"][1]),
                    ]
                )
            ):
                deref.type = SampleReferenceTypes.LOCAL_LIB_PAIRED
                deref.lib_paths = record["paths"]
                self._set_sample_from_local_lib(
                    ref=deref,
                    update=record,
                )
            # reference type invalid
            else:
                LOGGER.warning(
                    "Cannot determine type of sample reference for row "
                    f"{index + 1} of sample table '{path}'. Check spelling "
                    "and refer to documentation for supported syntax. "
                    "Skipping."
                )
                continue
            LOGGER.debug(
                f"Type of sample reference for row {index + 1} of sample "
                f"table '{path}': {deref.type}"
            )

    def _set_sample_from_local_lib(
        self,
        ref: SampleReference,
        update: Optional[Dict] = None,
    ) -> None:
        """Set sample configuration for local library.

        Args:
            ref: Sample reference object for a local library (single- or
                paired-ended).
            update: Dictionary of sample configuration parameters to update. If
                not set, class sample config is used.
        """
        if update is None:
            update = {}
        if ref.name is None and ref.lib_paths is not None:
            stems = [path.stem for path in ref.lib_paths if path is not None]
            ref.name = commonprefix(stems)
        sample = Sample(
            type=ref.type,
            name=ref.name,
            paths=ref.lib_paths,
            **self.sample_config.dict(),
        )
        self.samples.append(sample.copy(update=update))

    def _set_sample_from_remote_lib(
        self,
        ref: SampleReference,
        update: Optional[Dict] = None,
    ) -> None:
        """Set sample configuration for remote library.

        Args:
            ref: Sample reference object for a remote library (single- or
                paired-ended).
            update: Dictionary of sample configuration parameters to update. If
                not set, class sample config is used.
        """
        if update is None:
            update = {}
        if ref.name is None:
            ref.name = ref.identifier
        sample = Sample(
            type=ref.type,
            identifier=ref.identifier,
            name=ref.name,
            **self.sample_config.dict(),
        )
        self.samples.append(sample.copy(update=update))

    @staticmethod
    def resolve_sample_reference(
        ref: str,
    ) -> SampleReference:
        """Resolve sample reference.

        Args:
            ref: ZARP-cli sample reference.

        Returns:
            Dereferenced sample.
        """
        deref = SampleReference(
            ref=ref,
            type=SampleReferenceTypes.INVALID,
        )
        parts: List
        paths: List
        if SampleProcessor._is_unnamed_single_end(ref=ref):
            deref.type = SampleReferenceTypes.LOCAL_LIB_SINGLE
            deref.lib_paths = (Path(ref).absolute(), None)
        elif SampleProcessor._is_named_single_end(ref=ref):
            parts = ref.split("@", maxsplit=1)
            deref.type = SampleReferenceTypes.LOCAL_LIB_SINGLE
            deref.name = parts[0]
            deref.lib_paths = (Path(parts[1]).absolute(), None)
        elif SampleProcessor._is_unnamed_paired_end(ref=ref):
            paths = ref.split(",")
            deref.type = SampleReferenceTypes.LOCAL_LIB_PAIRED
            deref.lib_paths = (
                Path(paths[0]).absolute(),
                Path(paths[1]).absolute(),
            )
        elif SampleProcessor._is_named_paired_end(ref):
            parts = ref.split("@", maxsplit=1)
            paths = parts[1].split(",")
            deref.type = SampleReferenceTypes.LOCAL_LIB_PAIRED
            deref.name = parts[0]
            deref.lib_paths = (
                Path(paths[0]).absolute(),
                Path(paths[1]).absolute(),
            )
        elif SampleProcessor._is_unnamed_seq_identifier(ref=ref):
            deref.type = SampleReferenceTypes.REMOTE_LIB
            deref.identifier = ref.upper()
        elif SampleProcessor._is_named_seq_identifier(ref=ref):
            parts = ref.split("@", maxsplit=1)
            deref.type = SampleReferenceTypes.REMOTE_LIB
            deref.name = parts[0]
            deref.identifier = parts[1].upper()
        elif SampleProcessor._is_sample_table(ref=ref):
            parts = ref.split(":", maxsplit=1)
            deref.type = SampleReferenceTypes.TABLE
            deref.table_path = Path(parts[1]).absolute()
        return deref

    @staticmethod
    def _is_unnamed_single_end(
        ref: str,
    ) -> bool:
        """Check if sample reference is an unnamed single-end library.

        Args:
            ref: ZARP-cli sample reference.

        Returns:
            True if sample reference is an unnamed single-end library.
        """
        return Path(ref).is_file()

    @staticmethod
    def _is_named_single_end(
        ref: str,
    ) -> bool:
        """Check if sample reference is a named single-end library.

        Args:
            ref: ZARP-cli sample reference.

        Returns:
            True if sample reference is a named single-end library.
        """
        parts = ref.split("@", maxsplit=1)
        return (
            len(parts) == 2
            and bool(search(r"^[a-zA-Z0-9\-\_\.]+$", parts[0]))
            and Path(parts[1]).is_file()
        )

    @staticmethod
    def _is_unnamed_paired_end(
        ref: str,
    ) -> bool:
        """Check if sample reference is an unnamed paired-end library.

        Args:
            ref: ZARP-cli sample reference.

        Returns:
            True if sample reference is an unnamed paired-end library.
        """
        paths = ref.split(",")
        return len(paths) == 2 and all(Path(path).is_file() for path in paths)

    @staticmethod
    def _is_named_paired_end(
        ref: str,
    ) -> bool:
        """Check if sample reference is a named paired-end library.

        Args:
            ref: ZARP-cli sample reference.

        Returns:
            True if sample reference is a named paired-end library.
        """
        parts = ref.split("@", maxsplit=1)
        return (
            len(parts) == 2
            and bool(search(r"^[a-zA-Z0-9\-\_\.]+$", parts[0]))
            and len(parts[1].split(",")) == 2
            and all(Path(path).is_file() for path in parts[1].split(","))
        )

    @staticmethod
    def _is_unnamed_seq_identifier(
        ref: str,
    ) -> bool:
        """Check if sample reference is an unnamed sequence archive identifier.

        Args:
            ref: ZARP-cli sample reference.

        Returns:
            True if sample reference is an unnamed sequence archive identifier.
        """
        return bool(search(r"^[DES]RR\d{7,}$", ref.upper()))

    @staticmethod
    def _is_named_seq_identifier(
        ref: str,
    ) -> bool:
        """Check if sample reference is a named sequence archive identifier.

        Args:
            ref: ZARP-cli sample reference.

        Returns:
            True if sample reference is a named sequence archive identifier.
        """
        parts = ref.split("@", maxsplit=1)
        return (
            len(parts) == 2
            and bool(search(r"^[a-zA-Z0-9\-\_\.]+$", parts[0]))
            and bool(search(r"^[DES]RR\d{7,}$", parts[1].upper()))
        )

    @staticmethod
    def _is_sample_table(
        ref: str,
    ) -> bool:
        """Check if sample reference is a sample table.

        Args:
            ref: ZARP-cli sample reference.

        Returns:
            True if sample reference is a sample table.
        """
        parts = ref.split(":", maxsplit=1)
        return (
            len(parts) == 2
            and parts[0] == "table"
            and Path(parts[1]).is_file()
        )
