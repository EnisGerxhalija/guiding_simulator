"""Shared pytest fixtures.

A fixture is a helper that pytest hands to any test function that has a
parameter with the same name, e.g. ``def test_something(rng):``.
"""

import numpy as np
import pytest


@pytest.fixture
def rng() -> np.random.Generator:
    """A seeded random generator, so tests are repeatable."""
    return np.random.default_rng(12345)
