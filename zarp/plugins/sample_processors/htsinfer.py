"""Infer missing sample metadata with HTSinfer."""

import logging
from pathlib import Path
from typing import List, Tuple

import pandas as pd

from zarp.abstract_classes.sample_processor import SampleProcessor
from zarp.config.mappings import map_model_to_zarp, map_zarp_to_model
from zarp.config.models import ConfigFileHTSinfer
from zarp.samples import sample_table_processor as stp
from zarp.snakemake.config_file_processor import ConfigFileProcessor
from zarp.snakemake.run import SnakemakeExecutor

LOGGER = logging.getLogger(__name__)


class SampleProcessorHTSinfer(
    SampleProcessor
):  # pylint: disable=too-few-public-methods
    """Infer metadata with HTSinfer.

    Args:
        records: Pandas ``DataFrame`` object.
        config: ``Config`` object.

    Attributes:
        records: Pandas ``DataFrame`` object.
        config: ``Config`` object.
    """

    # pylint: disable=unused-argument
    def process(  # pylint: disable=arguments-differ
        self,
        loc: Path = Path.cwd(),
        workflow: Path = Path.cwd() / "Snakefile",
    ) -> pd.DataFrame:
        """Infer metadata with HTSinfer.

        Args:
            loc: Working directory. Data may be located within child
                directories. Defaults to current working directory.
            workflow: Path to Snakemake workflow for running HTSinfer.
                Defaults to ``Snakefile`` in current working directory.

        Returns: Dataframe with inferred sample metadata.
        """
        if self.records.empty:
            LOGGER.debug("No metadata to infer.")
            return self.records
        conf_file, conf_content = self._configure_run(root_dir=loc)
        bind_paths: List[Path] = list(
            self.records.paths_1.append(self.records.paths_2).dropna().unique()
        )
        executor: SnakemakeExecutor = SnakemakeExecutor(
            run_config=self.config.run,
            config_file=conf_file,
            exec_dir=loc,
            bind_paths=bind_paths,
        )
        cmd = executor.compile_command(snakefile=workflow)
        LOGGER.debug(f"Command: {cmd}")
        executor.run(cmd=cmd)
        df: pd.DataFrame
        if self.config.run.execution_mode == "DRY_RUN":
            df = self.records
        else:
            df = stp.read(
                path=Path(conf_content.samples_out),
                mapping=map_zarp_to_model,
            )
        return df

    def _select_records(self) -> None:
        """Select records to process."""

    def _configure_run(
        self,
        root_dir: Path = Path.cwd(),
    ) -> Tuple[Path, ConfigFileHTSinfer]:
        """Configure HTSinfer workflow run.

        The configuration and sample table files are written and all
        directories are created.

        Args:
            root_dir: Path to root directory for HTSinfer workflow run.

        Returns: Path to configuration file and configuration file content.
        """
        root_dir.mkdir(parents=True, exist_ok=True)
        run_dir: Path = root_dir / "runs" / self.config.run.identifier
        run_dir.mkdir(parents=True, exist_ok=True)
        outdir: Path = root_dir / "results"
        outdir.mkdir(parents=True, exist_ok=True)
        log_dir = root_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        cluster_log_dir = root_dir / "logs" / "cluster"
        cluster_log_dir.mkdir(parents=True, exist_ok=True)

        config_file: Path = run_dir / "config.yaml"
        content: ConfigFileHTSinfer = ConfigFileHTSinfer(
            samples=str(run_dir / "samples_htsinfer.tsv"),
            outdir=str(outdir),
            samples_out=str(run_dir / "samples_result.tsv"),
            log_dir=str(log_dir),
            cluster_log_dir=str(cluster_log_dir),
        )
        config_file_writer = ConfigFileProcessor()
        config_file_writer.set_content(content=content)
        config_file_writer.write(path=config_file)

        self._prepare_sample_table(sample_table=Path(content.samples))

        return config_file, content

    def _prepare_sample_table(self, sample_table: Path) -> None:
        """Write sample table for the HTSinfer Snakemake workflow."""
        stp.write(
            df=self.records,
            path=sample_table,
            mapping=map_model_to_zarp,
        )
