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


def test_workflow_paths_are_read_from_the_config(tmp_path: Path) -> None:
    (tmp_path / "docket.toml").write_text(
        '[docket]\nworkflow_paths = ["tools", ".claude"]\n', encoding="utf-8"
    )
    assert load(tmp_path).workflow_paths == ("tools", ".claude")


def test_workflow_paths_default_to_empty_which_disables_the_lanes(tmp_path: Path) -> None:
    """Fail closed: a lane that quietly answers from the whole queue is the bug."""
    assert load(tmp_path).workflow_paths == ()


def test_the_command_shape_rule_reads_its_cutover_and_its_trees(tmp_path: Path) -> None:
    """Both halves are needed before the rule refuses anything, so both are read.

    A cutover with no trees leaves it off rather than guessing which of a
    project's pytest runs its own check command already performs.
    """
    (tmp_path / "docket.toml").write_text(
        "[docket]\n"
        "verify_prerequisite_refused_from = 2026-09-20\n"
        'collected_test_paths = ["tests", "subprojects/docket/tests"]\n',
        encoding="utf-8",
    )
    config = load(tmp_path)

    assert config.verify_prerequisite_refused_from == date(2026, 9, 20)
    assert config.collected_test_paths == ("tests", "subprojects/docket/tests")


def test_the_command_shape_rule_is_off_until_a_project_adopts_it(tmp_path: Path) -> None:
    assert load(tmp_path).verify_prerequisite_refused_from is None
    assert load(tmp_path).collected_test_paths == ()


def test_the_k_selector_rule_reads_its_own_cutover(tmp_path: Path) -> None:
    """A date of its own rather than the prerequisite rule's, because the two close
    different sets: `PL-W4XQ` was captured on the prerequisite rule's first day
    carrying a `-k`, so sharing that date would refuse it the moment this landed."""
    (tmp_path / "docket.toml").write_text(
        "[docket]\nverify_k_selector_refused_from = 2026-09-23\n", encoding="utf-8"
    )

    assert load(tmp_path).verify_k_selector_refused_from == date(2026, 9, 23)
    assert Config().verify_k_selector_refused_from is None


def test_the_instruction_staleness_threshold_defaults_to_ninety(tmp_path: Path) -> None:
    """90 rather than 180, and the number is the decision (`PL-PHK4`).

    A threshold that first fires in about five months is a mechanism nobody
    can test until it matters; one that first fires in about ten weeks is
    validated by its own first firing, while the assertions it names are
    recent enough to be judged quickly. Pinned here so a later tidy-up back to
    a rounder number has to argue with this test.
    """
    assert load(tmp_path).instruction_stale_days == 90


def test_the_instruction_audit_is_off_until_a_project_names_its_files(tmp_path: Path) -> None:
    """Nothing in this package knows which files instruct a session."""
    assert load(tmp_path).instruction_paths == ()


def test_the_instruction_audit_settings_are_read_from_the_config(tmp_path: Path) -> None:
    (tmp_path / "docket.toml").write_text(
        "[docket]\n"
        "instruction_stale_days = 45\n"
        'instruction_paths = ["CLAUDE.md", ".claude/rules"]\n',
        encoding="utf-8",
    )
    config = load(tmp_path)

    assert config.instruction_stale_days == 45
    assert config.instruction_paths == ("CLAUDE.md", ".claude/rules")
