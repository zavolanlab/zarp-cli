"""Abstract sample processor classes."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Mapping, Optional, Sequence, Tuple

from zarp.config.models import Config, Sample


class SampleProcessor(ABC):  # pylint: disable=too-few-public-methods
    """Abstract sample processor class.

    Defines methods to process ``Sample`` objects.

    Args:
        samples: Sequence of ``Sample`` objects.
        config: ``Config`` object.

    Attributes:
        samples: Sequence of ``Sample`` objects.
        config: ``Config`` object.
    """

    def __init__(
        self,
        samples: Sequence[Sample],
        config: Config,
    ) -> None:
        """Class constructor method."""
        self.samples: Sequence[Sample] = samples
        self.config: Config = config

    @abstractmethod
    def update(self) -> None:
        """Update samples."""


class SampleFetcher(SampleProcessor):
    """Abstract sample fetcher class.

    Defines methods to fetch samples from remote sources.

    Args:
        samples: Sequence of ``Sample`` objects.
        config: ``Config`` object.

    Attributes:
        samples: Sequence of ``Sample`` objects.
        config: ``Config`` object.
    """

    def __init__(
        self,
        samples: Sequence[Sample],
        config: Config,
    ) -> None:
        """Class constructor method."""
        super().__init__(samples=samples, config=config)
        self._set_samples()

    @abstractmethod
    def fetch(
        self,
        loc: Path = Path.cwd(),
    ) -> Mapping[str, Tuple[Path, Optional[Path]]]:
        """Fetch remote samples.

        Args:
            loc: Path to fetch samples to. Samples may be located within child
                directories. Defaults to current working directory.

        Returns: Mapping of sample identifiers to local sample paths.
        """

    @abstractmethod
    def _set_samples(self) -> None:
        """Select samples to fetch."""
