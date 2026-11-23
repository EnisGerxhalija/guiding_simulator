"""Shared pytest fixtures, available to every test file automatically."""

import os

import numpy as np
import pytest


@pytest.fixture
def rng() -> np.random.Generator:
    """A seeded random generator, so tests are repeatable."""
    return np.random.default_rng(12345)


@pytest.fixture(autouse=True)
def _isolate_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stop the developer's own MY_PROJECT_* variables leaking into tests."""
    for key in list(os.environ):
        if key.startswith("MY_PROJECT_"):
            monkeypatch.delenv(key)
