"""Tests for run folders and metadata."""

import json

from my_project import __version__
from my_project.config import RunConfig
from my_project.provenance import create_run_dir, git_info, write_metadata


def test_run_dirs_are_never_reused(tmp_path):
    first = create_run_dir(tmp_path, "demo")
    second = create_run_dir(tmp_path, "demo")
    assert first != second
    assert first.is_dir()
    assert second.is_dir()


def test_metadata_records_config_and_versions(tmp_path):
    config = RunConfig(name="demo", seed=3)
    path = write_metadata(tmp_path, config=config, note="hello")

    meta = json.loads(path.read_text(encoding="utf-8"))
    assert RunConfig.model_validate(meta["config"]) == config
    assert meta["package"]["version"] == __version__
    assert meta["note"] == "hello"
    assert "pydantic" in {name.lower() for name in meta["dependencies"]}
    assert set(meta["git"]) == {"commit", "branch", "dirty"}


def test_git_info_outside_a_repository_is_empty(tmp_path):
    assert git_info(tmp_path)["commit"] is None
