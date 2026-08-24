"""Tests for per-project settings."""

from __future__ import annotations

from pathlib import Path

from docket.config import Config, load


def test_defaults_apply_without_a_config_file(tmp_path: Path) -> None:
    """A project should not need a config file to use this."""
    assert load(tmp_path) == Config()


def test_settings_override_the_defaults(tmp_path: Path) -> None:
    (tmp_path / "docket.toml").write_text(
        '[docket]\nitems_dir = "backlog"\ntop_band_limit = 3\nsafety_classes = ["critical"]\n',
        encoding="utf-8",
    )
    config = load(tmp_path)

    assert config.items_dir == "backlog"
    assert config.top_band_limit == 3
    assert config.safety_classes == ("critical",)
    assert config.process_classes == Config().process_classes
