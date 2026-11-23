"""Tests for the example module. Delete together with example.py.

Good scientific tests use synthetic data with KNOWN parameters, compare with
numerical tolerances, and include awkward inputs (reversed axes, NaNs, ...).
"""

import numpy as np
import pytest

from guiding_simulator.example import FWHM_PER_SIGMA, gaussian, sampled_maximum, simulate_peak


def test_gaussian_equals_amplitude_at_centre():
    assert gaussian(1.5, amplitude=3.0, centre=1.5, sigma=0.2) == pytest.approx(3.0)


def test_gaussian_is_half_maximum_at_half_fwhm():
    sigma = 0.7
    half_width = FWHM_PER_SIGMA * sigma / 2
    values = gaussian([-half_width, half_width], amplitude=2.0, centre=0.0, sigma=sigma)
    np.testing.assert_allclose(values, [1.0, 1.0], rtol=1e-12)


@pytest.mark.parametrize("sigma", [0.0, -1.0])
def test_gaussian_rejects_non_positive_sigma(sigma):
    with pytest.raises(ValueError, match="sigma"):
        gaussian([0.0], amplitude=1.0, centre=0.0, sigma=sigma)


def test_simulate_peak_is_reproducible_with_the_same_seed():
    x = np.linspace(-1, 1, 50)
    kwargs = {"amplitude": 1.0, "centre": 0.0, "sigma": 0.3, "noise_std": 0.1}
    a = simulate_peak(x, rng=np.random.default_rng(7), **kwargs)
    b = simulate_peak(x, rng=np.random.default_rng(7), **kwargs)
    np.testing.assert_array_equal(a, b)


def test_simulate_peak_noise_has_requested_size(rng):
    x = np.linspace(-5, 5, 20_000)
    y = simulate_peak(x, amplitude=1.0, centre=0.0, sigma=1.0, noise_std=0.05, rng=rng)
    residual = y - gaussian(x, 1.0, 0.0, 1.0)
    assert residual.std() == pytest.approx(0.05, rel=0.03)


def test_simulate_peak_rejects_negative_noise(rng):
    with pytest.raises(ValueError, match="noise_std"):
        simulate_peak([0.0], amplitude=1, centre=0, sigma=1, noise_std=-0.1, rng=rng)


def test_sampled_maximum_finds_known_peak(rng):
    x = np.linspace(-5, 5, 1001)
    y = simulate_peak(x, amplitude=1.0, centre=1.2, sigma=0.5, noise_std=0.01, rng=rng)
    peak = sampled_maximum(x, y)
    assert peak.position == pytest.approx(1.2, abs=0.1)
    assert peak.height == pytest.approx(1.0, abs=0.05)


def test_sampled_maximum_does_not_assume_sorted_x():
    x = np.array([2.0, 1.0, 0.0])  # e.g. a reversed sweep
    y = np.array([0.1, 0.9, 0.4])
    assert sampled_maximum(x, y).position == 1.0


@pytest.mark.parametrize(
    ("x", "y", "message"),
    [
        ([], [], "empty"),
        ([0, 1], [0, 1, 2], "equal shapes"),
        ([0, 1, 2], [0.0, np.nan, 1.0], "NaN"),  # NaN must not pass silently
        ([[0, 1]], [[0, 1]], "1-D"),
    ],
)
def test_sampled_maximum_rejects_bad_input(x, y, message):
    with pytest.raises(ValueError, match=message):
        sampled_maximum(x, y)
