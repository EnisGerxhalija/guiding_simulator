from guiding_simulator.simulate import make_gaussian_star, cut_fibre_hole, camera_readout
import matplotlib.pyplot as plt

# choose a star position and FWHM

x0, y0 = 640, 512  # center of the camera sensor
fwhm_arcsec = 1.2  # FWHM in arcseconds

light = make_gaussian_star(x0, y0, fwhm_arcsec)
light_with_hole = cut_fibre_hole(light)
# Simulate the camera readout process
image = camera_readout(light_with_hole)

# Show only the region of interest around the fibre hole
from guiding_simulator import constants as c

roi = int(c.DEFAULT_SEARCH_RADIUS_PX)
cx, cy = c.CAMERA_XRES // 2, c.CAMERA_YRES // 2
x_lo, x_hi, y_lo, y_hi = cx - roi, cx + roi + 1, cy - roi, cy + roi + 1

fig, ax = plt.subplots()
im = ax.imshow(image[y_lo:y_hi, x_lo:x_hi], origin="lower", cmap="gray",
               extent=(x_lo - 0.5, x_hi - 0.5, y_lo - 0.5, y_hi - 0.5))
ax.add_patch(plt.Circle((cx, cy), c.FIBER_DEFAULT_RADIUS_PX, fill=False, color="red", lw=1))
ax.set_xlabel("x (px)")
ax.set_ylabel("y (px)")
fig.colorbar(im, ax=ax)
plt.show()
