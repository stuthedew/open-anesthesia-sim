"""Tests for per-project settings."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

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


def test_version_policy_defaults_to_inferring(tmp_path: Path) -> None:
    assert load(tmp_path).version_policy == "infer"


def test_a_project_can_require_the_version_to_be_named(tmp_path: Path) -> None:
    """Some projects version by capability crossed, which no class label carries."""
    (tmp_path / "docket.toml").write_text('[docket]\nversion_policy = "manual"\n', encoding="utf-8")

    assert load(tmp_path).version_policy == "manual"


def test_protected_paths_are_read_from_the_config(tmp_path: Path) -> None:
    (tmp_path / "docket.toml").write_text(
        '[docket]\nprotected_paths = ["src/core", "docs/MODEL.md"]\n', encoding="utf-8"
    )
    assert load(tmp_path).protected_paths == ("src/core", "docs/MODEL.md")


def test_protected_paths_default_to_empty_which_disables_delegation(tmp_path: Path) -> None:
    """Fail closed: a project that never configured the partition gets no lane."""
    assert load(tmp_path).protected_paths == ()


def test_the_verify_cutover_reads_a_toml_date_literal(tmp_path: Path) -> None:
    (tmp_path / "docket.toml").write_text(
        "[docket]\nverify_required_from = 2026-08-30\n", encoding="utf-8"
    )
    assert load(tmp_path).verify_required_from == date(2026, 8, 30)


def test_the_verify_cutover_reads_a_quoted_date(tmp_path: Path) -> None:
    """Both spellings are natural to write and the difference is invisible."""
    (tmp_path / "docket.toml").write_text(
        '[docket]\nverify_required_from = "2026-08-30"\n', encoding="utf-8"
    )
    assert load(tmp_path).verify_required_from == date(2026, 8, 30)


def test_a_malformed_verify_cutover_is_rejected_rather_than_ignored(tmp_path: Path) -> None:
    """A cutover silently dropped leaves the rule off in a project that turned it on."""
    (tmp_path / "docket.toml").write_text(
        "[docket]\nverify_required_from = 20260830\n", encoding="utf-8"
    )
    with pytest.raises(ValueError):
        load(tmp_path)


def test_the_verify_requirement_is_off_until_a_project_adopts_it(tmp_path: Path) -> None:
    assert load(tmp_path).verify_required_from is None
