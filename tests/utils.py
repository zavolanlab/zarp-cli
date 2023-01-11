"""Test fixtures and utilities."""

from typing import Any, List, Type


class RaiseError:
    """Raise exception when called."""

    exception: Type[BaseException] = BaseException

    def __init__(self, exc: Type[BaseException]) -> None:
        """Class constructor."""
        RaiseError.exception = exc

    def __call__(self, *args, **kwargs) -> None:
        """Class instance call method."""
        raise RaiseError.exception


class MultiMocker:
    """Return different list element every time an instance is called."""

    counter: int = -1
    responses: List[Any] = []

    def __init__(self, responses: List[Any]) -> None:
        """Class constructor."""
        MultiMocker.responses = responses
        MultiMocker.counter = -1

    def __call__(self) -> Any:
        """Class instance call method."""
        MultiMocker.counter += 1
        return MultiMocker.responses[MultiMocker.counter]
