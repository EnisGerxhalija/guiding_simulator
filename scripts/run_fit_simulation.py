from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from guiding_simulator import constants as c
from guiding_simulator.simulate import simulate_star_with_fibre_hole
from guiding_simulator.fit_gaussian import fit_clipped_gaussian


# --- simulation settings for star perfectly on centre of fibre -------------------------------------------------
x0, y0 = c.CAMERA_XRES/2, c.CAMERA_YRES/2  # center of the camera sensor
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

# --- plot fitted FWHM and centroid offset vs true FWHM ---------------------------------------------------------
true_fwhm = np.array([r["true_fwhm_arcsec"] for r in results])
fit_fwhm = np.array([r["fwhm_arcsec"] for r in results])
offset = np.array([r["offset_arcsec"] for r in results])

fig, ax = plt.subplots(1, 1, figsize=(10, 4))
ax.plot(true_fwhm, fit_fwhm, "o-", label="fitted")
ax.plot(true_fwhm, true_fwhm, "k--", label="1:1")
ax.set_xlabel("True FWHM (arcsec)")
ax.set_ylabel("Fitted FWHM (arcsec)")
ax.set_title("Fitted FWHM vs True FWHM for Star Perfectly on Centre of Fibre Hole, no noise")
ax.legend()
fig.tight_layout()

# --- save figure to outputs/figures -----------------------------------------------------------------------------
fig_dir = Path(__file__).resolve().parents[1] / "outputs" / "figures"
fig_dir.mkdir(parents=True, exist_ok=True)
fig_path = fig_dir / "fit_vs_fwhm_no_noise.png"
fig.savefig(fig_path, dpi=200)
print(f"Saved figure to {fig_path}")

plt.show()
