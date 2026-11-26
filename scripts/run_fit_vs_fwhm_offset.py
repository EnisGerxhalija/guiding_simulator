from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from guiding_simulator import constants as c
from guiding_simulator.simulate import simulate_star_with_fibre_hole
from guiding_simulator.fit_gaussian import fit_clipped_gaussian
from guiding_simulator import save_figs as sf

# --- simulation settings for star offset from centre of fibre ---------------------------------------------------
offset_px = 1.0  # offset of the star from the fibre centre, in pixels (along x)
x0, y0 = c.CAMERA_XRES/2 + offset_px, c.CAMERA_YRES/2
fwhm_arcsecs = np.linspace(0.6, 1.2, 20)  # true star FWHMs in arcseconds

# --- run the simulation + fit for each FWHM ---------------------------------------------------------------------
results = []
for fwhm_arcsec in fwhm_arcsecs:
    image = simulate_star_with_fibre_hole(x0=x0, y0=y0, fwhm_arcsec=fwhm_arcsec)
    try:
        fit = fit_clipped_gaussian(image)
    except RuntimeError as err:  # curve_fit failed to converge
        print(f"FWHM {fwhm_arcsec:.2f}\" : fit failed ({err})")
        continue
    fit["true_fwhm_arcsec"] = fwhm_arcsec
    results.append(fit)

# --- plot fitted FWHM and recovered offset vs true FWHM ---------------------------------------------------------
true_fwhm = np.array([r["true_fwhm_arcsec"] for r in results])
fit_fwhm = np.array([r["fwhm_arcsec"] for r in results])
dx_px = np.array([r["dx_arcsec"] for r in results]) / c.ARCSEC_PER_PX
dy_px = np.array([r["dy_arcsec"] for r in results]) / c.ARCSEC_PER_PX

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
ax1.plot(true_fwhm, fit_fwhm, "o-", label="fitted")
ax1.plot(true_fwhm, true_fwhm, "k--", label="1:1")
ax1.set_xlabel("True FWHM (arcsec)")
ax1.set_ylabel("Fitted FWHM (arcsec)")
ax1.set_title("Fitted vs true FWHM")
ax1.legend()

ax2.plot(true_fwhm, dx_px, "o-", label="fitted dx")
ax2.plot(true_fwhm, dy_px, "s-", label="fitted dy")
ax2.axhline(offset_px, color="k", ls="--", label=f"true dx = {offset_px:g} px")
ax2.axhline(0, color="grey", ls=":", label="true dy = 0 px")
ax2.set_xlabel("True FWHM (arcsec)")
ax2.set_ylabel("Fitted offset (px)")
ax2.set_title("Recovered star offset")
ax2.legend()

fig.suptitle(f"Star offset {offset_px:g} px from centre of fibre hole, no noise")
fig.tight_layout()

# --- save figure to outputs/figures -----------------------------------------------------------------------------
sf.save_figure(fig, f"fit_vs_fwhm_offset_{offset_px:g}px_no_noise.png")
plt.show()
