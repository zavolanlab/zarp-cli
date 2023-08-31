"""Infer missing sample metadata with HTSinfer."""

import logging
from pathlib import Path
from typing import Tuple

import pandas as pd

from zarp.abstract_classes.sample_processor import SampleProcessor
from zarp.config.enums import ExecModes
from zarp.config.mappings import map_model_to_zarp, map_zarp_to_model
from zarp.config.models import ConfigFileZARP
from zarp.samples import sample_table_processor as stp
from zarp.snakemake.config_file_processor import ConfigFileProcessor
from zarp.snakemake.run import SnakemakeExecutor

LOGGER = logging.getLogger(__name__)


class SampleRunnerZARP(
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
        LOGGER.info("Preparing ZARP run...")
        if self.records.empty:
            LOGGER.info("No samples to run.")
            return self.records
        conf_file, _ = self._configure_run(root_dir=loc)
        executor: SnakemakeExecutor = SnakemakeExecutor(
            run_config=self.config.run,
            config_file=conf_file,
            exec_dir=loc,
        )
        cmd = executor.compile_command(snakefile=workflow)
        LOGGER.debug(f"Command: {cmd}")
        if self.config.run.execution_mode == ExecModes.PREPARE_RUN.value:
            LOGGER.info(
                "ZARP run is ready to execute (use '--execution-mode=RUN')"
            )
        else:
            LOGGER.info("Executing ZARP...")
            executor.run(cmd=cmd)
        return self.records

    def _configure_run(
        self,
        root_dir: Path = Path.cwd(),
    ) -> Tuple[Path, ConfigFileZARP]:
        """Configure ZARP workflow run.

        The configuration and sample table files are written and all
        directories are created.

        Args:
            root_dir: Path to root directory for ZARP workflow run.

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
        kallisto_index_dir = root_dir / "indexes" / "kallisto_indexes"
        kallisto_index_dir.mkdir(parents=True, exist_ok=True)
        salmon_index_dir = root_dir / "indexes" / "salmon_indexes"
        salmon_index_dir.mkdir(parents=True, exist_ok=True)
        star_index_dir = root_dir / "indexes" / "star_indexes"
        star_index_dir.mkdir(parents=True, exist_ok=True)
        alfa_index_dir = root_dir / "indexes" / "alfa_indexes"
        alfa_index_dir.mkdir(parents=True, exist_ok=True)

        rule_config: str
        if self.config.run.rule_config is None:
            rule_config = str(
                self.config.run.zarp_directory
                / "tests"
                / "input_files"
                / "rule_config.yaml"
            )
        else:
            rule_config = str(self.config.run.rule_config)

        config_file: Path = run_dir / "config.yaml"
        content: ConfigFileZARP = ConfigFileZARP(
            samples=str(run_dir / "samples_zarp.tsv"),
            output_dir=str(outdir),
            log_dir=str(log_dir),
            cluster_log_dir=str(cluster_log_dir),
            kallisto_indexes=str(kallisto_index_dir),
            salmon_indexes=str(salmon_index_dir),
            star_indexes=str(star_index_dir),
            alfa_indexes=str(alfa_index_dir),
            rule_config=rule_config,
            report_description=self.config.run.description,
            report_logo=str(self.config.user.logo),
            report_url=str(self.config.user.url),
            author_name=str(self.config.user.author),
            author_email=str(self.config.user.email),
        )
        config_file_writer = ConfigFileProcessor()
        config_file_writer.set_content(content=content)
        config_file_writer.write(path=config_file, exclude_none=True)

        self._prepare_sample_table(sample_table=Path(content.samples))

        return config_file, content

    def _prepare_sample_table(self, sample_table: Path) -> None:
        """Write sample table for the ZARP Snakemake workflow."""
        stp.write(
            df=self.records,
            path=sample_table,
            mapping=map_model_to_zarp,
            columns=list(map_zarp_to_model.keys()),
        )

    def _select_records(self) -> None:
        """Select records to process."""
        for _, row in self.records.iterrows():
            _row = row[map_model_to_zarp.keys()]  # type: ignore
            if _row.isnull().any():
                LOGGER.warning(
                    (
                        f"Sample '{row.loc['name']}' is dropped due to missing"
                        " metadata."
                    ),
                )
                self.records.drop(index=row.name, inplace=True)
