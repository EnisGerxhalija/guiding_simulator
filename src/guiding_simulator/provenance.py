"""Record how each set of results was produced.

Every run gets its own timestamped folder, so results are never overwritten,
and a ``run_metadata.json`` holding what you need to reproduce them: the
config, the git commit (and whether there were uncommitted changes), the
Python and package versions, and every installed dependency.
"""

import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from guiding_simulator import __version__

METADATA_FILENAME = "run_metadata.json"


def create_run_dir(output_root: str | Path, name: str) -> Path:
    """Create a new, empty folder for one run's outputs.

    Parameters
    ----------
    output_root : str or pathlib.Path
        Parent folder, e.g. ``settings.output_dir``. Created if needed.
    name : str
        Short run label, appended to the timestamp.

    Returns
    -------
    pathlib.Path
        A folder like ``<output_root>/20261118T130405Z_default``. If that
        already exists, ``_2``, ``_3``, ... is appended; existing folders are
        never reused.
    """
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    base = Path(output_root) / f"{stamp}_{name}"
    run_dir, n = base, 1
    while True:
        try:
            run_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            n += 1
            run_dir = base.with_name(f"{base.name}_{n}")
        else:
            return run_dir


def git_info(repo_dir: str | Path | None = None) -> dict[str, Any]:
    """Describe the git state of the code.

    Parameters
    ----------
    repo_dir : str or pathlib.Path, optional
        Any folder inside the repository. Defaults to the folder containing
        this package's source, i.e. the code that is actually running.

    Returns
    -------
    dict
        ``commit`` (hash), ``branch`` and ``dirty`` (True if there are
        uncommitted changes). All are None if git or the repository is not
        available, e.g. when the package was installed from a wheel.
    """
    cwd = Path(repo_dir) if repo_dir is not None else Path(__file__).resolve().parent

    def _git(*args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        return result.stdout.strip()

    try:
        return {
            "commit": _git("rev-parse", "HEAD"),
            "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": bool(_git("status", "--porcelain")),
        }
    except (OSError, subprocess.SubprocessError):
        return {"commit": None, "branch": None, "dirty": None}


def collect_metadata(
    config: BaseModel | dict[str, Any] | None = None, **extra: Any
) -> dict[str, Any]:
    """Gather everything needed to reproduce a run.

    Parameters
    ----------
    config : pydantic.BaseModel or dict, optional
        The run configuration.
    **extra
        Anything else worth recording, e.g. ``input_files=[...]``. Values must
        be JSON-serialisable (or convertible with ``str``).

    Returns
    -------
    dict
        JSON-serialisable metadata.
    """
    if isinstance(config, BaseModel):
        config = config.model_dump(mode="json")
    dependencies = {
        dist.metadata["Name"]: dist.version
        for dist in metadata.distributions()
        if dist.metadata["Name"]
    }
    return {
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "package": {"name": "guiding-simulator", "version": __version__},
        "command": sys.argv,
        "git": git_info(),
        "python": sys.version,
        "platform": platform.platform(),
        "config": config,
        **extra,
        "dependencies": dict(
            sorted(dependencies.items(), key=lambda kv: kv[0].lower())
        ),
    }


def write_metadata(
    run_dir: str | Path, config: BaseModel | dict[str, Any] | None = None, **extra: Any
) -> Path:
    """Write :func:`collect_metadata` output to ``run_dir/run_metadata.json``.

    Parameters
    ----------
    run_dir : str or pathlib.Path
        The run's output folder.
    config : pydantic.BaseModel or dict, optional
        The run configuration.
    **extra
        Additional fields, passed to :func:`collect_metadata`.

    Returns
    -------
    pathlib.Path
        Path of the written file.
    """
    path = Path(run_dir) / METADATA_FILENAME
    text = json.dumps(collect_metadata(config, **extra), indent=2, default=str)
    path.write_text(text + "\n", encoding="utf-8")
    return path
