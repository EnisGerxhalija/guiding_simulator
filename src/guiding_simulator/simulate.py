from guiding_simulator import constants as c
import numpy as np 

def fwhm_arcsec_to_sigma_px(fwhm_arcsec):
    """Convert a seeing FWHM in arcseconds to a Gaussian sigma in pixels."""
    fwhm_px = fwhm_arcsec / c.ARCSEC_PER_PX
    sigma_px = fwhm_px / c.FWHM_PER_SIGMA
    return sigma_px

def calculate_star_peak(fwhm_arcsec, total_counts = 100000):
    """Calculate the peak brightness of a star given its total counts and FWHM in arcseconds.
    
    Parameters:
    - total_counts: total counts of the star in pixel values.
    - fwhm_arcsec: The full width at half maximum of the star in arcseconds.
    
    Returns:
    - The peak brightness of the star in pixel values.
    """
    sigma_px = fwhm_arcsec_to_sigma_px(fwhm_arcsec)
    peak_brightness = total_counts / (2 * np.pi * sigma_px**2)

    return peak_brightness


def make_gaussian_star(x0, y0, fwhm_arcsec):
    """Return a pure light image containing one round Gaussian star.
    Parameters:
    - x0, y0: The center of the star in pixel coordinates.
    - fwhm_arcsec: The full width at half maximum of the star in arcseconds.
    - peak: The peak brightness of the star in pixel values.
    Returns:
    - A 2D numpy array representing the camera image with the Gaussian star.
    """

    sigma = fwhm_arcsec_to_sigma_px(fwhm_arcsec)
    y, x = np.indices((c.CAMERA_YRES, c.CAMERA_XRES)) # create a grid of pixel coordinates (first row index, second column index)
    r_squared = (x - x0) ** 2 + (y - y0) ** 2 # squared distance from the center of the star
    image = calculate_star_peak(fwhm_arcsec) * np.exp(-r_squared / (2 * sigma**2)) # gaussian function
    return image

def cut_fibre_hole(light, centre_hole_x = c.CAMERA_XRES/2, centre_hole_y = c.CAMERA_YRES/2, radius=c.FIBER_DEFAULT_RADIUS_PX):
    """Return a copy of the light with everything inside the fibre hole removed.
    
    parameters:
    - light: 2D numpy array representing the light intensity.
    - centre_hole_x, centre_hole_y: The center of the fibre hole in pixel coordinates.
    - radius: The radius of the fibre hole in pixels (default is FIBER_DEFAULT_RADIUS_PX).
    returns:
    - A 2D numpy array representing the light with the fibre hole removed.
    """
    y, x = np.indices(light.shape) # create a grid of pixel coordinates (first row index, second column index)
    r_squared = (x - centre_hole_x) ** 2 + (y - centre_hole_y) ** 2 # squared distance from the center of the hole
    r = np.sqrt(r_squared) # distance from the centre of the hole
    coverage = np.clip(radius + 0.5 - r, 0, 1) # fraction of each pixel inside the hole (1 inside, 0 outside, ramp at the edge)
    light_with_hole = light * (1 - coverage) # keep only the fraction of light outside the hole
    return light_with_hole

def camera_readout(light):
    """Turn light into what the camera records: capped at 4095, rounded to whole numbers."""
    light = np.minimum(light, c.CAMERA_MAX_PIXEL_VALUE)
    counts = np.round(light).astype(np.uint16)
    return counts

