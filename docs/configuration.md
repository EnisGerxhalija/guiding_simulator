# Configuration

There are two kinds of configuration, kept apart on purpose.

| | Machine settings | Run config |
|---|---|---|
| Says | *where* things are; secrets | *what* the analysis does |
| Lives in | environment variables / `.env` | `configs/*.toml` |
| Committed to git? | **No** (`.env.example` holds placeholders) | **Yes** |
| Python class | `Settings` | `RunConfig` |

Both are validated with Pydantic, so mistakes fail early with a clear
message rather than producing wrong results.

## Machine settings (`.env`)

```bash
cp .env.example .env
```

| Variable | Default | Meaning |
|---|---|---|
| `GUIDING_SIMULATOR_DATA_DIR` | `data` | Folder containing `raw/` and `processed/` |
| `GUIDING_SIMULATOR_OUTPUT_DIR` | `outputs` | Where run folders are written |
| `GUIDING_SIMULATOR_LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING` or `ERROR` |
| `GUIDING_SIMULATOR_API_KEY` | unset | Example secret; hidden when printed |

Relative paths are relative to the project root. A variable set in your shell
overrides the value in `.env`.

```python
from guiding_simulator.config import load_settings

settings = load_settings()
settings.raw_dir  # absolute path, wherever you run from
```

To add a setting, add a field to `Settings` in `src/guiding_simulator/config.py`
and a placeholder line to `.env.example`.

## Run configs (`configs/*.toml`)

```toml
name = "default"
seed = 42

[example]
n_points = 201
sigma = 0.8
```

Copy `configs/default.toml` to make a variant and pass it with `--config`.
Unknown keys are errors, so a typo such as `sead = 1` is caught rather than
silently ignored.

To add a parameter, add a field to the relevant model in
`src/guiding_simulator/config.py`, with bounds and a description that states the
units:

```python
temperature_mK: float = Field(gt=0, description="Mixing-chamber temperature in mK.")
```
