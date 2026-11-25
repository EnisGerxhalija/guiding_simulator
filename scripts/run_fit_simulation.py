import numpy as np

from guiding_simulator import constants as c
from guiding_simulator.simulate import make_gaussian_star, cut_fibre_hole, camera_readout
from guiding_simulator.fit_gaussian import fit_clipped_gaussian


# --- simulation settings -------------------------------------------------
x0, y0 = c.CAMERA_XRES/2, c.CAMERA_YRES/2  # center of the camera sensor
fwhm_arcsec = 0.6

light = make_gaussian_star(x0, y0, fwhm_arcsec)
light_with_hole = cut_fibre_hole(light)
# Simulate the camera readout process
image = camera_readout(light_with_hole)

fitted_params = fit_clipped_gaussian(image)
print(fitted_params)
