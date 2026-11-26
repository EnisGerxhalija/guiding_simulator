from guiding_simulator.simulate import make_gaussian_star, cut_fibre_hole, camera_readout
import matplotlib.pyplot as plt
from pathlib import Path

from guiding_simulator import constants as c
from guiding_simulator import save_figs as sf
# choose a star position and FWHM

x0, y0 = 640, 512  # center of the camera sensor
fwhm_arcsec = 1.2  # FWHM in arcseconds

light = make_gaussian_star(x0, y0, fwhm_arcsec)
light_with_hole = cut_fibre_hole(light)
# Simulate the camera readout process
image = camera_readout(light_with_hole)

# left: entire camera image, with the region of interest marked
plt.imshow(image, origin="lower", cmap="gray")
# --- save figure to outputs/figures -----------------------------------------------------------------------------
sf.save_figure(plt.gcf(), f"simulated_camera_frame_fwhm{fwhm_arcsec:.1f}arcsec.png")
plt.show()
