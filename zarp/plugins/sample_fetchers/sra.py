"""Fetch remote samples from SRA."""

import logging
from pathlib import Path
from typing import Dict, Mapping, Optional, Tuple

import pandas as pd

from zarp.abstract_classes.sample_processor import SampleFetcher
from zarp.config.enums import SampleReferenceTypes
from zarp.config.models import ConfigFileSRA
from zarp.plugins.sample_table_processors.zarp import SampleTableProcessorZARP
from zarp.snakemake.config_file import ConfigFileProcessor
from zarp.snakemake.run import SnakemakeExecutor

LOGGER = logging.getLogger(__name__)


class SampleFetcherSRA(SampleFetcher):
    """Fetch remote samples from SRA.

    Args:
        samples: Sequence of ``Sample`` objects.
        config: ``Config`` object.

    Attributes:
        samples: Sequence of ``Sample`` objects.
        config: ``Config`` object.
    """

    def fetch(  # pylint: disable=arguments-differ
        self,
        loc: Path = Path.cwd(),
        workflow: Path = Path("Snakefile"),
    ) -> Dict[str, Tuple[Path, Optional[Path]]]:
        """Fetch remote samples from SRA.

        Args:
            loc: Path to fetch samples to. Samples may be located within child
                directories. Defaults to current working directory.
            workflow: Path to Snakemake workflow for fetching samples from SRA.
                Defaults to ``Snakefile`` in current working directory.

        Returns: Mapping of sample identifiers to local sample paths.
        """
        LOGGER.info(
            "Fetching:"
            f" {', '.join([str(smpl.identifier) for smpl in self.samples])}"
        )

        conf_file: Path
        conf_content: ConfigFileSRA
        executor: SnakemakeExecutor
        paths: Dict[str, Tuple[Path, Optional[Path]]]

        conf_file, conf_content = self._configure_run(root_dir=loc)
        executor = SnakemakeExecutor(
            run_config=self.config.run,
            config_file=conf_file,
            exec_dir=loc,
        )
        cmd = executor.compile_command(snakefile=workflow)
        executor.run(cmd=cmd)
        paths = self._get_local_paths(sample_table=conf_content.samples_out)

        LOGGER.info(f"Fetched: {', '.join(paths.keys())}")

        return paths

    def update(  # pylint: disable=arguments-differ
        self,
        paths: Optional[Mapping[str, Tuple[Path, Optional[Path]]]] = None,
    ) -> None:
        """Update samples with local paths.

        Args:
            paths: Mapping of sample identifiers to local sample paths.
        """
        if paths is None:
            paths = {}
        for identifier in paths.keys():
            for sample in self.samples:
                if sample.identifier == identifier:
                    sample.paths = paths[identifier]

    def _set_samples(self) -> None:
        """Select samples to fetch."""
        self.samples = [
            sample
            for sample in self.samples
            if sample.type == SampleReferenceTypes.REMOTE_LIB_SRA.name
        ]

    def _prepare_sample_table(self, sample_table: Path) -> None:
        """Write sample table with remote sample identifiers."""
        sample_table_processor = SampleTableProcessorZARP()
        sample_table_processor.set_samples_from_objects(samples=self.samples)
        sample_table_processor.write(
            path=sample_table,
            columns=["sample"],
        )

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

        config_file: Path = run_dir / "config.yaml"

        content: ConfigFileSRA = ConfigFileSRA(
            samples=run_dir / "samples_remote.tsv",
            outdir=root_dir / "sra",
            samples_out=run_dir / "samples_local.tsv",
            log_dir=root_dir / "logs",
            cluster_log_dir=root_dir / "logs" / "cluster",
        )

        config_file_writer = ConfigFileProcessor()
        config_file_writer.set_content(content=content)
        config_file_writer.write(path=config_file)

        self._prepare_sample_table(sample_table=content.samples)

        return config_file, content

    @staticmethod
    def _get_local_paths(
        sample_table: Path,
    ) -> Dict[str, Tuple[Path, Optional[Path]]]:
        """Get local paths to downloaded samples."""
        data_dict: Dict
        data: pd.DataFrame
        sample_table_processor = SampleTableProcessorZARP()
        data = sample_table_processor.read(path=sample_table, index_col=0)
        data["fq1"] = data.get("fq1", "")
        data["fq2"] = data.get("fq2", "")
        data = data.where(data != "", None)
        data_dict = data.to_dict("index")
        local_paths: Dict[str, Tuple[Path, Optional[Path]]] = {}
        for identifier, paths in data_dict.items():
            local_paths[str(identifier)] = (
                Path(paths["fq1"]),
                Path(paths["fq2"]) if paths["fq2"] else None,
            )
        return local_paths
