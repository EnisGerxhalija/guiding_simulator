# Python project template

A base for new Python projects, built from the Frontiers Core Foundations
practices. It gives every project the same skeleton (src/ layout, tests,
config, docs, CI, git hooks) and leaves the science to you.

This file is about the template itself; `scripts/init_project.py` deletes it
when you create a project. Everything in `README.md` is written for the new
project and gets your names filled in.

## Start a new project

### One-off: put the template on GitHub

```bash
cd python-project-template
git init -b main
git add -A
git commit -m "Python project template"
# create an empty repo called python-project-template on GitHub, then:
git remote add origin https://github.com/<you>/python-project-template.git
git push -u origin main
```

On GitHub open **Settings** and tick **Template repository**.

### Every new project

1. On the template's GitHub page click **Use this template → Create a new
   repository** (this gives the new repo a clean history). Then clone it:

   ```bash
   git clone https://github.com/<you>/<new-project>.git
   cd <new-project>
   ```

   *(Without GitHub: `git clone <template> <new-project>`, then
   `rm -rf .git && git init -b main` inside it for a fresh history.)*

2. Fill in the names. The script asks for the project name, author, email and
   GitHub user, suggesting defaults from the folder name and your git config:

   ```bash
   python3 scripts/init_project.py
   ```

   Non-interactive form:

   ```bash
   python3 scripts/init_project.py --yes --name "Spin Qubit Analysis" \
       --author "Ada Lovelace" --email ada@cam.ac.uk --github ada-lab
   ```

3. Set up and check that everything passes:

   ```bash
   make setup        # needs Python >= 3.11; e.g. make setup PYTHON=python3.13
   make format       # re-wrap lines that the new names made too long
   make check        # lint + tests + docs
   git add -A && git commit -m "Initialise project from template"
   git push
   ```

4. Replace the example code with yours (see below) and edit `README.md`.

## What's inside, and why

| Piece | Why | Course |
|---|---|---|
| `src/` layout, `pyproject.toml` (setuptools), editable install | Imports work the same everywhere and only because the package is installed, not because you happen to be in the repo folder. | Week 2 |
| `.venv`, `.gitignore`, `.env` / `.env.example` | One isolated environment per project; secrets and generated files stay out of git. | Week 2 |
| Package code vs thin `scripts/` | Reusable, testable functions in the package; scripts only wire config to functions and save results. | Week 2 |
| Pydantic `Settings` + `RunConfig` | Paths and secrets from `.env`; analysis parameters from committed TOML files; typos and impossible values fail immediately. | Week 5 |
| Seeded RNG, run folders, `run_metadata.json` | Same config gives the same numbers; every result records config, git commit and versions. | Weeks 2, 4, 5 |
| Tests with known-answer synthetic data, doctests | Checks correctness and edge cases (NaNs, reversed axes), and that docstring examples are true. | Weeks 2, 3 |
| NumPy docstrings, README, MkDocs site, CHANGELOG, CITATION.cff | Units and assumptions documented where people look; API reference generated from docstrings. | Week 3 |
| `make build` + CI test-install of the wheel outside the repo | Proves the package installs and imports on a clean machine. | Week 3 |
| Pull request template | Every change says what changed, why, and how it was checked. | Week 3 |
| `Makefile` | One command per task; `make check` = what CI runs. (Make is itself a small DAG runner.) | Week 4 |
| pre-commit (ruff, nbstripout, secret checks) + GitHub Actions + Dependabot | The automation layer: checks run on every commit and pull request without you remembering to. | Beyond the course |

## Make it yours

**Replace the example.** Delete `src/my_project/example.py` and
`tests/test_example.py`; remove `ExampleParams` and the `example` field from
`config.py` and the `[example]` table from `configs/default.toml`; rewrite the
analysis section of `scripts/run_analysis.py`; drop
`::: my_project.example` from `docs/reference.md`. If nothing else uses NumPy,
remove it from `dependencies`.

**Remove what you don't need.**

- *No docs site:* delete `docs/`, `mkdocs.yml`, `.github/workflows/docs.yml`,
  the `docs` extra in `pyproject.toml`, the `docs` job in `ci.yml`, and
  `docs-build` from `make check`.
- *No notebooks:* delete `notebooks/`, the `nbstripout` hook, the `notebook`
  extra and `make kernel`.
- *No research data:* delete `data/`, `outputs/` and their `.gitignore` rules.

**Grow it.**

- New modules go in `src/my_project/`. Avoid names that shadow the standard
  library (`io`, `logging`, `random`, ...).
- A command-line tool: add `[project.scripts] my-project = "my_project.cli:main"`
  to `pyproject.toml`.
- Multi-stage pipelines: one function per stage in the package, chained by a
  script, a Makefile, or a DAG runner such as the course's `frontiers_dag`.
- Type checking: add `mypy` to the `dev` extra and a hook in
  `.pre-commit-config.yaml`.
- Conda instead of venv (compiled dependencies): add an `environment.yml`
  and run `pip install -e ".[dev]"` inside the conda env.

## Tooling notes (November 2026)

- `requires-python = ">=3.11"`: Python 3.10 reached end of life in October
  2026, and several dependencies (pydantic-settings, pre-commit,
  mkdocs-material) now need 3.11. CI tests 3.11 to 3.15. The macOS system
  `python3` is 3.9, so install a newer Python (python.org, Homebrew or
  `uv python install`).
- Docs use MkDocs 1.x, pinned `<2` because MkDocs 2.0 drops the plugin system
  that Material and mkdocstrings rely on. Material for MkDocs gets only
  critical fixes until its end of life on 5 May 2027 (each build prints a
  reminder; set `NO_MKDOCS_2_WARNING=1` to hide it). Its successor, Zensical,
  is made by the same team and reads the same `mkdocs.yml`, so plan to
  switch before then: <https://zensical.org/docs/compatibility/mkdocs/migration/>
- Hook versions in `.pre-commit-config.yaml` are pinned; run
  `make update-hooks` now and then. Dependabot updates the GitHub Actions.

## Updating the template

Improve the template repo itself, then copy the changes you want into
existing projects by hand. Projects don't track the template automatically.
