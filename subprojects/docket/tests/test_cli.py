"""Tests for the command line, exercised end to end against a temporary store."""

from __future__ import annotations

from pathlib import Path

import pytest

from docket.cli import main

READY = """---
id: PL-B1B1
title: A ready item
priority: P1
effort: S
status: ready
classes: perf
touches: a.py
added: 2026-08-01
---

**Problem.** x
**Why it matters.** y
**Done when.** z
"""


def _store(tmp_path: Path, *documents: str) -> Path:
    items = tmp_path / "items"
    items.mkdir()
    for index, document in enumerate(documents):
        (items / f"item-{index}.md").write_text(document, encoding="utf-8")
    return items


def _run(*args: str) -> int:
    return main([*args, "--no-git", "--today", "2026-08-24"])


def test_new_captures_several_ideas_in_one_call(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Interruptions rarely carry exactly one thought."""
    store = _store(tmp_path)
    assert _run("new", "First idea", "Second idea", "--items", str(store)) == 0

    written = sorted(store.glob("*.md"))
    assert len(written) == 2
    assert len({p.name.split("-")[1] for p in written}) == 2


def test_a_captured_idea_needs_no_priority(tmp_path: Path) -> None:
    store = _store(tmp_path)
    _run("new", "Half an idea", "--items", str(store))

    assert _run("check", "--items", str(store)) == 0


def test_check_exits_nonzero_on_a_broken_store(tmp_path: Path) -> None:
    store = _store(tmp_path, READY, READY)

    assert _run("check", "--items", str(store)) == 1


def test_check_exits_zero_on_a_clean_store(tmp_path: Path) -> None:
    assert _run("check", "--items", str(_store(tmp_path, READY))) == 0


def test_digest_is_silent_on_an_empty_store(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Session start must never be noisy."""
    _run("digest", "--items", str(_store(tmp_path)))

    assert capsys.readouterr().out == ""


def test_next_explains_why(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _run("next", "--items", str(_store(tmp_path, READY)))
    out = capsys.readouterr().out

    assert "PL-B1B1" in out
    assert "Highest-priority work" in out


def test_concurrent_never_certifies_a_pair_as_safe(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`touches` is a prediction; the wording must not imply otherwise."""
    _run("concurrent", "--items", str(_store(tmp_path, READY)))
    out = capsys.readouterr().out

    assert "not a guarantee" in out


def test_show_reports_a_missing_item_rather_than_guessing(tmp_path: Path) -> None:
    assert _run("show", "PL-Z9Z9", "--items", str(_store(tmp_path, READY))) == 1


def test_release_refuses_an_unfinished_milestone(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Shipping a version whose work is not done is the failure worth preventing."""
    store = _store(tmp_path, READY.replace("status: ready", "status: ready\nmilestone: v0.3.0"))

    assert _run("release", "v0.3.0", "--items", str(store)) == 1
    assert "Nothing was changed." in capsys.readouterr().out


def test_release_is_a_dry_run_before_it_writes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    done = READY.replace(
        "status: ready", "status: done\nmilestone: v0.3.0\ncommit: abc1234\nclosed: 2026-08-24"
    )
    store = _store(tmp_path, done)

    assert _run("release", "v0.3.0", "--dry-run", "--items", str(store)) == 0
    assert "Would bump" in capsys.readouterr().out
