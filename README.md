# My Project

[![CI](https://github.com/your-github-username/my-project/actions/workflows/ci.yml/badge.svg)](https://github.com/your-github-username/my-project/actions/workflows/ci.yml)

A short description of the project.

<!-- Two or three sentences: what question does this code answer, what data
does it work on, and what does it produce? -->

## Installation

Requires Python 3.11 or newer.

```bash
git clone https://github.com/your-github-username/my-project.git
cd my-project
make setup
```

`make setup` creates a `.venv`, installs the package in editable mode with all
extras, and enables the git hooks. Without `make` (e.g. on Windows):

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,docs,notebook]"
pre-commit install
```

## Quick start

```bash
cp .env.example .env             # optional: paths and secrets for this machine
python scripts/run_analysis.py --config configs/default.toml
```

This creates `outputs/<timestamp>_default/` with the results, a copy of the
config, the log and `run_metadata.json` (git commit, package versions, ...).

From Python:

```python
from my_project.example import gaussian

gaussian([0.0, 1.0], amplitude=2.0, centre=0.0, sigma=1.0)
```

## Project layout

```text
my-project/
├── src/my_project/      # the package: all reusable code lives here
│   ├── config.py        #   Settings (.env) and RunConfig (configs/*.toml)
│   ├── provenance.py    #   run folders and run_metadata.json
│   ├── logging_utils.py #   setup_logging() for scripts and notebooks
│   └── example.py       #   example analysis; replace with your own
├── scripts/             # thin entry points that call the package
├── configs/             # run configs (committed)
├── tests/               # pytest tests
├── notebooks/           # exploration; import from the package
├── data/raw/            # original data, read-only (not in git)
├── data/processed/      # derived data, regenerable (not in git)
├── outputs/             # one folder per run (not in git)
├── docs/ + mkdocs.yml   # documentation site
├── pyproject.toml       # metadata, dependencies, tool settings
├── Makefile             # shortcuts: make help
└── .env.example         # template for your private .env
```

## Development

| Command | What it does |
|---|---|
| `make test` | run the tests |
| `make lint` | run all pre-commit checks (ruff, formatting, notebook stripping, ...) |
| `make format` | auto-format and fix lint issues |
| `make check` | lint + tests + docs build: what CI runs |
| `make docs` | preview the documentation at <http://127.0.0.1:8000> |
| `make build` | build the wheel and sdist into `dist/` |
| `make freeze` | pin exact versions to `requirements-lock.txt` |
| `make kernel` | make `.venv` available as a Jupyter kernel |

Workflow: branch from an up-to-date `main`, commit (the hooks check your
changes), push, open a pull request. CI must pass before merging.

```bash
git switch main && git pull --ff-only
git switch -c feature/short-description
```

## Reproducibility

- Every run records its config, git commit (and whether the working tree had
  uncommitted changes), Python and package versions in `run_metadata.json`.
- Randomness comes only from the `seed` in the run config.
- For results that go into a paper: commit, tag the commit
  (`git tag v0.1.0`), and run `make freeze` to record exact dependency versions.

## Citation

If you use this code, please cite it using [`CITATION.cff`](CITATION.cff).

## License

[MIT](LICENSE)
