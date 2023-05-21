"""Infer missing sample metadata with HTSinfer."""

import logging
from pathlib import Path
from typing import Tuple

import pandas as pd

from zarp.abstract_classes.sample_processor import SampleProcessor
from zarp.samples import sample_table_processor as stp
from zarp.config.models import ConfigFileHTSinfer
from zarp.snakemake.config_file_processor import ConfigFileProcessor
from zarp.config.mappings import map_model_to_zarp
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
        # TODO: Uncomment when records selector and tests are implemented.
        if self.records.empty:
            LOGGER.debug("No metadata to infer.")
            return self.records
        LOGGER.info("Inferring missing metadata...")
        conf_file, _ = self._configure_run(root_dir=loc)
        executor: SnakemakeExecutor = SnakemakeExecutor(
            run_config=self.config.run,
            config_file=conf_file,
            exec_dir=loc,
        )
        cmd = executor.compile_command(snakefile=workflow)
        executor.run(cmd=cmd)

        return self.records

    def _prepare_sample_table(self, sample_table: Path) -> None:
        """Write sample table for the HTSinfer Snakemake workflow."""
        stp.write(
            df=self.records,
            path=sample_table,
            mapping=map_model_to_zarp,
            )

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
        run_dir: Path = root_dir
        run_dir.mkdir(parents=True, exist_ok=True)
        outdir: Path = root_dir
        outdir.mkdir(parents=True, exist_ok=True)

        config_file: Path = run_dir / "config.yaml"

        content: ConfigFileHTSinfer = ConfigFileHTSinfer(
            samples=str(run_dir / "samples_htsinfer.tsv"),
            outdir=str(outdir),
            samples_out=str(run_dir / "samples_result.tsv"),
        )

        config_file_writer = ConfigFileProcessor()
        config_file_writer.set_content(content=content)
        config_file_writer.write(path=config_file)

        self._prepare_sample_table(sample_table=Path(content.samples))

        return config_file, content

    def _select_records(self) -> None:
        """Select records to process."""
