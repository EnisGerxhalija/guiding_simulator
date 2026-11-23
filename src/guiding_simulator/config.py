"""Configuration: machine settings and validated run configs.

Two kinds of configuration live here, deliberately kept apart:

* :class:`Settings` says *where* things are on this machine (data and output
  folders) and holds any secrets. It is read from environment variables
  prefixed ``GUIDING_SIMULATOR_`` and from the project's ``.env`` file, which is
  never committed.
* :class:`RunConfig` says *what* an analysis run does (parameters, random
  seed). It is read from a TOML file in ``configs/``, which IS committed, so
  every result can be traced back to the exact parameters that produced it.

Both are Pydantic models, so a typo, a wrong type or an out-of-range value
fails immediately with a clear message instead of silently producing wrong
results later.
"""

import tomllib
from pathlib import Path
from typing import Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    ValidationError,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def find_project_root(start: Path | None = None) -> Path:
    """Find the project folder, so paths work from any subfolder.

    Parameters
    ----------
    start : pathlib.Path, optional
        Folder to start searching from. Defaults to the current working
        directory.

    Returns
    -------
    pathlib.Path
        The nearest folder at or above `start` that contains a
        ``pyproject.toml``, or `start` itself if there is none.
    """
    start = (start or Path.cwd()).resolve()
    for folder in (start, *start.parents):
        if (folder / "pyproject.toml").is_file():
            return folder
    return start


# ------------------------------------------------------------------ settings
class Settings(BaseSettings):
    """Machine-specific settings, read from the environment and ``.env``.

    Each field ``foo`` is read from the variable ``GUIDING_SIMULATOR_FOO``. A value
    in the real environment beats one in ``.env``, which beats the default.
    Relative paths are resolved against `project_root`, so the result is
    the same whether you run from the project root, ``notebooks/`` or
    ``scripts/``. Prefer :func:`load_settings` over calling this directly.
    """

    model_config = SettingsConfigDict(
        env_prefix="GUIDING_SIMULATOR_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    project_root: Path = Field(
        default_factory=find_project_root,
        description="Folder containing pyproject.toml; found automatically.",
    )
    data_dir: Path = Field(
        default=Path("data"),
        description="Data folder, containing raw/ and processed/.",
    )
    output_dir: Path = Field(
        default=Path("outputs"),
        description="Each run writes a new timestamped folder in here.",
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    api_key: SecretStr | None = Field(
        default=None,
        description=(
            "Example secret. SecretStr hides the value when printed or "
            "logged; read it with api_key.get_secret_value()."
        ),
    )

    @model_validator(mode="after")
    def _resolve_paths(self) -> Self:
        root = self.project_root.expanduser().resolve()
        self.project_root = root
        self.data_dir = (root / self.data_dir.expanduser()).resolve()
        self.output_dir = (root / self.output_dir.expanduser()).resolve()
        return self

    @property
    def raw_dir(self) -> Path:
        """Folder for raw data. Treat its contents as read-only."""
        return self.data_dir / "raw"

    @property
    def processed_dir(self) -> Path:
        """Folder for data produced by this project's code."""
        return self.data_dir / "processed"

    @property
    def config_dir(self) -> Path:
        """Folder holding the run configs (``configs/``)."""
        return self.project_root / "configs"


def load_settings(**overrides: object) -> Settings:
    """Load settings using the ``.env`` file in the project root.

    Parameters
    ----------
    **overrides
        Field values that take priority over the environment, e.g.
        ``load_settings(log_level="DEBUG")``.

    Returns
    -------
    Settings
        Validated settings with absolute paths.
    """
    root = find_project_root()
    return Settings(_env_file=root / ".env", project_root=root, **overrides)  # type: ignore[call-arg]


# --------------------------------------------------------------- run config
class _ConfigSection(BaseModel):
    """Base for config sections: unknown keys and later changes are errors."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class ExampleParams(_ConfigSection):
    """Parameters of the example analysis (``[example]`` in the TOML file).

    EXAMPLE: replace this class with the parameters of your own analysis.
    Put units in the field name or description.
    """

    n_points: int = Field(
        default=201, ge=3, le=10_000_000, description="Number of samples."
    )
    x_start: float = Field(default=-5.0, description="First x value.")
    x_stop: float = Field(
        default=5.0, description="Last x value, same units as x_start."
    )
    amplitude: float = Field(default=1.0, description="Peak height.")
    centre: float = Field(default=0.0, description="Peak position, same units as x.")
    sigma: float = Field(
        default=1.0, gt=0, description="Standard deviation (not FWHM), same units as x."
    )
    noise_std: float = Field(
        default=0.05, ge=0, description="Standard deviation of the added noise."
    )

    @model_validator(mode="after")
    def _check_range(self) -> Self:
        if self.x_stop <= self.x_start:
            raise ValueError(
                f"x_stop ({self.x_stop}) must be greater than x_start ({self.x_start})"
            )
        return self


class RunConfig(_ConfigSection):
    """Everything that defines one analysis run, loaded from ``configs/*.toml``."""

    name: str = Field(
        min_length=1,
        pattern=r"^[A-Za-z0-9_.-]+$",
        description="Short label for the run; used in the output folder name.",
    )
    seed: int = Field(
        default=0,
        ge=0,
        description="Seed for numpy.random.default_rng, for repeatable runs.",
    )
    example: ExampleParams = Field(default_factory=ExampleParams)


def load_run_config(path: str | Path) -> RunConfig:
    """Read and validate a run config from a TOML file.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to the TOML file, e.g. ``configs/default.toml``.

    Returns
    -------
    RunConfig
        The validated, read-only config.

    Raises
    ------
    FileNotFoundError
        If `path` does not exist.
    pydantic.ValidationError
        If a key is unknown, a value has the wrong type or is out of range.
    """
    path = Path(path)
    with path.open("rb") as fh:
        raw = tomllib.load(fh)
    try:
        return RunConfig.model_validate(raw)
    except ValidationError as exc:
        exc.add_note(f"(while loading the run config {path})")
        raise
