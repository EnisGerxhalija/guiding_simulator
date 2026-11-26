from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from guiding_simulator import constants as c
from guiding_simulator.simulate import make_gaussian_star, cut_fibre_hole, camera_readout, simulate_noisy_image
from guiding_simulator.fit_gaussian import fit_clipped_gaussian


# --- simulation settings ----------------------------------------------------------------------------------------
offsets_px = [0.0, 1.0]                          # star offset from fibre centre along x (pixels): centred, 1 px
fwhm_arcsecs = np.linspace(0.6, 1.2, 13)         # true star FWHMs in arcseconds
noise_fracs = [0.0, 0.01, 0.05, 0.10, 0.2]      # background noise sigma as a fraction of the observed star peak


# --- run the simulations (one noisy image per point) ------------------------------------------------------------
# results[offset][noise_frac] = {"fwhm": array, "dx": array} indexed by FWHM (nan where the fit failed)
results = {}
for offset_px in offsets_px:
    x0, y0 = c.CAMERA_XRES/2 + offset_px, c.CAMERA_YRES/2
    results[offset_px] = {}
    for noise_frac in noise_fracs:
        fit_fwhm, fit_dx = [], []
        for fwhm_arcsec in fwhm_arcsecs:
            image = simulate_noisy_image(x0, y0, fwhm_arcsec, noise_frac)
            try:
                fit = fit_clipped_gaussian(image)
                fit_fwhm.append(fit["fwhm_arcsec"])
                fit_dx.append(fit["dx_arcsec"] / c.ARCSEC_PER_PX)
            except RuntimeError:                # curve_fit failed to converge
                fit_fwhm.append(np.nan)
                fit_dx.append(np.nan)
        results[offset_px][noise_frac] = {"fwhm": np.array(fit_fwhm), "dx": np.array(fit_dx)}

# --- plot: one row per offset; left = fitted FWHM, right = recovered dx -----------------------------------------
fig, axes = plt.subplots(len(offsets_px), 2, figsize=(12, 4 * len(offsets_px)), squeeze=False)
for row, offset_px in enumerate(offsets_px):
    ax_fwhm, ax_dx = axes[row]
    for noise_frac in noise_fracs:
        r = results[offset_px][noise_frac]
        label = f"noise {noise_frac:.0%} of peak"
        ax_fwhm.plot(fwhm_arcsecs, r["fwhm"], "o-", ms=3, label=label)
        ax_dx.plot(fwhm_arcsecs, r["dx"], "o-", ms=3, label=label)
    ax_fwhm.plot(fwhm_arcsecs, fwhm_arcsecs, "k--", label="1:1")
    ax_fwhm.set_xlabel("True FWHM (arcsec)")
    ax_fwhm.set_ylabel("Fitted FWHM (arcsec)")
    ax_fwhm.set_title(f"Fitted vs true FWHM, star offset {offset_px:g} px")
    ax_fwhm.legend(fontsize=8)

    ax_dx.axhline(offset_px, color="k", ls="--", label=f"true dx = {offset_px:g} px")
    ax_dx.set_xlabel("True FWHM (arcsec)")
    ax_dx.set_ylabel("Fitted dx (px)")
    ax_dx.set_title(f"Recovered offset, star offset {offset_px:g} px")
    ax_dx.legend(fontsize=8)

fig.suptitle("Effect of white camera noise on the fit")
fig.tight_layout()

# --- save figure to outputs/figures -----------------------------------------------------------------------------
fig_dir = Path(__file__).resolve().parents[1] / "outputs" / "figures"
fig_dir.mkdir(parents=True, exist_ok=True)
fig_path = fig_dir / "fit_vs_fwhm_with_noise.png"
fig.savefig(fig_path, dpi=200)
print(f"Saved figure to {fig_path}")

plt.show()
