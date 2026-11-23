# Getting started

## Install

You need Python 3.11 or newer (`python3 --version`).

```bash
git clone https://github.com/your-github-username/my-project.git
cd my-project
python3 -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

`-e` makes an *editable* install: changes to `src/` take effect without
reinstalling. Reinstall only after changing `pyproject.toml`.

## Run the analysis

```bash
python scripts/run_analysis.py --config configs/default.toml
```

Each run creates a new folder in `outputs/`, named after the time and the
run's `name`:

```text
outputs/20261118T130405Z_default/
├── config.toml          # exact copy of the config used
├── run.log              # everything that was logged
├── run_metadata.json    # git commit, versions, platform, ...
├── signal.csv           # results
└── summary.json
```

Running the same config again gives identical results, because all randomness
comes from the config's `seed`.

## Use it from Python

```python
from my_project.example import gaussian

gaussian([0.0, 1.0], amplitude=2.0, centre=0.0, sigma=1.0)
# array([2.        , 1.21306132])
```
