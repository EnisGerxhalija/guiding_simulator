from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# --- save figure to outputs/figures -----------------------------------------------------------------------------

def save_figure(fig, filename):
    fig_dir = Path(__file__).resolve().parents[2] / "outputs" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig_path = fig_dir / filename
    fig.savefig(fig_path, dpi=200)
    print(f"Saved figure to {fig_path}")