# Data

| Folder | What goes here | In git? |
|---|---|---|
| `raw/` | Data exactly as it came from the instrument, simulation or collaborator. **Treat as read-only**: never edit or overwrite these files. | No (ignored) |
| `processed/` | Cleaned or converted data written by code in this repository. Can always be regenerated from `raw/`. | No (ignored) |

Large datasets can live elsewhere (a shared drive, OneDrive, HPC scratch). Set
`GUIDING_SIMULATOR_DATA_DIR` in `.env` to the folder that contains `raw/` and
`processed/`; the code reads it through `settings.raw_dir` and
`settings.processed_dir`.

To track a small file in git anyway (e.g. a reference dataset used by tests),
remove the matching rule from `.gitignore`, or put it in `tests/data/`.

## Data sources

Record every dataset here so someone new can find and interpret it.

| Dataset | Source and date | Format and units | Notes |
|---|---|---|---|
| *e.g.* `raw/sweep_01.csv` | *Fridge 2, 2026-11-18* | *CSV: gate voltage (mV), current (nA)* | *firmware v2.1; positive current = ...* |
