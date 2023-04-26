"""Fetch remote samples from SRA."""

import logging
from pathlib import Path
from typing import Tuple

import pandas as pd

from zarp.abstract_classes.sample_processor import SampleProcessor
from zarp.config.enums import SampleReferenceTypes
from zarp.config.models import ConfigFileSRA
from zarp.config.mappings import (
    columns_sra_in,
    map_model_to_sra_in,
    map_sra_out_to_model,
)
from zarp.samples import sample_table_processor as stp
from zarp.snakemake.config_file_processor import ConfigFileProcessor
from zarp.snakemake.run import SnakemakeExecutor

LOGGER = logging.getLogger(__name__)


class SampleFetcherSRA(
    SampleProcessor
):  # pylint: disable=too-few-public-methods
    """Fetch remote samples from SRA.

    Args:
        records: Pandas ``DataFrame`` object.
        config: ``Config`` object.

    Attributes:
        records: Pandas ``DataFrame`` object.
        config: ``Config`` object.
    """

    def process(  # pylint: disable=arguments-differ
        self,
        loc: Path = Path.cwd(),
        workflow: Path = Path("Snakefile"),
    ) -> pd.DataFrame:
        """Fetch remote samples from SRA.

        Args:
            loc: Path to fetch samples to. Samples may be located within child
                directories. Defaults to current working directory.
            workflow: Path to Snakemake workflow for fetching samples from SRA.
                Defaults to ``Snakefile`` in current working directory.

        Returns: Dataframe with local path information for sequencing
            libraries.
        """
        if self.records.empty:
            LOGGER.debug("No remote libraries to fetch from SRA.")
            return self.records
        LOGGER.info("Fetching remote libraries from SRA...")
        conf_file: Path
        conf_content: ConfigFileSRA
        conf_file, conf_content = self._configure_run(root_dir=loc)
        executor: SnakemakeExecutor = SnakemakeExecutor(
            run_config=self.config.run,
            config_file=conf_file,
            exec_dir=loc,
        )
        cmd = executor.compile_command(snakefile=workflow)
        executor.run(cmd=cmd)
        df: pd.DataFrame = self._process_sample_table(
            sample_table=Path(conf_content.samples_out)
        )
        LOGGER.info(f"Fetched: '{', '.join(df['identifier'].values)}'")
        return df

    def _select_records(self) -> None:
        """Select dataframe records to fetch."""
        self.records: pd.DataFrame = self.records[
            self.records["type"] == SampleReferenceTypes.REMOTE_LIB_SRA.name
        ]

    def _configure_run(
        self,
        root_dir: Path = Path.cwd(),
    ) -> Tuple[Path, ConfigFileSRA]:
        """Configure SRA download workflow run.

        The configuration and sample table files are written and all
        directories are created.

        Args:
            root_dir: Path to root directory for SRA download workflow run.

        Returns: Path to configuration file and configuration file content.
        """
        root_dir.mkdir(parents=True, exist_ok=True)
        run_dir: Path = root_dir / "runs" / self.config.run.identifier
        run_dir.mkdir(parents=True, exist_ok=True)
        outdir: Path = root_dir / "sra"
        outdir.mkdir(parents=True, exist_ok=True)
        cluster_log_dir = root_dir / "logs" / "cluster"
        cluster_log_dir.mkdir(parents=True, exist_ok=True)

        config_file: Path = run_dir / "config.yaml"

        content: ConfigFileSRA = ConfigFileSRA(
            samples=str(run_dir / "samples_remote.tsv"),
            outdir=str(outdir),
            samples_out=str(run_dir / "samples_local.tsv"),
            log_dir=str(root_dir / "logs"),
            cluster_log_dir=str(cluster_log_dir),
        )

        config_file_writer = ConfigFileProcessor()
        config_file_writer.set_content(content=content)
        config_file_writer.write(path=config_file)

        self._prepare_sample_table(sample_table=Path(content.samples))

        return config_file, content

    def _prepare_sample_table(self, sample_table: Path) -> None:
        """Write sample table with remote sample identifiers."""
        stp.write(
            df=self.records,
            path=sample_table,
            mapping=map_model_to_sra_in,
            columns=columns_sra_in,
        )

    @staticmethod
    def _process_sample_table(
        sample_table: Path,
    ) -> pd.DataFrame:
        """Get local paths to downloaded samples."""
        df: pd.DataFrame = stp.read(
            path=sample_table, mapping=map_sra_out_to_model
        )
        df["paths_1"] = df.get("paths_1", "")
        df["paths_2"] = df.get("paths_2", "")
        paths_missing: pd.DataFrame = df[df["paths_1"] == ""]
        if not paths_missing.empty:
            LOGGER.warning(
                "No FASTQ paths available for:"
                f" '{', '.join(paths_missing['identifier'])}'"
            )
            df = df[df["paths_1"] != ""]
        return df
