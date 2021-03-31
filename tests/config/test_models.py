"""Tests for module `zarp.config.models`."""

from zarp.config import models


class TestModels:
    """Unit tests for all models and enumerators."""

    def config_create():
        """Create instance of main configuration."""
        config = models.Config()
        assert config.user.surname is None
