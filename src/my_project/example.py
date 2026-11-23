"""Example analysis code. Delete or replace this module.

It is here to show the conventions the template expects:

* plain functions with explicit inputs and outputs (no globals or hidden state);
* NumPy-style docstrings that state units, assumptions and errors;
* input checks that fail loudly instead of returning plausible nonsense;
* randomness only through a :class:`numpy.random.Generator` passed in by the
  caller, so results are repeatable.
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

#: Ratio of full width at half maximum to standard deviation for a Gaussian.
FWHM_PER_SIGMA = 2.0 * np.sqrt(2.0 * np.log(2.0))


def gaussian(
    x: ArrayLike, amplitude: float, centre: float, sigma: float
) -> NDArray[np.float64]:
    """Evaluate a Gaussian peak.

    Parameters
    ----------
    x : array_like
        Positions at which to evaluate the peak.
    amplitude : float
        Peak height, in the units of the returned values.
    centre : float
        Peak position, in the same units as `x`.
    sigma : float
        Standard deviation, in the same units as `x`; must be positive. This
        is *not* the full width at half maximum: FWHM = 2.355 * sigma.

    Returns
    -------
    numpy.ndarray
        ``amplitude * exp(-(x - centre)**2 / (2 * sigma**2))``, with the same
        shape as `x`.

    Raises
    ------
    ValueError
        If `sigma` is not positive.

    Examples
    --------
    >>> gaussian([0.0, 1.0], amplitude=2.0, centre=0.0, sigma=1.0)
    array([2.        , 1.21306132])
    """
    if sigma <= 0:
        raise ValueError(f"sigma must be positive, got {sigma}")
    x = np.asarray(x, dtype=float)
    return amplitude * np.exp(-0.5 * ((x - centre) / sigma) ** 2)


def simulate_peak(
    x: ArrayLike,
    *,
    amplitude: float,
    centre: float,
    sigma: float,
    noise_std: float,
    rng: np.random.Generator,
) -> NDArray[np.float64]:
    """Simulate a Gaussian peak with additive Gaussian noise.

    Parameters
    ----------
    x : array_like
        Sample positions.
    amplitude, centre, sigma : float
        Peak parameters, as in :func:`gaussian`.
    noise_std : float
        Standard deviation of the noise, in the units of the signal; must be
        zero or positive.
    rng : numpy.random.Generator
        Source of randomness, e.g. ``numpy.random.default_rng(seed)``. Passing
        the same seeded generator gives identical output.

    Returns
    -------
    numpy.ndarray
        Noisy signal, same shape as `x`.

    Raises
    ------
    ValueError
        If `noise_std` is negative or `sigma` is not positive.
    """
    if noise_std < 0:
        raise ValueError(f"noise_std must be >= 0, got {noise_std}")
    clean = gaussian(x, amplitude, centre, sigma)
    return clean + rng.normal(0.0, noise_std, size=clean.shape)


@dataclass(frozen=True)
class PeakEstimate:
    """Position and height of the largest sampled point.

    Attributes
    ----------
    position : float
        x value of the largest sample.
    height : float
        Signal value at that sample.
    """

    position: float
    height: float


def sampled_maximum(x: ArrayLike, y: ArrayLike) -> PeakEstimate:
    """Return the largest sampled point of a 1-D signal.

    Parameters
    ----------
    x : array_like
        Sample positions, 1-D. They need not be sorted.
    y : array_like
        Signal values, same shape as `x`. Must be finite.

    Returns
    -------
    PeakEstimate
        Position and height of the largest sample.

    Raises
    ------
    ValueError
        If the inputs are empty, not 1-D, differ in shape, or `y` contains
        NaN or infinity.

    Notes
    -----
    This is the largest *noisy sample*, not a fitted peak centre. Its accuracy
    is limited by the sample spacing and the noise, and it comes with no
    uncertainty estimate. Fit a model if you need the true centre.

    Examples
    --------
    >>> sampled_maximum([0, 1, 2], [0.1, 0.9, 0.4])
    PeakEstimate(position=1.0, height=0.9)
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.ndim != 1 or x.shape != y.shape:
        raise ValueError(
            f"x and y must be 1-D with equal shapes, got {x.shape} and {y.shape}"
        )
    if x.size == 0:
        raise ValueError("x and y are empty")
    if not np.all(np.isfinite(y)):
        raise ValueError("y contains NaN or infinite values; clean the data first")
    i = int(np.argmax(y))
    return PeakEstimate(position=float(x[i]), height=float(y[i]))
