"""Run the example analysis from a config file.

Usage::

    python scripts/run_analysis.py                          # configs/default.toml
    python scripts/run_analysis.py --config configs/my_run.toml

Scripts like this one stay thin: they read the configuration, call functions
from the ``my_project`` package, and save the results. All real logic lives in
the package, where it can be tested and reused from notebooks.

Each run writes a new folder ``<output_dir>/<timestamp>_<name>/`` containing
the results, a copy of the config, the log and ``run_metadata.json``.
"""

import argparse
import json
import logging
import shutil
from dataclasses import asdict
from pathlib import Path

import numpy as np

from my_project.config import load_run_config, load_settings
from my_project.example import sampled_maximum, simulate_peak
from my_project.logging_utils import setup_logging
from my_project.provenance import create_run_dir, write_metadata

logger = logging.getLogger("run_analysis")


def main(argv: list[str] | None = None) -> int:
    """Run the analysis; return the process exit code."""
    settings = load_settings()

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--config",
        type=Path,
        default=settings.config_dir / "default.toml",
        help="run config (TOML); default: %(default)s",
    )
    args = parser.parse_args(argv)

    config = load_run_config(args.config)
    run_dir = create_run_dir(settings.output_dir, config.name)
    setup_logging(settings.log_level, log_file=run_dir / "run.log")
    logger.info("Run %r -> %s", config.name, run_dir)

    # Provenance first, so even a failed run records what was attempted.
    shutil.copy2(args.config, run_dir / "config.toml")
    write_metadata(run_dir, config=config, config_file=str(args.config))

    # --- the analysis (EXAMPLE: replace with your own) ----------------------
    rng = np.random.default_rng(config.seed)
    p = config.example
    x = np.linspace(p.x_start, p.x_stop, p.n_points)
    y = simulate_peak(
        x,
        amplitude=p.amplitude,
        centre=p.centre,
        sigma=p.sigma,
        noise_std=p.noise_std,
        rng=rng,
    )
    peak = sampled_maximum(x, y)

    # --- save results ------------------------------------------------------
    np.savetxt(
        run_dir / "signal.csv",
        np.column_stack([x, y]),
        delimiter=",",
        header="x,y",
        comments="",
    )
    (run_dir / "summary.json").write_text(
        json.dumps(asdict(peak), indent=2) + "\n", encoding="utf-8"
    )
    logger.info("Largest sample at x = %.4g (height %.4g)", peak.position, peak.height)
    logger.info("Done. Results in %s", run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
