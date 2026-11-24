# Guiding Simulator

Analysis and simulation code for tip/tilt guiding simulator

## Set up (once)

Needs Python 3.11 or newer (check with `python3 --version`).

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

`-e` means "editable": changes you make in `src/` work straight away,
without installing again. Run `source .venv/bin/activate` each time you open
a new terminal.

## Run the tests

```bash
python -m pytest
```

## Folders

```text
guiding_simulator/
├── src/guiding_simulator/   # your code; import it with  import guiding_simulator
├── tests/                   # tests, run with pytest
├── notebooks/               # exploring and plotting; import your code from src/
├── data/raw/                # original input files (not in git)
├── data/processed/          # files your code makes (not in git)
├── outputs/                 # results and figures (not in git)
├── pyproject.toml           # project name, Python version, libraries
├── LICENSE                  # MIT: others may reuse the code with credit
└── README.md
```

## The removed template parts

This is a simplified version of the original project template. The parts
taken out for now (settings and config files, run records, logging, docs,
scripts, changelog, citation file) are saved in git commit `4eb7792`. To get
one back, for example the docs folder:

```bash
git restore --source=4eb7792 -- docs/
```

## License

[MIT](LICENSE)
