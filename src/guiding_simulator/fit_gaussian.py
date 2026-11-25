"""Find where a star is when its middle has been cut out by the fibre hole.

The idea:
1. The star is a Gaussian, but the fibre hole removes its centre, so the camera
   only sees a ring of light around the hole.
2. We throw away the pixels inside the hole (they tell us nothing about the star).
3. We fit a full Gaussian to the pixels that are left. The fitted Gaussian
   "fills in" the missing middle, and its centre tells us where the star is.
4. The offset is the fitted centre minus the fibre centre.
"""

import numpy as np
from scipy.optimize import curve_fit

from guiding_simulator import constants as c


def gaussian_2d(xy, amplitude, x0, y0, sigma):
    """Round 2D Gaussian. xy is a pair (x, y) of pixel coordinate arrays."""
    x, y = xy
    r_squared = (x - x0) ** 2 + (y - y0) ** 2
    return amplitude * np.exp(-r_squared / (2 * sigma**2))


def fit_clipped_gaussian(image, hole_x=c.CAMERA_XRES / 2, hole_y=c.CAMERA_YRES / 2,
                         hole_radius=c.FIBER_DEFAULT_RADIUS_PX, roi_radius=c.DEFAULT_SEARCH_RADIUS_PX):
    """Fit a Gaussian to the light around the fibre hole and return the star's offset.

    Parameters:
    - image: 2D camera image (counts).
    - hole_x, hole_y: centre of the fibre hole in pixels.
    - hole_radius: radius of the fibre hole in pixels.
    - roi_radius: only pixels this close to the hole are used.
    """
    # Step 1: distance of every pixel from the fibre centre
    y, x = np.indices(image.shape)
    r = np.sqrt((x - hole_x) ** 2 + (y - hole_y) ** 2)

    # Step 2: keep pixels that are near the hole but NOT inside it,
    use = (r > hole_radius + 1) & (r < roi_radius)
    xs, ys, data = x[use], y[use], image[use].astype(float) # pick out pixels that are in the ring around the hole

    # Step 3: starting guess, the brightness-weighted average position of the ring
    x_guess = np.sum(data * xs) / np.sum(data)
    y_guess = np.sum(data * ys) / np.sum(data)
    guess = [data.max(), x_guess, y_guess, hole_radius / 2]

    # Step 4: fit the Gaussian to the ring of pixels
    params, cov = curve_fit(gaussian_2d, (xs, ys), data, p0=guess)
    amplitude, x0, y0, sigma = params
    x0_err, y0_err = np.sqrt(np.diag(cov))[1:3]

    # Step 5: offset of the star from the fibre centre
    dx, dy = x0 - hole_x, y0 - hole_y
    return {
        "x0": x0, "y0": y0, "x0_err": x0_err, "y0_err": y0_err,
        "fwhm_arcsec": abs(sigma) * c.FWHM_PER_SIGMA * c.ARCSEC_PER_PX,
        "dx_arcsec": dx * c.ARCSEC_PER_PX,
        "dy_arcsec": dy * c.ARCSEC_PER_PX,
        "offset_arcsec": np.hypot(dx, dy) * c.ARCSEC_PER_PX,
    }
