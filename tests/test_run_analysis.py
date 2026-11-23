"""End-to-end test: run the analysis script exactly as a user would."""

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "scripts" / "run_analysis.py"
CONFIG = PROJECT_ROOT / "configs" / "default.toml"


def run_script(output_dir):
    env = {**os.environ, "MY_PROJECT_OUTPUT_DIR": str(output_dir)}
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--config", str(CONFIG)],
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    (run_dir,) = output_dir.iterdir()
    return run_dir


def test_run_writes_results_and_provenance(tmp_path):
    run_dir = run_script(tmp_path)

    expected = {
        "signal.csv",
        "summary.json",
        "config.toml",
        "run.log",
        "run_metadata.json",
    }
    assert expected <= {p.name for p in run_dir.iterdir()}
    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    assert set(summary) == {"position", "height"}


def test_same_config_gives_identical_results(tmp_path):
    first = run_script(tmp_path / "a")
    second = run_script(tmp_path / "b")
    assert (first / "signal.csv").read_bytes() == (second / "signal.csv").read_bytes()
