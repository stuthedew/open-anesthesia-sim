"""Tests for the command line, exercised end to end against a temporary store."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from docket.cli import build_parser, main, merge_shared

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


def test_digest_still_reports_the_queue_when_there_is_no_roadmap(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A SessionStart hook degrades rather than failing: no plan, still a digest."""
    _run("digest", "--items", str(_store(tmp_path, READY)))
    out = capsys.readouterr().out

    assert "Docket:" in out
    assert "Plan:" not in out


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


def test_release_ships_nothing_when_nothing_is_finished(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _run("release", "--items", str(_store(tmp_path, READY))) == 0
    assert "Nothing to release" in capsys.readouterr().out


def test_release_needs_no_list_of_items(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The store knows what is finished; requiring it to be named loses work."""
    done = READY.replace("status: ready", "status: done\ncommit: abc1234\nclosed: 2026-08-24")
    (tmp_path / "pyproject.toml").write_text('version = "0.2.2"\n', encoding="utf-8")
    store = _store(tmp_path, done)

    assert _run("release", "--dry-run", "--items", str(store)) == 0
    out = capsys.readouterr().out
    assert "1 finished item(s)" in out
    assert "PL-B1B1" in out
    assert "Dry run: nothing was changed." in out


def test_release_infers_the_version_from_what_shipped(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A patch for fixes; a minor when new functionality went out."""
    feature = READY.replace("classes: perf", "classes: feature").replace(
        "status: ready", "status: done\ncommit: abc1234\nclosed: 2026-08-24"
    )
    (tmp_path / "pyproject.toml").write_text('version = "0.2.2"\n', encoding="utf-8")

    _run("release", "--dry-run", "--items", str(_store(tmp_path, feature)))

    assert "0.2.2 -> 0.3.0" in capsys.readouterr().out


def test_status_leads_with_features_not_items(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Nobody chooses what to do next by reading twenty item titles."""
    grouped = READY.replace("status: ready", "status: ready\nfeature: chart-readout")
    _run("status", "--items", str(_store(tmp_path, grouped)))
    out = capsys.readouterr().out

    assert "chart-readout" in out


def test_release_refuses_to_invent_a_version_under_a_manual_policy(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A plausible wrong version is a provenance error, not a convenience."""
    done = READY.replace("status: ready", "status: done\ncommit: abc1234\nclosed: 2026-08-24")
    (tmp_path / "pyproject.toml").write_text('version = "0.2.2"\n', encoding="utf-8")
    (tmp_path / "docket.toml").write_text('[docket]\nversion_policy = "manual"\n', encoding="utf-8")
    store = _store(tmp_path, done)

    assert _run("release", "--items", str(store)) == 1
    out = capsys.readouterr().out
    assert "Name the version" in out
    assert "PL-B1B1" in out


def _delegable_store(tmp_path: Path) -> Path:
    """A store holding one delegable item and three that must not be offered."""
    items = tmp_path / "docs" / "items"
    items.mkdir(parents=True)
    # Config is resolved from the store's parent, not the working directory,
    # so it belongs beside `docs/` here.
    (items.parent / "docket.toml").write_text(
        '[docket]\nprotected_paths = ["src/core"]\n', encoding="utf-8"
    )
    brief = "**Problem.** P\n**Why it matters.** W\n**Done when.** D\n"
    for ident, extra in (
        ("PL-AAAA", "verify: pytest tests/test_a.py\ntouches: tests/test_a.py\n"),
        ("PL-BBBB", "touches: tests/test_b.py\n"),  # no verify command
        ("PL-CCCC", "verify: pytest\ntouches: src/core/x.py\n"),  # protected
        ("PL-DDDD", "verify: pytest\ntouches: tests/test_d.py\nclasses: safety\n"),
    ):
        (items / f"{ident}-x.md").write_text(
            f"---\nid: {ident}\ntitle: Item {ident}\npriority: P1\neffort: S\n"
            f"status: ready\n{extra}added: 2026-08-01\n---\n\n{brief}",
            encoding="utf-8",
        )
    return items


def test_delegable_lists_only_what_qualifies(tmp_path: Path, capsys: object) -> None:
    """Three of the four items must not be offered, each for a different reason."""
    assert main(["--items", str(_delegable_store(tmp_path)), "--no-git", "delegable"]) == 0
    out = capsys.readouterr().out  # type: ignore[attr-defined]
    assert "PL-AAAA" in out
    assert "verify: pytest tests/test_a.py" in out
    for excluded in ("PL-BBBB", "PL-CCCC", "PL-DDDD"):
        assert excluded not in out


def test_delegable_says_so_when_nothing_qualifies(tmp_path: Path, capsys: object) -> None:
    """An empty result must read as 'nothing to do', not as a broken command."""
    items = tmp_path / "docs" / "items"
    items.mkdir(parents=True)
    (items / "PL-EEEE-x.md").write_text(
        "---\nid: PL-EEEE\ntitle: Item\npriority: P1\neffort: S\nstatus: ready\n"
        "touches: tests/x.py\nadded: 2026-08-01\n---\n\n"
        "**Problem.** P\n**Why it matters.** W\n**Done when.** D\n",
        encoding="utf-8",
    )
    assert main(["--items", str(items), "--no-git", "delegable"]) == 0
    assert "Nothing is delegable" in capsys.readouterr().out  # type: ignore[attr-defined]


def test_shared_options_work_on_either_side_of_the_subcommand() -> None:
    """The before-subcommand form was silently dropped, and dropped quietly.

    A subparser's defaults are written after the top-level options are parsed,
    so an ordinary `default=None` overwrote a value the user had supplied and
    the tool answered about the wrong store with no sign anything was ignored.
    """
    before = merge_shared(build_parser().parse_args(["--items", "/tmp/x", "--no-git", "check"]))
    after = merge_shared(build_parser().parse_args(["check", "--items", "/tmp/x", "--no-git"]))
    assert str(before.items) == str(after.items) == "/tmp/x"
    assert before.no_git is after.no_git is True


def test_shared_options_still_have_defaults_when_given_nowhere() -> None:
    args = merge_shared(build_parser().parse_args(["check"]))
    assert args.items is None
    assert args.today is None
    assert args.no_git is False


WAVE_ROADMAP = """# Roadmap

## The plan

### The timeline

| # | Step | What it is | Size |
| --- | --- | --- | --- |
| 1 | **v0.3.0 — the foundation** | Gate 0's frozen list. | 2 M |
| 2 | **v0.4.0 — the teachable case** | Scoped below. | 5 M |

## Milestone after next: v0.4.0 - the teachable case

### Goal

Make the model teachable.

### Debt gate: the frozen list

**Frozen 2026-08-25.**

- PL-B1B1 (S) The one entry on this gate

### Required scope

A displayed clinical unit.

### Definition of done

The learner can run one case.

### Explicitly out of scope for v0.4.0

Forking.
"""


def _wave_project(tmp_path: Path, *documents: str) -> Path:
    store = _store(tmp_path, *documents)
    (tmp_path / "pyproject.toml").write_text('version = "0.2.5"\n', encoding="utf-8")
    (tmp_path / "ROADMAP.md").write_text(WAVE_ROADMAP, encoding="utf-8")
    return store


def test_wave_reports_the_beat_from_the_plan_and_the_store(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = _wave_project(tmp_path, READY)
    assert _run("wave", "--items", str(store)) == 0

    out = capsys.readouterr().out
    assert "Version   0.2.5" in out
    assert "step 1 of 2: v0.3.0 — the foundation" in out
    assert "1 entry, 1 id" in out
    assert "0 cleared, 1 open" in out
    assert "clear the gate" in out


def test_next_leads_with_what_the_current_step_names(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """End to end: `next` reads the plan, not only the queue.

    The gate entry is `P3` here and the item the roadmap names nowhere is
    `P1`, so a ranking that only sorted by band would lead with the second.
    """
    store = _wave_project(
        tmp_path,
        READY.replace("priority: P1", "priority: P3"),
        READY.replace("PL-B1B1", "PL-C2C2").replace("A ready item", "Work no milestone names"),
    )
    assert _run("next", "--items", str(store)) == 0

    out = capsys.readouterr().out
    assert out.index("PL-B1B1") < out.index("PL-C2C2")
    assert "In scope for v0.4.0 — the teachable case" in out


def test_the_verify_advisory_follows_the_plan_the_way_next_does(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`check` must resolve the same roadmap `next` does, from the repository root.

    PL-B1B1 is `P3` and named by the current step; the three others are `P1`
    and named nowhere, so they fill the offering on band alone. A `check` that
    looked for ROADMAP.md beside the store instead of above it would find no
    plan, rank by band, and advise about the wrong three.
    """
    store = _wave_project(
        tmp_path,
        READY.replace("priority: P1", "priority: P3"),
        *(
            READY.replace("PL-B1B1", other).replace("A ready item", "Named nowhere")
            for other in ("PL-C2C2", "PL-D3D3", "PL-F4F4")
        ),
    )
    (tmp_path / "docket.toml").write_text(
        "[docket]\nverify_required_from = 2026-08-02\n", encoding="utf-8"
    )

    assert _run("check", "--items", str(store)) == 0
    out = capsys.readouterr().out
    assert "PL-B1B1" in out
    assert "3 of 4 ready item(s)" in out


def test_wave_says_there_is_no_plan_rather_than_reporting_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A project with no roadmap has no position to report, and saying so is
    the honest answer; printing a beat anyway would be inventing one."""
    store = _store(tmp_path, READY)
    assert _run("wave", "--items", str(store)) == 1
    assert "no ROADMAP.md to read" in capsys.readouterr().out


def test_wave_exits_nonzero_when_the_gate_names_an_item_that_is_not_there(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = _wave_project(tmp_path)
    assert _run("wave", "--items", str(store)) == 1
    assert "not in the store" in capsys.readouterr().out


DONE = """---
id: PL-D1D1
title: A finished item
priority: P2
effort: S
status: done
classes: perf
touches: a.py
added: 2026-08-01
closed: 2026-08-20
commit: abc1234
---

**Problem.** x
**Why it matters.** y
**Done when.** z
"""


def _release_repo(tmp_path: Path, *tag_names: str) -> Path:
    """A repository with one unreleased item, a version, and the tags given."""
    root = tmp_path / "repo"
    (root / "items").mkdir(parents=True)
    (root / "items" / "done.md").write_text(DONE, encoding="utf-8")
    (root / "pyproject.toml").write_text('[project]\nversion = "0.2.5"\n', encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        subprocess.run(["git", "config", name, value], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True, capture_output=True)
    for tag in tag_names:
        subprocess.run(["git", "tag", tag], cwd=root, check=True, capture_output=True)
    return root


def test_a_release_is_refused_while_the_previous_one_is_untagged(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Cutting on top of an untagged release extends a gap nothing can close later."""
    root = _release_repo(tmp_path, "v0.2.3")

    assert main(["release", "0.2.6", "--items", str(root / "items")]) == 1
    assert "v0.2.5 shipped and carries no tag" in capsys.readouterr().out
    assert 'version = "0.2.5"' in (root / "pyproject.toml").read_text()


def test_a_release_proceeds_once_the_previous_one_is_tagged(tmp_path: Path) -> None:
    root = _release_repo(tmp_path, "v0.2.5")

    assert main(["release", "0.2.6", "--items", str(root / "items")]) == 0
    assert 'version = "0.2.6"' in (root / "pyproject.toml").read_text()


def test_a_dry_run_warns_about_the_missing_tag_and_still_shows_the_notes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Withholding the preview would not make the tag appear."""
    root = _release_repo(tmp_path, "v0.2.3")

    assert main(["release", "0.2.6", "--dry-run", "--items", str(root / "items")]) == 0
    output = capsys.readouterr().out
    assert "carries no tag" in output
    assert "PL-D1D1" in output


def test_a_project_that_has_never_tagged_is_not_refused(tmp_path: Path) -> None:
    root = _release_repo(tmp_path)

    assert main(["release", "0.2.6", "--items", str(root / "items")]) == 0


RELEASE_ROADMAP = """# Roadmap

## Versioning decision

| Version | Status | Milestone |
| --- | --- | --- |
| v0.2.5 | Completed / current baseline | The current one. |

## Current baseline: v0.2.5

What it is.
"""


def test_a_cut_release_names_the_roadmap_edits_it_did_not_write(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-8HJ2: the sequence used to end in a test failure nobody had caused."""
    root = _release_repo(tmp_path, "v0.2.5")
    (root / "ROADMAP.md").write_text(RELEASE_ROADMAP, encoding="utf-8")

    assert main(["release", "0.2.6", "--items", str(root / "items")]) == 0
    out = capsys.readouterr().out
    assert "the version table has no row for v0.2.6" in out
    assert "still marked" in out
    assert "still names v0.2.5" in out
    assert "make check" in out
    assert 'git tag -a v0.2.6 <merge commit> -m "v0.2.6"' in out


def test_a_release_whose_roadmap_is_already_written_says_nothing_is_owed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _release_repo(tmp_path, "v0.2.5")
    (root / "ROADMAP.md").write_text(RELEASE_ROADMAP.replace("v0.2.5", "v0.2.6"), encoding="utf-8")

    assert main(["release", "0.2.6", "--items", str(root / "items")]) == 0
    assert "nothing is owed there" in capsys.readouterr().out


def test_a_project_with_no_roadmap_still_gets_the_rest_of_the_hand_off(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The roadmap is this project's convention, not a requirement of the tool."""
    root = _release_repo(tmp_path, "v0.2.5")

    assert main(["release", "0.2.6", "--items", str(root / "items")]) == 0
    out = capsys.readouterr().out
    assert "Stale in" not in out
    assert "git push origin v0.2.6" in out


UNTRIAGED = """---
id: PL-U1U1
title: An idea nobody has weighed yet
status: untriaged
added: 2026-08-20
---

**Problem.** The induction curve looks wrong at low flows.
"""


def _triage(tmp_path: Path, *documents: str, config: str = "") -> str:
    store = _store(tmp_path, *documents)
    if config:
        (tmp_path / "docket.toml").write_text(config, encoding="utf-8")
    assert _run("triage", "--items", str(store)) == 0
    return store.name


def test_triage_prints_the_body_and_what_is_still_unset(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A title alone cannot be triaged by someone who was not there."""
    _triage(tmp_path, UNTRIAGED, READY)
    output = capsys.readouterr().out

    assert "PL-U1U1" in output
    assert "induction curve looks wrong" in output
    assert "priority*" in output and "effort*" in output
    assert "**Why it matters.**" in output  # the brief sections still missing


def test_triage_states_the_rules_the_answers_must_satisfy(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The point is the rules being present, not a session recalling them."""
    _triage(
        tmp_path,
        UNTRIAGED,
        READY,
        config='[docket]\nprotected_paths = ["src/core"]\nverify_required_from = 2026-08-01\n',
    )
    output = capsys.readouterr().out

    assert "force P0 or P1" in output
    assert "the top band is P1, holding 1 of the 5" in output
    assert "src/core" in output
    assert "`verify:` command" in output


def test_triage_leaves_a_project_that_declares_no_protected_paths_alone(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _triage(tmp_path, UNTRIAGED)

    assert "non-delegable" not in capsys.readouterr().out


def test_triage_decides_nothing_and_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Priority, effort, classes and feature are judgment and stay with the session."""
    store = _store(tmp_path, UNTRIAGED)
    before = (store / "item-0.md").read_text()

    assert _run("triage", "--items", str(store)) == 0

    assert (store / "item-0.md").read_text() == before
    assert "priority: " not in capsys.readouterr().out


def test_triage_says_so_when_nothing_is_waiting(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _triage(tmp_path, READY)

    assert "Nothing is untriaged." in capsys.readouterr().out


DEBT = """---
id: PL-E1E1
title: A defect in the milestone's own scope
priority: P2
effort: M
status: ready
classes: defect
feature: teachable-case
touches: a.py
added: 2026-08-01
---

**Problem.** x
**Why it matters.** y
**Done when.** z
"""


def test_gate_splits_the_debt_the_milestone_clears_from_the_debt_before_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Recording Gate 0 by hand was a full pass over 48 items; this is that pass."""
    store = _store(tmp_path, READY, DEBT)

    assert _run("gate", "--feature", "teachable-case", "--items", str(store)) == 0

    output = capsys.readouterr().out
    before, _, after = output.partition("Cleared by the milestone itself")
    assert "PL-B1B1" in before and "PL-E1E1" not in before
    assert "PL-E1E1" in after
    assert "1 M" in after


def test_gate_writes_nothing_and_reaches_no_verdict(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Freezing the list stays a deliberate act; the command removes the typing."""
    store = _store(tmp_path, READY, DEBT)
    before = {path.name: path.read_text() for path in store.glob("*.md")}

    assert _run("gate", "--feature", "teachable-case", "--items", str(store)) == 0

    assert {path.name: path.read_text() for path in store.glob("*.md")} == before
    assert "not decided here" in capsys.readouterr().out
