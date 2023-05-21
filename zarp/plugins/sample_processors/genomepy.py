"""Fetch genome resources with ``mod:genomepy``."""

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd

from zarp.abstract_classes.sample_processor import SampleProcessor
from zarp.utils import sanitize_strings

LOGGER = logging.getLogger(__name__)


class SampleProcessorGenomePy(
    SampleProcessor
):  # pylint: disable=too-few-public-methods
    """Fetch genome resources with ``mod:genomepy``.

    Args:
        records: Pandas ``DataFrame`` object.
        config: ``Config`` object.

    Attributes:
        records: Pandas ``DataFrame`` object.
        config: ``Config`` object.
    """

    PROVIDER = "Ensembl"

    def process(  # pylint: disable=arguments-differ
        self,
        loc: Path = Path.cwd(),  # pylint: disable=unused-argument
    ) -> pd.DataFrame:
        """Fetch genome resources with ``mod:genomepy``.

        Args:
            loc: Path to fetch resources to. Resources may be located within
                child directories. Defaults to current working directory.

        Returns: Dataframe with local path information for genome resources.
        """
        if self.records.empty:
            LOGGER.debug("No genome resources to fetch.")
            return self.records

        LOGGER.info("Fetching genome resources...")
        self.set_assemblies()
        resource_paths = self.fetch_resources(genomes_dir_root=loc)
        self.set_resource_paths(resource_paths)
        LOGGER.info(f"Fetched: {list(resource_paths.keys())}")
        return self.records

    def set_assemblies(self) -> None:
        """Set assemblies."""
        LOGGER.debug("Setting assemblies...")
        df: pd.DataFrame = pd.read_csv(
            self.config.run.genome_assemblies_map,
            sep=";",
            header=None,
            names=["organism", "assembly"],
        )
        source_assembly_map: Dict = dict(zip(df.organism, df.assembly))
        self.records["source_sanitized"] = self.records["source"].map(
            sanitize_strings
        )
        self.records["assembly"] = self.records["source_sanitized"].map(
            source_assembly_map
        )
        LOGGER.debug(
            "Assemblies set:"
            f" {self.records[['name', 'source', 'assembly']].to_string()}..."
        )

    def fetch_resources(
        self, genomes_dir_root: Path
    ) -> Dict[str, Tuple[Path, Path]]:
        """Fetch assemblies."""
        # Workaround for
        # https://github.com/vanheeringen-lab/genomepy/issues/238
        # pylint: disable=import-outside-toplevel
        import genomepy  # type: ignore

        LOGGER.info("Fetching assemblies...")

        force: bool = True
        genomes_dir: Path = genomes_dir_root / "latest"
        resources: Dict[str, genomepy.Genome] = {}
        resource_paths: Dict[str, Tuple[Path, Path]] = {}

        if self.config.run.resources_version is not None:
            genomes_dir = genomes_dir_root / str(
                self.config.run.resources_version
            )
            force = False
        genomes_dir.mkdir(parents=True, exist_ok=True)

        assemblies: pd.ArrayLike = self.records["assembly"].dropna().unique()
        LOGGER.debug(f"Assemblies to fetch: {assemblies}")
        for assembly in assemblies:
            LOGGER.debug(f"Fetching assembly: {assembly}")
            resources[assembly] = genomepy.install_genome(
                name=assembly,
                provider=self.PROVIDER,
                genomes_dir=str(genomes_dir),
                annotation=True,
                force=force,
                threads=self.config.run.cores,
                version=self.config.run.resources_version,  # type: ignore
            )

        for name, assembly in resources.items():
            if not Path(assembly.genome_file).is_file():
                LOGGER.warning(f"No genome available for assembly {name}.")
                continue
            # Workaround for
            # https://github.com/vanheeringen-lab/genomepy/issues/237
            # pylint: disable=protected-access
            anno: Optional[str] = assembly._check_annotation_file(ext="gtf")
            if anno is None:
                LOGGER.warning(f"No annotation available for assembly {name}.")
                continue
            resource_paths[name] = (Path(assembly.genome_file), Path(anno))

        return resource_paths

    def set_resource_paths(
        self,
        resource_paths: Dict[str, Tuple[Path, Path]],
    ) -> None:
        """Set resource paths.

        Args:
            resource_paths: Dictionary with genome resource paths.
        """
        LOGGER.debug("Setting resource paths...")
        self.records["reference_sequences"] = self.records["assembly"].map(
            {name: paths[0] for name, paths in resource_paths.items()}
        )
        self.records["annotations"] = self.records["assembly"].map(
            {name: paths[1] for name, paths in resource_paths.items()}
        )
        LOGGER.debug("Resource paths set.")

    def _select_records(self) -> None:
        """Select records to process."""
