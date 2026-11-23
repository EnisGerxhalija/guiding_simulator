"""Tests for settings and run configs."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from my_project.config import (
    RunConfig,
    Settings,
    find_project_root,
    load_run_config,
    load_settings,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# --- run configs -------------------------------------------------------------
@pytest.mark.parametrize(
    "path", sorted((PROJECT_ROOT / "configs").glob("*.toml")), ids=lambda p: p.name
)
def test_committed_configs_are_valid(path):
    load_run_config(path)


def write_toml(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "run.toml"
    path.write_text(text, encoding="utf-8")
    return path


def test_unknown_key_is_rejected(tmp_path):
    path = write_toml(tmp_path, 'name = "x"\nsead = 1\n')  # typo for "seed"
    with pytest.raises(ValidationError, match="sead"):
        load_run_config(path)


def test_error_mentions_the_file(tmp_path):
    path = write_toml(tmp_path, 'name = "x"\nseed = -1\n')
    with pytest.raises(ValidationError) as excinfo:
        load_run_config(path)
    assert str(path) in "".join(excinfo.value.__notes__)


def test_reversed_range_is_rejected():
    with pytest.raises(ValidationError, match="x_stop"):
        RunConfig.model_validate(
            {"name": "x", "example": {"x_start": 1.0, "x_stop": -1.0}}
        )


def test_config_is_read_only():
    config = RunConfig(name="x")
    with pytest.raises(ValidationError):
        config.seed = 3  # type: ignore[misc]


def test_config_round_trips_through_json():
    config = RunConfig(name="x", seed=5)
    assert RunConfig.model_validate_json(config.model_dump_json()) == config


# --- settings ----------------------------------------------------------------
def test_environment_variable_overrides_default(monkeypatch, tmp_path):
    monkeypatch.setenv("MY_PROJECT_LOG_LEVEL", "DEBUG")
    assert Settings(_env_file=None, project_root=tmp_path).log_level == "DEBUG"


def test_relative_paths_are_resolved_against_project_root(tmp_path):
    settings = Settings(_env_file=None, project_root=tmp_path, output_dir="results")
    assert settings.output_dir == tmp_path.resolve() / "results"
    assert settings.raw_dir == tmp_path.resolve() / "data" / "raw"


def test_load_settings_works_from_a_subfolder(monkeypatch, tmp_path):
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    (tmp_path / ".env").write_text("MY_PROJECT_OUTPUT_DIR=results\n", encoding="utf-8")
    (tmp_path / "notebooks").mkdir()
    monkeypatch.chdir(tmp_path / "notebooks")

    assert find_project_root() == tmp_path.resolve()
    settings = load_settings()
    assert settings.output_dir == tmp_path.resolve() / "results"


def test_secrets_are_hidden_when_printed(tmp_path):
    settings = Settings(_env_file=None, project_root=tmp_path, api_key="s3cret")
    assert "s3cret" not in repr(settings)
    assert settings.api_key is not None
    assert settings.api_key.get_secret_value() == "s3cret"
