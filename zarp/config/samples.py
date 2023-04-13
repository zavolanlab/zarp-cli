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

import pandas as pd  # type: ignore
from pandas.errors import EmptyDataError  # type: ignore

from zarp.config.enums import SampleReferenceTypes
from zarp.config.models import (
    ConfigRun,
    ConfigSample,
    Sample,
    SampleReference,
)
from zarp.config.sample_tables import SampleTableProcessor
from zarp.run.snakemake import SnakemakeExecutor


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
        samples_remote: List of remote sample objects.
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
        self.samples_remote: List[Sample] = []

    def set_samples(self) -> None:
        """Resolve sample references and set sample configuration."""
        for ref_str in self.references:
            ref = self._resolve_sample_reference(ref=ref_str)
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
        self._set_samples_remote()
        LOGGER.debug(self.samples_remote)

    def fetch_remote_libraries(
        self,
        workflow_path_suffix: str = "workflow/rules/sra_download.smk",
    ) -> Path:
        """Fetch remote sequencing libraries and convert to FASTQ.

        Args:
            dry_run: If ``True``, do not actually download any files.
            workflow_path_suffix: Path to Snakemake workflow file for fetching
                remote libraries, relative to the ZARP workflow repository
                path.

        Returns:
            Path to sample table with FASTQ paths of remote files.

        Raises:
            FileNotFoundError: If the Snakemake workflow file cannot be found.
            ValueError: If the ZARP workflow repository path is not set in the
                configuration.
        """
        executor: SnakemakeExecutor = SnakemakeExecutor(
            run_config=self.run_config,
            workflow_id="sra_download",
        )
        executor.setup()
        sample_table_out: Path = executor.run_dir / "samples_remote_loc.tsv"
        ids = ", ".join(
            [str(sample.identifier) for sample in self.samples_remote]
        )
        LOGGER.info(f"Fetching: {ids}")
        sample_table: Path = self.write_remote_sample_table(
            samples=self.samples_remote,
            outpath=executor.run_dir / "samples_remote.tsv",
        )
        config: Dict = {
            "samples": str(sample_table),
            "outdir": str(executor.exec_dir / "sra"),
            "samples_out": str(sample_table_out),
            "log_dir": str(executor.exec_dir / "logs"),
            "cluster_log_dir": str(executor.exec_dir / "logs" / "cluster"),
        }
        executor.set_configuration_file(config=config)
        LOGGER.debug(f"Run configuration file created: {executor.config_file}")
        if self.run_config.zarp_directory is None:
            raise ValueError(
                "ZARP workflow repository path is not set in the configuration"
            )
        smk: Path = self.run_config.zarp_directory / workflow_path_suffix
        if not smk.exists():
            raise FileNotFoundError(
                f"Cannot find SRA download workflow at '{smk}'. Make sure"
                " the ZARP workflow repository path is set correctly in"
                " the configuration; currently set to:"
                f" {self.run_config.zarp_directory}"
            )
        executor.set_command(snakefile=smk)
        LOGGER.debug(
            f"Snakemake command compiled: {' '.join(executor.command)}"
        )
        LOGGER.debug("Starting SRA download workflow...")
        executor.run()
        LOGGER.info(f"Sample table with FASTQ paths: {sample_table_out}")
        LOGGER.info("SRA download workflow completed")
        return sample_table_out

    def update_sample_paths(self, sample_table: Path) -> None:
        """Update sample paths from SRA download workflow ouptput sample table.

        Args:
            sample_table: Path to sample table.
        """
        with open(sample_table, encoding="utf-8") as _file:
            data = pd.read_csv(
                _file,
                comment="#",
                sep="\t",
                keep_default_na=False,
            )
            for _, row in data.iterrows():
                sample = next(
                    (
                        sample
                        for sample in self.samples
                        if sample.identifier == row["sample"]
                    ),
                    None,
                )
                if sample is not None:
                    if "fq1" not in data.columns or row["fq1"] == "":
                        LOGGER.warning(
                            "No FASTQ path available, sample skipped:"
                            f" '{row['sample']}'"
                        )
                        continue
                    row["fq1"] = self._normalize_path(
                        _path=row["fq1"], anchor=sample_table.parent
                    )
                    if "fq2" in data.columns:
                        row["fq2"] = self._normalize_path(
                            _path=row["fq2"], anchor=sample_table.parent
                        )
                        if row["fq2"] == "":
                            row["fq2"] = None
                    else:
                        row["fq2"] = None
                    sample.paths = (
                        Path(row["fq1"]).absolute(),
                        row["fq2"],
                    )
                else:
                    LOGGER.warning(
                        f"Sample '{row['sample']}' not found in sample table"
                    )

    def _process_sample_table(self, path: Path) -> None:
        """Set sample configuration for all samples in a sample table.

        Args:
            path: Path to sample table.
        """
        table = SampleTableProcessor()
        table.read(path=path)
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
        self.samples.append(sample.copy(update=update))  # type: ignore

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
        self.samples.append(sample.copy(update=update))  # type: ignore

    def _set_samples_remote(self) -> None:
        """Subset sample configuration for remote samples."""
        self.samples_remote = [
            sample
            for sample in self.samples
            if sample.type == SampleReferenceTypes.REMOTE_LIB.name
        ]

    @staticmethod
    def write_sample_table(
        samples: List[Sample],
        outpath: Optional[Path] = None,
    ) -> Path:
        """Write table of samples to file.

        Args:
            samples: List of sample objects.
            outpath: Path to write sample table to.

        Returns:
            Path to sample table.
        """
        if outpath is None:
            outpath = Path.cwd() / "samples.tsv"
        records = [sample.dict() for sample in samples]
        table = SampleTableProcessor(records=records)
        table.write(path=outpath)
        return outpath

    @staticmethod
    def write_remote_sample_table(
        samples: List[Sample],
        outpath: Optional[Path] = None,
    ) -> Path:
        """Write table of remote samples to file.

        Args:
            samples: List of sample objects.
            outpath: Path to write sample table to.

        Returns:
            Path to sample table.
        """
        if outpath is None:
            outpath = Path.cwd() / "samples_remote.tsv"
        sra_ids = [sample.identifier for sample in samples]
        with open(outpath, "w", encoding="utf-8") as _file:
            _file.write("sample\n")
            for sra_id in sra_ids:
                _file.write(f"{sra_id}\n")
        return outpath

    @staticmethod
    def _resolve_sample_reference(
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

    @staticmethod
    def _normalize_path(_path: str, anchor: Path = Path.cwd()) -> str:
        """Normalize relative paths to absolute paths.

        Args:
            _path: Path to normalize.
            anchor: Anchor path to use if ``_path`` is relative.
        """
        if _path == "":
            return ""
        if not Path(_path).is_absolute():
            return str(anchor / _path)
        return _path
