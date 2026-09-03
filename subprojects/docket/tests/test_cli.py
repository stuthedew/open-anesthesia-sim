"""Tests for the command line, exercised end to end against a temporary store."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from docket.cli import build_parser, main, merge_shared
from docket.vcs import lost

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


def test_delegable_lists_only_what_qualifies(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Three of the four items must not be offered, each for a different reason."""
    assert main(["--items", str(_delegable_store(tmp_path)), "--no-git", "delegable"]) == 0
    out = capsys.readouterr().out
    assert "PL-AAAA" in out
    assert "verify: pytest tests/test_a.py" in out
    for excluded in ("PL-BBBB", "PL-CCCC", "PL-DDDD"):
        assert excluded not in out


def test_delegable_says_so_when_nothing_qualifies(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
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
    assert "Nothing is delegable" in capsys.readouterr().out


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
    # Named as the roadmap arranges it rather than as "the current step": this
    # fixture puts the gate under v0.4.0 and the step on v0.3.0, and calling
    # the first the second is what PL-1J0P fixed.
    assert "On the debt gate recorded under v0.4.0 — the teachable case" in out
    assert "v0.3.0 — the foundation clears it" in out
    assert "the step the project is on" not in out


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
    # A real git checkout, built by running real git from `PATH`: the release
    # commands read tags and refs, so a stub would test the stub.
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


def test_a_version_file_the_bump_rejects_leaves_the_items_unstamped(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-DL1X: a release records all of itself or none of it.

    Every item was stamped before the version moved, so a version file the
    bump rejects left the store recording a release that never happened - and
    the next run then reported nothing to release, because the work it would
    have shipped claimed to have shipped already.
    """
    root = _release_repo(tmp_path, "v0.2.5")
    (root / "pyproject.toml").write_text('[project]\nname = "x"\n', encoding="utf-8")

    assert main(["release", "0.2.6", "--items", str(root / "items")]) == 1

    assert "no version field to bump" in capsys.readouterr().out
    assert "milestone:" not in (root / "items" / "done.md").read_text(encoding="utf-8")
    assert not (root / "docs" / "releases").exists()


def test_a_missing_version_file_leaves_the_items_unstamped(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The other way the bump fails, and the one a project adopting docket meets."""
    root = _release_repo(tmp_path, "v0.2.5")
    (root / "pyproject.toml").unlink()

    assert main(["release", "0.2.6", "--items", str(root / "items")]) == 1

    assert "Cannot bump pyproject.toml" in capsys.readouterr().out
    assert "milestone:" not in (root / "items" / "done.md").read_text(encoding="utf-8")


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


STUBBED = """---
id: PL-U2U2
title: An idea captured over the format's own headings
status: untriaged
added: 2026-08-20
---

**Problem.** The stub above a real brief, which is how `PL-RWZV` was written.

**Why it matters.**

**Done when.**
"""


def test_triage_reads_the_brief_exactly_as_the_checker_will(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-RWZV`: two readings of one rule, and the README promises there is one.

    `triage` had its own literal-substring test, so it would have called this
    brief complete a moment before `docket check` errored on it - and would
    have demanded a section from an item whose heading merely continued past
    the words. Both now come from `brief_gaps`.
    """
    _triage(tmp_path, STUBBED)
    output = capsys.readouterr().out

    assert "brief has nothing under: **Why it matters.**, **Done when.**" in output
    assert "brief still missing" not in output


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


def _branched_repo(tmp_path: Path) -> Path:
    """A repository whose second branch carries an item `main` has never seen.

    Real git, for the same reason `_release_repo` uses it: the injected-runner
    tests assert the filtering, and only a real checkout proves the commands
    are spelled in a way git accepts.
    """
    root = tmp_path / "repo"
    (root / "items").mkdir(parents=True)
    (root / "items" / "PL-0001-on-main.md").write_text(READY.replace("PL-B1B1", "PL-0001"))
    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(root)],
        check=True,
        capture_output=True,
    )
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        subprocess.run(["git", "config", name, value], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "checkout", "-qb", "abandoned"], cwd=root, check=True, capture_output=True
    )
    (root / "items" / "PL-K7QX-lost.md").write_text(
        READY.replace("PL-B1B1", "PL-K7QX").replace("A ready item", "A lost thought")
    )
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "capture"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "checkout", "-q", "main"], cwd=root, check=True, capture_output=True)
    return root


def test_stranded_finds_an_item_that_exists_only_on_a_branch(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _branched_repo(tmp_path)

    assert main(["--items", str(root / "items"), "stranded"]) == 0

    out = capsys.readouterr().out
    assert "PL-K7QX  A lost thought" in out
    assert "only on: abandoned" in out
    assert "git checkout abandoned -- items/PL-K7QX-lost.md" in out


def test_stranded_reports_nothing_when_every_branch_has_landed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _branched_repo(tmp_path)
    subprocess.run(["git", "merge", "-q", "abandoned"], cwd=root, check=True, capture_output=True)

    assert main(["--items", str(root / "items"), "stranded"]) == 0

    assert "No item exists only on a branch" in capsys.readouterr().out


def test_stranded_says_so_when_it_was_told_not_to_ask_git(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Silence would read as a clean answer; it is an unasked question."""
    assert _run("stranded", "--items", str(_store(tmp_path, READY))) == 0

    assert "branch detection is off" in capsys.readouterr().out


# The name a web harness gives a branch: built from the opening prompt, so it
# carries no item id and cannot be renamed afterwards.
BRANCH = "roadmap-release-write-failure-nhsjwo"


def _flight_repo(tmp_path: Path, subject: str) -> Path:
    """A repository whose one live branch is named the way the harness names one.

    Real git, for the reason `_branched_repo` uses it: the injected-runner
    tests in `test_vcs.py` assert the rules, and only a real checkout proves
    that `--source`, `%cs` and the merge-base guard are spelled in a way git
    accepts. The commit dates are fixed so the reported age is too.
    """
    root = tmp_path / "repo"
    (root / "items").mkdir(parents=True)
    (root / "items" / "PL-0001-on-main.md").write_text(READY.replace("PL-B1B1", "PL-0001"))
    dated = os.environ | {
        "GIT_AUTHOR_DATE": "2026-08-20T12:00:00+00:00",
        "GIT_COMMITTER_DATE": "2026-08-20T12:00:00+00:00",
    }

    def git(*args: str, env: dict[str, str] | None = None) -> None:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, env=env)

    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(root)],
        check=True,
        capture_output=True,
    )
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        git("config", name, value)
    git("add", "-A")
    git("commit", "-qm", "base", env=dated)
    git("checkout", "-qb", BRANCH)
    (root / "items" / "scratch.txt").write_text("work in progress\n")
    git("add", "-A")
    git("commit", "-qm", subject, env=dated)
    git("checkout", "-q", "main")
    return root


def test_flight_finds_work_on_a_branch_whose_name_carries_no_id(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The case the command exists for: a harness-named branch, mid-item."""
    root = _flight_repo(tmp_path, "PL-K7QX Do the thing")

    assert main(["--items", str(root / "items"), "--today", "2026-08-23", "flight"]) == 0

    out = capsys.readouterr().out
    assert "PL-K7QX  roadmap-release-write-failure-nhsjwo" in out
    assert "last commit 3 days ago" in out


def test_show_marks_an_item_a_branch_has_in_flight(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-5KR2: the guard against two sessions doing one item reaches `show`.

    `plan.recommend` excludes in-flight ids, so a session that arrived through
    `next` is covered. One handed an item by name never calls `next`, and
    `triage`, `check` and `show` all said nothing - so the path where a person
    chose the work was the path with no check.
    """
    root = _flight_repo(tmp_path, "PL-0001 Do the thing")

    assert main(["--items", str(root / "items"), "show", "PL-0001"]) == 0

    out = capsys.readouterr().out
    assert "IN FLIGHT on a branch - do not start PL-0001 again." in out
    assert "PL-0001" in out.splitlines()[0]


def test_triage_names_an_item_already_in_flight(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-PRHN: two sessions triaged one pair of items and collided at merge.

    Triage is the more exposed entry point rather than the less. `show` guards
    the path where a session has *chosen* an item; triage is what a session
    runs straight off a digest that reports the untriaged count and nothing
    about who is holding those items. The branch is named, not merely the fact
    of one, because the reader has to be able to tell another session's work
    from its own without leaving the output.
    """
    # A valid id, which `UNTRIAGED`'s own `PL-U1U1` is not: the alphabet drops
    # the vowels, so a subject leading with that one carries no id at all.
    root = _flight_repo(tmp_path, "PL-N3W1 Triage it")
    (root / "items" / "PL-N3W1-untriaged.md").write_text(
        UNTRIAGED.replace("PL-U1U1", "PL-N3W1"), encoding="utf-8"
    )

    assert main(["--items", str(root / "items"), "triage"]) == 0

    out = capsys.readouterr().out
    assert f"IN FLIGHT on {BRANCH} - triaging it here as well collides at merge." in out
    # Reported, not withheld: the mark is bounded by what has been pushed, so
    # it advises and the item stays answerable underneath it.
    assert "induction curve looks wrong" in out


def test_triage_names_the_refs_that_bound_its_in_flight_answer(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An unmarked item means "no ref proved it", never "no ref carries it".

    Silence about a ref the checkout could not read presents a partial reading
    as a complete one - which is the collapse that makes the mark trusted in
    exactly the case it is least entitled to be.
    """
    root = _flight_repo(tmp_path, "PL-K7QX Do the thing")
    for args in (
        ["checkout", "-q", "--orphan", "unrelated"],
        ["commit", "-qm", "PL-N3W1 Triage it"],
    ):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "checkout", "-q", "main"], cwd=root, check=True, capture_output=True)
    (root / "items" / "PL-N3W1-untriaged.md").write_text(
        UNTRIAGED.replace("PL-U1U1", "PL-N3W1"), encoding="utf-8"
    )

    assert main(["--items", str(root / "items"), "triage"]) == 0

    out = capsys.readouterr().out
    assert "1 ref could not be compared with main" in out
    assert "`bin/docket flight` names it." in out
    assert "IN FLIGHT" not in out


def test_show_leaves_an_item_no_branch_carries_out_of_flight(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The mark is a claim about this id, not about the branch existing."""
    root = _flight_repo(tmp_path, "PL-K7QX Do the thing")

    assert main(["--items", str(root / "items"), "show", "PL-0001"]) == 0

    assert "IN FLIGHT" not in capsys.readouterr().out


def test_flight_does_not_read_a_mentioned_id_as_work_in_progress(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A false positive here makes `docket next` skip an item that is startable."""
    root = _flight_repo(tmp_path, "Capture PL-K7QX, found while doing something else")

    assert main(["--items", str(root / "items"), "flight"]) == 0

    assert "No branch carries an item id" in capsys.readouterr().out


def _squash_merge(root: Path, branch: str, subject: str) -> None:
    """Land a branch the way GitHub's squash button does, keeping the ref.

    One new commit on the default branch holding the branch's content and none
    of its commits - which is why `--merged` never names the branch again, and
    why a checkout that has not pruned goes on holding a ref for finished work.
    """
    for args in (["merge", "--squash", "-q", branch], ["commit", "-qm", subject]):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def test_flight_does_not_report_a_squash_merged_branch_whose_ref_survives(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Real git, because the containment test this replaces was spelled right too.

    The ref is what a session's own container never holds - GitHub deletes the
    head branch on merge - and what a long-lived local checkout holds until
    somebody prunes.
    """
    root = _flight_repo(tmp_path, "PL-K7QX Do the thing")
    _squash_merge(root, BRANCH, "PL-K7QX Do the thing (#71)")

    assert main(["--items", str(root / "items"), "flight"]) == 0

    assert "No branch carries an item id" in capsys.readouterr().out


def test_flight_keeps_a_squash_merged_branch_out_after_the_base_moves_on(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The default branch editing the same file again does not un-land the work.

    This is the case a comparison against the default branch's *tip* gets
    wrong, and it is the ordinary one here: the triage pass that follows a
    capture rewrites the very file the capturing branch added.
    """
    root = _flight_repo(tmp_path, "PL-K7QX Do the thing")
    _squash_merge(root, BRANCH, "PL-K7QX Do the thing (#71)")
    (root / "items" / "scratch.txt").write_text("triaged since\n")
    for args in (["add", "-A"], ["commit", "-qm", "PL-K7QX Close it out"]):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

    assert main(["--items", str(root / "items"), "flight"]) == 0

    assert "No branch carries an item id" in capsys.readouterr().out


def test_flight_names_a_ref_it_could_not_read_rather_than_ignoring_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The container an agent session runs in is a truncated clone.

    History it simply lacks answers the same way genuinely unrelated history
    does - no merge-base - and both must be named rather than contributing
    silent nothing to a report that then reads as complete.
    """
    root = _flight_repo(tmp_path, "PL-K7QX Do the thing")
    for args in (["checkout", "-q", "--orphan", "unrelated"], ["commit", "-qm", "PL-9Y42 Other"]):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "checkout", "-q", "main"], cwd=root, check=True, capture_output=True)

    assert main(["--items", str(root / "items"), "flight"]) == 0

    out = capsys.readouterr().out
    assert "1 ref cannot be compared with main" in out
    assert "  unrelated" in out
    assert "PL-9Y42" not in out


def _diverged_repo(tmp_path: Path) -> Path:
    """A branch carrying its own commit while the default branch moved under it.

    The shape the session-start check exists for, and the one it could not see:
    the branch was current when the session opened and is not by the time the
    discussion becomes implementation. No remote, so `default_base` falls back
    to the local `main` - which is also the fallback this exercises.
    """
    root = tmp_path / "diverged"
    (root / "items").mkdir(parents=True)
    (root / "items" / "PL-0001-on-main.md").write_text(READY.replace("PL-B1B1", "PL-0001"))
    dated = os.environ | {
        "GIT_AUTHOR_DATE": "2026-08-20T12:00:00+00:00",
        "GIT_COMMITTER_DATE": "2026-08-20T12:00:00+00:00",
    }

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, env=dated)

    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(root)],
        check=True,
        capture_output=True,
    )
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        git("config", name, value)
    git("add", "-A")
    git("commit", "-qm", "base")
    git("checkout", "-qb", "claude/pl-k7qx-live")
    (root / "items" / "scratch.txt").write_text("work in progress\n")
    git("add", "-A")
    git("commit", "-qm", "PL-K7QX Do the thing")
    git("checkout", "-q", "main")
    (root / "items" / "PL-9Y42-landed.md").write_text(READY.replace("PL-B1B1", "PL-9Y42"))
    git("add", "-A")
    git("commit", "-qm", "PL-9Y42 Validate wash-in (#131)")
    git("checkout", "-q", "claude/pl-k7qx-live")
    return root


def test_branch_state_is_spelled_in_a_way_real_git_answers(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The plumbing half: `rev-list --left-right --count` and the fork-point walk.

    `--no-fetch` because a test must not reach the network, and because it is
    the flag a checkout without one uses - so the caveat it prints is asserted
    here too.
    """
    root = _diverged_repo(tmp_path)

    assert main(["--items", str(root / "items"), "branch", "--no-fetch"]) == 0

    out = capsys.readouterr().out
    assert "Branch: claude/pl-k7qx-live is 1 behind main and 1 ahead." in out
    assert "git merge main" in out
    assert "Landed on main since this branch forked: PL-9Y42." in out
    # No caveat: this checkout's base is a local branch, which no fetch refreshes.
    assert "last fetch" not in out


def test_branch_state_says_nothing_to_the_digest_with_nothing_to_compare(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The hook's silence, kept: the default branch with no remote copy of it.

    Comparing a ref with itself answers nothing, and the digest is resent on
    every turn of the session - so `--brief`, which is what the hook passes,
    prints no line at all. A person who ran the command is told why.
    """
    root = _diverged_repo(tmp_path)
    subprocess.run(["git", "checkout", "-q", "main"], cwd=root, check=True, capture_output=True)
    store = str(root / "items")

    assert main(["--items", store, "branch", "--no-fetch", "--brief"]) == 0
    assert capsys.readouterr().out == ""

    assert main(["--items", store, "branch", "--no-fetch"]) == 0
    assert "no remote copy to compare with" in capsys.readouterr().out


def test_the_branch_guard_flag_speaks_only_when_the_branch_is_stale(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`--if-stale` is for the caller that speaks unasked, so silence is the default.

    The first-edit hook prints into a session that did not ask for it, and "your
    base has not moved" is not worth interrupting an edit for.
    """
    root = _diverged_repo(tmp_path)
    store = str(root / "items")
    flags = ["branch", "--no-fetch", "--brief", "--if-stale"]

    assert main(["--items", store, *flags]) == 0
    assert "1 behind main and 1 ahead" in capsys.readouterr().out

    subprocess.run(
        ["git", "checkout", "-q", "-b", "claude/pl-9y42-fresh", "main"],
        cwd=root,
        check=True,
        capture_output=True,
    )

    assert main(["--items", store, *flags]) == 0
    assert capsys.readouterr().out == ""


def _shallow_pair(tmp_path: Path) -> Path:
    """A clone deep enough to resolve a merge-base and too shallow to walk past it.

    An agent session's container in miniature, built the only way that proves
    anything: real git, real depths, real grafts. The default branch is fetched
    to a depth that leaves its own history ending at a grafted commit, and the
    branch is fetched deep enough to reach round that graft - which the merge
    of the default branch that resolving a conflict leaves behind is enough to
    do. Both fetches are ordinary. Together they make `git merge-base` resolve
    while `^origin/main` still fails to exclude the default branch's own
    commits, which is the intermediate depth the incident of 2026-08-31 hit and
    a `--depth 1` clone does not reach: there the merge-base declines instead.
    """
    origin = tmp_path / "origin"
    (origin / "items").mkdir(parents=True)
    (origin / "items" / "PL-0001-on-main.md").write_text(READY.replace("PL-B1B1", "PL-0001"))
    dated = os.environ | {
        "GIT_AUTHOR_DATE": "2026-08-20T12:00:00+00:00",
        "GIT_COMMITTER_DATE": "2026-08-20T12:00:00+00:00",
        "GIT_AUTHOR_NAME": "T",
        "GIT_COMMITTER_NAME": "T",
        "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_EMAIL": "t@example.com",
    }

    def git(*args: str, cwd: Path = origin) -> None:
        subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, env=dated)

    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(origin)],
        check=True,
        capture_output=True,
    )

    def commit(number: int) -> None:
        (origin / f"f{number}").write_text(f"main {number}\n")
        git("add", "-A")
        git("commit", "-qm", f"PL-M0{number} Main work {number}")

    for number in range(1, 7):
        commit(number)
    git("checkout", "-qb", BRANCH, "main~5")
    (origin / "items" / "scratch.txt").write_text("work in progress\n")
    git("add", "-A")
    git("commit", "-qm", "PL-K7QX Do the thing")
    git("merge", "-q", "--no-edit", "-m", "Merge main into the branch", "main")
    git("checkout", "-q", "main")
    for number in range(7, 11):
        commit(number)

    work = tmp_path / "work"
    # Depths chosen for the topology above: five leaves `origin/main` ending at
    # a graft, and three carries the branch past it to the commit it forked
    # from, which the default branch can then no longer account for.
    subprocess.run(
        ["git", "clone", "-q", "--depth=5", "--branch", "main", origin.as_uri(), str(work)],
        check=True,
        capture_output=True,
        env=dated,
    )
    git("fetch", "-q", "--depth=3", "origin", f"{BRANCH}:refs/remotes/origin/{BRANCH}", cwd=work)
    return work


def test_flight_does_not_answer_from_a_walk_the_clone_truncated(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The defect: a readable merge-base does not make the walk complete.

    Without the guard the walk reports `PL-M01` - a commit of the default
    branch's own, below the horizon `^origin/main` can exclude - as work this
    branch is carrying, and `docket next` then withholds that item under the
    words "do not start these again".
    """
    work = _shallow_pair(tmp_path)
    assert subprocess.run(
        ["git", "merge-base", "origin/main", f"origin/{BRANCH}"],
        cwd=work,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip(), "the merge-base must resolve, or this tests the case already covered"

    assert main(["--items", str(work / "items"), "flight"]) == 0

    out = capsys.readouterr().out
    assert "No branch carries an item id" in out
    assert "PL-M01" not in out
    assert "1 ref cannot be compared with origin/main" in out
    assert f"  origin/{BRANCH}" in out


def test_the_queue_commands_say_when_a_ref_went_unread(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-S1P1: the gap reached `docket flight` and stopped there.

    Every other command read the ids alone, so the same checkout that tells
    `flight` it could not read a ref told `next` that the queue was fully
    known - and `next` is the one a session actually asks. The refs here are
    real and so is the truncation: `_shallow_pair` is the container in
    miniature, and it is the ordinary state of one.
    """
    work = _shallow_pair(tmp_path)
    store = str(work / "items")

    commands: tuple[tuple[str, ...], ...] = (
        ("next",),
        ("list",),
        ("status",),
        ("digest",),
        ("delegable",),
        ("concurrent",),
        # `show` marks against the in-flight ids too (PL-5KR2), so it owes the
        # same sentence: a mark drawn from refs that went unread is a partial
        # reading, and silence would present it as a complete one.
        ("show", "PL-0001"),
        # `check` was the seventh reader and the one this test's own list left
        # out (PL-3576): its grooming advisories name whichever item the
        # ranking put first, and the ranking excludes what is in flight. It
        # says so in the section it already keeps for checks that could not
        # run, so the sentence arrives with a prefix the others have no use for.
        ("check",),
    )
    for command in commands:
        assert main(["--items", store, *command]) == 0
        out = capsys.readouterr().out
        assert "1 ref could not be compared with origin/main" in out, command
        assert "bin/docket flight" in out, command


def _merge_deleting_an_item(tmp_path: Path) -> Path:
    """A repository whose merge resolution removed an item nothing else deleted.

    Real git, because the whole finding is about what git's *diff* walk does
    not show: `git log --diff-filter=D` over the store returns nothing here,
    and only a real merge commit reproduces that. An injected runner would be
    asserting the reproduction rather than the behaviour.
    """
    root = tmp_path / "merged"
    (root / "items").mkdir(parents=True)
    (root / "items" / "PL-0001-on-main.md").write_text(READY.replace("PL-B1B1", "PL-0001"))
    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(root)],
        check=True,
        capture_output=True,
    )
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        subprocess.run(["git", "config", name, value], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True, capture_output=True)

    subprocess.run(["git", "checkout", "-qb", "feature"], cwd=root, check=True, capture_output=True)
    (root / "items" / "PL-K7QX-captured-here.md").write_text(READY.replace("PL-B1B1", "PL-K7QX"))
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-qm", "PL-K7QX: capture"], cwd=root, check=True, capture_output=True
    )

    subprocess.run(["git", "checkout", "-q", "main"], cwd=root, check=True, capture_output=True)
    (root / "items" / "PL-0001-on-main.md").write_text(
        READY.replace("PL-B1B1", "PL-0001").replace("A ready item", "A ready item, edited")
    )
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-qm", "main moves"], cwd=root, check=True, capture_output=True
    )

    subprocess.run(["git", "checkout", "-q", "feature"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "merge", "-q", "main", "-m", "merge main into feature"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    # The resolution: the merge's own tree loses the item. Amending folds it
    # into the merge commit, which is what a conflict resolution produces.
    subprocess.run(
        ["git", "rm", "-q", "items/PL-K7QX-captured-here.md"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-q", "--amend", "--no-edit"], cwd=root, check=True, capture_output=True
    )
    return root


def test_a_merge_resolution_deleting_an_item_is_invisible_to_the_diff_walk(tmp_path: Path) -> None:
    """The premise of `PL-P0QT`, asserted rather than assumed.

    If this ever starts failing, the object walk `lost` pays for is no longer
    needed and the cheaper `--diff-filter=D` read would do.
    """
    root = _merge_deleting_an_item(tmp_path)

    deletions = subprocess.run(
        ["git", "log", "--diff-filter=D", "--name-only", "--format=", "--", "items/"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout

    assert "PL-K7QX" not in deletions


def test_lost_finds_the_item_a_merge_resolution_removed(tmp_path: Path) -> None:
    root = _merge_deleting_an_item(tmp_path)

    report = lost(root, items_dir="items")

    assert report.known
    assert [item.identifier for item in report.items] == ["PL-K7QX"]
    assert report.items[0].path == "items/PL-K7QX-captured-here.md"
    recovered = subprocess.run(
        ["git", "cat-file", "-p", report.items[0].blob],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "PL-K7QX" in recovered


def test_lost_reports_nothing_when_the_merge_kept_every_item(tmp_path: Path) -> None:
    """The same repository without the deletion, so a clean answer is proved clean."""
    root = _merge_deleting_an_item(tmp_path)
    subprocess.run(
        ["git", "revert", "-q", "--no-edit", "-m", "1", "HEAD"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    subprocess.run(
        ["git", "checkout", "-q", "HEAD~1", "--", "items/"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "restore"], cwd=root, check=True, capture_output=True)

    assert lost(root, items_dir="items").items == ()


RECORD_ITEM = """---
id: {id}
title: A closed item
priority: P2
effort: S
status: {status}
classes: infra
touches: a.py
added: 2026-08-01
{extra}---

**Problem.** x
"""


def _record_repo(tmp_path: Path, *, closes: bool = True, extra: str = "") -> Path:
    """A checkout whose tip commit closes `PL-K7QX`, built with real git.

    `record` compares a commit's tree against its parent's, and only a real
    checkout proves those commands are spelled in a way git accepts.
    """
    root = tmp_path / "repo"
    items = root / "items"
    items.mkdir(parents=True)
    name = "PL-K7QX-a-closed-item.md"
    (items / name).write_text(
        RECORD_ITEM.format(id="PL-K7QX", status="ready", extra=""), encoding="utf-8"
    )
    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(root)],
        check=True,
        capture_output=True,
    )
    for key, value in (("user.email", "t@example.com"), ("user.name", "T")):
        subprocess.run(["git", "config", key, value], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "capture"], cwd=root, check=True, capture_output=True)
    # A second commit either way, so the tip always has a parent to be compared
    # against: a root commit declines, which is a different case with its own
    # test. Where it does not close, it captures - the shape of a triage merge.
    if closes:
        (items / name).write_text(
            RECORD_ITEM.format(id="PL-K7QX", status="done", extra=extra), encoding="utf-8"
        )
        subject = "PL-K7QX: do the thing"
    else:
        (items / "PL-B1C2-another-idea.md").write_text(
            RECORD_ITEM.format(id="PL-B1C2", status="ready", extra=""), encoding="utf-8"
        )
        subject = "PL-B1C2: capture another idea"
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-qm", subject], cwd=root, check=True, capture_output=True)
    return root


def _pr_field(root: Path) -> str:
    text = (root / "items" / "PL-K7QX-a-closed-item.md").read_text(encoding="utf-8")
    return next((line for line in text.splitlines() if line.startswith("pr:")), "")


def test_record_writes_the_number_onto_what_the_merge_closed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The write half of the advisory `check` used to hand to a session."""
    root = _record_repo(tmp_path)

    assert main(["record", "257", "--items", str(root / "items")]) == 0

    assert _pr_field(root) == "pr: 257"
    assert "PL-K7QX: recorded `pr: 257`" in capsys.readouterr().out


def test_record_leaves_the_rest_of_the_item_alone(tmp_path: Path) -> None:
    """A round trip that reordered or dropped a field would put noise in every diff."""
    root = _record_repo(tmp_path)
    before = (root / "items" / "PL-K7QX-a-closed-item.md").read_text(encoding="utf-8")

    main(["record", "257", "--items", str(root / "items")])

    after = (root / "items" / "PL-K7QX-a-closed-item.md").read_text(encoding="utf-8")
    assert after == before.replace("added: 2026-08-01\n", "added: 2026-08-01\npr: 257\n")


def test_record_is_idempotent(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The job that runs it can be re-run, and a session can run it without checking first."""
    root = _record_repo(tmp_path, extra="pr: 257\n")

    assert main(["record", "257", "--items", str(root / "items")]) == 0

    assert "already records `pr: 257`" in capsys.readouterr().out
    assert _pr_field(root) == "pr: 257"


def test_record_refuses_to_overwrite_a_different_number(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Two numbers for one closure means one is wrong, and this cannot know which."""
    root = _record_repo(tmp_path, extra="pr: 99\n")

    assert main(["record", "257", "--items", str(root / "items")]) == 1

    assert "records `pr: 99`" in capsys.readouterr().out
    assert _pr_field(root) == "pr: 99"


def test_record_dry_run_writes_nothing(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _record_repo(tmp_path)

    assert main(["record", "257", "--dry-run", "--items", str(root / "items")]) == 0

    assert "would record `pr: 257`" in capsys.readouterr().out
    assert _pr_field(root) == ""


def test_record_writes_nothing_where_the_commit_closed_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A capture-only merge owes no number, and must not stamp one on the store."""
    root = _record_repo(tmp_path, closes=False)

    assert main(["record", "257", "--items", str(root / "items")]) == 0

    assert "closed no item" in capsys.readouterr().out
    assert _pr_field(root) == ""


def test_record_refuses_a_number_that_is_not_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _record_repo(tmp_path)

    assert main(["record", "0", "--items", str(root / "items")]) == 2

    assert "not a pull request number" in capsys.readouterr().out
    assert _pr_field(root) == ""


def test_record_declines_where_the_parent_is_out_of_reach(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Loudly, and writing nothing.

    The job that runs this uses `fetch-depth: 0` for exactly this reason. A
    truncated checkout that answered anyway would read every done item as
    closed by this commit and stamp one number across the store.
    """
    root = tmp_path / "repo"
    (root / "items").mkdir(parents=True)
    (root / "items" / "PL-K7QX-a-closed-item.md").write_text(
        RECORD_ITEM.format(id="PL-K7QX", status="done", extra=""), encoding="utf-8"
    )
    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(root)],
        check=True,
        capture_output=True,
    )
    for key, value in (("user.email", "t@example.com"), ("user.name", "T")):
        subprocess.run(["git", "config", key, value], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "root"], cwd=root, check=True, capture_output=True)

    assert main(["record", "257", "--items", str(root / "items")]) == 2

    assert "declined" in capsys.readouterr().out
    assert _pr_field(root) == ""


def _owed_clone(tmp_path: Path, *, subject: str = "PL-K7QX: close it (#148)") -> Path:
    """A checkout whose `origin/main` holds a closure recording no `pr`.

    The state every merge leaves behind, built with real git and a real remote
    because `closures_on_base` resolves the default base through one. `subject`
    is what the squash merge wrote, which is where the number comes from.
    """
    origin = tmp_path / "origin"
    items = origin / "items"
    items.mkdir(parents=True)
    name = "PL-K7QX-a-closed-item.md"

    def git(*args: str, cwd: Path = origin) -> None:
        subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)

    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(origin)],
        check=True,
        capture_output=True,
    )
    for key, value in (("user.email", "t@example.com"), ("user.name", "T")):
        git("config", key, value)
    (items / name).write_text(
        RECORD_ITEM.format(id="PL-K7QX", status="ready", extra=""), encoding="utf-8"
    )
    git("add", "-A")
    git("commit", "-qm", "PL-K7QX: capture it")
    (items / name).write_text(
        RECORD_ITEM.format(id="PL-K7QX", status="done", extra=""), encoding="utf-8"
    )
    git("add", "-A")
    git("commit", "-qm", subject)

    work = tmp_path / "work"
    subprocess.run(["git", "clone", "-q", str(origin), str(work)], check=True, capture_output=True)
    return work


def _work_pr(work: Path) -> str:
    text = (work / "items" / "PL-K7QX-a-closed-item.md").read_text(encoding="utf-8")
    return next((line for line in text.splitlines() if line.startswith("pr:")), "")


def test_bare_record_writes_every_number_the_base_is_owed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The normal form, and what `make fix` runs.

    It asks the question `check` asks and writes the answer, so the field costs
    no commit of its own - it rides whatever the session was about to commit.
    """
    work = _owed_clone(tmp_path)

    assert main(["record", "--items", str(work / "items")]) == 0

    assert _work_pr(work) == "pr: 148"
    assert "PL-K7QX: recorded `pr: 148`" in capsys.readouterr().out


def test_bare_record_says_so_when_nothing_is_owed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Safe to run unattended, which is what putting it in `make fix` requires."""
    work = _owed_clone(tmp_path)
    main(["record", "--items", str(work / "items")])
    capsys.readouterr()

    assert main(["record", "--items", str(work / "items")]) == 0

    assert "every closure already records its pull request" in capsys.readouterr().out


def test_bare_record_writes_nothing_where_the_base_names_no_number(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A UI-generated title names no id and no number (`PL-2XTF`).

    Guessing here would be worse than the gap: `check` is the command that
    decides whether an unnameable closure is provenance lost, a decline, or a
    truncated checkout, and this must not pre-empt it.
    """
    work = _owed_clone(tmp_path, subject="Add some safety checks")

    assert main(["record", "--items", str(work / "items")]) == 0

    assert _work_pr(work) == ""
    out = capsys.readouterr().out
    assert "1 landed closure(s) record no `pr`" in out
    assert "names a number for none of them" in out


def test_bare_record_does_not_call_an_unlanded_closure_unnameable(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The ordinary state mid-item, and it must not read as lost provenance.

    A closure written in the working tree and not yet merged owes no number at
    all. Counting it among the ones the base cannot name says the way back is
    gone, which is the confident wrong answer this package refuses - and it is
    what `make fix` printed the first time it ran this.
    """
    work = _owed_clone(tmp_path)
    main(["record", "--items", str(work / "items")])
    name = "PL-B1C2-a-closed-item.md"
    (work / "items" / name).write_text(
        RECORD_ITEM.format(id="PL-B1C2", status="done", extra=""), encoding="utf-8"
    )
    capsys.readouterr()

    assert main(["record", "--items", str(work / "items")]) == 0

    out = capsys.readouterr().out
    assert "none has reached `origin/main` yet, so no number is owed" in out
    assert "names a number for none of them" not in out


def test_bare_record_dry_run_writes_nothing(tmp_path: Path) -> None:
    work = _owed_clone(tmp_path)

    assert main(["record", "--dry-run", "--items", str(work / "items")]) == 0

    assert _work_pr(work) == ""


def test_record_refuses_a_merge_without_the_number_it_is(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`--merge` names one commit; the bare form reads the base and takes none."""
    work = _owed_clone(tmp_path)

    assert main(["record", "--merge", "HEAD", "--items", str(work / "items")]) == 2

    assert "needs the number that merge is" in capsys.readouterr().out
    assert _work_pr(work) == ""
