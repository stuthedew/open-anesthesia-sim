"""Tests for the command line, exercised end to end against a temporary store.

The helpers below build scratch repositories with real git, one per test. That
is affordable only because the repository root's `conftest.py` keeps the
developer's global git configuration out of them: with it reaching in, a
single `commit.gpgsign = true` made every commit here cost about fifteen times
as much, and the bill looked
like it belonged to these helpers rather than to a setting none of them names
(`PL-YRYR`, measured 2026-09-21).
"""

from __future__ import annotations

import argparse
import ast
import inspect
import os
import re
import subprocess
import sys
from collections.abc import Callable
from dataclasses import replace as with_fields
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from docket import arming, claims, cli, vcs
from docket.checks import STATUS_REQUIREMENTS, brief_gaps
from docket.claims import CUTOVER_MARKER, SESSION_VARIABLE, Holdings
from docket.cli import build_parser, main, merge_shared
from docket.config import Config
from docket.model import parse_item, recurrence_count
from docket.vcs import commands_written_here, lost, records_on_base
from docket.verify import LANDED_GUARD, GitUnanswered

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


def _run_with_git(*args: str) -> int:
    """`_run` for a test of a git read itself, which `--no-git` stops (`PL-NGBM`)."""
    return main([*args, "--today", "2026-08-24"])


@pytest.fixture(autouse=True)
def _no_inherited_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clear the re-entry guard this suite may have inherited.

    The same fixture `test_verify.py` carries, and needed here for the same
    reason once `check --verify` became a thing CI runs: that run sets
    `DOCKET_SKIP_LANDED` for every command it executes, and one of those
    commands is `PL-P3B6`'s own `verify:`, which runs this file. Without this,
    `test_check_replays_verify_commands_when_asked` reads the declined report
    meant for a nested run and fails in CI while passing by hand - which is the
    environment-dependent result the guard's own check exists to make visible.
    """
    monkeypatch.delenv(LANDED_GUARD, raising=False)


@pytest.fixture(autouse=True)
def _no_session(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the session running the suite from deciding `mine` for any claim read here.

    `test_claims.py`'s fixture, for the release fixtures below that cut under a
    claim: a claim's `mine` is decided by this variable where it carries a token.
    """
    monkeypatch.delenv(SESSION_VARIABLE, raising=False)


def test_new_captures_several_ideas_in_one_call(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Interruptions rarely carry exactly one thought."""
    store = _store(tmp_path)
    assert _run("new", "First idea", "Second idea", "--items", str(store)) == 0

    written = sorted(store.glob("*.md"))
    assert len(written) == 2
    assert len({p.name.split("-")[1] for p in written}) == 2


def test_touches_before_the_title_no_longer_swallows_it(tmp_path: Path) -> None:
    """The capture path is the one place in this project meant to be frictionless.

    `--touches` was `nargs="*"`, so it consumed the title and argparse then
    reported the title as missing - naming the one thing that had been supplied.
    Capture has to work when usage is nearly spent and a thought is one
    interruption from gone, so a plausible argument order failing is friction in
    exactly the wrong place (`PL-YNCW`).
    """
    store = _store(tmp_path)

    # The brief's own reproduction, unquoted path and all: under `nargs="*"` this
    # raised `SystemExit` from argparse's "the following arguments are required:
    # title", having just been handed one.
    exit_code = _run(
        "new",
        "--feature",
        "parallel-sessions",
        "--touches",
        "src/a.py",
        "Some title",
        "--items",
        str(store),
    )

    assert exit_code == 0
    written = sorted(store.glob("*.md"))
    assert len(written) == 1
    body = written[0].read_text()
    assert "title: Some title" in body
    assert "touches: src/a.py" in body
    assert "feature: parallel-sessions" in body


def test_touches_may_be_repeated_as_well_as_comma_separated(tmp_path: Path) -> None:
    """Both spellings reach the same field, so neither order has to be remembered."""
    store = _store(tmp_path)

    assert (
        _run(
            "new",
            "--touches",
            "src/a.py",
            "--touches",
            "src/b.py,src/c.py",
            "One idea",
            "--items",
            str(store),
        )
        == 0
    )

    assert "touches: src/a.py, src/b.py, src/c.py" in next(store.glob("*.md")).read_text()


CLUSTERED = """---
id: PL-G5G5
title: alpha beta gamma delta epsilon zeta
priority: P2
effort: M
status: ready
classes: defect
touches: z.py
added: 2026-08-01
---

**Problem.** x
**Why it matters.** y
**Done when.** z
"""

SUPPRESSION = """---
id: PL-C1C1
title: verify's suppression check reads prose as code
priority: P2
effort: M
status: ready
classes: defect
touches: subprojects/docket/src/docket/verify.py
added: 2026-08-01
---

**Problem.** x
**Why it matters.** y
**Done when.** z
"""


def test_new_names_an_existing_item_with_a_near_identical_title(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The warning that was missing while one defect was diagnosed five times.

    `PL-LBR6` sat `ready` for six days with the `docket record` rename
    diagnosed while `PL-5QLP` and `PL-QMC0` were filed as fresh discoveries of
    it, and the suppression-check defect was captured five times across two
    days. Every one of those sessions ran this command, which held the title,
    the store and the session's attention, and said nothing.

    **It warns and still files.** The capture rule is unconditional, so the
    exit code, the id and the written file are all unchanged - a session whose
    finding is a genuine second instance must not be stopped, and neither must
    one that stops reading after the first line.
    """
    store = _store(tmp_path, SUPPRESSION)

    exit_code = _run(
        "new",
        "--touches",
        "subprojects/docket/src/docket/verify.py",
        "verify's suppression check reads every added line as code",
        "--items",
        str(store),
    )

    assert exit_code == 0
    assert len(sorted(store.glob("*.md"))) == 2

    printed = capsys.readouterr().out
    assert "PL-C1C1" in printed
    assert "(ready)" in printed
    assert "subprojects/docket/src/docket/verify.py" in printed


def test_new_records_the_filing_on_the_item_it_matched(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The evidence written down, instead of waiting for a session to notice it.

    `PL-STC4`'s brief documents its own duplication three separate times in its
    own prose and nothing was promoted until a session read the cluster by
    hand, five captures in. The entry carries the date and the capture's id so
    a reader can open both briefs and decide, which is the judgment a
    similarity score may not make.
    """
    store = _store(tmp_path, SUPPRESSION)

    assert (
        _run(
            "new",
            "--touches",
            "subprojects/docket/src/docket/verify.py",
            "verify's suppression check reads every added line as code",
            "--items",
            str(store),
        )
        == 0
    )

    matched = next(p for p in store.glob("*.md") if "PL-C1C1" in p.read_text())
    filed = next(p for p in store.glob("*.md") if p != matched)
    identifier = re.search(r"^id: (PL-\S+)", filed.read_text(), re.M).group(1)
    assert f"recurrences: 2026-08-24 {identifier}" in matched.read_text()
    assert "Recorded on PL-C1C1: 1 filing matched to it" in capsys.readouterr().out


def test_a_second_filing_extends_the_line_the_first_one_wrote(tmp_path: Path) -> None:
    """The counter accumulates on one item rather than starting over.

    Two entries on one line, because that is what `recurrence_count` reads and
    what `plan.recurring` counts to three. The append is byte-faithful for the
    reason `PL-7K8Y` established - `verify.sanctioned_queue_edit` forgives a
    queue edit that removes nothing, so re-rendering the file would fail the
    close-out of any worker that captured a finding, which `CLAUDE.md` requires
    unconditionally.

    The two capture titles share little with each other and a lot with the
    target, so the second filing matches the target rather than the first
    capture - which is the real ranking, not a contrivance: a session filing
    two unrelated findings against one module is the ordinary case.
    """
    store = _store(tmp_path, CLUSTERED)

    assert _run("new", "--touches", "z.py", "alpha beta gamma theta", "--items", str(store)) == 0
    assert _run("new", "--touches", "z.py", "delta epsilon zeta kappa", "--items", str(store)) == 0

    matched = next(p for p in store.glob("*.md") if "PL-G5G5" in p.read_text())
    entries = re.search(r"^recurrences: (.+)$", matched.read_text(), re.M).group(1)
    assert matched.read_text().count("recurrences: ") == 1
    assert len(entries.split(", ")) == 2


MATCHED = """---
id: PL-D2D2
title: alpha beta gamma delta epsilon zeta
priority: P3
effort: S
status: ready
classes: defect
touches: z.py
added: 2026-08-01
recurrences: 2026-08-20 PL-F6F6, 2026-08-21 PL-G7G7
---

**Problem.** x
**Why it matters.** y
**Done when.** z
"""

#: The item whose brief says why a match was wrong. It declares the store
#: directory, which is where `_store` writes every item, so the path advisory
#: stays silent - the condition it fires on is tested separately.
WITHDRAWING = """---
id: PL-H8H8
title: the brief that says why that match was wrong
priority: P3
effort: S
status: ready
classes: infra
touches: items
added: 2026-08-22
---

**Problem.** x
**Why it matters.** y
**Done when.** z
"""


def test_a_recurrence_entry_can_be_withdrawn(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The correction the field had no path for at all, and what shape it takes.

    Two filings were matched onto `PL-SHTR` on shared vocabulary alone, both
    measured afterwards at below the similarity floor `#794` shipped - so the
    matches were false, the field is deliberately outside `docket set`, and
    nothing could unwrite one. A false entry inflates an item toward the
    generator tier, which ranks above every band but `P0` (`PL-34BG`).

    **The entry is annotated, not deleted**, which is the half a deletion
    cannot do: the file goes on saying the match was made and records that it
    was disowned, on this date, citing the brief that says why. A deleted entry
    would leave a file reading as though `docket new` had never matched
    anything, which is a quieter record than the one that was there before.
    """
    store = _store(tmp_path, MATCHED, WITHDRAWING)
    matched = next(p for p in store.glob("*.md") if "PL-D2D2" in p.read_text())
    before = matched.read_text()

    exit_code = _run(
        "withdraw", "PL-D2D2", "PL-F6F6", "--because", "PL-H8H8", "--items", str(store)
    )

    assert exit_code == 0
    after = matched.read_text()
    assert (
        "recurrences: 2026-08-20 PL-F6F6 withdrawn 2026-08-24 PL-H8H8, 2026-08-21 PL-G7G7\n"
        in after
    )
    # Every other byte where it was: the withdrawal's diff is one line, for the
    # reason the append's is (`PL-7K8Y`).
    assert (
        after.replace("2026-08-20 PL-F6F6 withdrawn 2026-08-24 PL-H8H8", "2026-08-20 PL-F6F6")
        == before
    )
    printed = capsys.readouterr().out
    assert "the 2026-08-20 filing from PL-F6F6" in printed
    assert "PL-D2D2 now counts 1 filing" in printed


def test_a_withdrawn_entry_stops_counting_toward_the_generator_tier(tmp_path: Path) -> None:
    """The whole point of the correction: the count the store reports goes down.

    The entry stays in the file, so this is the property that has to be read
    from the count rather than from the text - `docket show` prints the
    withdrawn match under its own heading, outside the filings.
    """
    store = _store(tmp_path, MATCHED, WITHDRAWING)

    assert (
        _run("withdraw", "PL-D2D2", "PL-F6F6", "--because", "PL-H8H8", "--items", str(store)) == 0
    )
    assert (
        _run("withdraw", "PL-D2D2", "PL-G7G7", "--because", "PL-H8H8", "--items", str(store)) == 0
    )

    item = next(p for p in store.glob("*.md") if "PL-D2D2" in p.read_text())
    read = parse_item(item.read_text(encoding="utf-8"), item.name)
    assert recurrence_count(read) == 0
    assert "PL-F6F6" in item.read_text() and "PL-G7G7" in item.read_text()


def test_withdrawing_an_entry_twice_changes_nothing_and_says_so(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A re-run is safe, because the state it asks for is the state that holds.

    Exit 0 rather than a refusal: a command that has to be run exactly once is
    one a session cannot put in a `verify:` line or re-run after a conflict.
    What it must not do is stack a second withdrawal onto the entry, which
    would make the record read as two events.
    """
    store = _store(tmp_path, MATCHED, WITHDRAWING)
    assert (
        _run("withdraw", "PL-D2D2", "PL-F6F6", "--because", "PL-H8H8", "--items", str(store)) == 0
    )
    matched = next(p for p in store.glob("*.md") if "PL-D2D2" in p.read_text())
    once = matched.read_text()
    capsys.readouterr()

    exit_code = _run(
        "withdraw", "PL-D2D2", "PL-F6F6", "--because", "PL-H8H8", "--items", str(store)
    )

    assert exit_code == 0
    assert matched.read_text() == once
    assert "was already withdrawn from PL-D2D2 on 2026-08-24" in capsys.readouterr().out


def test_withdrawing_a_filing_the_item_never_recorded_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A mistyped id writes nothing, and the refusal names what is recorded.

    The alternative is the failure this command exists to correct, one step
    further on: a session that meant to disown one match silently annotating
    nothing, and reading the exit code as proof the entry is gone.
    """
    store = _store(tmp_path, MATCHED, WITHDRAWING)
    matched = next(p for p in store.glob("*.md") if "PL-D2D2" in p.read_text())
    before = matched.read_text()

    exit_code = _run(
        "withdraw", "PL-D2D2", "PL-J9J9", "--because", "PL-H8H8", "--items", str(store)
    )

    assert exit_code == 1
    assert matched.read_text() == before
    assert "records no filing from PL-J9J9; it records PL-F6F6, PL-G7G7" in capsys.readouterr().out


def test_a_withdrawal_warns_where_the_brief_has_not_declared_the_file_it_changes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The `REJECT` this saves, at the only moment anything knows to speak.

    A withdrawal is not exempt from the close-out audit the way `docket new`'s
    append is - it is a deliberate act with something to gain, so the item
    doing it declares the file like any other work. Unsaid, that is a rejected
    close-out at the end of a branch for a path one command would have fixed.

    Silent in the test above, where the brief declares the store: an advisory
    that fires every run is one nobody reads (`PL-ZBJ0`).
    """
    undeclared = WITHDRAWING.replace("touches: items\n", "touches: a.py\n")
    store = _store(tmp_path, MATCHED, undeclared)

    assert (
        _run("withdraw", "PL-D2D2", "PL-F6F6", "--because", "PL-H8H8", "--items", str(store)) == 0
    )

    printed = capsys.readouterr().out
    assert "PL-H8H8 does not declare items/item-0.md" in printed
    assert "outside its commission" in printed


def test_new_infers_candidate_paths_from_the_working_tree(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The hole the fifth filing of the suppression defect fell straight through.

    Nine of thirteen known duplicate pairs share a declared `touches` path and
    the shared-path key finds them; **all four misses are `PL-0KQP`**, which
    `bin/docket new` wrote with no `touches` at all. The session that filed it
    was on a branch whose commits touch
    `subprojects/docket/src/docket/verify.py` - the exact path all four items it
    duplicates declare. The information was there and nothing read it.

    No new argument, no prompt, no refusal: the capture is written exactly as it
    would have been, and the warning is the only difference.
    """
    root = tmp_path / "repo"
    store = root / "items"
    store.mkdir(parents=True)
    (store / "existing.md").write_text(SUPPRESSION, encoding="utf-8")
    target = root / "subprojects" / "docket" / "src" / "docket"
    target.mkdir(parents=True)
    (target / "verify.py").write_text("# the module this session is changing\n", encoding="utf-8")
    for command in (
        ["git", "init", "-q", str(root)],
        ["git", "-C", str(root), "config", "user.email", "t@example.com"],
        ["git", "-C", str(root), "config", "user.name", "T"],
        ["git", "-C", str(root), "add", "-A"],
        ["git", "-C", str(root), "commit", "-qm", "base"],
    ):
        subprocess.run(command, check=True, capture_output=True)
    # Uncommitted, which is where a session usually is when it notices something.
    (target / "verify.py").write_text("# now being changed\n", encoding="utf-8")

    exit_code = main(
        [
            "new",
            "verify's suppression check reads every added line as code",
            "--items",
            str(store),
            "--today",
            "2026-08-24",
        ]
    )

    assert exit_code == 0
    printed = capsys.readouterr().out
    assert "PL-C1C1" in printed
    assert "a path this branch is changing" in printed, "the key's source is named"


def test_a_capture_with_no_git_to_read_is_written_exactly_as_before(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Capture is frictionless or it is not capture.

    A reading git cannot answer leaves the search with no key, so it finds
    nothing and says nothing - rather than falling back to scoring titles
    across the store, which is the refuted key and would fire on the sixteen
    recurring triage passes.
    """
    store = _store(tmp_path, SUPPRESSION)

    assert _run("new", "verify's suppression check reads prose as code", "--items", str(store)) == 0

    assert "PL-C1C1" not in capsys.readouterr().out
    assert len(sorted(store.glob("*.md"))) == 2


def test_new_says_nothing_about_an_item_declaring_a_different_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The refuted key, pinned shut at the command rather than only in the module.

    Title closeness alone catches 0 of 13 known duplicate pairs at any usable
    threshold and finds the sixteen recurring triage passes instead
    (`PL-TZ7T`). So a capture whose title all but matches an open item's is
    still not warned about when the two declare different paths, and a change
    that reversed the key would be a silently worse command rather than a
    failing test.
    """
    store = _store(tmp_path, SUPPRESSION)

    exit_code = _run(
        "new",
        "--touches",
        "src/anesthesia_sim/core/tissue.py",
        "verify's suppression check reads prose as code",
        "--items",
        str(store),
    )

    assert exit_code == 0
    assert "PL-C1C1" not in capsys.readouterr().out


def test_a_space_separated_second_path_is_refused_rather_than_captured_as_a_title(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The failure the parser fix would otherwise have made silent.

    With `--touches` no longer variadic, a space-separated second path lands in
    the title, which would capture an item called `src/b.py` and write it. A loud
    refusal naming the value is the only acceptable outcome; the rule is narrow
    enough that a title anybody meant to write cannot trip it, because a real
    title has a space in it (`PL-YNCW`).
    """
    store = _store(tmp_path)

    exit_code = _run(
        "new", "--touches", "src/a.py", "src/b.py", "Some title", "--items", str(store)
    )

    assert exit_code == 1
    assert list(store.glob("*.md")) == []
    output = capsys.readouterr().out
    assert "src/b.py" in output
    assert "reads as a path rather than a title" in output
    assert "--touches a.py,b.py" in output


def test_a_title_with_a_space_is_never_read_as_a_path(tmp_path: Path) -> None:
    """The guard above may not refuse an ordinary capture that mentions a file."""
    store = _store(tmp_path)

    assert (
        _run(
            "new",
            "--touches",
            "src/a.py",
            "src/controller.py holds the run's storage as well",
            "--items",
            str(store),
        )
        == 0
    )

    assert len(list(store.glob("*.md"))) == 1


def test_a_captured_idea_needs_no_priority(tmp_path: Path) -> None:
    store = _store(tmp_path)
    _run("new", "Half an idea", "--items", str(store))

    assert _run("check", "--items", str(store)) == 0


def test_a_brief_written_into_a_captured_item_leaves_no_template_above_it(tmp_path: Path) -> None:
    """`PL-D188`: capture writes the one line that is true, so appending composes.

    A session holding the brief appends it below what capture wrote. That is
    the operation it was performing when it stranded the four-heading template,
    and it is now the correct one - what is left is a well-formed brief rather
    than a dead stub above one, with nothing to delete before `check` reads the
    item the way its author wrote it.
    """
    store = _store(tmp_path)
    assert _run("new", "The induction curve looks wrong at low flows", "--items", str(store)) == 0

    captured = next(store.glob("*.md"))
    body = captured.read_text(encoding="utf-8")
    assert body.rstrip().endswith("**Problem.** The induction curve looks wrong at low flows")
    assert "**Why it matters.**" not in body

    captured.write_text(
        body
        + "\n**Why it matters.** It is the first curve a resident is shown.\n"
        + "\n**Where.** The uptake model.\n"
        + "\n**Done when.** It matches the published case.\n",
        encoding="utf-8",
    )

    assert _run("check", "--items", str(store)) == 0
    assert captured.read_text(encoding="utf-8").count("**Problem.**") == 1


def test_new_seed_is_not_double_written(tmp_path: Path) -> None:
    """`PL-JL2M`: a seed carrying no empty heading is one no brief can be stranded above.

    Two candidates were on the table - a seed that cannot be double-written,
    and a checker tolerating the double write by accepting any occurrence with
    text under it. The first is preferred because it removes the failure rather
    than detecting it afterwards, and because the second would pass a stub
    whose real brief was never written. What holds it is this: the seed carries
    no heading with nothing under it, so an appended brief has nothing to
    strand, and the sections it has yet to supply report as honestly missing.
    """
    store = _store(tmp_path)
    assert _run("new", "A seed that cannot strand a brief", "--items", str(store)) == 0

    body = next(store.glob("*.md")).read_text(encoding="utf-8").split("---\n")[2]
    missing, empty, stub = brief_gaps(body)

    assert empty == []
    assert stub is None
    assert missing == ["**Why it matters.**", "**Done when.**"]


CAPTURED_OVER_A_TEMPLATE = """---
id: PL-V3V3
title: An idea briefed underneath the headings capture used to write
status: untriaged
added: 2026-08-20
---

**Problem.** An idea briefed underneath the headings capture used to write

**Why it matters.**

**Where.**

**Done when.**

**Problem.** The real brief, written below the template rather than over it.

**Why it matters.** The stub is what the checker reads.

**Done when.** The stub is gone.
"""


def test_a_stub_left_above_a_brief_fails_the_check_while_the_item_is_untriaged(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-D188`: caught in the session that wrote it, not at a triage pass weeks on.

    The brief checks exempt an untriaged capture, and rightly - demanding a
    brief at the moment an idea occurs is how ideas stop being written down.
    This one is exempt from that exemption because it demands nothing: writing
    less can never trigger it, only writing a brief and leaving a template
    above it. `make docket` is what a session runs after editing the store, so
    the shape is reported to the session that created it.
    """
    store = _store(tmp_path, CAPTURED_OVER_A_TEMPLATE)

    assert _run("check", "--items", str(store)) == 1
    output = capsys.readouterr().out
    assert "the capture template is still above the brief" in output
    assert "brief has nothing under" not in output


def test_check_exits_nonzero_on_a_broken_store(tmp_path: Path) -> None:
    store = _store(tmp_path, READY, READY)

    assert _run("check", "--items", str(store)) == 1


def test_check_exits_zero_on_a_clean_store(tmp_path: Path) -> None:
    assert _run("check", "--items", str(_store(tmp_path, READY))) == 0


def test_check_names_the_config_file_it_loaded(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Which policy a store was read under is a fact about the run (`PL-K5PW`).

    Named on the run that found its config as well as on the run that did not,
    so that the two are distinguishable: silence would read the same as a
    version of the command that reports nothing, and it is the difference
    between the two lines that carries the diagnosis. Pinning the found case to
    the exact path is what makes a regression of `PL-P757` - root resolution
    moving again, so a different `docket.toml` is read - fail here rather than
    pass quietly.
    """
    store = _store(tmp_path, READY)
    (tmp_path / "docket.toml").write_text("[docket]\n", encoding="utf-8")

    assert _run("check", "--items", str(store)) == 0
    line = capsys.readouterr().out.splitlines()[1]
    assert line.strip() == f"settings: {tmp_path / 'docket.toml'}"


def test_check_says_when_it_found_no_config_beside_the_store(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The half that carries the diagnosis (`PL-K5PW`, filed twice).

    A store whose repository holds no `docket.toml` runs on package defaults,
    which is a supported way to use this tool and not a fault. What was missing
    was any way to tell that from the output: `PL-P757` put the whole of this
    project's store on defaults by resolving the root from the store's parent,
    and that was the quietest of the three failures it caused - found only
    incidentally, because no run said which policy it had been read under.

    So this pins the text a reader needs to reach that conclusion, not merely
    that some line appears. The store here is clean, so the line stands alone
    rather than beside findings it would explain: what is under test is that
    the reading is named, not that a wrong policy produced errors.
    """
    store = _store(tmp_path, READY)
    assert not (tmp_path / "docket.toml").exists()

    assert _run("check", "--items", str(store)) == 0
    line = capsys.readouterr().out.splitlines()[1]
    assert line.strip().startswith(f"settings: no {tmp_path / 'docket.toml'},")
    assert "library defaults govern this run" in line


#: A `ready` item - one of `LANDED_STATUSES` - whose `verify:` command leaves a
#: file behind. Whether that file exists after a run is the only direct evidence
#: that the command was executed, which is what the two tests below turn on.
#:
#: It fails after marking, deliberately. A command exiting 0 would be reported
#: as already passing, which is an error, so the run's exit status would then
#: answer "did the replay find something" rather than "did the replay happen" -
#: and the marker is the thing under test. Failing is also the shape a `ready`
#: item's command is supposed to have before its work exists.
MARKING = """---
id: PL-M4RK
title: An item whose command leaves a trace
priority: P1
effort: S
status: ready
classes: perf
touches: a.py
verify: touch ran.marker && false
added: 2026-08-01
---

**Problem.** x
**Why it matters.** y
**Done when.** z
"""


def test_check_does_not_replay_verify_commands_unless_asked(tmp_path: Path) -> None:
    """The store validation is the gate; the replay is not (`PL-P3B6`).

    Running every open item's command was 31 s of `make check`'s 67 s, for a
    finding about work that had already *merged* - which a pre-commit gate on a
    feature branch cannot have changed. The command still runs in CI, which
    passes `--verify`.
    """
    store = _store(tmp_path, MARKING)

    assert _run("check", "--items", str(store)) == 0
    assert not (tmp_path / "ran.marker").exists()


def test_check_replays_verify_commands_when_asked(tmp_path: Path) -> None:
    """The other half: `--verify` is what CI runs, so it has to still do it."""
    store = _store(tmp_path, MARKING)

    assert _run("check", "--verify", "--items", str(store)) == 0
    assert (tmp_path / "ran.marker").exists()


def test_verify_base_outside_a_repository_declines_the_replay(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`--verify-base` is the flag CI passes on a pull request (`PL-SDHR`).

    Outside a repository both of the replay's halves decline now, so it
    declines whole and says why, rather than running nothing and reporting
    clean. This test once asserted that as the flag narrowing, because
    `changed_items` read `git diff`'s exit 1 there as git answering no. It
    declines since `PL-19T3`, and `changed_paths` since `PL-9RFP`. Narrowing
    proper, a base that resolves with nothing changed, is the first half of
    `test_a_branch_that_invalidates_another_item_s_command_replays_it`.
    """
    store = _store(tmp_path, MARKING)

    assert (
        _run_with_git(
            "check", "--verify", "--verify-base", "docket-no-such-ref", "--items", str(store)
        )
        == 0
    )
    printed = capsys.readouterr().out
    assert not (tmp_path / "ran.marker").exists()
    assert "not checked" in printed
    assert "could not be read" in printed


def test_verify_refuses_a_base_no_candidate_resolved(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The commission audit is a claim about a base, so a guessed one voids it.

    `PL-73P0`, and worse than the silent clean it was filed as. `changed_paths`
    asks for `diff --name-only <base>...HEAD`, discards the exit status, and
    `_run` returns git's *combined* output - so on a checkout with no default
    branch the audit reads git's three-line fatal message as three changed
    paths. Measured 2026-09-22: it reported `fatal: ambiguous argument
    'main...HEAD'...` as a path outside the commission, and named neither of
    the two files the branch had actually changed.

    A real repository rather than an injected runner, because what is under
    test is the whole path from `default_base`'s probe through to the refusal.
    """
    subprocess.run(
        ["git", "init", "--quiet", "--initial-branch=feature", str(tmp_path)], check=True
    )
    for setting, value in (("user.email", "t@example.invalid"), ("user.name", "Test")):
        subprocess.run(["git", "config", setting, value], cwd=tmp_path, check=True)
    store = tmp_path / "docs" / "items"
    store.mkdir(parents=True)
    (store / "item-0.md").write_text(MARKING, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", "PL-M4RK Seed"], cwd=tmp_path, check=True)

    assert _run_with_git("verify", "PL-M4RK", "--items", str(store)) == 1
    out = capsys.readouterr().out
    assert "no candidate default branch resolved" in out
    assert "--base <ref>" in out
    # What it must no longer do: report git's own complaint as a finding about
    # the branch, on a check whose whole job is to certify that branch's scope.
    assert "fatal:" not in out
    assert "ambiguous argument" not in out


#: An item whose command reads a file, so that editing the file - and nothing
#: else - can change what the command returns. `touch` runs first so the marker
#: says the command was executed at all, which is the question the scope is
#: being tested on.
READING = """---
id: PL-R34D
title: An item whose command reads a file it does not own
priority: P1
effort: S
status: ready
classes: perf
touches: a.py
verify: touch ran.marker && grep -q sentinel README.md
added: 2026-08-01
---

**Problem.** x
**Why it matters.** y
**Done when.** z
"""


def _reading_repo(tmp_path: Path) -> tuple[Path, str]:
    """A checkout holding `READING`, and the base its branch is measured against.

    The file is named as the store names one - `<id>-<slug>.md` - because half
    the replay's scope is read out of a diff, and `vcs.ITEM_FILE_RE` recovers
    the id from the file name. Under any other name a branch that edits the
    item is a branch that changed no item, which is not the store's behaviour
    and would have hidden `PL-WF3X` from the test below.
    """
    root = tmp_path / "repo"
    (root / "items").mkdir(parents=True)
    (root / "items" / "PL-R34D-reading.md").write_text(READING, encoding="utf-8")
    (root / "README.md").write_text("nothing here yet\n", encoding="utf-8")
    # A real checkout, for the reason `_release_repo` gives: the scope is read
    # from a diff, so a stub would test the stub.
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        subprocess.run(["git", "config", name, value], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True, capture_output=True)
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()
    return root, base


def test_a_branch_that_invalidates_another_item_s_command_replays_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The end-to-end shape of `PL-XMNC`, through the flag CI actually passes.

    The branch never opens `PL-R34D`'s item file; it writes the word its
    command greps for. Scoped to the items a branch edited, that replayed
    nothing and the break surfaced only on the whole-store sweep after the
    merge - six recorded times.
    """
    root, base = _reading_repo(tmp_path)
    store = str(root / "items")

    # Nothing changed yet, so the command is out of scope and does not run.
    assert _run_with_git("check", "--verify", "--verify-base", base, "--items", store) == 0
    assert not (root / "ran.marker").exists()

    (root / "README.md").write_text("sentinel\n", encoding="utf-8")

    assert _run_with_git("check", "--verify", "--verify-base", base, "--items", store) == 1
    assert (root / "ran.marker").exists()
    printed = capsys.readouterr().out
    assert "PL-R34D" in printed
    assert "whose `verify:` command reads a file it changed" in printed


def test_a_base_a_repository_cannot_resolve_declines_the_replay(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The shape CI produces: a shallow clone whose base ref was never fetched.

    Inside a repository `git diff --name-only <base>...HEAD` exits 128 for a
    base that does not resolve, and the empty set that came back was
    indistinguishable from a branch that changed no item file. The replay was
    scoped to nothing, ran nothing, and the run reported a clean result - on
    the gate a pull request is held to. The reason travels with the answer now
    (`PL-ZPDM`), so the replay declines whole and the headline counts it.

    Still exit 0, deliberately: "not checked" is not a finding about the store,
    and `Report.declined` is the channel that keeps the two apart.
    """
    root, _ = _reading_repo(tmp_path)
    store = str(root / "items")

    assert (
        _run_with_git("check", "--verify", "--verify-base", "docket-no-such-ref", "--items", store)
        == 0
    )

    printed = capsys.readouterr().out
    assert not (root / "ran.marker").exists()
    assert "not checked" in printed
    assert "scoped to what this branch changed against docket-no-such-ref" in printed
    assert "could not be read" in printed


def test_a_changed_file_list_git_does_not_answer_declines_the_replay(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The replay's second half declines on its own read, not only on the first's.

    `changed_items` can answer where `changed_paths` cannot, for example a
    `git status` refused by a damaged index. The second half is the one that
    replays a command the branch *invalidates*. Until `PL-9RFP` its failure
    came back as git's complaint read as paths, which matched no command. That
    scoped the half to nothing on exactly the branch below, which edits the
    file `PL-R34D`'s command reads.
    """
    root, base = _reading_repo(tmp_path)
    (root / "README.md").write_text("sentinel\n", encoding="utf-8")

    def unanswered(*_: object) -> tuple[str, ...]:
        raise GitUnanswered("`git status` exited 128: fatal: index file corrupt")

    monkeypatch.setattr(cli, "changed_paths", unanswered)

    assert (
        _run_with_git("check", "--verify", "--verify-base", base, "--items", str(root / "items"))
        == 0
    )
    printed = capsys.readouterr().out
    assert not (root / "ran.marker").exists()
    assert "not checked" in printed
    assert "index file corrupt" in printed


def test_the_replay_scope_reads_the_store_the_run_was_pointed_at(tmp_path: Path) -> None:
    """The other half of the same addressing bug, on the scope rather than a count.

    `cmd_check` took the replay's scope diff against `config.items_dir` while
    `--items` decided which store was read, so a queue anywhere else had its
    diff taken against a directory it does not live in: the branch's own item
    came back unchanged, the replay was scoped to nothing, and a scoped
    `--verify` run reported a clean result having replayed nothing
    (`PL-WF3X`). The store here sits at `items/`, which is where the defect is
    visible and where a store that is not this project's usually sits.

    The marker is the evidence, because it is written by the command itself:
    the branch edits `PL-R34D`'s own file and nothing else, so the item is in
    scope through `changed_items` alone - `items_reading`, the other half,
    matches a command against the paths a branch changed and this command
    names only `README.md`, which is untouched here. Exit 0 with the command
    having run is the open item's ordinary state: it greps for a sentinel the
    README does not carry, so the replay finds nothing already passing.
    """
    root, base = _reading_repo(tmp_path)
    store = root / "items"
    item = store / "PL-R34D-reading.md"
    item.write_text(
        item.read_text(encoding="utf-8").replace("classes: perf", "classes: perf, defect"),
        encoding="utf-8",
    )

    assert _run_with_git("check", "--verify", "--verify-base", base, "--items", str(store)) == 0

    assert (root / "ran.marker").exists()


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


def test_next_computes_the_flight_report_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`next` asked twice, and every ask shells out to git per branch ref (`PL-PMT7`).

    `cmd_next` and `cmd_digest` each reached the report twice - once through
    `_offered`, once directly. Measured on a four-core container, `next` issued 26
    git subprocesses where `flight` and `status` issued 13, and roughly 180 ms of
    its ~460 ms was the repeated work.

    Asserted as a count of computations rather than as a duration, because the
    duration is the machine's and the count is the defect. `digest` is checked
    beside it: the two shared the shape and a cache that only covered one would
    leave the other paying.
    """
    calls: list[str] = []

    def counted(
        root: Path, *, now: datetime, items_dir: str = "docs/items", runner: object = None
    ) -> Holdings:
        calls.append(items_dir)
        return Holdings(now=now)

    monkeypatch.setattr("docket.cli.holdings", counted)
    store = str(_store(tmp_path, READY))
    # `_run` passes `--no-git`, which short-circuits the read this is about, so
    # the parser is driven directly here.
    ran = ["--items", store, "--today", "2026-08-24"]

    main([*ran, "next"])
    assert len(calls) == 1

    calls.clear()
    main([*ran, "digest"])
    assert len(calls) == 1


def test_the_flight_cache_does_not_outlive_one_invocation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One process, one answer - and never an answer carried into the next command.

    The cache lives on the `argparse` namespace precisely so that its lifetime is
    the invocation's. A module-level cache would be faster still and wrong: a
    caller ranking against a stale view of what is in flight hands a session an
    item another session is holding, which is the collision the read exists to
    prevent.
    """
    calls: list[str] = []

    def counted(
        root: Path, *, now: datetime, items_dir: str = "docs/items", runner: object = None
    ) -> Holdings:
        calls.append(items_dir)
        return Holdings(now=now)

    monkeypatch.setattr("docket.cli.holdings", counted)
    store = str(_store(tmp_path, READY))
    ran = ["--items", store, "--today", "2026-08-24"]

    main([*ran, "next"])
    main([*ran, "next"])

    assert len(calls) == 2


@pytest.mark.parametrize("unbuffered", [True, False], ids=["unbuffered", "buffered"])
def test_a_reader_that_stops_early_ends_the_command_quietly(
    tmp_path: Path, unbuffered: bool
) -> None:
    """`bin/docket next | head -3` must not end in a traceback (`PL-VJPJ`).

    Driven as a real process on a real pipe, because each half of the defect
    lived where no in-process call reaches. Unbuffered, which is how these
    sessions run Python, the first `print` after the reader went raised a
    traceback. Buffered, as in a terminal, nothing raised until the
    interpreter's own flush at exit, which printed "Exception ignored" and
    changed the status to 120. The read end is closed before the command
    starts, so the first write fails on every run rather than whenever `head`
    happens to exit, and the status proves that write was attempted at all.
    """
    argv = ["next", "--items", str(_store(tmp_path, READY)), "--no-git", "--today", "2026-08-24"]
    env = {name: value for name, value in os.environ.items() if name != "PYTHONUNBUFFERED"}
    env["PYTHONPATH"] = str(Path(cli.__file__).resolve().parents[1])
    if unbuffered:
        env["PYTHONUNBUFFERED"] = "1"
    read_end, write_end = os.pipe()
    os.close(read_end)
    try:
        done = subprocess.run(
            [sys.executable, "-m", "docket", *argv],
            stdout=write_end,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            check=False,
        )
    finally:
        os.close(write_end)

    assert done.stderr == ""
    assert done.returncode == cli.READER_CLOSED


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
    """A store holding one delegable item and four that must not be offered."""
    items = tmp_path / "docs" / "items"
    items.mkdir(parents=True)
    # Config is resolved from the store's parent, not the working directory,
    # so it belongs beside `docs/` here.
    (items.parent / "docket.toml").write_text(
        '[docket]\nprotected_paths = ["src/core"]\n', encoding="utf-8"
    )
    brief = "**Problem.** P\n**Why it matters.** W\n**Done when.** D\n"
    for ident, extra in (
        ("PL-8888", "verify: pytest tests/test_a.py\ntouches: tests/test_a.py\n"),
        ("PL-BBBB", "touches: tests/test_b.py\n"),  # no verify command
        ("PL-CCCC", "verify: pytest\ntouches: src/core/x.py\n"),  # protected
        ("PL-DDDD", "verify: pytest\ntouches: tests/test_d.py\nclasses: safety\n"),
        # A gate path, and deliberately from the package default rather than
        # from the config written above: this is the end-to-end guard that
        # `cmd_delegable` passes `gate_paths` through at all, which no unit
        # test of `Item.delegability` can see (`PL-S2L4`).
        ("PL-GGFF", "verify: pytest\ntouches: Makefile\n"),
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
    """Four of the five items must not be offered, each for a different reason."""
    assert main(["--items", str(_delegable_store(tmp_path)), "--no-git", "delegable"]) == 0
    out = capsys.readouterr().out
    assert "PL-8888" in out
    assert "verify: pytest tests/test_a.py" in out
    for excluded in ("PL-BBBB", "PL-CCCC", "PL-DDDD", "PL-GGFF"):
        assert excluded not in out


def test_delegable_sends_the_worker_to_the_instructions_that_qualify_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """This one line is the whole delivery path for the decision-section rule.

    `docs/worker.md` carries the rule that a `**Decision needed.**` heading on
    an offered item is a record of a settled question rather than a live one -
    the answer is written underneath it, 16 to 46 lines below across the four
    items that carried the section on 2026-09-22. Without that rule a worker
    meets the heading, reads it as an unclear brief under "Stop. Do not guess.",
    and returns the item: the round trip `delegable` exists to remove
    (`PL-NJ9M`).

    The listing cannot annotate the items themselves, and deliberately does not
    try. Nothing in the front matter distinguishes an answered decision section
    from an open one - that reading is prose, which is the judgment half - so
    the guidance is standing rather than per-item. Which makes this footer the
    only thing carrying it to a worker, and it was untested.
    """
    assert main(["--items", str(_delegable_store(tmp_path)), "--no-git", "delegable"]) == 0
    assert "docs/worker.md" in capsys.readouterr().out


def test_delegable_says_so_when_nothing_qualifies(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An empty result must read as 'nothing to do', not as a broken command."""
    items = tmp_path / "docs" / "items"
    items.mkdir(parents=True)
    (items / "PL-GGGG-x.md").write_text(
        "---\nid: PL-GGGG\ntitle: Item\npriority: P1\neffort: S\nstatus: ready\n"
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
    assert "the project stands on v0.3.0 — the foundation" in out
    assert "clears it" not in out
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


#: The release item every cut below is made under. Untriaged, so it changes no
#: count a release test asserts: a cut ships finished work only.
TRAIN_ITEM = """---
id: PL-TR4N
title: Cut the release
status: untriaged
resource: release-train
added: 2026-08-01
---

**Problem.** Cut the release
"""

#: The branch those cuts are made from, named the way a session names one.
TRAIN_BRANCH = "claude/pl-tr4n-cut-the-release"


def _hold_the_train(root: Path, store: str = "items") -> None:
    """Move `root` onto a branch whose live claim on a release item holds the release train.

    `bin/docket release` refuses a branch holding no train claim (`PL-331V`),
    so every fixture that cuts takes this step first, as release mode does.
    The claim is the empty commit `claim` writes, made after the cutover marker
    is in the tree so it is read by the current rules, and dated by the clock
    so its lease is live when the command reads it.
    """

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        git("config", name, value)
    git("checkout", "-q", "-b", TRAIN_BRANCH)
    marker = root / CUTOVER_MARKER
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("# the claim reader\n", encoding="utf-8")
    (root / store / "PL-TR4N-cut-the-release.md").write_text(TRAIN_ITEM, encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "PL-TR4N: file the release")
    git("commit", "-q", "--allow-empty", "-m", f"PL-TR4N: start\n\nClaim: PL-TR4N {TRAIN_BRANCH}")


def _release_repo(tmp_path: Path, *tag_names: str, git: bool = True) -> Path:
    """A repository with one unreleased item, a version, and the tags given.

    `git=False` leaves it a plain directory, which is how a real `git tag
    --list` is made to fail: it exits 128 outside a repository, and how that
    exit is classified is half of what the refusal below is tested on.

    With git, the checkout is left on `TRAIN_BRANCH` holding the release train,
    and `main` is the base the tags sit on.
    """
    root = tmp_path / "repo"
    (root / "items").mkdir(parents=True)
    (root / "items" / "done.md").write_text(DONE, encoding="utf-8")
    (root / "pyproject.toml").write_text('[project]\nversion = "0.2.5"\n', encoding="utf-8")
    if not git:
        return root
    # A real git checkout, built by running real git from `PATH`: the release
    # commands read tags and refs, so a stub would test the stub.
    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(root)],
        check=True,
        capture_output=True,
    )
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        subprocess.run(["git", "config", name, value], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True, capture_output=True)
    for tag in tag_names:
        subprocess.run(["git", "tag", tag], cwd=root, check=True, capture_output=True)
    _hold_the_train(root)
    return root


def test_a_release_is_refused_while_the_previous_one_is_untagged(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Cutting on top of an untagged release extends a gap nothing can close later."""
    root = _release_repo(tmp_path, "v0.2.3")

    assert main(["release", "0.2.6", "--items", str(root / "items")]) == 1
    assert "v0.2.5 shipped and carries no tag" in capsys.readouterr().out
    assert 'version = "0.2.5"' in (root / "pyproject.toml").read_text()


def test_a_release_is_refused_where_git_will_not_say_which_tags_exist(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A silence is not "this project does not tag", and this gate turns on that.

    `is_untagged` holds a project with no tags to nothing, which is right for a
    repository that answered and was free passage for one that did not: the
    same empty set came back from a `git tag --list` that failed, so the one
    gate guarding a gap nothing can repair afterwards skipped itself with
    nothing said (`PL-ZPDM`).

    The untagged warning is deliberately not what prints. It asserts a specific
    fact - v0.2.5 carries no tag - which is exactly what has not been
    established here, and sends the operator to push a tag that may exist.
    """
    root = _release_repo(tmp_path, git=False)

    assert main(["release", "0.2.6", "--items", str(root / "items")]) == 1

    printed = capsys.readouterr().out
    assert "Cannot tell whether v0.2.5 is tagged" in printed
    assert "shipped and carries no tag" not in printed
    assert 'version = "0.2.5"' in (root / "pyproject.toml").read_text()


def test_a_release_proceeds_once_the_previous_one_is_tagged(tmp_path: Path) -> None:
    root = _release_repo(tmp_path, "v0.2.5")

    assert main(["release", "0.2.6", "--items", str(root / "items")]) == 0
    assert 'version = "0.2.6"' in (root / "pyproject.toml").read_text()


def test_a_cut_does_not_rename_the_files_it_stamps(tmp_path: Path) -> None:
    """`milestone:` is a field write like `pr:`, and renamed for the same reason.

    A release stamps a whole batch in one commit, so one drifted name among
    them put a rename nobody asked for into the commit a release tag points at
    (`PL-LBR6`). `done.md` is the shape: a file whose name its title no longer
    generates.
    """
    root = _release_repo(tmp_path, "v0.2.5")

    assert main(["release", "0.2.6", "--items", str(root / "items")]) == 0

    stamped = root / "items" / "done.md"
    assert sorted(path.name for path in (root / "items").glob("*.md")) == [
        "PL-TR4N-cut-the-release.md",
        "done.md",
    ]
    assert "milestone: v0.2.6" in stamped.read_text(encoding="utf-8")


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


def test_a_release_the_default_branch_already_holds_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-66FP: two sessions cut v0.3.7, and no guard could see the second one.

    A release carries no item id, so a read of item ids alone is blind to
    it. What the default branch already holds is the
    part of that which is certain, and this is the command proving it is read
    from git as git actually spells it.
    """
    root = _release_repo(tmp_path, "v0.2.5")
    subprocess.run(["git", "checkout", "-q", "main"], cwd=root, check=True, capture_output=True)
    notes = root / "docs" / "releases"
    notes.mkdir(parents=True)
    (notes / "v0.2.6.md").write_text("## v0.2.6\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-qm", "Release v0.2.6"], cwd=root, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "checkout", "-q", TRAIN_BRANCH], cwd=root, check=True, capture_output=True
    )

    assert main(["release", "0.2.6", "--items", str(root / "items")]) == 1
    output = capsys.readouterr().out
    assert "v0.2.6 is already released on" in output
    assert "docs/releases/v0.2.6.md is on it" in output
    assert 'version = "0.2.5"' in (root / "pyproject.toml").read_text()


def test_a_base_already_bumped_to_the_version_refuses_it_too(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The version field catches a release landed without notes this can read."""
    root = _release_repo(tmp_path, "v0.2.5")

    assert main(["release", "0.2.5", "--items", str(root / "items")]) == 1
    assert "its pyproject.toml already reads 0.2.5" in capsys.readouterr().out


def test_a_dry_run_says_the_release_is_already_out_and_still_shows_the_notes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Withholding the preview would not un-ship what already shipped."""
    root = _release_repo(tmp_path, "v0.2.5")

    assert main(["release", "0.2.5", "--dry-run", "--items", str(root / "items")]) == 0
    output = capsys.readouterr().out
    assert "is already released on" in output
    assert "PL-D1D1" in output


def test_a_version_the_default_branch_has_not_seen_is_cut_as_before(tmp_path: Path) -> None:
    root = _release_repo(tmp_path, "v0.2.5")

    assert main(["release", "0.2.6", "--items", str(root / "items")]) == 0
    assert (root / "docs" / "releases" / "v0.2.6.md").is_file()


def _side_cut(root: Path, version: str) -> None:
    """A second branch carrying a release nobody has merged, left off the base."""
    base = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    subprocess.run(["git", "checkout", "-qb", "sidecut"], cwd=root, check=True, capture_output=True)
    notes = root / "docs" / "releases"
    notes.mkdir(parents=True, exist_ok=True)
    (notes / f"v{version}.md").write_text(f"## v{version}\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-qm", f"Release v{version}"], cwd=root, check=True, capture_output=True
    )
    subprocess.run(["git", "checkout", "-q", base], cwd=root, check=True, capture_output=True)


def test_a_release_another_branch_is_already_cutting_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-66FP: the half the default branch cannot see, which is the half that raced.

    The v0.3.7 collision was between two *unmerged* cuts, so a check reading
    only the base would have passed both.
    """
    root = _release_repo(tmp_path, "v0.2.5")
    _side_cut(root, "0.2.6")

    assert main(["release", "0.2.6", "--no-fetch", "--items", str(root / "items")]) == 1
    output = capsys.readouterr().out
    assert "A release is already being cut on a branch nothing has merged" in output
    assert "sidecut is cutting v0.2.6" in output
    assert 'version = "0.2.5"' in (root / "pyproject.toml").read_text()


def test_a_cut_of_a_different_version_is_refused_too(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Two concurrent releases under different numbers is the worse case, not the safer one.

    Both stamp `milestone:` onto an overlapping set of items, so whichever
    merges second claims work the first already shipped.
    """
    root = _release_repo(tmp_path, "v0.2.5")
    _side_cut(root, "0.2.6")

    assert main(["release", "0.3.0", "--no-fetch", "--items", str(root / "items")]) == 1
    assert "sidecut is cutting v0.2.6" in capsys.readouterr().out


def test_a_dry_run_names_the_parallel_cut_and_still_shows_the_notes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _release_repo(tmp_path, "v0.2.5")
    _side_cut(root, "0.2.6")

    assert (
        main(["release", "0.2.6", "--no-fetch", "--dry-run", "--items", str(root / "items")]) == 0
    )
    output = capsys.readouterr().out
    assert "already being cut" in output
    assert "PL-D1D1" in output


def test_a_cut_this_checkout_is_carrying_does_not_refuse_it_to_itself(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A session told to yield to itself would stop for nobody."""
    root = _release_repo(tmp_path, "v0.2.5")
    _side_cut(root, "0.2.6")
    subprocess.run(["git", "merge", "-q", "sidecut"], cwd=root, check=True, capture_output=True)

    assert main(["release", "0.3.0", "--no-fetch", "--items", str(root / "items")]) == 0
    assert "already being cut" not in capsys.readouterr().out


def test_a_cut_is_refused_where_the_duplicate_guards_could_not_be_read(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """A git that does not answer must not read as "nobody else is cutting".

    Both guards above look for *evidence* of a parallel cut, so their clean
    answer and their unread answer are the same shape - nothing found. Before
    `PL-Q9Z1` gave the runner a failure channel the two were the same value as
    well, so a silence passed the guard that exists to stop the v0.3.7
    collision (`PL-66FP`). The silence here is real rather than an empty
    string: `answered` is what separates them.
    """
    from docket import vcs

    # No parallel cut exists here: the point is that the guard cannot *tell*,
    # and a real one would be found by the branch above this refusal.
    root = _release_repo(tmp_path, "v0.2.5")
    truthful = vcs._run_git

    def mute_the_notes_listing(args: list[str], where: Path) -> str:
        return vcs.SILENT if "ls-tree" in args else truthful(args, where)

    monkeypatch.setattr(vcs, "_run_git", mute_the_notes_listing)

    assert main(["release", "0.2.6", "--no-fetch", "--items", str(root / "items")]) == 1
    output = capsys.readouterr().out
    assert "Cannot check whether another session is already cutting" in output
    assert 'version = "0.2.5"' in (root / "pyproject.toml").read_text()


def test_a_release_refreshes_the_refs_before_deciding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """PL-66FP: without this, neither release guard is worth asking.

    The session that lost the v0.3.7 race cut from a checkout that did not yet
    hold an item merged eight minutes before the winning release landed, so
    every ref it could read was older than the collision it was in. The item
    assumed the session-start fetch was enough; it was not.
    """
    root = _release_repo(tmp_path, "v0.2.5")
    fetched: list[Path] = []
    monkeypatch.setattr("docket.cli.fetch_remote", lambda where, runner: fetched.append(where))

    assert main(["release", "0.2.6", "--items", str(root / "items")]) == 0
    assert fetched == [root]


def test_no_fetch_is_honored_for_a_caller_that_refreshed_or_cannot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _release_repo(tmp_path, "v0.2.5")
    fetched: list[Path] = []
    monkeypatch.setattr("docket.cli.fetch_remote", lambda where, runner: fetched.append(where))

    assert main(["release", "0.2.6", "--no-fetch", "--items", str(root / "items")]) == 0
    assert fetched == []


def test_no_git_skips_the_release_guards_entirely(tmp_path: Path) -> None:
    root = _release_repo(tmp_path, "v0.2.5")
    _side_cut(root, "0.2.6")

    assert main(["release", "0.2.6", "--no-git", "--items", str(root / "items")]) == 0


def test_a_version_file_the_bump_rejects_leaves_the_items_unstamped(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-DL1X: a bump the version file rejects strands no stamp.

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


class _ContainerLost(Exception):
    """The container going away part way through a write, as a raisable thing.

    Not `KeyboardInterrupt`, which pytest treats as a signal to abandon the
    whole session rather than as a failure a test can assert on. What the
    tests below need is only that the writes stop part way and the tree is
    left in the state that leaves.
    """


def _interruptible_repo(tmp_path: Path, count: int) -> Path:
    """A release repository holding `count` finished items instead of one."""
    root = _release_repo(tmp_path, "v0.2.5")
    for index in range(count - 1):
        identifier = f"PL-G{index}G{index}"
        (root / "items" / f"done-{index}.md").write_text(
            DONE.replace("PL-D1D1", identifier).replace(
                "title: A finished item", f"title: Another finished item {index}"
            ),
            encoding="utf-8",
        )
    return root


def _interrupt_after(monkeypatch: pytest.MonkeyPatch, written: int) -> None:
    """Stop `cmd_release`'s stamp loop part way through, as a lost container does."""
    real = cli.rewrite_item
    seen = 0

    def stop(*args: object, **kwargs: object) -> Path:
        nonlocal seen
        if seen >= written:
            raise _ContainerLost("the container went away")
        seen += 1
        return real(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(cli, "rewrite_item", stop)


def test_a_cut_interrupted_inside_the_stamp_loop_is_resumed_whole(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-1MKQ: the re-run used to cut a short release under the full one's name.

    The stamps are written a file at a time and the notes after the whole
    loop, so an interruption inside it leaves work stamped for a release that
    does not exist. `unreleased` reads a stamped item as already shipped, so
    the second run saw only the remainder, wrote notes naming it, bumped and
    exited 0 - a 33-item release recorded as 7, which a person caught by
    reading the two counts side by side and no check would have caught at all.
    """
    root = _interruptible_repo(tmp_path, 4)
    _interrupt_after(monkeypatch, 3)

    with pytest.raises(_ContainerLost):
        main(["release", "0.2.6", "--items", str(root / "items")])

    stamped = [
        path
        for path in (root / "items").glob("*.md")
        if "milestone: v0.2.6" in path.read_text(encoding="utf-8")
    ]
    assert len(stamped) == 3
    assert not (root / "docs" / "releases" / "v0.2.6.md").exists()
    assert 'version = "0.2.5"' in (root / "pyproject.toml").read_text(encoding="utf-8")

    monkeypatch.undo()
    assert main(["release", "0.2.6", "--items", str(root / "items")]) == 0

    out = capsys.readouterr().out
    assert "Resuming an interrupted cut of v0.2.6: 3 of these 4 item(s)" in out
    assert "4 finished item(s)" in out
    notes = (root / "docs" / "releases" / "v0.2.6.md").read_text(encoding="utf-8")
    assert sorted(re.findall(r"^- (PL-\S+)", notes, re.M)) == [
        "PL-D1D1",
        "PL-G0G0",
        "PL-G1G1",
        "PL-G2G2",
    ]
    assert 'version = "0.2.6"' in (root / "pyproject.toml").read_text(encoding="utf-8")


def test_a_cut_interrupted_after_its_bump_still_writes_the_notes_it_owes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The other side of the loop, and the one that used to have no way forward.

    Every item stamped and the version moved leaves nothing unreleased at all,
    so the re-run reported "Nothing to release" and exited 0 while the release
    it was asked for had no notes. The untagged guard would have refused it
    first, naming the version being finished as one that shipped without a tag.
    """
    root = _interruptible_repo(tmp_path, 3)

    # The one call `cmd_release` makes between `bump.write()` and the notes
    # write, so raising here leaves exactly the state that gap leaves.
    def stop(version: str) -> str:
        raise _ContainerLost("the container went away")

    monkeypatch.setattr(cli, "notes_name", stop)
    with pytest.raises(_ContainerLost):
        main(["release", "0.2.6", "--items", str(root / "items")])
    monkeypatch.undo()

    assert 'version = "0.2.6"' in (root / "pyproject.toml").read_text(encoding="utf-8")
    assert not (root / "docs" / "releases" / "v0.2.6.md").exists()
    assert main(["release", "0.2.6", "--items", str(root / "items")]) == 0
    notes = (root / "docs" / "releases" / "v0.2.6.md").read_text(encoding="utf-8")
    assert notes.count("\n- PL-") == 3


def test_a_different_version_is_refused_while_a_cut_is_unfinished(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Two numbers over one unfinished cut makes both sets of notes wrong."""
    root = _interruptible_repo(tmp_path, 4)
    _interrupt_after(monkeypatch, 2)
    with pytest.raises(_ContainerLost):
        main(["release", "0.2.6", "--items", str(root / "items")])
    monkeypatch.undo()

    assert main(["release", "0.2.7", "--items", str(root / "items")]) == 1

    out = capsys.readouterr().out
    assert "A cut of v0.2.6 was interrupted" in out
    assert "make release VERSION=0.2.6" in out
    assert not (root / "docs" / "releases" / "v0.2.7.md").exists()


def _cut_stopped_after(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, count: int, stamped: int
) -> Path:
    """A repository whose cut of v0.2.6 stamped `stamped` of `count` items and wrote no notes."""
    root = _interruptible_repo(tmp_path, count)
    _interrupt_after(monkeypatch, stamped)
    with pytest.raises(_ContainerLost):
        main(["release", "0.2.6", "--items", str(root / "items")])
    monkeypatch.undo()
    return root


def test_the_digest_names_an_interrupted_cut_behind_the_releasable_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-1BS2: the digest offered what an unfinished cut had not reached as a release.

    `readiness` leaves the stamps out by contract, so a six-item cut stopped
    after two read `Releasable: 4 finished item(s) since 0.2.5` with an offer
    beside it, and nothing said a cut was half made. The line names the
    version, the notes never written and the command that finishes it.
    """
    root = _cut_stopped_after(tmp_path, monkeypatch, 6, 2)
    capsys.readouterr()

    assert main(["digest", "--items", str(root / "items")]) == 0

    out = capsys.readouterr().out
    assert (
        "Releasable: a cut of v0.2.6 was interrupted: 2 item(s) carry `milestone: v0.2.6` "
        "and docs/releases/v0.2.6.md was never written. Finish it before offering another "
        "- `make release VERSION=0.2.6` cuts all 6."
    ) in out
    assert "4 finished item(s)" not in out
    assert "Offer" not in out


def test_the_digest_names_an_interrupted_cut_that_left_nothing_unstamped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Stopped after its bump, a cut leaves no remainder, and the line used to be absent."""
    root = _interruptible_repo(tmp_path, 3)

    def stop(version: str) -> str:
        raise _ContainerLost("the container went away")

    monkeypatch.setattr(cli, "notes_name", stop)
    with pytest.raises(_ContainerLost):
        main(["release", "0.2.6", "--items", str(root / "items")])
    monkeypatch.undo()
    capsys.readouterr()

    assert main(["digest", "--items", str(root / "items")]) == 0

    out = capsys.readouterr().out
    assert "Releasable: a cut of v0.2.6 was interrupted: 3 item(s) carry" in out
    assert "`make release VERSION=0.2.6` cuts all 3." in out


def test_status_names_an_interrupted_cut_the_way_the_digest_does(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-1BS2: `status` read the same short remainder as `Unreleased:`."""
    root = _cut_stopped_after(tmp_path, monkeypatch, 6, 2)
    capsys.readouterr()

    assert main(["status", "--items", str(root / "items")]) == 0

    out = capsys.readouterr().out
    assert "Unreleased: a cut of v0.2.6 was interrupted: 2 item(s) carry" in out
    assert "`make release VERSION=0.2.6` cuts all 6." in out
    assert "Next version would be" not in out


def test_check_reports_a_release_whose_notes_were_never_written(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The detection half, which holds wherever the resume is not re-run."""
    root = _interruptible_repo(tmp_path, 4)
    (root / "docs" / "releases").mkdir(parents=True)
    (root / "docs" / "releases" / "v0.2.5.md").write_text("## v0.2.5\n", encoding="utf-8")
    _interrupt_after(monkeypatch, 3)
    with pytest.raises(_ContainerLost):
        main(["release", "0.2.6", "--items", str(root / "items")])
    monkeypatch.undo()

    assert main(["check", "--items", str(root / "items"), "--today", "2026-08-24"]) == 1

    out = capsys.readouterr().out
    assert "3 item(s) carry `milestone: v0.2.6`" in out
    assert "docs/releases/v0.2.6.md was never written" in out


def test_check_reports_notes_that_name_work_the_store_does_not_stamp(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The milder inverse, and the same two files disagreeing."""
    root = _release_repo(tmp_path, "v0.2.5")
    notes = root / "docs" / "releases"
    notes.mkdir(parents=True)
    (notes / "v0.2.5.md").write_text("## v0.2.5\n\n- PL-D1D1 A finished item\n", encoding="utf-8")

    assert main(["check", "--items", str(root / "items"), "--today", "2026-08-24"]) == 1
    assert "names 1 item(s) that do not carry `milestone: v0.2.5`" in capsys.readouterr().out


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
    assert 'git tag -a v0.2.6 MERGE_COMMIT -m "v0.2.6"' in out


def test_no_command_the_release_prints_carries_a_shell_redirection(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A placeholder a shell eats is worse than no placeholder at all.

    `git tag -a v0.3.1 <merge commit> -m "v0.3.1"` never reached git: a shell
    reads `<merge` as input redirection from a file named `merge`, so zsh answered
    "no such file or directory: merge", which names neither git nor the tag nor
    the thing that is missing. The advisory fires once per release at the moment
    somebody is copying it, and the release cannot be finished until the tag lands
    (`PL-HKF4`).

    Asserted over every indented command line rather than over the one string, so
    a placeholder added to a different instruction is caught too.
    """
    root = _release_repo(tmp_path, "v0.2.5")
    (root / "ROADMAP.md").write_text(RELEASE_ROADMAP, encoding="utf-8")

    assert main(["release", "0.2.6", "--items", str(root / "items")]) == 0

    for line in capsys.readouterr().out.splitlines():
        if line.startswith("  git ") or line.startswith("  make "):
            assert "<" not in line and ">" not in line, line


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
id: PL-V1V1
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

    assert "PL-V1V1" in output
    assert "induction curve looks wrong" in output
    assert "priority*" in output and "effort*" in output
    assert "**Why it matters.**" in output  # the brief sections still missing


def test_triage_states_the_payoff_rule_before_a_pass_writes_ready(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A rule that fires at `ready` has to be stated where `ready` gets written.

    `triage` is the command whose job is to print the rules the answers must
    satisfy, and a pass that learns about `payoff:` from the refusal instead has
    been told too late (`PL-WYKF`).
    """
    _triage(tmp_path, UNTRIAGED, config="[docket]\npayoff_required_from = 2026-08-01\n")
    output = capsys.readouterr().out

    assert "must carry a `payoff:`" in output
    assert "every item has a consequence" in output


def test_triage_says_nothing_about_a_payoff_where_the_rule_is_off(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _triage(tmp_path, UNTRIAGED)

    assert "payoff" not in capsys.readouterr().out


STUBBED = """---
id: PL-V2V2
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


def test_triage_names_the_stub_rather_than_reporting_an_empty_section(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """One author for the rule, so `triage` and `check` cannot disagree about it."""
    _triage(tmp_path, CAPTURED_OVER_A_TEMPLATE)
    output = capsys.readouterr().out

    assert "the capture template is still above the brief" in output
    assert "brief has nothing under:" not in output


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
    assert "the top band is P1, holding 1 startable of the 5" in output
    assert "src/core" in output
    assert "`verify:` command" in output


def test_triage_states_the_rules_a_chosen_status_adds(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The block is presented as complete, so an enforced rule missing from it misleads.

    `checks.py` errors on an item at `needs-decision` with no `**Decision
    needed.**` section, and the rules block never said so - a session that
    trusted it wrote the edit, ran `make docket` and found out afterwards
    (`PL-F4JS`). The same held for the two `dropped` fields and for
    `blocked-by`.
    """
    _triage(tmp_path, UNTRIAGED, READY)
    output = capsys.readouterr().out

    for status, rule in STATUS_REQUIREMENTS:
        assert rule in output, f"the {status} rule is enforced but not printed"


@pytest.mark.parametrize("status", [status for status, _ in STATUS_REQUIREMENTS])
def test_every_status_rule_the_triage_block_prints_is_one_check_enforces(
    tmp_path: Path, status: str
) -> None:
    """The table is prose; this is what stops it drifting from the checker.

    Printing a rule nobody enforces is the same defect as enforcing one nobody
    prints - both leave a session unable to trust the block - so each entry is
    pinned to a refusal here rather than to the wording of `checks.py`.
    """
    document = f"""---
id: PL-S1S1
title: An item at a status that demands more of it
priority: P2
effort: S
status: {status}
classes: perf
touches: a.py
added: 2026-08-01
---

**Problem.** x
**Why it matters.** y
**Done when.** z
"""

    assert _run("check", "--items", str(_store(tmp_path, document))) == 1


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


def _featured(identifier: str, status: str, **extra: str) -> str:
    """One item carrying a feature, at the status a progress listing has to draw."""
    fields = {
        "id": identifier,
        "title": f"An item that is {status}",
        "priority": "P2",
        "effort": "S",
        "status": status,
        "classes": "perf",
        "feature": "chart-readout",
        "touches": "a.py",
        "added": "2026-08-01",
        **extra,
    }
    front = "".join(f"{key}: {value}\n" for key, value in fields.items())
    return f"---\n{front}---\n\n**Problem.** x\n**Why it matters.** y\n**Done when.** z\n"


def test_feature_draws_a_dropped_entry_distinctly_from_an_open_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Counting the boxes has to reproduce the two figures printed above them.

    `bin/docket feature teachable-case` printed "18/28 done (9 left)" over ten
    empty boxes: the tenth was `dropped`, correctly outside both counts and drawn
    identically to the nine that were open. A reader counting to check the number
    gets the wrong answer and cannot tell which of the two is lying (`PL-VFVW`).
    """
    store = _store(
        tmp_path,
        _featured("PL-D0D0", "done", closed="2026-08-10"),
        _featured("PL-Q0Q0", "ready"),
        _featured("PL-X0X0", "dropped", closed="2026-08-11", reason="superseded"),
    )

    assert _run("feature", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert "chart-readout: 1/3 done (1 left)" in output
    assert "[x] PL-D0D0" in output
    assert "[ ] PL-Q0Q0" in output
    assert "[-] PL-X0X0" in output
    # The counts and the marks are now two renderings that agree: one `[x]` for
    # the numerator, one `[ ]` for what is left, three lines for the denominator.
    assert output.count("[x]") == 1
    assert output.count("[ ]") == 1


def test_milestone_draws_a_dropped_entry_distinctly_too(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The milestone listing counts by the same two rules and drew the same box.

    Fixed from one author rather than twice, so the next status added cannot
    reach one listing and miss the other.
    """
    store = _store(
        tmp_path,
        _featured("PL-D1D1", "done", milestone="v0.9.0", closed="2026-08-10"),
        _featured("PL-X1X1", "dropped", milestone="v0.9.0", closed="2026-08-11", reason="no"),
    )

    assert _run("milestone", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert "[x] PL-D1D1" in output
    assert "[-] PL-X1X1" in output


def test_triage_says_so_when_nothing_is_waiting(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _triage(tmp_path, READY)

    assert "Nothing is untriaged." in capsys.readouterr().out


DEBT = """---
id: PL-G1G1
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


def test_gate_splits_the_store_s_open_debt_by_the_feature_it_carries(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Recording Gate 0 by hand was a full pass over 48 items; this is that pass."""
    store = _store(tmp_path, READY, DEBT)

    assert _run("gate", "--feature", "teachable-case", "--items", str(store)) == 0

    output = capsys.readouterr().out
    before, _, after = output.partition("Carrying `teachable-case`")
    assert "PL-B1B1" in before and "PL-G1G1" not in before
    assert "PL-G1G1" in after
    assert "1 M" in after


def test_gate_names_its_split_for_the_feature_and_never_for_the_roadmap_rule(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-RFHH`. `bin/docket wave` prints "cleared by the milestone itself" for
    the roadmap's test - `Required scope` names the id - and this printed the
    same phrase over a feature split that differs from it in both directions,
    so `PL-YVP7` was filed on the wrong one of the two. Each command now names
    the test it ran, and this one says where the other answer is."""
    store = _store(tmp_path, READY, DEBT)

    assert _run("gate", "--feature", "teachable-case", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert "milestone itself" not in output
    assert "2 open debt items in the store, split by whether each carries" in output
    assert "bin/docket wave" in output and "Required scope" in output


def test_gate_over_a_store_with_no_debt_does_not_imply_debt_without_the_feature() -> None:
    """The list is every open debt item, so an empty one means the store holds
    none; naming the feature in that message said there was debt without it."""
    from docket.plan import Gate
    from docket.render import format_gate

    printed = format_gate(Gate(feature="teachable-case", inside=[], outside=[]), ("defect",))

    assert printed == "No open debt in the store. Nothing to clear."


def test_gate_writes_nothing_and_reaches_no_verdict(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Freezing the list stays a deliberate act; the command removes the typing."""
    store = _store(tmp_path, READY, DEBT)
    before = {path.name: path.read_text() for path in store.glob("*.md")}

    assert _run("gate", "--feature", "teachable-case", "--items", str(store)) == 0

    assert {path.name: path.read_text() for path in store.glob("*.md")} == before
    assert "not decided here" in capsys.readouterr().out


def _branched_repo(tmp_path: Path, store: str = "items") -> Path:
    """A repository whose second branch carries an item `main` has never seen.

    Real git, for the same reason `_release_repo` uses it: the injected-runner
    tests assert the filtering, and only a real checkout proves the commands
    are spelled in a way git accepts.

    `store` places the queue under the root, one level down by default and two
    for `PL-P757`, whose symptom only appears where the two differ.
    """
    root = tmp_path / "repo"
    (root / store).mkdir(parents=True)
    (root / store / "PL-0001-on-main.md").write_text(READY.replace("PL-B1B1", "PL-0001"))
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
    (root / store / "PL-K7QX-lost.md").write_text(
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


def test_settings_are_read_from_the_repository_root_not_the_store_s_parent(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-P757's third symptom, and the quietest of the three.

    `_load` resolves settings from the project that owns the store, so that
    `--items` pointed at another project's queue is not answered under this
    project's policy. Taking the store's parent for that project's root made
    the rule true only one level down: `--items docs/items` looked for
    `docket.toml` in `docs/`, found none, and ran on the package defaults -
    so `check` judged this repository's own queue against a vocabulary,
    a band limit and a path partition nobody wrote.

    `known_classes` is the observable end of it: declared, it replaces the
    derived vocabulary entirely, so a class that is only in the file is
    accepted when the file was read and an error when it was not.
    """
    root = tmp_path / "repo"
    (root / ".git").mkdir(parents=True)
    (root / "docket.toml").write_text('[docket]\nknown_classes = ["weather"]\n', encoding="utf-8")
    store = root / "docs" / "items"
    store.mkdir(parents=True)
    (store / "PL-0001-forecast.md").write_text(
        READY.replace("PL-B1B1", "PL-0001").replace("classes: perf", "classes: weather"),
        encoding="utf-8",
    )

    assert _run("check", "--items", str(store)) == 0

    assert "weather" not in capsys.readouterr().out, "the declared vocabulary was read"


def test_stranded_reads_a_store_two_levels_down(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-P757's second symptom, from the same wrong root.

    `git ls-tree` run from a subdirectory prints paths relative to *that*
    directory, while `<rev>:<path>` is always resolved from the repository
    root. With the root taken as `docs/`, the listing said
    `items/PL-K7QX-lost.md` and the `show` for it found nothing - so every
    finding printed as `(title unreadable)`, and the recovery line handed over
    a path that checks out nothing from the root it would be pasted at.
    """
    root = _branched_repo(tmp_path, store="docs/items")

    assert main(["--items", str(root / "docs" / "items"), "stranded"]) == 0

    out = capsys.readouterr().out
    assert "PL-K7QX  A lost thought" in out
    assert "(title unreadable)" not in out
    assert "git checkout abandoned -- docs/items/PL-K7QX-lost.md" in out


def test_stranded_reports_nothing_when_every_branch_has_landed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _branched_repo(tmp_path)
    subprocess.run(["git", "merge", "-q", "abandoned"], cwd=root, check=True, capture_output=True)

    assert main(["--items", str(root / "items"), "stranded"]) == 0

    assert "No item exists only on a branch" in capsys.readouterr().out


def test_stranded_refreshes_the_base_before_deciding_anything_is_lost(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-39B7: the finding is a claim about what the base does not hold.

    Read against a base eight minutes old, an item merged in those eight
    minutes reads as existing only on a branch - and the recovery this command
    prints then overwrites the merged copy with the older one, which is what
    was run on 2026-09-05 (`PL-KBFN`).
    """
    root = _branched_repo(tmp_path)
    fetched: list[Path] = []
    monkeypatch.setattr("docket.cli.fetch_remote", lambda where, runner: fetched.append(where))

    assert main(["--items", str(root / "items"), "stranded"]) == 0

    assert fetched == [root]
    assert "Nothing refreshed the default branch" not in capsys.readouterr().out


def test_stranded_says_so_when_told_not_to_refresh(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A checkout with no network still gets an answer, and is told what it rests on."""
    root = _branched_repo(tmp_path)
    fetched: list[Path] = []
    monkeypatch.setattr("docket.cli.fetch_remote", lambda where, runner: fetched.append(where))

    assert main(["--items", str(root / "items"), "stranded", "--no-fetch"]) == 0

    out = capsys.readouterr().out
    assert fetched == []
    assert "Nothing refreshed the default branch" in out
    # Above the recovery command, not under it: a reader who has reached the
    # `git checkout` has already made the decision the caveat informs.
    assert out.index("Nothing refreshed") < out.index("git checkout abandoned")


def _pushed_after_merge_repo(tmp_path: Path) -> Path:
    """A repository in the geometry that loses a commit, built with real git.

    The sequence is the one observed on `#284`: a branch commits its work, the
    pull request squash-merges that head, and the session then pushes one more
    commit to the same branch. Nothing merges a merged pull request a second
    time, so the last commit lands nowhere - and it touches no item file, which
    is what made it invisible to every check this project ran (`PL-3D2M`).

    Real git rather than the injected runner, for the reason `_branched_repo`
    gives: the rules are asserted in `test_vcs.py`, and only a checkout proves
    the commands are spelled in a way git accepts.
    """
    root = tmp_path / "repo"
    (root / "items").mkdir(parents=True)
    (root / "items" / "PL-0001-on-main.md").write_text(READY.replace("PL-B1B1", "PL-0001"))

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(root)],
        check=True,
        capture_output=True,
    )
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        git("config", name, value)
    git("add", "-A")
    git("commit", "-qm", "base")

    git("checkout", "-qb", "claude/pl-k7qx-do-the-thing")
    (root / "work.py").write_text("the change the pull request took\n")
    git("add", "-A")
    git("commit", "-qm", "PL-K7QX: the work the pull request took")

    git("checkout", "-q", "main")
    git("merge", "-q", "--squash", "claude/pl-k7qx-do-the-thing")
    git("commit", "-qm", "PL-K7QX: the work the pull request took (#1)")

    git("checkout", "-q", "claude/pl-k7qx-do-the-thing")
    (root / "rule.md").write_text("the behavior change the owner asked for\n")
    git("add", "-A")
    git("commit", "-qm", "PL-K7QX: the rule pushed after the merge")
    git("checkout", "-q", "main")
    return root


def test_stranded_reports_a_commit_pushed_after_its_pull_request_merged(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _pushed_after_merge_repo(tmp_path)

    assert main(["--items", str(root / "items"), "stranded"]) == 0

    out = capsys.readouterr().out
    assert "claude/pl-k7qx-do-the-thing  (1 file of its work already landed)" in out
    assert "PL-K7QX: the rule pushed after the merge" in out
    assert "    rule.md" in out
    # The commit is replayed rather than its file checked out, which would
    # overwrite whatever the base has changed in that file since (`PL-GHHW`).
    pushed = subprocess.run(
        ["git", "rev-parse", "claude/pl-k7qx-do-the-thing"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert f"recover: git cherry-pick {pushed[:9]}\n" in out
    assert "git checkout claude/pl-k7qx-do-the-thing" not in out
    # The commit the pull request did take is not offered for recovery.
    assert "work.py" not in out


def test_stranded_is_silent_when_the_merge_took_the_commit_and_merged_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The shape that made this check fire falsely on its first live run.

    A branch commits, the base moves on to edit the same file, and the squash
    merge writes the combined text. The branch's copy of that file then matches
    nothing the base has ever held, so a content comparison calls it work left
    behind - while the base is in fact *ahead* of the branch. Observed on
    `origin/claude/snapshot-run-history-copy-dw6djz` carrying the v0.3.8
    release commit, squash-merged as `#312` while `#311` edited the same
    `ROADMAP.md` prose (`PL-JHJ3`).

    Real git, because the confusion is entirely in what a squash against a
    moved base writes, and an injected runner cannot produce that.
    """
    root = tmp_path / "repo"
    (root / "items").mkdir(parents=True)
    (root / "items" / "PL-0001-on-main.md").write_text(READY.replace("PL-B1B1", "PL-0001"))
    (root / "NOTES.md").write_text("first line\n")

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(root)],
        check=True,
        capture_output=True,
    )
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        git("config", name, value)
    git("add", "-A")
    git("commit", "-qm", "base")

    git("checkout", "-qb", "claude/pl-k7qx-release")
    (root / "NOTES.md").write_text("first line\nthe branch's own paragraph\n")
    (root / "shipped.md").write_text("what the branch shipped\n")
    git("add", "-A")
    git("commit", "-qm", "PL-K7QX: the release commit")

    # The base moves on, editing the same file, and the squash writes the
    # combined text - so the branch's copy of NOTES.md is on no tree the base
    # has held, while every line of it is.
    git("checkout", "-q", "main")
    (root / "NOTES.md").write_text("first line\nan edit that landed first\n")
    git("add", "-A")
    git("commit", "-qm", "PL-0TH3: an edit that landed first (#1)")
    (root / "NOTES.md").write_text(
        "first line\nan edit that landed first\nthe branch's own paragraph\n"
    )
    (root / "shipped.md").write_text("what the branch shipped\n")
    git("add", "-A")
    git("commit", "-qm", "PL-K7QX: the release commit (#2)")

    assert main(["--items", str(root / "items"), "stranded"]) == 0

    out = capsys.readouterr().out
    assert "No branch carries work its own pull request left behind" in out
    assert "claude/pl-k7qx-release" not in out


def test_stranded_leaves_a_branch_whose_work_is_all_unlanded_alone(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An ordinary live branch, which must not read as work left behind."""
    root = _branched_repo(tmp_path)

    assert main(["--items", str(root / "items"), "stranded"]) == 0

    assert "No branch carries work its own pull request left behind" in capsys.readouterr().out


def _queue_repo(tmp_path: Path) -> tuple[Path, Callable[..., None]]:
    """An empty repository whose store sits where `--items` puts the root.

    `--items <root>/items` makes the store's parent the repository root, which
    is the convention every fixture above follows and what both halves of this
    command read the queue at.
    """
    root = tmp_path / "repo"
    (root / "items").mkdir(parents=True)

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(root)],
        check=True,
        capture_output=True,
    )
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        git("config", name, value)
    return root, git


def test_stranded_hands_a_diff_for_an_item_edited_only_on_a_branch(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-KSCW`: the item is on `main` and a section of it is on a branch alone.

    A `git checkout` is the wrong recovery here and the whole reason the two
    findings print separately: the base holds a copy of its own, so restoring
    the branch's over it discards whatever landed since.
    """
    root, git = _queue_repo(tmp_path)
    item = root / "items" / "PL-0001-on-main.md"
    item.write_text(READY.replace("PL-B1B1", "PL-0001"))
    git("add", "-A")
    git("commit", "-qm", "PL-0001: file the item")

    git("checkout", "-qb", "claude/pl-0001-a-fourth-instance")
    item.write_text(item.read_text() + "\n**Found again.** A fourth instance, unreported.\n")
    git("add", "-A")
    git("commit", "-qm", "PL-0001: record the fourth instance")
    git("checkout", "-q", "main")

    assert main(["--items", str(root / "items"), "stranded"]) == 0

    out = capsys.readouterr().out
    assert "1 item the default branch holds, edited only on a branch" in out
    assert "PL-0001  A ready item" in out
    assert "edited on: claude/pl-0001-a-fourth-instance" in out
    assert (
        "read: git diff main:items/PL-0001-on-main.md "
        "claude/pl-0001-a-fourth-instance:items/PL-0001-on-main.md"
    ) in out
    # The recovery a reader must never be handed for a file the base holds.
    assert "git checkout" not in out


def test_stranded_does_not_offer_to_restore_a_copy_the_base_has_closed_since(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-MBTZ`, in the geometry that produced it, built with real git.

    A release branch's work squash-merged; the branch then wrote an item file
    of its own, and `main` closed that item by another route - so the branch's
    `untriaged` copy is a blob `main` has never held, and the two-dot diff
    `_superseded` reads sees the older `status:` line as an *addition* and
    calls the path outstanding. The recovery printed for it was a `git
    checkout` replacing `main`'s `done` copy with the branch's untriaged one,
    discarding the `closed:` and `pr:` the closure recorded (`PL-KBFN`,
    `PL-39B7`).
    """
    root, git = _queue_repo(tmp_path)
    (root / "items" / "PL-0001-on-main.md").write_text(READY.replace("PL-B1B1", "PL-0001"))
    git("add", "-A")
    git("commit", "-qm", "base")

    git("checkout", "-qb", "claude/pl-k7qx-cut-the-release")
    (root / "work.py").write_text("the change the pull request took\n")
    git("add", "-A")
    git("commit", "-qm", "PL-K7QX: the work the pull request took")

    git("checkout", "-q", "main")
    git("merge", "-q", "--squash", "claude/pl-k7qx-cut-the-release")
    git("commit", "-qm", "PL-K7QX: the work the pull request took (#1)")

    # The branch files the release-tag item after its own merge, so its blob is
    # one `main` has never held; `main` files and closes a copy of its own.
    tag = root / "items" / "PL-K7QX-tag-the-release.md"
    filed = READY.replace("PL-B1B1", "PL-K7QX").replace("status: ready", "status: untriaged")
    git("checkout", "-q", "claude/pl-k7qx-cut-the-release")
    tag.write_text(filed)
    git("add", "-A")
    git("commit", "-qm", "PL-K7QX: file the tag item")

    git("checkout", "-q", "main")
    tag.write_text(filed.replace("status: untriaged", "status: done\nclosed: 2026-09-13\npr: 549"))
    git("add", "-A")
    git("commit", "-qm", "PL-K7QX: tag the release (#2)")

    assert main(["--items", str(root / "items"), "stranded"]) == 0

    out = capsys.readouterr().out
    assert "No branch carries work its own pull request left behind" in out
    assert "PL-K7QX-tag-the-release.md" not in out
    assert "git checkout" not in out


def test_stranded_says_so_when_it_was_told_not_to_ask_git(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Silence would read as a clean answer; it is an unasked question."""
    assert _run("stranded", "--items", str(_store(tmp_path, READY))) == 0

    assert "branch detection is off" in capsys.readouterr().out


# The name a web harness gives a branch: built from the opening prompt, so it
# carries no item id and cannot be renamed afterwards.
BRANCH = "roadmap-release-write-failure-nhsjwo"


def _flight_repo(
    tmp_path: Path,
    subject: str,
    wrote: str = "src/scratch.txt",
    store: str = "items",
    when: str = "2026-08-20T12:00:00+00:00",
) -> Path:
    """A repository whose one live branch is named the way the harness names one.

    Real git, for the reason `_branched_repo` uses it: the injected-runner
    tests in `test_vcs.py` assert the rules, and only a real checkout proves
    that `--source`, `%cI`, `--name-only` and the merge-base guard are spelled
    in a way git accepts. The commit dates are fixed so the reported age is too.

    `wrote` is the file the branch's commit changes, which is what says whether
    that commit was implementing the item its subject leads with or only
    recording something into the queue. It defaults outside the store, because
    a commit that reaches past the queue is what every test here but one means
    by a branch mid-item.

    `store` is where the queue sits under the root, and defaults to the one
    level down every other test here happened to use - which is why `PL-P757`
    went unseen for as long as it did. The nested form is this project's own.

    `when` dates both commits, so a test can place the branch's last commit
    minutes before the instant it reads the age at (`PL-3QM9`).
    """
    root = tmp_path / "repo"
    (root / store).mkdir(parents=True)
    (root / store / "PL-0001-on-main.md").write_text(READY.replace("PL-B1B1", "PL-0001"))
    dated = os.environ | {"GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}

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
    written = root / wrote
    written.parent.mkdir(parents=True, exist_ok=True)
    written.write_text("work in progress\n")
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


def test_a_branch_committed_an_hour_ago_is_not_reported_a_day_old(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-3QM9 as it was observed: a commit at 23:34, read at 00:29.

    Subtracting calendar dates counted the midnight between them, so a session
    that had committed under an hour before read "last commit 1 day ago" - the
    direction that reads a live session as abandoned work.
    """
    root = _flight_repo(tmp_path, "PL-0001 Do the thing", when="2026-09-20T23:34:46+00:00")
    argv = ["--items", str(root / "items"), "--now", "2026-09-21T00:29:00+00:00", "flight"]

    assert main([*argv, "--no-remote"]) == 0

    row = next(line for line in capsys.readouterr().out.splitlines() if line.startswith("PL-0001"))
    assert row.endswith("last commit 54 minutes ago")
    assert "day" not in row


def _forge(root: Path, command: str) -> None:
    """Point the repository's `open_pull_requests_command` at `command`."""
    (root / "docket.toml").write_text(f"[docket]\nopen_pull_requests_command = '{command}'\n")


def test_a_branch_minutes_old_carries_its_pull_request_rather_than_a_verdict(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-7TVT: in its first hour an age cannot tell a live session from an ended one.

    PR #757 sat green for 25 minutes after its session was archived, and every
    row said only how old the branch was, under a closing line telling the
    reader the age was what separated the two. The pull request is the fact
    that separates part of it, so the row carries it, and the closing line
    says what an age cannot say instead of what to conclude from one.
    """
    root = _flight_repo(tmp_path, "PL-0001 Do the thing", when="2026-09-22T10:00:00+00:00")
    _forge(root, f'printf "{BRANCH} 757\\n"')

    argv = ["--items", str(root / "items"), "--now", "2026-09-22T10:07:30+00:00", "flight"]
    assert main(argv) == 0

    out = capsys.readouterr().out
    row = next(line for line in out.splitlines() if line.startswith("PL-0001"))
    assert "last commit 7 minutes ago" in row
    assert row.endswith("pull request #757 open")
    assert "A branch outlives its session, so no row here says anybody is still on it" in out
    assert "the work is written and waits on review" in out
    assert "the age is what separates them" not in out
    assert "do not start" not in out


def test_a_forge_that_answered_with_nothing_open_says_so_on_the_row(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """ "None open" and "could not look" are opposite answers, and each row says which."""
    root = _flight_repo(tmp_path, "PL-0001 Do the thing", when="2026-09-22T10:00:00+00:00")
    _forge(root, "true")
    argv = ["--items", str(root / "items"), "--now", "2026-09-22T10:07:30+00:00", "flight"]

    assert main(argv) == 0
    answered = capsys.readouterr().out
    _forge(root, "false")
    assert main(argv) == 0
    unanswered = capsys.readouterr().out

    assert next(line for line in answered.splitlines() if line.startswith("PL-0001")).endswith(
        "no pull request open"
    )
    assert "could not be read here" not in answered
    assert next(line for line in unanswered.splitlines() if line.startswith("PL-0001")).endswith(
        "last commit 7 minutes ago"
    )
    assert "pull request open" not in unanswered
    assert "Whether a pull request is open for any of them could not be read here" in unanswered


def test_flight_moves_a_branch_that_closed_its_item_into_the_settled_rows(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-Q664`'s rows, end to end, read from the holds since `PL-N162`.

    The close-out releases the branch's claim, so the row it keeps in flight
    is the disposition the same status move made; a pull request open on the
    branch puts it back among the live rows, waiting on review.
    """
    root = _flight_repo(tmp_path, "PL-0001 Do the thing", when="2026-09-22T10:00:00+00:00")
    closed = READY.replace("PL-B1B1", "PL-0001").replace("status: ready", "status: done")
    _commit_on(
        root,
        BRANCH,
        {"items/PL-0001-on-main.md": closed},
        "PL-0001 Close it out",
        "2026-09-22T11:00:00+00:00",
    )
    argv = ["--items", str(root / "items"), "--now", "2026-09-22T12:00:00+00:00", "flight"]

    _forge(root, "true")
    assert main(argv) == 0
    settled = capsys.readouterr().out
    _forge(root, f'printf "{BRANCH} 812\\n"')
    assert main(argv) == 0
    reviewing = capsys.readouterr().out

    assert "No branch is carrying an item anybody is still working." in settled
    assert (
        "On 1 branch every item it carries is already closed, and no pull request is open for it"
        in settled
    )
    assert f"  {BRANCH}  PL-0001  last commit 1 hour ago" in settled
    assert "already closed" not in reviewing
    row = next(line for line in reviewing.splitlines() if line.startswith("PL-0001"))
    assert row.endswith("pull request #812 open")


def test_now_without_an_offset_is_refused_rather_than_guessed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An age is a subtraction, and a reference meaning two instants is PL-3QM9 again."""
    with pytest.raises(SystemExit):
        main(["--items", str(tmp_path), "--now", "2026-09-21T00:29:00", "flight"])
    assert "carries no UTC offset" in capsys.readouterr().err


def test_flight_ignores_a_branch_that_only_wrote_to_the_queue(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Against real git: `--name-only` output, parsed, decides the claim.

    `test_vcs.py` asserts the rule against an injected runner. What this adds
    is that git actually prints the paths under the commit they belong to in
    the shape the walk parses, on this checkout's git - the half a fake cannot
    prove (queue item PL-X3WZ).
    """
    root = _flight_repo(tmp_path, "PL-K7QX Do the thing", wrote="items/PL-K7QX-a-note.md")

    assert main(["--items", str(root / "items"), "--today", "2026-08-23", "flight"]) == 0

    assert "PL-K7QX" not in capsys.readouterr().out


def test_files_in_flight_lists_both_names_of_a_rename(tmp_path: Path) -> None:
    """Against real git: a branch that moves a file has changed the path it left.

    git prints a rename as its new name alone, so the observed half of
    `concurrent` told a session working in the old path that no branch had
    touched it (`PL-KR69`). The fakes in `test_vcs.py` answer whatever they are
    asked, so only a real checkout shows which names git prints.
    """
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    (root / "src" / "moved.py").write_text("VALUE = 1\n")

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(root)],
        check=True,
        capture_output=True,
    )
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        git("config", name, value)
    git("add", "-A")
    git("commit", "-qm", "base")
    git("checkout", "-qb", BRANCH)
    (root / "tools").mkdir()
    git("mv", "src/moved.py", "tools/moved.py")
    git("commit", "-qm", "PL-K7QX move it")
    git("checkout", "-q", "main")
    report = vcs.FlightReport(branches=(vcs.Branch(name=BRANCH, item_id="PL-K7QX"),), base="main")

    files = vcs.files_in_flight(root, report)

    assert [entry.paths for entry in files.branches] == [("src/moved.py", "tools/moved.py")]


def test_a_nested_store_reads_the_same_in_flight_answer_as_the_default(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """PL-P757: `--items docs/items` is this project's own layout, and it read wrong.

    The root was derived as the store's *parent*, which is the root only where
    the store sits one level below it - the layout every other test in this
    file happens to use. Two levels down it resolved to `docs/`, so the queue
    prefix became `items/` where git prints `docs/items/...`, nothing matched,
    and a commit whose whole diff is inside the queue came back as work. Exit
    zero, and the mark is indistinguishable from a real one.

    The two invocations below differ in nothing but how the root is found: the
    default `items_dir` is already `docs/items`, so they are asking about the
    same store and their answers have to be the same string.
    """
    root = _flight_repo(
        tmp_path, "PL-K7QX Do the thing", wrote="docs/items/PL-K7QX-a-note.md", store="docs/items"
    )

    assert main(["--items", str(root / "docs" / "items"), "--today", "2026-08-23", "flight"]) == 0
    pointed = capsys.readouterr().out
    monkeypatch.chdir(root)
    assert main(["--today", "2026-08-23", "flight"]) == 0
    found = capsys.readouterr().out

    assert "PL-K7QX" not in found, "the reading that was already right, pinned"
    assert pointed == found


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

    assert main(["--items", str(root / "items"), "--today", "2026-08-23", "show", "PL-0001"]) == 0

    out = capsys.readouterr().out
    assert f"IN FLIGHT on {BRANCH}" in out
    # What the branch holds, not that somebody holds it: a branch outlives its
    # session, so the line may not presume one (`PL-7TVT`).
    assert "live legacy claim, made 2026-08-20 12:00 UTC; last commit 3 days ago" in out
    assert "That branch has claimed PL-0001, so starting it here would redo its work." in out
    assert "does not say anybody is still on it" in out
    assert "do not start" not in out
    assert "PL-0001" in out.splitlines()[0]


def test_show_does_not_tell_a_session_to_stop_working_its_own_branch(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The false alarm the precedence read removes.

    Re-reading the item you are implementing is the commonest reason to run
    `show` twice, and the answer was "do not start it again" - a warning about
    the reader's own work, printed at the moment a session is most likely to
    look and least able to act on it.
    """
    root = _flight_repo(tmp_path, "PL-0001 Do the thing")
    subprocess.run(["git", "checkout", "-q", BRANCH], cwd=root, check=True, capture_output=True)

    assert main(["--items", str(root / "items"), "--today", "2026-08-23", "show", "PL-0001"]) == 0

    out = capsys.readouterr().out
    assert f"IN FLIGHT on this branch ({BRANCH})" in out
    assert "do not start" not in out


def test_show_reads_a_branch_ahead_of_its_tracking_ref_as_this_session(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The case a name comparison gets wrong, against real refs.

    `git log --source` credits a commit two refs reach to one of them, and
    which one is not the command-line order - so a branch one merge ahead of
    its own tracking ref has its claim reported under `origin/...` and a check
    on the branch *name* concludes somebody else is holding it. That is a
    session told to stand down from its own work, which is the failure the
    containment test exists to prevent.
    """
    root = _flight_repo(tmp_path, "PL-0001 Do the thing")
    remote = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True, capture_output=True)

    # Dated inside the claim's lease: an undated commit takes the wall clock,
    # and a gap longer than the term would break the chain it renews.
    dated = os.environ | {
        "GIT_AUTHOR_DATE": "2026-08-21T12:00:00+00:00",
        "GIT_COMMITTER_DATE": "2026-08-21T12:00:00+00:00",
    }

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, env=dated)

    git("remote", "add", "origin", str(remote))
    git("push", "-q", "origin", "main", BRANCH)
    git("checkout", "-q", BRANCH)
    (root / "items" / "later.txt").write_text("unpushed\n")
    git("add", "-A")
    git("commit", "-qm", "carry on without pushing")

    assert main(["--items", str(root / "items"), "--today", "2026-08-23", "show", "PL-0001"]) == 0

    out = capsys.readouterr().out
    assert "IN FLIGHT on this branch" in out
    assert "do not start" not in out


def test_show_says_which_branch_holds_an_item_two_are_carrying(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-YHD3: the second session is told it is the second, from real refs.

    Real git rather than an injected runner, because what is being proved here
    is that two branches claiming one item produce one order git can actually
    be asked for - `Holdings.order`, on `(%aI, hash)` - against a checkout
    whose HEAD is the later of the two. The second commit reaches outside the
    queue, since these commits predate the claim writer and are read by the
    old rule, under which a queue-only one claims nothing (`PL-N162`).
    """
    root = _flight_repo(tmp_path, "PL-0001 Do the thing")
    later = os.environ | {
        "GIT_AUTHOR_DATE": "2026-08-21T09:00:00+00:00",
        "GIT_COMMITTER_DATE": "2026-08-21T09:00:00+00:00",
    }

    def git(*args: str, env: dict[str, str] | None = None) -> None:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, env=env)

    git("checkout", "-qb", "claude/pl-0001-second", "main")
    (root / "src").mkdir()
    (root / "src" / "second.txt").write_text("the other session\n")
    git("add", "-A")
    git("commit", "-qm", "PL-0001 Do the thing as well", env=later)

    assert main(["--items", str(root / "items"), "--today", "2026-08-23", "show", "PL-0001"]) == 0

    out = capsys.readouterr().out
    assert "PL-0001 is claimed on 2 branches" in out
    assert "which session yields" in out
    assert f"holds it  {BRANCH}" in out
    assert "yields    claude/pl-0001-second (this branch)" in out
    assert "This branch yields" in out
    assert "made 2026-08-20 12:00 UTC" in out
    assert "made 2026-08-21 09:00 UTC" in out


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
    root = _flight_repo(tmp_path, "PL-V1V1 Triage it")
    (root / "items" / "PL-V1V1-untriaged.md").write_text(UNTRIAGED, encoding="utf-8")

    assert main(["--items", str(root / "items"), "--today", "2026-08-23", "triage"]) == 0

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
        ["commit", "-qm", "PL-V1V1 Triage it"],
    ):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "checkout", "-q", "main"], cwd=root, check=True, capture_output=True)
    (root / "items" / "PL-V1V1-untriaged.md").write_text(UNTRIAGED, encoding="utf-8")

    assert main(["--items", str(root / "items"), "triage"]) == 0

    out = capsys.readouterr().out
    assert "1 ref could not be compared with main" in out
    assert "`bin/docket flight` names it." in out
    assert "IN FLIGHT" not in out


def test_triage_names_an_item_whose_file_a_branch_has_already_edited(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-N1JK: two sessions triaged one pair of items and collided at merge.

    The mark above this one cannot fire for a triage pass. A pass that fills in
    fields writes nothing outside the queue and records no claim - so the two
    sessions each
    fetched, each ran `show`, and each were told correctly that nothing was in
    flight. Against real git rather than an injected runner, because what is
    being proved here is that `--name-only` names the item file in a shape the
    walk parses into an id.
    """
    root = _flight_repo(tmp_path, "PL-V1V1 Triage it", wrote="items/PL-V1V1-untriaged.md")
    (root / "items" / "PL-V1V1-untriaged.md").write_text(UNTRIAGED, encoding="utf-8")

    assert main(["--items", str(root / "items"), "triage"]) == 0

    out = capsys.readouterr().out
    assert f"Its file is already edited on {BRANCH}." in out
    assert "a second resolution of the same file, so skip it." in out
    # The weaker mark, worded as the weaker mark: `IN FLIGHT` means work is on
    # a branch, and reading a capture commit as work is what PL-X3WZ removed.
    assert "IN FLIGHT" not in out
    assert "induction curve looks wrong" in out


def test_show_names_the_branch_that_has_already_edited_the_item_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Naming an item reaches `show` and nothing else, so the warning lives here.

    It has to say the opposite of what `IN FLIGHT` says about starting: the
    item is startable, and one file of it will need resolving.
    """
    root = _flight_repo(tmp_path, "PL-0001 Capture a note", wrote="items/PL-0001-on-main.md")

    assert main(["--items", str(root / "items"), "--today", "2026-08-23", "show", "PL-0001"]) == 0

    out = capsys.readouterr().out
    assert f"Its file is already edited on {BRANCH} (last commit 3 days ago)." in out
    assert "PL-0001 is startable" in out
    assert "IN FLIGHT" not in out


def test_show_names_a_round_that_retitled_the_item_file_as_editing_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Against real git: a design round that retitles its item still marks the file edited.

    A title edit renames the file, and git reads a light one as a rename. Asked
    with `--no-renames`, as every read of which paths a change touched is, git
    lists both names, sorted, so where the new title sorts first the path the
    walk keeps for the item is the one the branch deleted. Handed that path,
    `_superseded` sees removals only - an edit the base already holds - and the
    mark vanishes with nothing to say so; `_editing` finds the tip's copy by id
    instead. A new title sorting after the old passes either way, so the order
    is the point of the case (`PL-J16N`).
    """
    root = tmp_path / "repo"
    old, new = "items/PL-0001-on-main.md", "items/PL-0001-a-narrower-title.md"
    deciding = READY.replace("PL-B1B1", "PL-0001").replace(
        "status: ready", "status: needs-decision"
    )
    (root / "items").mkdir(parents=True)
    (root / old).write_text(deciding + "**Decision needed.** Which of two?\n", encoding="utf-8")
    dated = os.environ | {
        "GIT_AUTHOR_DATE": "2026-08-20T12:00:00+00:00",
        "GIT_COMMITTER_DATE": "2026-08-20T12:00:00+00:00",
    }

    def git(*args: str) -> str:
        done = subprocess.run(
            ["git", *args], cwd=root, check=True, capture_output=True, text=True, env=dated
        )
        return done.stdout

    git("-c", "init.defaultBranch=main", "init", "-q")
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        git("config", name, value)
    git("add", "-A")
    git("commit", "-qm", "base")
    git("checkout", "-qb", BRANCH)
    git("mv", old, new)
    retitled = (root / new).read_text(encoding="utf-8")
    (root / new).write_text(
        retitled.replace("title: A ready item", "title: A narrower title")
        + "**Recommendation:** the first.\n",
        encoding="utf-8",
    )
    git("add", "-A")
    git("commit", "-qm", "PL-0001: narrow the question and recommend an answer")
    git("checkout", "-q", "main")
    # The premise, read from git rather than assumed. A heavier edit is a
    # rewrite, listed as a deletion and an addition whatever is asked, and the
    # case would then pass without ever meeting a rename.
    assert git("diff", "--name-status", "-M", f"main...{BRANCH}").startswith("R")
    assert git("diff", "--name-only", "--no-renames", f"main...{BRANCH}").split() == [new, old]

    assert main(["--items", str(root / "items"), "--today", "2026-08-23", "show", "PL-0001"]) == 0

    out = capsys.readouterr().out
    assert f"Its file is already edited on {BRANCH} (last commit 3 days ago)." in out
    assert "IN FLIGHT" not in out


def test_show_prefers_the_in_flight_mark_to_the_file_edit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """One item, one answer. A closure writes the item and the code together.

    Closing the item in the branch's own copy releases the branch's claim, and
    the status it moved is then what holds the item: a disposition, which is
    the mark printed (`PL-N162`).
    """
    root = _flight_repo(tmp_path, "PL-0001 Do the thing")
    dated = os.environ | {
        "GIT_AUTHOR_DATE": "2026-08-21T12:00:00+00:00",
        "GIT_COMMITTER_DATE": "2026-08-21T12:00:00+00:00",
    }
    subprocess.run(["git", "checkout", "-q", BRANCH], cwd=root, check=True, capture_output=True)
    (root / "items" / "PL-0001-on-main.md").write_text(
        READY.replace("PL-B1B1", "PL-0001").replace("status: ready", "status: done"),
        encoding="utf-8",
    )
    for args in (["add", "-A"], ["commit", "-qm", "PL-0001 Close it out"]):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, env=dated)
    subprocess.run(["git", "checkout", "-q", "main"], cwd=root, check=True, capture_output=True)

    assert main(["--items", str(root / "items"), "--today", "2026-08-23", "show", "PL-0001"]) == 0

    out = capsys.readouterr().out
    assert f"STATUS HELD on {BRANCH}" in out
    assert "live status disposition, moved to `done` 2026-08-21 12:00 UTC" in out
    assert "Its file is already edited" not in out


def test_next_still_offers_an_item_whose_file_a_branch_has_only_edited(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-X3WZ intact, which is the half this change must not break.

    Capturing a finding before a session ends is mandatory, so an item whose
    file a live branch has touched is the ordinary case rather than the rare
    one. Ranking on that would withhold startable items from every session, for
    as long as the branch went unmerged - which for a branch nobody merges is
    forever.
    """
    root = _flight_repo(tmp_path, "PL-0001 Capture a note", wrote="items/PL-0001-on-main.md")

    assert main(["--items", str(root / "items"), "next"]) == 0

    assert "PL-0001" in capsys.readouterr().out


def test_next_withholds_a_recurrence_cluster_on_an_item_already_in_flight(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The offer is to promote, and an item on a branch has no position left to move.

    `plan.recurring` holds the rule; this holds the wiring, which is the half a
    unit test cannot reach. Both call sites - here and the session-start digest -
    have to hand the flight ids over, and one left unwired ships the defect with
    every plan-level test still green (`PL-CJ5R`).

    Asserted inside the block rather than over the whole output, because `next`
    names an in-flight id on its own line by design: "excluded, already in
    flight" is the ranking working, and only this block's copy is the offer
    nobody can take.
    """
    root = _flight_repo(
        tmp_path,
        "PL-0002 Fix the thing three sessions have filed",
        when="2026-09-20T12:00:00+00:00",
    )
    filings = "recurrences: 2026-09-18 PL-8888, 2026-09-19 PL-BBBB, 2026-09-20 PL-CCCC"
    for identifier in ("PL-0002", "PL-0003"):
        body = READY.replace("PL-B1B1", identifier).replace("added:", f"{filings}\nadded:")
        (root / "items" / f"{identifier}-clustered.md").write_text(body, encoding="utf-8")

    assert main(["--items", str(root / "items"), "--today", "2026-09-21", "next"]) == 0

    out = capsys.readouterr().out
    offered = out.split("Filed more than once, and never promoted for it:")[1]
    offered = offered.split("Not ranked above")[0]
    assert "PL-0003" in offered
    assert "PL-0002" not in offered


def test_show_leaves_an_item_no_branch_carries_out_of_flight(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The mark is a claim about this id, not about the branch existing."""
    root = _flight_repo(tmp_path, "PL-K7QX Do the thing")
    ran = ["--items", str(root / "items"), "--today", "2026-08-23"]

    # Inside the lease, so the other branch is live: read at the wall clock it
    # lapsed, nothing was in flight, and the absence below proved nothing.
    assert main([*ran, "flight"]) == 0
    assert "PL-K7QX" in capsys.readouterr().out
    assert main([*ran, "show", "PL-0001"]) == 0

    assert "IN FLIGHT" not in capsys.readouterr().out


def _commit_on(root: Path, branch: str, files: dict[str, str], subject: str, when: str) -> None:
    """One dated commit writing `files` on `branch`, which is made from `main` where it is new.

    The checkout is left on `main`, where the `show`s below read from unless
    they check out the holding branch first.
    """
    dated = os.environ | {"GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
    if subprocess.run(["git", "checkout", "-q", branch], cwd=root, capture_output=True).returncode:
        subprocess.run(
            ["git", "checkout", "-qb", branch, "main"], cwd=root, check=True, capture_output=True
        )
    for path, text in files.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text, encoding="utf-8")
    for args in (["add", "-A"], ["commit", "-qm", subject], ["checkout", "-q", "main"]):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, env=dated)


def test_show_names_a_branch_holding_an_item_only_by_moving_its_status(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-N162`'s review: a triage pass readying an item holds it, and `show` said nothing.

    The refuter's repro: one queue-only commit takes the item from `untriaged`
    to `ready`. `next` stops offering it, as a status disposition, and `show`
    printed no mark at all, since the old precedence read had no carrier for
    it and the file-edit line skips held items. It is named now, with its kind
    and state, and worded as a decision about the item rather than as work.
    """
    root = _flight_repo(tmp_path, "Tidy up")
    _commit_on(
        root,
        "main",
        {"items/PL-V1V1-untriaged.md": UNTRIAGED},
        "PL-V1V1: capture",
        "2026-08-20T12:00:00+00:00",
    )
    triage = "claude/triage-pass-q2w3e4"
    _commit_on(
        root,
        triage,
        {"items/PL-V1V1-untriaged.md": UNTRIAGED.replace("status: untriaged", "status: ready")},
        "PL-V1V1: triage",
        "2026-08-21T09:00:00+00:00",
    )
    ran = ["--items", str(root / "items"), "--today", "2026-08-23"]

    assert main([*ran, "show", "PL-V1V1"]) == 0

    out = capsys.readouterr().out
    assert f"STATUS HELD on {triage}" in out
    assert "live status disposition, moved to `ready` 2026-08-21 09:00 UTC" in out
    assert "a triage or grooming pass, or a close-out" in out
    assert "which is a decision about the item, not somebody working it" in out
    assert "IN FLIGHT" not in out
    assert "Its file is already edited" not in out


def test_show_names_a_branch_holding_an_item_only_by_its_name(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-TZ3R`'s hold, which nothing claims: named as the branch's name, and live."""
    root = _flight_repo(tmp_path, "Tidy up")
    named = "claude/pl-0001-named"
    _commit_on(root, named, {"src/named.txt": "x\n"}, "tidy", "2026-08-21T09:00:00+00:00")

    assert main(["--items", str(root / "items"), "--today", "2026-08-23", "show", "PL-0001"]) == 0

    out = capsys.readouterr().out
    assert f"IN FLIGHT on {named}, by its name" in out
    assert "live branch name, first commit 2026-08-21 09:00 UTC; last commit 2 days ago" in out
    assert "records no claim" in out


def test_show_says_a_lapsed_claim_on_an_open_item_holds_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A claim past its lease holds nothing, so it is no mark, and the item is free to claim.

    Not gated on `get_session` or the owner's word, which is `claim`'s refusal
    to get past a *live* claim (`PL-N162`'s review): `claim` passes a lapsed
    one, and `--over` is offered for the record it adds. The file-edit mark is
    not silenced by it, since nothing is held.
    """
    root = _flight_repo(tmp_path, "PL-0001 Do the thing")
    _commit_on(
        root,
        "claude/capture-z9x8c7",
        {"items/PL-0001-on-main.md": READY.replace("PL-B1B1", "PL-0001") + "A note.\n"},
        "PL-0001: note",
        "2026-08-30T09:00:00+00:00",
    )

    assert main(["--items", str(root / "items"), "--today", "2026-09-02", "show", "PL-0001"]) == 0

    out = capsys.readouterr().out
    assert f"LAPSED on {BRANCH}" in out
    assert (
        "lapsed legacy claim, made 2026-08-20 12:00 UTC; lapsed 2026-08-27 12:00 UTC,"
        " 7 days after the last commit that renewed it"
    ) in out
    assert "That claim holds nothing, so `bin/docket claim PL-0001` takes the item." in out
    assert f'bin/docket claim PL-0001 --over {BRANCH} --reason "..."' in out
    assert "get_session" not in out
    assert "IN FLIGHT" not in out
    assert "Its file is already edited on claude/capture-z9x8c7" in out


def test_show_offers_no_takeover_of_a_lapsed_claim_where_another_claim_is_live(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-N162`'s review: a lapsed claim is not what stands in the way once another is live.

    The next session claims plainly over a lapsed claim, which stays unspent
    until its branch goes. `show` went on printing its takeover beside the live
    claim - "do not start this" and "take it over" on one screen, the second
    refused by `claim` - and printed it to the live holder too.
    """
    root = _flight_repo(tmp_path, "PL-0001 Do the thing")
    second = "claude/second-abc"
    _commit_on(
        root, second, {"src/second.txt": "x\n"}, "PL-0001 Carry on", "2026-08-30T09:00:00+00:00"
    )
    ran = ["--items", str(root / "items"), "--today", "2026-09-01", "show", "PL-0001"]

    assert main(ran) == 0
    out = capsys.readouterr().out
    assert f"IN FLIGHT on {second}" in out

    subprocess.run(["git", "checkout", "-q", second], cwd=root, check=True, capture_output=True)
    assert main(ran) == 0
    held = capsys.readouterr().out
    assert f"IN FLIGHT on this branch ({second})" in held

    for said in (out, held):
        assert "LAPSED" not in said
        assert "--over" not in said


def test_show_words_a_hold_on_this_branch_as_this_branch_s_own(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A disposition, a name and a lapsed claim, each read from the branch holding it.

    `PL-N162`'s review: the other-branch wording is what a session must never
    be shown about its own branch - told to read its own copy first, or
    offered `--over` to take over its own claim - and every other `show` test
    here reads from `main`.
    """
    root = _flight_repo(tmp_path, "PL-0001 Do the thing")
    triage = "claude/triage-pass-q2w3e4"
    _commit_on(
        root,
        triage,
        {
            "items/PL-0001-on-main.md": READY.replace("PL-B1B1", "PL-0001").replace(
                "status: ready", "status: blocked"
            )
        },
        "Triage",
        "2026-08-31T09:00:00+00:00",
    )
    named = "claude/pl-0002-named"
    _commit_on(
        root,
        named,
        {"items/PL-0002-other.md": READY.replace("PL-B1B1", "PL-0002"), "src/n.txt": "x\n"},
        "tidy",
        "2026-08-31T09:00:00+00:00",
    )
    _commit_on(
        root,
        "main",
        {"items/PL-0002-other.md": READY.replace("PL-B1B1", "PL-0002")},
        "file it",
        "2026-08-31T08:00:00+00:00",
    )
    ran = ["--items", str(root / "items"), "--today", "2026-09-02", "show"]

    def show(branch: str, item: str) -> str:
        subprocess.run(["git", "checkout", "-q", branch], cwd=root, check=True, capture_output=True)
        assert main([*ran, item]) == 0
        return capsys.readouterr().out

    status = show(triage, "PL-0001")
    assert f"STATUS HELD on this branch ({triage}) - its copy moves PL-0001 to `blocked`." in status
    assert "Read that copy before starting" not in status.replace("\n  ", " ")

    name = show(named, "PL-0002")
    assert f"IN FLIGHT on this branch ({named}), by its name - PL-0002 is this session's" in name
    assert "`bin/docket claim PL-0002` does." in name

    lapsed = show(BRANCH, "PL-0001")
    assert f"LAPSED on this branch ({BRANCH}) - its claim on PL-0001 no longer holds it." in lapsed
    assert "`bin/docket claim PL-0001` claims it again, from now." in lapsed
    assert "--over" not in lapsed


def test_show_marks_a_named_branch_that_closed_its_claimed_item_by_the_status_alone(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-N162`'s review: blocking its own item left the name holding it as work in flight.

    The branch claimed its item, then blocked it, which releases the claim.
    Its name went on holding the item beside the disposition, worded as work
    that "records no claim" - and, to the session itself, as an instruction
    to claim again what it had just stopped. A branch that recorded a claim
    holds by that record, so the status it moved is the one mark.
    """
    root = _flight_repo(tmp_path, "Tidy up")
    work = "claude/pl-0001-work"
    _commit_on(
        root, work, {"src/w.txt": "x\n"}, "PL-0001 Start the work", "2026-08-21T09:00:00+00:00"
    )
    _commit_on(
        root,
        work,
        {
            "items/PL-0001-on-main.md": READY.replace("PL-B1B1", "PL-0001").replace(
                "status: ready", "status: blocked"
            )
        },
        "PL-0001 Block it",
        "2026-08-21T10:00:00+00:00",
    )
    ran = ["--items", str(root / "items"), "--today", "2026-08-23", "show", "PL-0001"]

    assert main(ran) == 0
    out = capsys.readouterr().out
    subprocess.run(["git", "checkout", "-q", work], cwd=root, check=True, capture_output=True)
    assert main(ran) == 0
    own = capsys.readouterr().out

    assert f"STATUS HELD on {work}" in out
    assert f"STATUS HELD on this branch ({work})" in own
    for said in (out, own):
        assert said.count("STATUS HELD") == 1
        assert "IN FLIGHT" not in said
        assert "records no claim" not in said
        assert "bin/docket claim" not in said


def test_show_marks_a_named_branch_that_moved_its_unclaimed_item_s_status_once(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A name and a disposition on one branch are one mark, the disposition, as `flight` prefers."""
    root = _flight_repo(tmp_path, "Tidy up")
    named = "claude/pl-0001-groom"
    _commit_on(
        root,
        named,
        {
            "items/PL-0001-on-main.md": READY.replace("PL-B1B1", "PL-0001").replace(
                "status: ready", "status: blocked"
            )
        },
        "groom",
        "2026-08-21T09:00:00+00:00",
    )

    assert main(["--items", str(root / "items"), "--today", "2026-08-23", "show", "PL-0001"]) == 0

    out = capsys.readouterr().out
    assert f"STATUS HELD on {named}" in out
    assert "by its name" not in out


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


def _rewritten_repo(tmp_path: Path) -> Path:
    """A branch left on a history the default branch has since been rebuilt from.

    The shape of `PL-YGF3`'s incident, built with plumbing every git ships:
    the same two subjects at the same author dates, committed twice over
    different content, which is what a purge of a file out of history leaves.
    Rebuilding every commit shares no root with the original, so there is no
    merge base at all - measured against a real `filter-branch` rewrite on
    2026-09-06, and the reason the fork-point guard could not be left in front
    of this.
    """
    root = tmp_path / "rewritten"
    (root / "items").mkdir(parents=True)
    (root / "items" / "PL-0001-on-main.md").write_text(READY.replace("PL-B1B1", "PL-0001"))
    history = (
        ("PL-0001 First", "2026-08-01T12:00:00+00:00"),
        ("PL-0002 Second", "2026-08-02T12:00:00+00:00"),
    )

    def git(*args: str, when: str = "2026-08-05T12:00:00+00:00") -> None:
        env = os.environ | {"GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, env=env)

    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(root)],
        check=True,
        capture_output=True,
    )
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        git("config", name, value)
    for index, (subject, when) in enumerate(history):
        (root / f"f{index}.txt").write_text("before the rewrite\n")
        git("add", "-A")
        git("commit", "-qm", subject, when=when)

    git("checkout", "-qb", "claude/pl-k7qx-live")
    (root / "items" / "PL-9Y42-captured.md").write_text(READY.replace("PL-B1B1", "PL-9Y42"))
    git("add", "-A")
    git("commit", "-qm", "PL-9Y42 Capture what only this branch holds", when=history[-1][1])

    git("checkout", "-q", "main")
    git("checkout", "-q", "--orphan", "rewritten")
    for index, (subject, when) in enumerate(history):
        (root / f"f{index}.txt").write_text("after the rewrite\n")
        git("add", "-A")
        git("commit", "-qm", subject, when=when)
    git("branch", "-qM", "main")
    (root / "items" / "PL-0003-after.md").write_text(READY.replace("PL-B1B1", "PL-0003"))
    git("add", "-A")
    git("commit", "-qm", "PL-0003 Landed after the rewrite")
    git("checkout", "-q", "claude/pl-k7qx-live")
    return root


def test_a_rewritten_base_is_spelled_in_a_way_real_git_answers(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The plumbing half of the rewrite rule: `git log --left-right` over the divergence.

    What the digest said before this existed was "3 behind and 3 ahead" with
    `git merge main` under it - which replays the base's own history against
    itself - or nothing at all, because a rewrite usually leaves no merge base
    and the fork-point guard declined. Either way the branch's one unique
    commit went unnamed, and `PL-YGF3` is what that cost.
    """
    root = _rewritten_repo(tmp_path)

    assert main(["--items", str(root / "items"), "branch", "--no-fetch"]) == 0

    out = capsys.readouterr().out
    assert "Branch: claude/pl-k7qx-live is 3 behind main and 3 ahead." in out
    assert "rewritten history, not divergence: 2 of this branch's 3 commits" in out
    assert "PL-9Y42 Capture what only this branch holds" in out
    assert "git checkout -B claude/pl-k7qx-live-rewritten main" in out
    # Both of the answers that lose the commit above, and the decline that
    # printed neither, are gone.
    assert "git merge main" not in out
    assert "--deepen" not in out


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
        git("commit", "-qm", f"PL-M0{number} Main work {number}")  # not-an-id

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


def _unevenly_truncated_pair(tmp_path: Path) -> Path:
    """A clone whose default branch is grafted on one path and complete on another.

    `_shallow_pair`'s default branch is linear, so a walk that descends below its
    horizon must end on a grafted commit - which is the signature `PL-MGNC`'s
    guard catches. This is the same container with one difference that removes
    that signature: `main` reaches the root down a **second, shorter path**, so a
    single `--depth` truncates the long path while leaving the short one whole.

    Depth is counted per path from the tip, which is what makes the truncation
    uneven from one ordinary number. A branch forked from a commit on the long
    path below the graft then descends through commits `^main` cannot exclude and
    terminates against the fork point the *short* path still reaches - a clean
    stop, with every commit carrying a parent (`PL-W1LN`).
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

    def commit(name: str, subject: str) -> None:
        (origin / name).write_text(f"{name}\n")
        git("add", "-A")
        git("commit", "-qm", subject)

    commit("root", "PL-R00T Lay the first commit")
    commit("shared", "PL-SH4R Where both paths meet")
    # The long path. Its ids are spelled to the id grammar - four consonant-safe
    # characters - because `PL-M01` is not an id `ID_PATTERN` matches and a
    # subject carrying one is credited to nobody, which would make this fixture
    # prove nothing. `PL-M3NW` is the commit the live branch forks from, and the
    # one the report will wrongly carry.
    for name, subject in (
        ("a1", "PL-M1QJ Main work 1"),
        ("a2", "PL-M2KT Main work 2"),
        ("a3", "PL-M3NW Main work 3"),
        ("a4", "PL-M4RB Main work 4"),
        ("a5", "PL-M5VC Main work 5"),
        ("a6", "PL-M6WD Main work 6"),
    ):
        commit(name, subject)
    # The short path, merged back in: this is what leaves `main` reaching the
    # root at a depth that still grafts the long one.
    git("checkout", "-qb", "side", "main~6")
    commit("side", "PL-S1D3 The short path")
    git("checkout", "-q", "main")
    git("merge", "-q", "--no-edit", "-m", "Merge the short path", "side")
    commit("tip", "PL-T1PP The tip")
    # The live branch, forked from a commit of `main`'s own long path *below* the
    # graft the depth leaves: `main~5` is `PL-M3NW`, and `--depth=5` reaches only
    # as far as `PL-M4RB` down this path.
    git("checkout", "-qb", BRANCH, "main~5")
    commit("branch-work", "PL-K7QX Do the thing")
    git("checkout", "-q", "main")

    work = tmp_path / "work"
    # Five leaves `main` grafted partway down the long path while the short path
    # reaches the root inside the same depth, which is the uneven horizon. The
    # branch is then fetched whole, so its own descent carries full parentage.
    subprocess.run(
        ["git", "clone", "-q", "--depth=5", "--no-single-branch", "--branch", "main"]
        + [origin.as_uri(), str(work)],
        check=True,
        capture_output=True,
        env=dated,
    )
    git("fetch", "-q", "origin", f"{BRANCH}:refs/remotes/origin/{BRANCH}", cwd=work)
    return work


def test_flight_still_reports_a_branch_pushed_to_after_its_pull_request_squashed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The shape every long-lived branch here ends up in, against real git.

    A session runs a design round on an item, that pull request squash-merges,
    and the session goes on to push the implementation to the same branch. The
    merge carries the item file to `main` and its subject leads with the id, so
    both facts `_taken_on_base` judged a claim by were true of the branch from
    the moment it merged - and they said nothing about the commit that came
    after. Measured 2026-09-20 on `origin/claude/lucid-dijkstra-i1qy6x`, where
    `PL-3K9B`'s whole implementation went unreported and a second session was
    told three times to start it (`PL-8JQQ`).

    Real git rather than an injected runner, for the reason `_branched_repo`
    uses it: the walk that dates the base's take is a `git log --format` this
    fixture is the only thing proving git accepts.
    """
    root = tmp_path / "repo"
    (root / "items").mkdir(parents=True)
    item = root / "items" / "PL-K7QX-the-item.md"
    item.write_text(READY.replace("PL-B1B1", "PL-K7QX"))
    (root / "a.py").write_text("first\n")
    clock = {"now": "2026-09-20T10:00:00+00:00"}

    def git(*args: str) -> None:
        env = os.environ | {"GIT_AUTHOR_DATE": clock["now"], "GIT_COMMITTER_DATE": clock["now"]}
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, env=env)

    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(root)],
        check=True,
        capture_output=True,
    )
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        git("config", name, value)
    git("add", "-A")
    git("commit", "-qm", "PL-K7QX: capture the item")

    # The design round: a queue-only commit, which is what the pull request took.
    git("checkout", "-qb", "work")
    clock["now"] = "2026-09-20T15:00:00+00:00"
    item.write_text(item.read_text() + "\nThe decision.\n")
    git("commit", "-qam", "PL-K7QX: ratify the rule and seat the implementation")
    git("checkout", "-q", "main")
    git("merge", "-q", "--squash", "work")
    clock["now"] = "2026-09-20T15:30:00+00:00"
    git("commit", "-qm", "PL-K7QX: ratify the rule and seat the implementation (#801)")

    # And the work itself, pushed to the same branch afterwards. It leaves the
    # item file alone, because the round that merged is what wrote it.
    git("checkout", "-q", "work")
    clock["now"] = "2026-09-20T16:00:00+00:00"
    (root / "a.py").write_text("fixed\n")
    (root / "test_a.py").write_text("def test_a() -> None:\n    pass\n")
    git("add", "-A")
    git("commit", "-qm", "PL-K7QX: the whole implementation")
    git("checkout", "-q", "main")

    assert main(["--items", str(root / "items"), "flight"]) == 0

    out = capsys.readouterr().out
    assert "PL-K7QX" in out
    assert "work" in out


def test_flight_reads_below_an_uneven_horizon_by_the_landed_prefix(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The limit `PL-MGNC`'s guard cannot reach, which the claim record's landed prefix does.

    **This test asserted a known-wrong answer on purpose until `PL-N162`**, on
    `PL-W1LN`'s decision: the shape is real and reproducible, and no *sound* fix
    to the walk is available inside a truncated checkout. Whether an emitted
    commit is one the base reaches in the **full** history is a question about
    exactly the commits the clone does not hold, and naming a ref unread whenever
    the base is truncated would silence `flight` in every agent container
    (project owner, 2026-09-13).

    `flight` now answers from `claims.holdings`, and that read asks a different
    question the clone *can* answer: whether the branch's work up to a commit is
    content the base already holds (`claims._landed_through`). The default
    branch's own commits, reached below the graft, wrote nothing the base lacks,
    so every claim they carry is spent by landing, since each claim is its own
    commit or an ancestor of a landed one, and the branch's own commit after
    them is still read. The walk guard is unchanged and stays silent,
    since every emitted commit still has a parent; what changed is that the
    wrong ids no longer survive past it. `vcs._unmerged_commits` kept the limit
    until `PL-FX5Q` deleted it.
    """
    work = _unevenly_truncated_pair(tmp_path)
    walk = (
        subprocess.run(
            ["git", "log", "--format=%H %p %s", "^origin/main", f"origin/{BRANCH}", "--"],
            cwd=work,
            check=True,
            capture_output=True,
            text=True,
        )
        .stdout.strip()
        .splitlines()
    )

    # The precondition that makes this the uncaught shape rather than the caught
    # one: the walk reaches past the horizon and every commit it emits has a
    # parent, so there is no parentless commit for the guard to key on.
    assert len(walk) > 1, "the walk must descend past the branch's own commit"
    for line in walk:
        assert len(line.split()) >= 3, f"every emitted commit must carry a parent: {line!r}"

    assert main(["--items", str(work / "items"), "--today", "2026-08-23", "flight"]) == 0
    out = capsys.readouterr().out

    # The branch's own work, correctly reported.
    assert "PL-K7QX" in out
    # A commit of `main`'s own, spent by the landed prefix rather than reported.
    assert "PL-M3NW" not in out
    # And the guard stayed silent: the walk was not refused, its wrong ids were
    # answered after it.
    assert "cannot be compared with origin/main" not in out


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
    assert "PL-M01" not in out  # not-an-id
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


def _record_repo(
    tmp_path: Path, *, closes: bool = True, extra: str = "", name: str = "PL-K7QX-a-closed-item.md"
) -> Path:
    """A checkout whose tip commit closes `PL-K7QX`, built with real git.

    `record` compares a commit's tree against its parent's, and only a real
    checkout proves those commands are spelled in a way git accepts.

    `name` is the file the item lives in. It defaults to the one its title
    generates; pass a stale one to stand for a file whose slug has drifted.
    """
    root = tmp_path / "repo"
    items = root / "items"
    items.mkdir(parents=True)
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


def test_record_leaves_a_hand_written_block_alone(tmp_path: Path) -> None:
    """`PL-7K8Y`: the test above passes on a file the tool itself wrote.

    On a hand-typed one it did not. `record` rendered from the parsed item, so
    keys in any other order came back canonical and a value continued over an
    indented line came back on one - removals, in a diff about the close-out's
    own work. `verify.sanctioned_queue_edit` grants the backfill its exemption
    only where the diff removes nothing, so the close-out that ran the command
    exactly as the skill instructs was reported as editing a file outside its
    commission, and the per-commit reading meant a later fixup commit could
    not clear it. Both shapes are here because both were live: 118 of the
    store's item files carried a non-canonical order on 2026-09-20 and 12
    carried a multi-line value.
    """
    scrambled = (
        "verify: true\nreason: two problems, and the second one\n  is PL-B1C2\nclosed: 2026-09-01\n"
    )
    root = _record_repo(tmp_path, extra=scrambled)
    before = (root / "items" / "PL-K7QX-a-closed-item.md").read_text(encoding="utf-8")

    assert main(["record", "257", "--items", str(root / "items")]) == 0

    after = (root / "items" / "PL-K7QX-a-closed-item.md").read_text(encoding="utf-8")
    assert after == before.replace("closed: 2026-09-01\n", "closed: 2026-09-01\npr: 257\n")
    assert set(before.splitlines()) <= set(after.splitlines()), "a line was removed"


def test_record_keeps_a_drifted_filename(tmp_path: Path) -> None:
    """A field write must not rename, however stale the slug it finds.

    The store names a file from its title, so re-rendering a drifted one
    through `write_item` renames it. That turns the single added line two
    sessions are told git will merge into a delete-plus-add, which takes a
    modify/delete conflict against whoever else holds the file (`PL-LBR6`) -
    and backing it out with `git checkout --` restores the tracked deletion
    while leaving the untracked new name, so `check` then reports one id used
    by two files (`PL-5QLP`).
    """
    root = _record_repo(tmp_path, name="PL-K7QX-an-older-title.md")
    items = root / "items"

    assert main(["record", "257", "--items", str(items)]) == 0

    assert sorted(path.name for path in items.glob("*.md")) == ["PL-K7QX-an-older-title.md"]
    assert "pr: 257" in (items / "PL-K7QX-an-older-title.md").read_text(encoding="utf-8")


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


def _owed_clone(
    tmp_path: Path, *, subject: str = "PL-K7QX: close it (#148)", version: str = ""
) -> Path:
    """A checkout whose `origin/main` holds a closure recording no `pr`.

    The state every merge leaves behind, built with real git and a real remote
    because `closures_on_base` resolves the default base through one. `subject`
    is what the squash merge wrote, which is where the number comes from.

    `version` puts a version file on the base as well, which is what the
    release guards read to answer whether a number has already shipped. Off by
    default: a checkout that only has to answer `record` needs no version, and
    the guards decline on a base they cannot read rather than guessing.
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
    if version:
        (origin / "pyproject.toml").write_text(
            f'[project]\nversion = "{version}"\n', encoding="utf-8"
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


# --- the number reaching the notes, not only the item ------------------------
#
# `PL-W7WL`, filed four times from four separate cuts. The documented order is
# `make release` and then `docket record`, so an item that merged between the
# previous cut and this one had no `pr` when the notes were rendered and its
# bullet shipped naming no pull request - and `release` answers `Nothing to
# release` once the version is cut, correctly, so nothing could put one there
# afterwards. Nine of `v0.4.22`'s fifteen bullets and twelve of `v0.4.35`'s
# sixteen were in that state.


def _releasable_owed_clone(tmp_path: Path, *, subject: str = "PL-K7QX: close it (#148)") -> Path:
    """An `_owed_clone` that a release can also be cut from.

    The two halves of the observed case in one checkout: the base names the
    number, and the item about to ship does not record it yet.
    """
    work = _owed_clone(tmp_path, subject=subject, version="0.2.5")
    subprocess.run(["git", "tag", "v0.2.5"], cwd=work, check=True, capture_output=True)
    _hold_the_train(work)
    return work


def _shipped_notes(work: Path, version: str = "0.2.6") -> str:
    return (work / "docs" / "releases" / f"v{version}.md").read_text(encoding="utf-8")


def test_a_cut_backfills_a_pull_request_number_the_base_already_names(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The observed defect, driven end to end: the bullet cites the merge.

    The number is in the base's history at the moment the notes are rendered.
    Nothing had read it there, because the only reader ran after the cut.
    """
    work = _releasable_owed_clone(tmp_path)

    assert main(["release", "0.2.6", "--no-fetch", "--items", str(work / "items")]) == 0

    assert "- PL-K7QX A closed item — #148" in _shipped_notes(work)
    assert "PL-K7QX: recorded `pr: 148`, so these notes can cite it" in capsys.readouterr().out


def test_a_cut_backfill_writes_the_number_onto_the_item_as_well(tmp_path: Path) -> None:
    """Both records or neither; one repaired half is the same disagreement.

    A cut that cited the number and left the store owing it would keep
    `docket check`'s missing-`pr` advisory counting the item forever.
    """
    work = _releasable_owed_clone(tmp_path)

    main(["release", "0.2.6", "--no-fetch", "--items", str(work / "items")])

    assert _work_pr(work) == "pr: 148"


def test_a_dry_run_cut_shows_the_number_it_would_record_and_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The dry run exists to review the notes, so it has to render the real ones."""
    work = _releasable_owed_clone(tmp_path)

    assert (
        main(["release", "0.2.6", "--dry-run", "--no-fetch", "--items", str(work / "items")]) == 0
    )

    out = capsys.readouterr().out
    assert "PL-K7QX: would record `pr: 148`" in out
    assert "- PL-K7QX A closed item — #148" in out
    assert _work_pr(work) == ""
    assert not (work / "docs" / "releases").exists()


def test_a_cut_ships_the_bullet_as_it_stands_when_no_commit_names_a_number(tmp_path: Path) -> None:
    """Never a refusal: provenance one `git fetch` away must not stop a release.

    The bullet goes out as it would have before, and `docket record` repairs it
    afterwards - which is the half of this that a cut can never do.
    """
    work = _releasable_owed_clone(tmp_path, subject="PL-K7QX: close it")

    assert main(["release", "0.2.6", "--no-fetch", "--items", str(work / "items")]) == 0

    assert "- PL-K7QX A closed item\n" in _shipped_notes(work)


def test_record_restates_a_released_bullet_that_shipped_without_a_number(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The repair half: the only supported route to a bullet already shipped.

    Re-cutting the version would regenerate it and is refused, correctly
    (`PL-1MKQ`), so without this the line can only be corrected by hand - which
    is what happened to `v0.4.32` and did not happen to the other twenty-one.
    """
    work = _releasable_owed_clone(tmp_path)
    releases = work / "docs" / "releases"
    releases.mkdir(parents=True)
    (releases / "v0.2.5.md").write_text(
        "## v0.2.5 - 2026-08-20\n\n### infra\n\n- PL-K7QX A closed item\n", encoding="utf-8"
    )

    assert main(["record", "--items", str(work / "items")]) == 0

    assert "- PL-K7QX A closed item — #148" in (releases / "v0.2.5.md").read_text(encoding="utf-8")
    assert "restated 1 bullet(s)" in capsys.readouterr().out


def test_record_leaves_a_notes_file_whose_bullets_all_cite_their_merge(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """No diff on a healthy tree, which is what `make fix` running it requires."""
    work = _releasable_owed_clone(tmp_path)
    releases = work / "docs" / "releases"
    releases.mkdir(parents=True)
    healthy = "## v0.2.5 - 2026-08-20\n\n### infra\n\n- PL-K7QX A closed item — #148\n"
    (releases / "v0.2.5.md").write_text(healthy, encoding="utf-8")

    assert main(["record", "--items", str(work / "items")]) == 0

    assert (releases / "v0.2.5.md").read_text(encoding="utf-8") == healthy
    assert "restated" not in capsys.readouterr().out


def test_a_dry_run_record_says_what_it_would_restate_without_writing_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    work = _releasable_owed_clone(tmp_path)
    releases = work / "docs" / "releases"
    releases.mkdir(parents=True)
    shipped = "- PL-K7QX A closed item\n"
    (releases / "v0.2.5.md").write_text(shipped, encoding="utf-8")

    assert main(["record", "--dry-run", "--items", str(work / "items")]) == 0

    assert (releases / "v0.2.5.md").read_text(encoding="utf-8") == shipped
    assert "would restate 1 bullet(s)" in capsys.readouterr().out


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


def _shallow_clone(tmp_path: Path) -> tuple[Path, Path]:
    """A `--depth 1` clone of a remote whose last three commits each closed one item.

    The container an agent session runs in has no checkout, so it clones
    `--depth 1` - which is shallow *and* single-branch. Every item is `done` in
    the tree it lands in and none records a `pr`, which is the state every
    merge leaves and the one `record` exists to clear.

    Built against real git rather than a fake, because the defect was a wrong
    belief about what git does at a graft boundary: it reports every file in
    the boundary commit's tree as *added*, so each of the three items looks
    closed by that one commit. No fake would have been written with that shape
    unless somebody already knew.

    Returns the origin and the clone, because the test deepens the clone from
    the origin to show the decline lifting.
    """
    origin = tmp_path / "origin"
    items = origin / "items"
    items.mkdir(parents=True)

    def git(*args: str, cwd: Path = origin) -> None:
        subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)

    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(origin)],
        check=True,
        capture_output=True,
    )
    for key, value in (("user.email", "t@example.com"), ("user.name", "T")):
        git("config", key, value)
    for identifier in ("PL-6Q8N", "PL-GJDW", "PL-VRMK"):
        (items / f"{identifier}-a-closed-item.md").write_text(
            RECORD_ITEM.format(id=identifier, status="ready", extra=""), encoding="utf-8"
        )
    git("add", "-A")
    git("commit", "-qm", "capture three items")
    for identifier, number in (("PL-6Q8N", 399), ("PL-GJDW", 400), ("PL-VRMK", 401)):
        (items / f"{identifier}-a-closed-item.md").write_text(
            RECORD_ITEM.format(id=identifier, status="done", extra=""), encoding="utf-8"
        )
        git("add", "-A")
        git("commit", "-qm", f"{identifier}: do the thing (#{number})")

    work = tmp_path / "work"
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", origin.as_uri(), str(work)],
        check=True,
        capture_output=True,
    )
    return origin, work


def _pr_fields(work: Path) -> dict[str, str]:
    fields = {}
    for identifier in ("PL-6Q8N", "PL-GJDW", "PL-VRMK"):
        text = (work / "items" / f"{identifier}-a-closed-item.md").read_text(encoding="utf-8")
        fields[identifier] = next(
            (line for line in text.splitlines() if line.startswith("pr:")), ""
        )
    return fields


def test_record_declines_on_a_checkout_it_cannot_walk(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """It wrote one merge's number onto every closure in the tree (`PL-KX9N`).

    Observed 2026-09-06 in a session whose container had cloned `--depth 1`:
    `record` wrote `#401` onto five items, of which four had merged in `#399`,
    `#400` and `#402`. The clone holds one commit, so the walk that recovers a
    number reached only that commit, and at a graft boundary every file reads
    as added and every closed item as closed right there.

    The silent half is what made it worth an item rather than a fix. `check`
    declines to *verify* a recorded number on this same clone - it says so,
    under `Not checked` - and then `record` wrote one anyway, after which
    `check` reports no error at all: the field is present and well formed, and
    the one check that could have contradicted it had already excused itself.

    Deepening is the other half of the assertion. A decline that a fetch cannot
    lift would be a refusal to work in the only checkout these sessions have.
    """
    origin, work = _shallow_clone(tmp_path)

    assert main(["record", "--items", str(work / "items")]) == 0

    assert _pr_fields(work) == {"PL-6Q8N": "", "PL-GJDW": "", "PL-VRMK": ""}
    out = capsys.readouterr().out
    assert "401" not in out
    assert "git fetch --unshallow origin" in out

    subprocess.run(
        ["git", "fetch", "-q", "--unshallow", origin.as_uri()],
        cwd=work,
        check=True,
        capture_output=True,
    )

    assert main(["record", "--items", str(work / "items")]) == 0

    assert _pr_fields(work) == {"PL-6Q8N": "pr: 399", "PL-GJDW": "pr: 400", "PL-VRMK": "pr: 401"}


def test_record_refuses_a_merge_without_the_number_it_is(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`--merge` names one commit; the bare form reads the base and takes none."""
    work = _owed_clone(tmp_path)

    assert main(["record", "--merge", "HEAD", "--items", str(work / "items")]) == 2

    assert "needs the number that merge is" in capsys.readouterr().out
    assert _work_pr(work) == ""


def _owed_project(tmp_path: Path, *, store: str = "docs/items") -> Path:
    """A clone whose `origin/main` holds a shipped closure recording no `pr`, plus work.

    Shipped, because a closure no cut has stamped is not owed its number yet:
    the cut writes it before it renders the notes (`PL-XYQW`).

    `store` is where the queue sits, and the default is the default setting
    rather than a constraint. It was a constraint when this was written: the
    git reads behind the closure advisory took their path from
    `config.items_dir`, so a store anywhere else was invisible to them and
    every count under test agreed at zero for the wrong reason. Those reads go
    through the invocation's `tracked` since `PL-T441`, which is what lets this take the
    location as an argument at all.

    The open item is what gives `next` a pick, which is the only state in
    which it prints a count at all.
    """
    origin = tmp_path / "origin"
    items = origin / store
    items.mkdir(parents=True)
    closed = "PL-K7QX-a-closed-item.md"

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=origin, check=True, capture_output=True)

    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(origin)],
        check=True,
        capture_output=True,
    )
    for key, value in (("user.email", "t@example.com"), ("user.name", "T")):
        git("config", key, value)
    (items / "PL-B1B1-a-ready-item.md").write_text(READY, encoding="utf-8")
    (items / closed).write_text(
        RECORD_ITEM.format(id="PL-K7QX", status="ready", extra=""), encoding="utf-8"
    )
    git("add", "-A")
    git("commit", "-qm", "PL-K7QX: capture it")
    (items / closed).write_text(
        RECORD_ITEM.format(
            id="PL-K7QX", status="done", extra="closed: 2026-08-10\nmilestone: v0.1.0\n"
        ),
        encoding="utf-8",
    )
    git("add", "-A")
    git("commit", "-qm", "PL-K7QX: close it (#148)")

    work = tmp_path / "work"
    subprocess.run(["git", "clone", "-q", str(origin), str(work)], check=True, capture_output=True)
    return work / store


def _grooming_counts(store: Path, capsys: pytest.CaptureFixture[str]) -> dict[str, int]:
    """What each command that prints a grooming count printed, on one store."""

    def count(pattern: str, text: str) -> int:
        found = re.search(pattern, text)
        return int(found.group(1)) if found else 0

    main(["check", "--items", str(store), "--today", "2026-08-24"])
    check = capsys.readouterr().out
    main(["digest", "--items", str(store), "--today", "2026-08-24"])
    digest = capsys.readouterr().out
    main(["next", "--items", str(store), "--today", "2026-08-24"])
    following = capsys.readouterr().out
    return {
        "check": count(r"(\d+) advisor(?:y|ies)", check),
        "digest": count(r"Grooming due: (\d+) advisor", digest),
        "next": count(r"(\d+) grooming advisor", following),
    }


def test_the_digest_and_next_count_the_grooming_debt_check_counts(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """One store, one commit, three commands that print a count of it.

    The digest reported 10 advisories where `check` reported 19, because
    `cmd_digest` never passed `closures` and `checks.py` reads a caller that
    did not ask as a caller with nothing to report - so the `pr`-backfill
    advisories were structurally invisible to the one line a session reads
    before anything else (`PL-VKGJ`). `next` under-reported for a second
    reason, having omitted `milestones` as well.

    Pinned as an equality rather than as a number so it keeps holding when the
    advisories themselves change: what must not come back is one command
    printing a total another command would contradict.
    """
    counts = _grooming_counts(_owed_project(tmp_path), capsys)

    assert counts["check"] >= 1, counts
    assert counts["digest"] == counts["check"]
    assert counts["next"] == counts["check"]


def test_every_command_that_prints_a_count_asks_the_same_questions(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The equality above, held one level up from the store it was measured on.

    A count is only as complete as the inputs behind it, and `analyze` skips
    the check behind any input it was not handed. So the test that survives a
    new input being added is not "these totals match on this fixture" but
    "these commands asked the same questions" - which fails the moment one
    call site gains an input the others do not, whether or not the fixture
    happens to exercise it.

    The name is what is compared, not the answer: a roadmap this checkout
    cannot read makes `milestones` `None` for all three alike, which is the
    question asked and declined rather than the question skipped. `landed` is
    the one input a command may differ on and it is passed either way - here
    as `None`, because `--verify` is off and `make docket`, the command the
    digest's line names, does not pass it either.
    """
    asked: dict[str, set[str]] = {}
    real = cli.analyze

    def spy(*args: object, **kwargs: object) -> object:
        asked[current] = set(kwargs)
        return real(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(cli, "analyze", spy)
    store = _owed_project(tmp_path)
    for current in ("check", "digest", "next"):
        main([current, "--items", str(store), "--today", "2026-08-24"])
        capsys.readouterr()

    assert {
        "closures",
        "history",
        "lost",
        "milestones",
        "notes",
        "offered",
        "records",
        "version",
        "window",
    } <= asked["check"]
    assert asked["digest"] == asked["check"]
    assert asked["next"] == asked["check"]


def test_counts_resolve_the_store_from_the_tracked_directory(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """One project, two queue locations, and the same answer from both.

    `--items` is the documented way to point at a store, and the settings are
    read from beside the store rather than from the working directory - so a
    store the loaded config does not name is the ordinary case rather than an
    exotic one. The git reads behind the printed counts took their path from
    `config.items_dir` all the same, so every `git show` missed, nothing read
    as landed, no `pr` was owed, and all three commands reported a clean
    provenance record for a store they never read (`PL-T441`). Exit zero, a
    plausible count, and nothing on the line saying the question went unasked.

    Pinned as an equality between the two layouts rather than as a number, so
    it keeps holding when the advisories themselves change: what must not come
    back is where the queue sits changing the answer. The advisory naming the
    closure is asserted too, because that is the finding that went missing and
    a total can agree for other reasons.
    """
    default = _grooming_counts(_owed_project(tmp_path / "default"), capsys)
    elsewhere = _owed_project(tmp_path / "elsewhere", store="queue")

    main(["check", "--items", str(elsewhere), "--today", "2026-08-24"])
    out = capsys.readouterr().out

    assert "PL-K7QX" in out and "#148" in out
    assert default["check"] >= 1
    assert _grooming_counts(elsewhere, capsys) == default


def test_no_git_read_in_the_cli_takes_the_store_from_the_settings() -> None:
    """`items_dir=` is never handed what the settings call the store.

    The test above holds on the fixture it runs; this holds one level up from
    it, over every reader in the module - including one added later whose
    advisory that fixture does not happen to raise. Worth stating because the
    same surface has now been reached three ways: the root resolved from the
    store's parent (`PL-P757`), the settings read from `docs/` (`PL-K5PW`),
    and the reads behind a count resolved from the settings (`PL-T441`).

    The rule is exact, which is what keeps it out of the
    advisory-nobody-reads category rather than a matter of taste: a keyword
    `items_dir=` naming the settings' copy is the repository-root path of
    whatever store the *config* describes, which is the right answer only by
    coincidence, and `_tracked` is the one spelling that answers for the store
    the caller was actually pointed at.
    """
    tree = ast.parse(Path(cli.__file__).read_text(encoding="utf-8"))
    from_settings = sorted(
        keyword.value.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        for keyword in node.keywords
        if keyword.arg == "items_dir"
        and isinstance(keyword.value, ast.Attribute)
        and keyword.value.attr == "items_dir"
    )

    assert not from_settings, (
        f"cli.py line(s) {from_settings} hand a git read the store the settings name, "
        f"not the one `--items` pointed at; `_tracked` is what resolves it"
    )


def test_every_git_read_in_the_cli_takes_the_invocations_runner() -> None:
    """Every read `cli.py` asks of `vcs` is handed the one runner the command holds.

    The runner facet of `PL-NGBM`'s generator. Every function in `vcs` takes a
    `runner` and builds a plain one where none is passed, so an omission
    raises nothing, prints nothing and answers correctly - and costs the
    command its memo and its `cat-file` batch, which is how `cmd_flight` came
    to re-ask git what the rest of the invocation already knew (`PL-M6FY`).
    Twenty-three call sites had drifted that way when this was written.

    The census is the module's own imports from `vcs` and `claims` rather than
    a list - `claims.holdings` is the in-flight walk since `PL-N162` - so a read
    added later is held without anybody remembering to add it here, and a runner is
    anything that is not a call: a site constructing one of its own is the
    same omission spelled out. `ref_walk` is the one deliberate exception, and
    it is held to passing its plain runner explicitly - measuring must never
    land in what it measures, and a bare call would read as the drift this
    test exists to catch.
    """
    tree = ast.parse(Path(cli.__file__).read_text(encoding="utf-8"))
    modules = {"vcs": vcs, "claims": claims}
    imported = {
        alias.asname or alias.name: getattr(modules[node.module], alias.name)
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module in modules
        for alias in node.names
    }
    reads = {
        name
        for name, value in imported.items()
        if inspect.isfunction(value) and "runner" in inspect.signature(value).parameters
    }
    drifted: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in modules
        ):
            name = node.func.attr
        else:
            continue
        if name not in reads:
            continue
        given = next((keyword.value for keyword in node.keywords if keyword.arg == "runner"), None)
        if given is None or (isinstance(given, ast.Constant) and given.value is None):
            drifted.append(f"{name} (line {node.lineno}) builds a runner of its own")
        elif name != "ref_walk" and isinstance(given, ast.Call):
            drifted.append(f"{name} (line {node.lineno}) is handed a new runner")

    assert {"holdings", "settled_branches"} <= reads, "the census missed the reads it is holding"
    assert not drifted, (
        "cli.py asks git through a runner other than the invocation's: " + "; ".join(drifted)
    )


def test_a_store_at_the_repository_root_is_the_empty_prefix(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The root itself and a store outside the checkout are one case, and take one value.

    `PL-3T2Q`. Resolving the root against itself answers `.`, not the empty
    string, so a store at the root took the prefix no path git prints can
    begin with while the docstring promised the empty prefix - which a
    membership test reads as the opposite answer. Both are now the empty
    prefix, and the readers that cannot ask git about one skip or refuse on it
    in the same words for both.
    """
    root = tmp_path / "repo"
    (root / "docs" / "items").mkdir(parents=True)
    (tmp_path / "elsewhere").mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)

    def tracked(*argv: str) -> str:
        args = merge_shared(build_parser().parse_args(["list", *argv]))
        return cli._invocation(args).tracked

    assert tracked("--items", str(root)) == ""
    assert tracked("--items", str(root / "docs" / "items")) == "docs/items"
    (root / "docket.toml").write_text('[docket]\nitems_dir = "../elsewhere"\n', encoding="utf-8")
    monkeypatch.chdir(root)
    assert tracked() == ""


def test_flight_shares_the_invocations_git_runner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`flight`'s three reads are handed one runner, and it is the invocation's (`PL-M6FY`).

    `cmd_flight` called `branches_in_flight` with no runner, so the library
    built one of its own and the memo every other branch-walking command
    shares was never reached by the command whose whole job is the walk. The
    reads are wrapped rather than replaced, so each still answers and the
    command runs to the end. The walk is `claims.holdings` since `PL-N162`.
    """
    seen: dict[str, object] = {}
    for name in ("holdings", "settled_branches", "open_pull_requests"):
        real = getattr(cli, name)

        def spy(*args: Any, _name: str = name, _real: Any = real, **kwargs: Any) -> Any:
            seen[_name] = kwargs.get("runner")
            return _real(*args, **kwargs)

        monkeypatch.setattr(cli, name, spy)

    assert main(["--items", str(_store(tmp_path, READY)), "--today", "2026-08-24", "flight"]) == 0

    assert set(seen) == {"holdings", "settled_branches", "open_pull_requests"}
    runners = list(seen.values())
    assert isinstance(runners[0], vcs.GitRunner)
    assert all(runner is runners[0] for runner in runners)


#: Every command, spelled to reach the reads it has: the scoped replay, the
#: profile, each command that refreshes before it reads, and both forms of
#: `record`. The writers come last because they change the store the readers
#: above them read.
NO_GIT_ARGV: tuple[tuple[str, ...], ...] = (
    ("check",),
    ("check", "--verify"),
    ("check", "--verify", "--verify-base", "main"),
    ("list",),
    ("digest",),
    ("digest", "--profile"),
    ("flight",),
    ("branch",),
    ("branch", "--brief"),
    ("branch", "--if-stale"),
    ("stranded",),
    ("record", "--dry-run"),
    ("record", "7", "--dry-run"),
    ("triage",),
    ("next",),
    ("next", "--oldest"),
    ("next", "workflow"),
    ("gate",),
    ("feature",),
    ("generators",),
    ("show", "PL-B1B1"),
    ("concurrent",),
    ("concurrent", "PL-B1B1"),
    ("milestone",),
    ("release", "0.2.6", "--dry-run"),
    ("delegable",),
    ("verify", "PL-B1B1"),
    ("status",),
    ("wave",),
    ("trend",),
    ("withdraw", "PL-B1B1", "PL-D4D4", "--because", "PL-D1D1"),
    ("set", "PL-B1B1", "--payoff", "a payoff"),
    ("new", "An idea captured under the flag"),
    ("claim", "PL-B1B1"),
    ("yield", "PL-B1B1"),
    ("arm",),
)


def test_no_git_stops_every_git_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """`--no-git` asks git nothing, in every command, whichever read it would have made.

    The flag facet of `PL-NGBM`'s generator. Each command decided for itself
    whether the flag applied, so it held for branch detection and not for the
    five reads behind a printed count, `check --verify-base`, `digest
    --profile`, `flight`, `branch`, `verify`, `record`, and the fetch
    `stranded` made before looking.

    A real repository, holding a branch with work on it, so that every read
    the flag failed to stop would succeed and be seen rather than fail early
    and hide the reads after it. `Popen` is where to watch, because
    `subprocess.run` constructs one: `vcs._run_git`, the `cat-file` batch and
    `verify._run` all arrive there. A shell command is the project's own
    `verify:` and not docket's read, so it is left out - a bare `--verify`
    still replays under the flag.

    Every command in the parser is run, and the table is held to the parser,
    so a command added later cannot pass by not being listed.
    """
    root = tmp_path / "repo"
    store = root / "docs" / "items"
    store.mkdir(parents=True)
    (root / "docket.toml").write_text('[docket]\nworkflow_paths = ["tools"]\n', encoding="utf-8")
    (root / "pyproject.toml").write_text('[project]\nversion = "0.2.5"\n', encoding="utf-8")
    for name, document in (
        ("PL-B1B1-ready.md", READY),
        ("PL-D1D1-done.md", DONE),
        ("PL-D4D4-captured.md", CAPTURED),
    ):
        (store / name).write_text(document, encoding="utf-8")

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

    git("-c", "init.defaultBranch=main", "init", "-q")
    for setting, value in (("user.email", "t@example.com"), ("user.name", "T")):
        git("config", setting, value)
    git("add", "-A")
    git("commit", "-qm", "base")
    git("checkout", "-qb", "claude/pl-b1b1-work")
    (root / "a.py").write_text("work = True\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "PL-B1B1: the work")

    subcommands = next(
        action
        for action in build_parser()._actions
        if isinstance(action, argparse._SubParsersAction)
    )
    assert {argv[0] for argv in NO_GIT_ARGV} == set(subcommands.choices)

    running = [""]
    spawned: dict[str, list[str]] = {}
    real = subprocess.Popen

    def watched(argv: Any, *rest: Any, **kwargs: Any) -> Any:
        words = [argv] if isinstance(argv, str) else [str(word) for word in argv]
        if not kwargs.get("shell") and words and Path(words[0]).name == "git":
            spawned.setdefault(running[0], []).append(" ".join(words[1:3]))
        return real(argv, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", watched)
    for argv in NO_GIT_ARGV:
        running[0] = " ".join(argv)
        main([*argv, "--items", str(store), "--no-git", "--today", "2026-09-23"])
    capsys.readouterr()

    assert not spawned, "`--no-git` still asked git: " + "; ".join(
        f"`{command}` ran {', '.join(sorted(set(calls)))}" for command, calls in spawned.items()
    )


def _laned_store(tmp_path: Path) -> Path:
    """A store split across the boundary, with one item on each side of it."""
    items = tmp_path / "docs" / "items"
    items.mkdir(parents=True)
    (items.parent / "docket.toml").write_text(
        '[docket]\nworkflow_paths = ["tools", ".claude"]\n', encoding="utf-8"
    )
    brief = "**Problem.** P\n**Why it matters.** W\n**Done when.** D\n"
    for ident, touches in (
        ("PL-PR0D", "src/core/blood.py"),
        ("PL-W0RK", "tools/doc_check.py"),
        ("PL-B0TH", "tools/doc_check.py, src/core/blood.py"),
    ):
        (items / f"{ident}-x.md").write_text(
            f"---\nid: {ident}\ntitle: Item {ident}\npriority: P2\neffort: S\n"
            f"status: ready\nclasses: perf\ntouches: {touches}\nadded: 2026-08-01\n"
            f"---\n\n{brief}",
            encoding="utf-8",
        )
    return items


def _raise_to_p1(item: Path) -> None:
    """Put one laned item at the top of the ranking, whatever its neighbours are."""
    item.write_text(item.read_text(encoding="utf-8").replace("P2", "P1"), encoding="utf-8")


def test_next_takes_a_lane_so_two_sessions_never_rank_onto_one_item(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = str(_laned_store(tmp_path))

    assert _run("next", "product", "--items", store) == 0
    product = capsys.readouterr().out
    assert _run("next", "workflow", "--items", store) == 0
    workflow = capsys.readouterr().out

    assert "PL-PR0D" in product and "PL-W0RK" not in product
    assert "PL-W0RK" in workflow and "PL-PR0D" not in workflow
    assert "in the product lane" in product
    assert "in the workflow lane" in workflow


def test_next_without_a_lane_still_answers_for_the_whole_queue(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The split adds a way to ask; it does not change the default answer.

    The ranking is what must not change. This once also asserted the word
    "lane" was absent from the output, and `PL-0D4X` is what that cost: a
    session prompted for one lane read an answer from the other and had
    nothing in front of it saying so. The line below is the fix, and it says
    nothing about which items are offered or in what order.
    """
    assert _run("next", "--items", str(_laned_store(tmp_path))) == 0
    out = capsys.readouterr().out

    assert "PL-PR0D" in out and "PL-W0RK" in out and "PL-B0TH" in out
    assert "Set aside" not in out


def test_next_without_a_lane_names_the_lane_of_its_answer(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The mismatch a lane-named prompt has to see, in the output it is reading.

    `PL-0D4X`: a session opened with "Next workflow item" ran the bare command
    and started the product-lane pick it was handed. The digest had named both
    lanes, but it is read once and scrolls away, so the fact has to be beside
    the answer rather than upstream of it.
    """
    store = _laned_store(tmp_path)
    _raise_to_p1(store / "PL-PR0D-x.md")

    assert _run("next", "--items", str(store)) == 0
    out = capsys.readouterr().out

    assert "Lane of this answer: PL-PR0D is product work (P1)." in out
    assert "The workflow lane's own pick is PL-W0RK (P2): Item PL-W0RK" in out
    assert "`docket next workflow`" in out
    # `PL-Z27P`: the band rides along even with no roadmap to read, because it
    # is the half of "why this one" that needs no plan. A bare id and title
    # here could not tell a `P1` on the gate from a `P3` placed nowhere, and
    # this line is one of the two places the project owner meets the other
    # lane at all.
    assert "PL-W0RK)" not in out


def test_the_lane_line_names_both_lanes_when_the_answer_is_in_neither(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Crossing work has no "other lane", so both are named rather than one.

    The sentence also says *why* it is unplaced, because the two reasons are
    recovered differently: a crossing item wants a session that can hold the
    whole change, an unplaced one wants somebody to write its `touches`.
    """
    assert _run("next", "--items", str(_laned_store(tmp_path))) == 0
    out = capsys.readouterr().out

    assert "PL-B0TH reaches both halves, so no lane places it." in out
    assert "product: PL-PR0D (P2): Item PL-PR0D" in out
    assert "workflow: PL-W0RK (P2): Item PL-W0RK" in out


def test_the_lane_line_is_silent_when_no_boundary_is_declared(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Fail closed, exactly as `Item.lane` does: no boundary, no lane."""
    assert _run("next", "--items", str(_store(tmp_path, READY))) == 0
    out = capsys.readouterr().out

    assert "PL-B1B1" in out
    assert "Lane of this answer" not in out


def test_a_lane_names_the_work_it_set_aside_rather_than_dropping_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A filter that silently drops part of a queue is how work goes missing."""
    assert _run("next", "workflow", "--items", str(_laned_store(tmp_path))) == 0
    out = capsys.readouterr().out

    assert "Set aside, reaching both halves (1): PL-B0TH" in out
    assert "`docket next` without a lane offers these" in out


def test_a_lane_is_refused_when_no_boundary_is_declared(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Fail closed. A lane that quietly answers from the whole queue is the bug."""
    store = str(_store(tmp_path, READY))

    assert _run("next", "workflow", "--items", store) == 1
    out = capsys.readouterr().out
    assert "no `workflow_paths` are declared" in out
    assert "PL-B1B1" not in out


def test_an_unknown_lane_is_rejected_by_the_parser(tmp_path: Path) -> None:
    """Only the two sides are selectable; `crossing` is an outcome, not a request."""
    with pytest.raises(SystemExit):
        _run("next", "crossing", "--items", str(_laned_store(tmp_path)))


# `READY`'s id, band and capture date changed, for the `--oldest` tests below.
OLDER_P3 = (
    READY.replace("PL-B1B1", "PL-C2C2")
    .replace("priority: P1", "priority: P3")
    .replace("added: 2026-08-01", "added: 2026-07-01")
)
FEATURE = READY.replace("PL-B1B1", "PL-F3F3").replace("classes: perf", "classes: feature")


def test_next_oldest_hands_out_the_longest_waiting_and_names_the_plans_pick_last(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """End to end: age orders the answer, and the plan's own pick is named last.

    The older item is `P3` and the newer `P1`, so the two orders disagree -
    the case the footer exists for, since a session handed work by age must
    see what the plan would have handed it instead (`PL-Q89J`).
    """
    assert _run("next", "--oldest", "--items", str(_store(tmp_path, READY, OLDER_P3))) == 0
    out = capsys.readouterr().out

    assert out.index("1. P3 PL-C2C2") < out.index("2. P1 PL-B1B1")
    assert "Added 2026-07-01, 54 days waiting." in out
    assert out.rstrip().splitlines()[-1] == "The plan's own pick is PL-B1B1 (P1): `docket next`."


def test_next_oldest_composes_with_a_lane_and_an_effort(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The lane filters first, as it does for the plan's ranking, and the footer
    names the plan's pick for the same lane and effort."""
    assert (
        _run("next", "product", "--oldest", "--effort", "S", "--items", str(_laned_store(tmp_path)))
        == 0
    )
    answer, footer = capsys.readouterr().out.split("The plan's own pick")

    assert "1. P2 PL-PR0D" in answer and "PL-W0RK" not in answer
    assert footer.startswith(
        " in the product lane is PL-PR0D (P2): `docket next product --effort S`."
    )


def test_next_oldest_lists_decisions_on_a_line_of_their_own(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An unanswered decision is named, never ranked, however long it has waited."""
    decision = OLDER_P3.replace("status: ready", "status: needs-decision")
    assert _run("next", "--oldest", "--items", str(_store(tmp_path, READY, decision))) == 0
    out = capsys.readouterr().out

    assert "  1. P1 PL-B1B1" in out and "  2. " not in out
    assert (
        "Waiting on a decision, oldest first (1): PL-C2C2 (added 2026-07-01, 54 days waiting)."
        in out
    )


def test_next_without_oldest_still_ranks_new_work(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The flag filters only under itself: a bare `next` is the plan's ranking,
    new work included, with none of `--oldest`'s lines."""
    store = str(_store(tmp_path, READY, FEATURE))

    assert _run("next", "--items", store) == 0
    plain = capsys.readouterr().out
    assert _run("next", "--oldest", "--items", store) == 0
    oldest = capsys.readouterr().out

    assert "PL-F3F3" in plain
    assert "longest-waiting" not in plain and "The plan's own pick" not in plain
    assert "PL-F3F3" not in oldest.split("The plan's own pick")[0]
    assert "Left out as new work, classed feature or planning: 1 item(s)" in oldest


def test_next_oldest_reads_what_counts_as_new_work_from_the_config(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A setting the loader dropped would look applied and not be, so it is read
    end to end: declared empty, nothing is left out."""
    store = str(_store(tmp_path, FEATURE))
    (tmp_path / "docket.toml").write_text("[docket]\nnew_work_classes = []\n", encoding="utf-8")

    assert _run("next", "--oldest", "--items", store) == 0
    out = capsys.readouterr().out

    assert "  1. P1 PL-F3F3" in out
    assert "Left out as new work" not in out


def test_the_digest_names_each_lane_s_pick_for_a_parallel_session(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The digest is read before a session would think to ask for a lane."""
    assert _run("digest", "--items", str(_laned_store(tmp_path))) == 0
    out = capsys.readouterr().out

    assert "By lane, for a second session: product PL-PR0D (P2), workflow PL-W0RK (P2)" in out
    assert "1 in neither lane" in out


def test_the_digest_lane_line_says_what_each_pick_buys(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The offer the project owner has no other way to judge (`PL-WYKF`).

    A simulator item's title describes something they already have an opinion
    about; an apparatus item's does not, and the lane line is the one place the
    digest names the workflow pick. So it carries the payoff below it, on its
    own line, where a pick has one.
    """
    store = _laned_store(tmp_path)
    work = store / "PL-W0RK-x.md"
    work.write_text(
        work.read_text(encoding="utf-8").replace(
            "added: 2026-08-01\n", "added: 2026-08-01\npayoff: the doc check stops lying\n"
        ),
        encoding="utf-8",
    )

    assert _run("digest", "--items", str(store)) == 0
    out = capsys.readouterr().out

    assert "PL-W0RK payoff: the doc check stops lying" in out
    assert "PL-PR0D payoff" not in out


def test_the_digest_says_nothing_about_lanes_when_no_boundary_is_declared(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A line costing every session's context needs a project that asked for it."""
    assert _run("digest", "--items", str(_store(tmp_path, READY))) == 0
    out = capsys.readouterr().out

    assert "Top: PL-B1B1" in out
    assert "By lane" not in out


def test_the_digest_lane_line_names_an_empty_lane_rather_than_omitting_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Silence about one lane reads as 'no lanes here' to the session in it."""
    items = tmp_path / "docs" / "items"
    items.mkdir(parents=True)
    (items.parent / "docket.toml").write_text(
        '[docket]\nworkflow_paths = ["tools"]\n', encoding="utf-8"
    )
    (items / "only-product.md").write_text(
        "---\nid: PL-PR0D\ntitle: Item PL-PR0D\npriority: P2\neffort: S\nstatus: ready\n"
        "classes: perf\ntouches: src/core/blood.py\nadded: 2026-08-01\n---\n\n"
        "**Problem.** P\n**Why it matters.** W\n**Done when.** D\n",
        encoding="utf-8",
    )

    assert _run("digest", "--items", str(items)) == 0
    out = capsys.readouterr().out

    assert "product PL-PR0D (P2), workflow none" in out
    assert "in neither lane" not in out


# --- reading a closed item's recorded `verify:` from real git ----------------
#
# `test_vcs.py` injects git and asserts the narrowing; this asserts the command
# spellings, which a stub cannot. Three of them are new here - a `...` diff, a
# working-tree diff, and an `ls-tree` of the items directory - and a
# misspelling in any of them fails silently, because `_run_git` answers a
# failed command with empty output and an empty answer is "nothing rewritten".

RECORDED_ITEM = """---
id: PL-K7QX
title: Do the thing
priority: P2
effort: S
status: done
classes: perf
touches: a.py
added: 2026-08-01
closed: 2026-08-02
pr: 148
verify: pytest recorded
---

**Problem.** x

**Why it matters.** y

**Done when.** z
"""


def _verify_record_repo(tmp_path: Path) -> Path:
    """A checkout whose default branch holds one closed item, with a branch off it."""
    root = tmp_path / "repo"
    (root / "docs" / "items").mkdir(parents=True)
    (root / "docs" / "items" / "PL-K7QX-a.md").write_text(RECORDED_ITEM, encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        subprocess.run(["git", "config", name, value], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "checkout", "-qb", "work"], cwd=root, check=True, capture_output=True)
    return root


def _rewrite_verify(root: Path, command: str) -> None:
    path = root / "docs" / "items" / "PL-K7QX-a.md"
    path.write_text(
        path.read_text(encoding="utf-8").replace("verify: pytest recorded", f"verify: {command}"),
        encoding="utf-8",
    )


def test_an_untouched_closed_item_is_not_read_from_a_real_checkout(tmp_path: Path) -> None:
    root = _verify_record_repo(tmp_path)

    assert records_on_base(root, {"PL-K7QX": "PL-K7QX-a.md"}).records == ()


def test_an_uncommitted_rewrite_is_read_from_a_real_checkout(tmp_path: Path) -> None:
    # `make check` runs before the commit, which is when restoring the recorded
    # command costs nothing.
    root = _verify_record_repo(tmp_path)
    _rewrite_verify(root, "pytest rewritten")

    assert records_on_base(root, {"PL-K7QX": "PL-K7QX-a.md"}).commands == {
        "PL-K7QX": "pytest recorded"
    }


def test_a_committed_rewrite_is_read_from_a_real_checkout(tmp_path: Path) -> None:
    # And CI runs after it, on a pull request, where the edit is committed and
    # the working-tree diff is empty.
    root = _verify_record_repo(tmp_path)
    _rewrite_verify(root, "pytest rewritten")
    subprocess.run(["git", "commit", "-qam", "rewrite"], cwd=root, check=True, capture_output=True)

    assert records_on_base(root, {"PL-K7QX": "PL-K7QX-a.md"}).commands == {
        "PL-K7QX": "pytest recorded"
    }


def test_a_retitled_item_is_still_found_in_a_real_checkout(tmp_path: Path) -> None:
    # Retitling renames the file, so the base does not hold the tree's path.
    root = _verify_record_repo(tmp_path)
    _rewrite_verify(root, "pytest rewritten")
    subprocess.run(
        ["git", "mv", "docs/items/PL-K7QX-a.md", "docs/items/PL-K7QX-b.md"],
        cwd=root,
        check=True,
        capture_output=True,
    )

    assert records_on_base(root, {"PL-K7QX": "PL-K7QX-b.md"}).commands == {
        "PL-K7QX": "pytest recorded"
    }


# --- which open items' commands a branch wrote (`PL-1P5V`) --------------------
#
# The capture date says when an item arrived, never when its command was
# written, so a rule dated by capture misses every command written afterwards
# for an older item. The branch that changes the command is where it was
# written, and these read that from a real checkout.

LEGACY_COMMAND = "uv run pytest tests/unit/test_a.py"
OPEN_ITEM = (
    RECORDED_ITEM.replace("status: done", "status: ready")
    .replace("closed: 2026-08-02\npr: 148\n", "")
    .replace("verify: pytest recorded", f"verify: {LEGACY_COMMAND}")
)


def _written_repo(tmp_path: Path) -> Path:
    """A checkout whose base holds one open item with a legacy command, and a branch."""
    root = tmp_path / "repo"
    (root / "docs" / "items").mkdir(parents=True)
    (root / "docs" / "items" / "PL-K7QX-a.md").write_text(OPEN_ITEM, encoding="utf-8")
    (root / "docket.toml").write_text(
        '[docket]\nverify_allowlist_from = "2026-09-24"\n', encoding="utf-8"
    )
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        subprocess.run(["git", "config", name, value], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "checkout", "-qb", "work"], cwd=root, check=True, capture_output=True)
    return root


def _edit_item(root: Path, old: str, new: str) -> None:
    path = root / "docs" / "items" / "PL-K7QX-a.md"
    path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")


def test_a_command_the_branch_left_alone_is_not_written_here(tmp_path: Path) -> None:
    # Editing an old item for any other reason asks nothing of its command.
    root = _written_repo(tmp_path)
    _edit_item(root, "effort: S", "effort: M")

    report = commands_written_here(root, {"PL-K7QX": LEGACY_COMMAND})

    assert report.known
    assert report.identifiers == frozenset()


def test_a_rewritten_command_is_written_here_committed_or_not(tmp_path: Path) -> None:
    root = _written_repo(tmp_path)
    _edit_item(root, LEGACY_COMMAND, "bin/docket check")

    assert commands_written_here(root, {"PL-K7QX": "bin/docket check"}).identifiers == {"PL-K7QX"}
    subprocess.run(["git", "commit", "-qam", "rewrite"], cwd=root, check=True, capture_output=True)
    assert commands_written_here(root, {"PL-K7QX": "bin/docket check"}).identifiers == {"PL-K7QX"}


def test_check_holds_a_command_written_for_an_old_item_to_the_admitted_shapes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """End to end: the item predates the cutover, so only the branch dates its command."""
    root = _written_repo(tmp_path)
    store = str(root / "docs" / "items")
    check = ["check", "--items", store, "--today", "2026-09-24"]
    assert main(check) == 0
    capsys.readouterr()

    _edit_item(root, LEGACY_COMMAND, "bin/docket check")

    assert main(check) == 1
    out = capsys.readouterr().out
    assert "its `verify:`, written on this branch, runs `bin/docket check`" in out


def _trend_store(tmp_path: Path, *, lanes: bool = True) -> Path:
    """A store with closures on both sides of the boundary, a week apart."""
    items = tmp_path / "docs" / "items"
    items.mkdir(parents=True)
    declared = 'workflow_paths = ["tools"]\n' if lanes else ""
    (items.parent / "docket.toml").write_text(f"[docket]\n{declared}", encoding="utf-8")
    brief = "**Problem.** P\n**Why it matters.** W\n**Done when.** D\n"
    for ident, touches, closed, effort in (
        ("PL-4401", "src/core.py", "2026-08-25", "M"),
        ("PL-4402", "tools/x.py", "2026-08-25", "S"),
        ("PL-4403", "tools/y.py", "2026-09-02", "S"),
        ("PL-4404", "tools/x.py, src/core.py", "2026-09-02", "S"),
    ):
        (items / f"{ident}-x.md").write_text(
            f"---\nid: {ident}\ntitle: Item {ident}\npriority: P2\neffort: {effort}\n"
            f"status: done\nclasses: perf\ntouches: {touches}\nadded: 2026-08-01\n"
            f"closed: {closed}\n---\n\n{brief}",
            encoding="utf-8",
        )
    return items


def test_trend_reports_each_measure_and_names_the_work_no_lane_could_place(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Three columns, and the crossing item visible rather than folded into a side."""
    store = str(_trend_store(tmp_path))

    assert main(["trend", "--items", store, "--no-git", "--today", "2026-09-05"]) == 0
    out = capsys.readouterr().out

    assert "closed items" in out and "weighted" in out
    rows = {line.split()[0]: line.split()[1:] for line in out.splitlines() if line[:2] == "20"}
    # Week one: one product `M` against one workflow `S`. Half the items and a
    # quarter of the weight - the correction the second column exists to make.
    assert rows["2026-08-25..08-31"] == ["1/1", "0", "0", "50%", "1/3", "25%"]
    # Week two: the crossing item counted in its own column, and left out of
    # the share rather than folded into either side.
    assert rows["2026-09-01..09-05"] == ["1/0", "1", "0", "100%", "1/0", "100%"]


def test_trend_omits_the_churn_columns_when_git_cannot_be_read(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Absent rather than zero: a zero would read as a week nobody wrote code in."""
    store = str(_trend_store(tmp_path))

    assert main(["trend", "--items", store, "--no-git", "--today", "2026-09-05"]) == 0
    out = capsys.readouterr().out

    assert "churn" in out  # the legend still explains why it is missing
    assert "appar./product" not in out


def test_trend_refuses_a_project_that_has_not_drawn_the_boundary(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Fails closed like the lane arguments: with no boundary there are no halves."""
    store = str(_trend_store(tmp_path, lanes=False))

    assert main(["trend", "--items", store, "--no-git", "--today", "2026-09-05"]) == 1
    out = capsys.readouterr().out

    assert "no `workflow_paths` are declared" in out
    assert "closed items" not in out


def test_trend_takes_a_day_at_a_time_when_asked(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = str(_trend_store(tmp_path))

    assert (
        main(["trend", "--items", store, "--no-git", "--by", "day", "--today", "2026-09-05"]) == 0
    )
    out = capsys.readouterr().out

    labels = [line.split()[0] for line in out.splitlines() if line[:2] == "20"]
    assert labels == ["2026-08-25", "2026-09-02"]


def test_trend_rejects_a_window_it_does_not_have(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main(["trend", "--items", str(_trend_store(tmp_path)), "--by", "fortnight"])


UNTRIAGED_CAPTURE = """---
id: PL-C2C2
title: An untriaged capture
status: untriaged
added: 2026-08-02
---

**Problem.** something was noticed
"""


def test_next_reports_the_same_open_count_as_status(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """One store, one number labelled "open" - whichever command prints it.

    `PL-ZWBK`: `cmd_next` computed its own count from `report.open_items`,
    which is the set that is a candidate for *work* and so leaves untriaged
    captures out. `status`, `list` and the digest all go through
    `render.open_count`, which adds them back. So the two disagreed by exactly
    the untriaged count, and disagreed most after a capture-heavy session,
    which is when the backlog most needs stating at full size.

    Asserting the two agree rather than asserting a literal, because the bug
    was a divergence rather than a wrong constant.
    """
    items = _store(tmp_path, READY, UNTRIAGED_CAPTURE)
    assert _run("next", "--items", str(items)) == 0
    next_out = capsys.readouterr().out
    assert _run("list", "--items", str(items)) == 0
    list_out = capsys.readouterr().out

    from_next = re.search(r"(\d+) open\. Suggested next", next_out)
    from_list = re.search(r"Docket: (\d+) open", list_out)
    assert from_next and from_list, (next_out, list_out)
    assert from_next.group(1) == from_list.group(1) == "2", (next_out, list_out)


# `PL-7QKY`: `show` is where a notes thread becomes reachable. It is the
# command a session runs having been handed an item, which is the path
# `docket next` never sees, and the file's own "read this if your task touches
# an open thread" cannot be evaluated without reading the file.

NOTES_ITEM = """---
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


def _notes_project(tmp_path: Path, notes_file: str = "NOTES.md") -> Path:
    store = _store(tmp_path, NOTES_ITEM)
    (tmp_path / "docket.toml").write_text(
        f'[docket]\nnotes_file = "{notes_file}"\n', encoding="utf-8"
    )
    (tmp_path / "NOTES.md").write_text(
        "# Notes\n\n## Open thread: the chart - PL-B1B1\n\nBody.\n\n"
        "## Another thread\n\nMentions PL-B1B1 in passing.\n",
        encoding="utf-8",
    )
    return store


def test_show_names_the_notes_threads_that_concern_the_item(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The pointer, with the line to jump to and which kind of mention it is."""
    store = _notes_project(tmp_path)

    assert _run("show", "PL-B1B1", "--items", str(store)) == 0

    out = capsys.readouterr().out
    assert "notes: 2 thread(s) in NOTES.md name PL-B1B1" in out
    assert "NOTES.md:3 (about) Open thread: the chart - PL-B1B1" in out
    assert "NOTES.md:7 (mentions) Another thread" in out
    assert "Whether a thread is still true is not something this can tell you." in out


def _payoff_store(tmp_path: Path) -> Path:
    """A ready item carrying one line of what closing it buys."""
    return _store(
        tmp_path,
        READY.replace(
            "added: 2026-08-01\n",
            "added: 2026-08-01\npayoff: the induction plot stops implying a measurement\n",
        ),
    )


def test_show_names_what_the_item_buys_under_its_band(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`show` is the path a named item arrives on, and it skips `next` entirely.

    So without this the surface the project owner reaches most carries the
    band, the effort and the gate relation - every decidable fact - and nothing
    saying what the work is for (`PL-WYKF`).
    """
    assert _run("show", "PL-B1B1", "--items", str(_payoff_store(tmp_path))) == 0
    lines = capsys.readouterr().out.splitlines()

    assert "  payoff: the induction plot stops implying a measurement" in lines
    assert lines.index("  payoff: the induction plot stops implying a measurement") == 2


def test_show_says_nothing_where_the_item_carries_no_payoff(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _run("show", "PL-B1B1", "--items", str(_store(tmp_path, READY))) == 0

    assert "payoff" not in capsys.readouterr().out


def test_show_says_what_changed_since_an_item_was_filed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An old item describes the tree it was filed against, so `show` says how that tree moved.

    Real git, dated commits on both sides of `added:`, because the date
    boundary and the deletion are what git has to be asked correctly for: a
    change made before filing is not a change since, and a deleted path is
    reported as gone rather than as unchanged (`PL-TQN2`).
    """
    root = tmp_path / "repo"
    (root / "items").mkdir(parents=True)
    (root / "items" / "PL-B1B1-ready.md").write_text(
        READY.replace(
            "touches: a.py", "touches: kept.py, changed.py, gone.py, planned.py, é.py"
        ).replace("added: 2026-08-01", "added: 2026-08-05")
    )

    def commit(when: str, message: str) -> None:
        dated = os.environ | {"GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
        for args in (["add", "-A"], ["commit", "-qm", message]):
            subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, env=dated)

    subprocess.run(["git", "-c", "init.defaultBranch=main", "init", "-q", str(root)], check=True)
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        subprocess.run(["git", "config", name, value], cwd=root, check=True)
    for name in ("kept.py", "changed.py", "gone.py", "é.py"):
        (root / name).write_text("one\n")
    commit("2026-08-01T12:00:00+00:00", "base")
    (root / "changed.py").write_text("two\n")
    commit("2026-08-02T12:00:00+00:00", "a change before the item was filed")
    (root / "changed.py").write_text("three\n")
    (root / "é.py").write_text("two\n")
    commit("2026-08-15T12:00:00+00:00", "a change after it")
    (root / "gone.py").unlink()
    commit("2026-08-16T12:00:00+00:00", "delete a path the item names")

    assert _run_with_git("show", "PL-B1B1", "--items", str(root / "items")) == 0

    lines = capsys.readouterr().out.splitlines()
    assert (
        "  filed 2026-08-05, 19 days ago - since then,"
        " counting commits on or after that date (UTC):" in lines
    )
    assert "    kept.py - unchanged" in lines
    assert "    changed.py - changed by 1 commit" in lines
    # git quotes this name unless asked for its bytes, and a quoted name matches nothing.
    assert "    é.py - changed by 1 commit" in lines
    assert "    gone.py - gone - a commit since then deleted it" in lines
    assert (
        "    planned.py - not in the tree, and untouched since -"
        " a file the work creates, or one gone before" in lines
    )
    assert any(
        line.startswith("  RE-CONFIRM before starting: filed more than 14 days ago")
        for line in lines
    )


def test_show_asks_for_re_confirmation_only_past_the_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Day 14 is inside the line and day 15 past it, and the setting moves it."""
    store = _store(tmp_path, READY.replace("added: 2026-08-01", "added: 2026-08-10"))

    for today, fires in (("2026-08-24", False), ("2026-08-25", True)):
        assert main(["show", "PL-B1B1", "--items", str(store), "--no-git", "--today", today]) == 0
        assert ("RE-CONFIRM before starting" in capsys.readouterr().out) is fires

    (tmp_path / "docket.toml").write_text("[docket]\nrecheck_after_days = 30\n", encoding="utf-8")
    assert (
        main(["show", "PL-B1B1", "--items", str(store), "--no-git", "--today", "2026-08-25"]) == 0
    )
    assert "RE-CONFIRM" not in capsys.readouterr().out


def test_show_says_the_commits_were_not_read_rather_than_that_nothing_changed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Under `--no-git` the tree still answers whether a path is there; the history answers nothing.

    "Unchanged" there would be a claim about a read that was never made, and
    it is the one reading that tells a session the old brief is still safe.
    """
    store = _store(tmp_path, READY.replace("touches: a.py", "touches: a.py, b.py"))
    (tmp_path / "a.py").write_text("here\n")

    assert _run("show", "PL-B1B1", "--items", str(store)) == 0

    lines = capsys.readouterr().out.splitlines()
    assert (
        "  filed 2026-08-01, 23 days ago - commits since then not read: `--no-git` asks git nothing"
        in lines
    )
    assert "    a.py - in the tree" in lines
    assert "    b.py - not in the tree" in lines
    assert not any("unchanged" in line or "0 commits" in line for line in lines)


def test_show_says_an_undated_item_has_no_known_age_and_a_closed_one_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """No re-confirm line has to mean "young", so an undated item says its age is unknown."""
    store = _store(tmp_path, READY.replace("added: 2026-08-01\n", ""))
    assert _run("show", "PL-B1B1", "--items", str(store)) == 0
    assert "filed: no `added:` date, so its age is not known" in capsys.readouterr().out

    (tmp_path / "closed").mkdir()
    closed = _store(tmp_path / "closed", DONE)
    assert _run("show", "PL-D1D1", "--items", str(closed)) == 0
    assert "filed" not in capsys.readouterr().out


def test_set_writes_a_payoff(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The field is written by command, like every other field triage answers."""
    store = _store(tmp_path, READY)
    line = "a renamed CI job stops blocking merges forever"

    assert _run("set", "PL-B1B1", "--payoff", line, "--items", str(store)) == 0

    assert f"payoff: {line}\n" in _item_text(store)
    assert f"PL-B1B1: payoff: {line}" in capsys.readouterr().out


def test_set_writes_a_deferral_and_refuses_one_with_no_reason(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The one command a gate's disposition error prints (`PL-WD5Z`).

    A value naming no reason is refused at the write, in `docket check`'s own
    words, because that half of the rule needs no roadmap to decide.
    """
    store = _store(tmp_path, READY)

    assert _run("set", "PL-B1B1", "--deferred-from", "v0.6.0", "--items", str(store)) == 1
    assert "gives no reason" in capsys.readouterr().out
    assert _item_text(store) == READY

    value = "v0.6.0 - captured after the freeze"
    assert _run("set", "PL-B1B1", "--deferred-from", value, "--items", str(store)) == 0
    assert f"touches: a.py\ndeferred-from: {value}\nadded:" in _item_text(store)


def test_show_says_nothing_when_no_thread_names_the_item(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Silence is the common case, and a line reporting it would print on nearly
    every `show` while changing no decision."""
    store = _store(tmp_path, NOTES_ITEM)
    (tmp_path / "docket.toml").write_text('[docket]\nnotes_file = "NOTES.md"\n', encoding="utf-8")
    (tmp_path / "NOTES.md").write_text("# Notes\n\n## A thread about nothing\n\nx\n", "utf-8")

    assert _run("show", "PL-B1B1", "--items", str(store)) == 0

    assert "notes:" not in capsys.readouterr().out


def test_show_says_nothing_when_the_project_configures_no_notes_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The setting is empty by default, so most projects must see no change."""
    store = _store(tmp_path, NOTES_ITEM)

    assert _run("show", "PL-B1B1", "--items", str(store)) == 0

    assert "notes:" not in capsys.readouterr().out


def test_show_survives_a_notes_file_the_checkout_does_not_have(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A configured path that is absent must not fail a sound item.

    The file may have been deleted or moved, or the checkout truncated. Failing
    `show` on any of those would break the one command a session runs before
    starting work.
    """
    store = _store(tmp_path, NOTES_ITEM)
    (tmp_path / "docket.toml").write_text('[docket]\nnotes_file = "gone.md"\n', encoding="utf-8")

    assert _run("show", "PL-B1B1", "--items", str(store)) == 0

    out = capsys.readouterr().out
    assert "notes:" not in out
    assert "PL-B1B1 A ready item" in out


def _clustered(identifier: str, title: str, *, names: str = "", **extra: str) -> str:
    """One item of a root-cause cluster, carrying `root-cause-of:` only where asked."""
    fields = {
        "id": identifier,
        "title": title,
        "priority": "P2",
        "effort": "S",
        "status": "ready",
        "classes": "defect",
        "touches": "a.py",
        "added": "2026-08-01",
        **extra,
    }
    if names:
        fields["root-cause-of"] = names
    front = "".join(f"{key}: {value}\n" for key, value in fields.items())
    return f"---\n{front}---\n\n**Problem.** x\n**Why it matters.** y\n**Done when.** z\n"


def _cluster(tmp_path: Path, **head_fields: str) -> Path:
    """A three-item cluster under one head, which is what a sound claim needs."""
    return _store(
        tmp_path,
        _clustered("PL-4040", "The shared refresh nobody owns", **head_fields),
        _clustered("PL-B1B1", "A member of the cluster"),
        _clustered("PL-C2C2", "Another member"),
        _clustered("PL-D3D3", "A third member"),
    )


def test_show_names_the_generator_that_explains_a_member(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The head, its status and the size of its cluster, on the member's own `show`.

    `root-cause-of:` is recorded on the head alone, so a member's file says
    nothing about it and this command printed nothing - while `CLAUDE.md`
    pulls a root cause rather than queueing it, which means the decision above
    can re-scope or drop the item a session is about to start (`PL-C97K`).
    """
    store = _cluster(tmp_path, names="PL-B1B1, PL-C2C2, PL-D3D3", status="needs-decision")

    assert _run("show", "PL-B1B1", "--items", str(store)) == 0

    out = capsys.readouterr().out
    assert "Explained by a generator - a root cause is fixed at its head, not here:" in out
    assert "PL-4040 (needs-decision) root cause of 3 items - The shared refresh nobody owns" in out
    assert "Read it before starting: its decision can re-scope or drop this item." in out


def test_show_says_nothing_about_a_generator_where_no_head_names_the_item(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Almost every item is explained by nothing, and a line that prints on
    almost every `show` while changing no decision is a defect in the line
    rather than thoroughness (`PL-7QKY`)."""
    store = _store(tmp_path, READY)

    assert _run("show", "PL-B1B1", "--items", str(store)) == 0

    assert "Explained by" not in capsys.readouterr().out


def test_show_withholds_a_root_cause_claim_the_checker_refuses(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Two ids are not a generator, and the three readers of the field must agree.

    `plan.recommend` refuses to rank a claim naming fewer than three items and
    `docket check` reports it as an error, so announcing it here would leave
    `show` asserting what the other two refuse to - on the one field whose
    purpose is to lift an item above every band but `P0`.
    """
    store = _cluster(tmp_path, names="PL-B1B1, PL-C2C2")

    assert _run("show", "PL-B1B1", "--items", str(store)) == 0

    out = capsys.readouterr().out
    assert "Explained by" not in out
    assert "PL-4040" not in out


def test_show_counts_a_generators_items_as_the_checker_counts_them(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Distinct ids, because three entries spelling one id name one item.

    `root_cause_faults` counts the claim that way, so a count taken over the
    written entries would print a number the checker holds the same claim to
    disagree with - a wrong answer from the surface a session reads before
    starting work.
    """
    store = _cluster(tmp_path, names="PL-B1B1, PL-B1B1, PL-C2C2, PL-D3D3")

    assert _run("show", "PL-B1B1", "--items", str(store)) == 0

    assert "root cause of 3 items" in capsys.readouterr().out


def test_show_still_names_a_generator_that_has_since_closed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A root cause still explains a member after the head closes.

    `plan.recommend` re-decides soundness against every id including the closed
    ones, so that a claim does not decay as its cluster is worked; the reverse
    edge is read from the same set for the same reason. The printed status is
    what separates the two readings - an open head is a decision pending, a
    closed one asks whether this member still reproduces at all.
    """
    store = _cluster(
        tmp_path, names="PL-B1B1, PL-C2C2, PL-D3D3", status="done", closed="2026-08-20"
    )

    assert _run("show", "PL-B1B1", "--items", str(store)) == 0

    assert "PL-4040 (done) root cause of 3 items" in capsys.readouterr().out


def test_triage_marks_an_item_whose_filing_commit_also_changed_code(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """#635's shape, against a real checkout: the commit files the item and lands the work.

    Against git rather than an injected runner, because `test_vcs.py` asserts
    the filtering and this asserts that the commands are spelled in a way git
    accepts - the split that file's own docstring draws (`PL-SWP3`).
    """
    root = tmp_path / "repo"
    (root / "items").mkdir(parents=True)
    (root / "README.md").write_text("nothing here yet\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        subprocess.run(["git", "config", name, value], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True, capture_output=True)

    items = root / "items"
    (items / "PL-0J9K-batch-the-blob-reads.md").write_text(
        "---\nid: PL-0J9K\ntitle: Batch the blob reads\nstatus: untriaged\nadded: 2026-09-16\n"
        "---\n\n**Problem.** Batch the blob reads\n",
        encoding="utf-8",
    )
    (items / "PL-QQQQ-a-finding-captured-in-passing.md").write_text(
        "---\nid: PL-QQQQ\ntitle: A finding captured in passing\nstatus: untriaged\n"
        "added: 2026-09-16\n---\n\n**Problem.** A finding captured in passing\n",
        encoding="utf-8",
    )
    (root / "vcs.py").write_text("def batch():\n    return 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-qm", "PL-0J9K: batch the blob reads (#635)"],
        cwd=root,
        check=True,
        capture_output=True,
    )

    assert main(["--items", str(items), "triage"]) == 0
    out = capsys.readouterr().out

    assert "Filed by" in out and "(#635)" in out and "vcs.py" in out
    # The commit filed both and named only one. The other is the ordinary
    # capture-in-passing that made the unconditional key match 78% of the store.
    assert out.index("PL-0J9K") < out.index("Filed by") < out.index("PL-QQQQ")
    assert out.count("Filed by") == 1


# --- set: triage's answers, written by the tool rather than typed ---------

SCRAMBLED = """---
id: PL-C3C3
verify: true
title: A hand-written item
status: ready
added: 2026-08-01
classes: infra
touches: a.py
effort: S
priority: P3
---

**Problem.** x
**Why it matters.** y
**Done when.** z
"""

CAPTURED = """---
id: PL-D4D4
title: A captured idea
status: untriaged
added: 2026-08-20
---

**Problem.** A captured idea
**Why it matters.** y
**Done when.** z
"""


def _item_text(store: Path) -> str:
    return (store / "item-0.md").read_text(encoding="utf-8")


def test_set_writes_fields_in_canonical_order(tmp_path: Path) -> None:
    """A hand-typed block comes out in the order every tool-written one has.

    The body is untouched and the file keeps its name: a field write that
    reordered prose or renamed the file would put a change nobody asked for
    into a diff about something else (`PL-LBR6`).
    """
    store = _store(tmp_path, SCRAMBLED)

    assert _run("set", "PL-C3C3", "--feature", "tidy", "--items", str(store)) == 0

    front, body = _item_text(store).split("---\n")[1:]
    assert front == (
        "id: PL-C3C3\ntitle: A hand-written item\npriority: P3\neffort: S\n"
        "status: ready\nclasses: infra\nfeature: tidy\ntouches: a.py\n"
        "added: 2026-08-01\nverify: true\n"
    )
    assert body == "\n**Problem.** x\n**Why it matters.** y\n**Done when.** z\n"
    assert [p.name for p in store.glob("*.md")] == ["item-0.md"]


def test_set_refuses_an_unknown_field(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A misspelled field is silently ignored by every reader, so it is never written.

    `--pr` is refused the same way rather than read as `--priority`: the field
    exists, `docket record` is its writer, and an abbreviation that lands on a
    different field is the silent acceptance this refusal exists to stop.
    """
    store = _store(tmp_path, READY)
    for flag in ("--priorty", "--pr"):
        with pytest.raises(SystemExit) as stop:
            _run("set", "PL-B1B1", flag, "2", "--items", str(store))
        assert stop.value.code == 2
        assert f"unrecognized arguments: {flag}" in capsys.readouterr().err
    assert _item_text(store) == READY


def test_every_set_flag_is_a_field_set_writes() -> None:
    """A flag the parser accepts and the table does not name is written nowhere, silently."""
    args = merge_shared(build_parser().parse_args(["set", "PL-0000"]))

    flags = set(vars(args)) - {
        "command",
        "item",
        "overwrite",
        "func",
        "items",
        "today",
        "now",
        "no_git",
    }
    assert flags == {attribute for _key, attribute in cli.SET_FIELDS}


def test_set_refuses_to_replace_a_recorded_value_unless_told_to(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Replacing a value nobody looked at is the duplicate-key hazard through the front door."""
    store = _store(tmp_path, READY)

    assert _run("set", "PL-B1B1", "--priority", "P2", "--items", str(store)) == 1

    out = capsys.readouterr().out
    assert "`priority` already records `P1`" in out
    assert "--overwrite" in out
    assert _item_text(store) == READY

    assert _run("set", "PL-B1B1", "--priority", "P2", "--overwrite", "--items", str(store)) == 0
    assert "priority: P2\n" in _item_text(store)


def test_set_moves_a_status_without_being_told_to_overwrite(tmp_path: Path) -> None:
    """A status is a position in a lifecycle, and moving it is what triage does."""
    store = _store(tmp_path, CAPTURED)

    assert (
        _run(
            "set",
            "PL-D4D4",
            "--status",
            "ready",
            "--priority",
            "P2",
            "--effort",
            "S",
            "--classes",
            "infra",
            "--items",
            str(store),
        )
        == 0
    )

    assert "status: ready\n" in _item_text(store)
    assert "untriaged" not in _item_text(store)


def test_set_refuses_a_write_the_checker_would_fail_and_says_why(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The rules arrive from `checks.py` in its own words, at the moment of writing.

    `ready` owes a priority and an effort; a safety class owes the top band.
    Neither rule is restated by `set`, and either refuses the write whole.
    """
    store = _store(tmp_path, CAPTURED)

    assert _run("set", "PL-D4D4", "--status", "ready", "--items", str(store)) == 1
    out = capsys.readouterr().out
    assert "nothing was written" in out
    assert "no priority" in out
    assert "no effort" in out
    assert _item_text(store) == CAPTURED

    fields = ("--status", "ready", "--priority", "P3", "--effort", "S", "--classes", "safety")
    assert _run("set", "PL-D4D4", *fields, "--items", str(store)) == 1
    assert "safety-critical work starts at P0 or P1" in capsys.readouterr().out
    assert _item_text(store) == CAPTURED


def test_set_holds_a_command_it_writes_to_the_admitted_shapes_whatever_the_item_s_age(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`check` dates a command by its item's capture; `set` is the moment it is written.

    The item predates `verify_allowlist_from`, so its legacy command stands and
    another field can be written beside it. A command `set` writes onto it is
    held to the list all the same - the triage of old items and the repair of
    legacy commands, which a rule dated by capture alone never reaches
    (`PL-1P5V`).
    """
    old = OPEN_ITEM.replace("id: PL-K7QX", "id: PL-F6F6")
    store = _store(tmp_path, old)
    (tmp_path / "docket.toml").write_text(
        '[docket]\nverify_allowlist_from = "2026-09-24"\n', encoding="utf-8"
    )

    def write(*fields: str) -> int:
        return main(
            ["set", "PL-F6F6", *fields, "--overwrite", "--items", str(store)]
            + ["--no-git", "--today", "2026-09-24"]
        )

    assert write("--effort", "M") == 0
    assert f"verify: {LEGACY_COMMAND}\n" in _item_text(store)
    capsys.readouterr()

    assert write("--verify", "bin/docket check") == 1
    out = capsys.readouterr().out
    assert "nothing was written" in out
    assert "runs `bin/docket check`, which is neither a `grep` clause" in out
    assert f"verify: {LEGACY_COMMAND}\n" in _item_text(store)

    assert write("--verify", "grep -q 'def test_a' tests/unit/test_a.py") == 0
    assert "verify: grep -q 'def test_a' tests/unit/test_a.py\n" in _item_text(store)


def test_set_refuses_a_file_it_could_not_rewrite_faithfully(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A doubled key would be collapsed to the parser's pick; an unknown one would be dropped.

    So would a line no field reads, and with it the tail of the value it
    wraps (`PL-JD4L`). All are what `check` reports, and a writer repairing
    one on its way past would be choosing a value on nobody's behalf
    (`PL-BR4G`).
    """
    doubled = READY.replace("effort: S\n", "effort: S\neffort: M\n")
    unknown = READY.replace("touches: a.py\n", "touches: a.py\ncolour: red\n")
    unread = READY.replace("touches: a.py\n", "touches: a.py\nb.py\n")
    for name, document in (("a", doubled), ("b", unknown), ("c", unread)):
        (tmp_path / name).mkdir()
        store = _store(tmp_path / name, document)

        assert _run("set", "PL-B1B1", "--feature", "x", "--items", str(store)) == 1

        assert "nothing was written" in capsys.readouterr().out
        assert _item_text(store) == document


def test_set_removes_a_field_given_an_empty_value(tmp_path: Path) -> None:
    """The renderer omits what is empty, so an empty value is how a field is unset."""
    withheld = READY.replace("added:", "not-delegable: wants the strongest model\nadded:")
    store = _store(tmp_path, withheld)

    assert _run("set", "PL-B1B1", "--not-delegable", "", "--overwrite", "--items", str(store)) == 0

    assert "not-delegable" not in _item_text(store)


BLOCKER = """---
id: PL-C1C1
title: The blocker
priority: P2
effort: S
status: ready
classes: perf
touches: a.py
added: 2026-08-01
payoff: unblocks the two items waiting on it
verify: grep -q x a.py
---

**Problem.** x
**Why it matters.** y
**Done when.** z
"""

HELD = """---
id: PL-D2D2
title: Held by the blocker alone
priority: P2
effort: S
status: blocked
classes: perf
touches: b.py
blocked-by: PL-C1C1
added: 2026-08-01
---

**Problem.** x
**Why it matters.** y
**Done when.** z
"""

HELD_TWICE = """---
id: PL-G3G3
title: Held by the blocker and by something still open
priority: P2
effort: S
status: blocked
classes: perf
touches: c.py
blocked-by: PL-C1C1, PL-B1B1
added: 2026-08-01
---

**Problem.** x
**Why it matters.** y
**Done when.** z
"""


def test_closing_an_item_names_what_it_just_unblocked(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The reverse of `blocked-by` is derived and printed where the blocker closes.

    `PL-PQC7`. `docket check` has reported the same set all along and
    `cli._say_promotable` names it to a session choosing work, but neither
    fires at the moment a blocker closes - so the reading reached only a
    session running a deliberate grooming pass, and two of those ran over the
    same four items on one day.
    """
    store = _store(tmp_path, READY, BLOCKER, HELD, HELD_TWICE)

    assert (
        _run("set", "PL-C1C1", "--status", "done", "--closed", "2026-08-24", "--items", str(store))
        == 0
    )

    out = capsys.readouterr().out
    assert "Closing PL-C1C1 clears the last recorded blocker on 1 item(s):" in out
    assert "PL-D2D2" in out
    # Still held by PL-B1B1, which is open, so closing this one released nothing.
    assert "PL-G3G3" not in out
    assert "Not promoted for you" in out


def test_closing_an_item_that_unblocks_nothing_says_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An advisory that fires on every close would be read on none of them."""
    store = _store(tmp_path, READY, BLOCKER, HELD_TWICE)

    assert (
        _run("set", "PL-C1C1", "--status", "done", "--closed", "2026-08-24", "--items", str(store))
        == 0
    )

    assert "clears the last recorded blocker" not in capsys.readouterr().out


def test_a_write_that_is_not_a_closure_names_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The trigger is a status reaching `CLOSED_STATUSES`, not any write.

    A `blocked-by` edit can make an item promotable the instant it lands. That
    is a different event with a different reader, and reporting it here would
    put the standing backlog in front of somebody who did not cause it.
    """
    store = _store(tmp_path, READY, BLOCKER, HELD)

    assert _run("set", "PL-C1C1", "--payoff", "y", "--overwrite", "--items", str(store)) == 0

    assert "clears the last recorded blocker" not in capsys.readouterr().out


def test_dropping_a_blocker_releases_what_it_held(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`dropped` closes an item as `done` does, and `promotable` resolves both."""
    store = _store(tmp_path, READY, BLOCKER, HELD)

    assert (
        _run(
            "set",
            "PL-C1C1",
            "--status",
            "dropped",
            "--reason",
            "overtaken by the tree",
            "--closed",
            "2026-08-24",
            "--items",
            str(store),
        )
        == 0
    )

    assert (
        "Closing PL-C1C1 clears the last recorded blocker on 1 item(s):" in capsys.readouterr().out
    )


WAITING_IN_PROSE = """---
id: PL-H4H4
title: Waits on the blocker, and says so
priority: P2
effort: S
status: blocked
classes: perf
touches: d.py
blocked-by: PL-C1C1
added: 2026-08-01
---

**Problem.** x

**Blocked on `PL-C1C1`** for the unit.

**Why it matters.** y
**Done when.** z
"""

DECIDING = """---
id: PL-F5F5
title: Waits on a question, and says so
priority: P2
effort: S
status: needs-decision
classes: perf
touches: e.py
added: 2026-08-01
payoff: settles the question
verify: grep -q x e.py
---

**Problem.** x
**Why it matters.** y
**Done when.** z

Left at `needs-decision` until the owner answers.

**Decision needed.** Which? **Recommendation:** the first.
"""


def test_closing_an_item_names_the_briefs_still_waiting_on_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-8YXJ`: closing a blocker never showed the brief saying it still waits.

    The session closing it is the one that knows it closed, so the passage is
    named to it, with the marker dated for the closure, rather than left for
    whoever runs `check` next.
    """
    store = _store(tmp_path, READY, BLOCKER, WAITING_IN_PROSE)

    assert (
        _run("set", "PL-C1C1", "--status", "done", "--closed", "2026-08-24", "--items", str(store))
        == 0
    )

    out = capsys.readouterr().out
    assert "1 passage(s) now say what this write changed" in out
    assert "names PL-C1C1 as work it waits on or lands with" in out
    assert "[superseded 2026-08-24]" in out


def test_moving_a_status_names_the_passage_narrating_the_old_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`docket set --status ready` is a one-line diff that never shows the
    paragraph saying "Left at `needs-decision`" - `PL-SYG4`'s, which stood
    unreported until `PL-X4RX` found it by reading."""
    store = _store(tmp_path, DECIDING)

    assert _run("set", "PL-F5F5", "--status", "ready", "--items", str(store)) == 0

    out = capsys.readouterr().out
    assert "its brief says it is at `needs-decision` and its front matter says `ready`" in out


def test_a_write_that_moves_no_state_names_no_passage(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The trigger is a `status` or `blocked-by` write. The passage above
    already contradicts nothing, and a payoff edit could not make it."""
    store = _store(tmp_path, DECIDING)

    assert _run("set", "PL-F5F5", "--payoff", "y", "--overwrite", "--items", str(store)) == 0

    assert "passage(s) now say" not in capsys.readouterr().out


def _drained_cluster(tmp_path: Path, *members: str, **head_fields: str) -> Path:
    """A cluster whose head is closed over members at the statuses given.

    `_cluster` above builds the shape a *claim* needs - three open members
    under one head. This builds the shape a *drain* report needs, which is the
    one every generator this project has recorded actually has: the head
    closed, and most of what it named still open.
    """
    fields = {"status": "done", "closed": "2026-08-20", "names": "PL-B1B1, PL-C2C2, PL-D3D3"}
    return _store(
        tmp_path,
        _clustered("PL-4040", "The shared refresh nobody owns", **{**fields, **head_fields}),
        *members,
    )


def test_a_generator_head_reports_how_much_of_its_cluster_is_open(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A head at `done` must not read as a cluster that is finished.

    Every `root-cause-of:` head this project carries is closed and most of what
    each one names is not, so a reader taking the head's own status for the
    cluster's state sees the generator work as finished while 58 of 99 members
    are open. Nothing counted them, and the question was answered twice in two
    days by a throwaway script over the whole store instead (`PL-XF5V`).
    """
    store = _drained_cluster(
        tmp_path,
        _clustered("PL-B1B1", "A member that closed", status="done", closed="2026-08-22"),
        _clustered("PL-C2C2", "A member still open"),
        _clustered("PL-D3D3", "A third member, open"),
    )

    assert _run("generators", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert "1 generator, 0 drained - 3 distinct members, 2 still open" in output
    assert "PL-4040 3 members, 2 open - 1 closed since the head closed 2026-08-20" in output


def test_generators_does_not_count_a_same_date_closure_as_drain(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`closed:` is a date, so a member closed on the head's date did not drain after it.

    The trend is measured against the head's own close date, and 32 of this
    store's 99 member closures share it. Counting those as drain would report
    movement the dates cannot support, in the one place the answer exists to be
    trusted - which is what `.claude/rules/apparatus-standard.md`'s floor
    refuses. Naming the bucket beside the drain is what the dates do support.
    """
    store = _drained_cluster(
        tmp_path,
        _clustered("PL-B1B1", "Closed with the head", status="done", closed="2026-08-20"),
        _clustered("PL-C2C2", "A member still open"),
        _clustered("PL-D3D3", "A third member, open"),
    )

    assert _run("generators", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert "2 open - none closed since the head closed 2026-08-20 (1 closed on that date)" in output


def test_generators_reports_a_drained_cluster_as_finished(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Half of "are the generators dealt with" is the ones that are.

    Four of this project's eleven clusters are drained and no surface said so,
    which is the same missing count wearing its other face. The date is the
    last member's rather than the head's: the head closing is the cause being
    fixed, and the cluster drains after it.
    """
    store = _drained_cluster(
        tmp_path,
        _clustered("PL-B1B1", "Closed after the head", status="done", closed="2026-08-21"),
        _clustered("PL-C2C2", "Closed later still", status="done", closed="2026-08-23"),
        _clustered(
            "PL-D3D3", "Dropped", status="dropped", closed="2026-08-22", reason="not reproducible"
        ),
    )

    assert _run("generators", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert "1 generator, 1 drained - 3 distinct members, 0 still open" in output
    assert "PL-4040 3 members, drained 2026-08-23" in output


def test_generators_names_an_unsound_claim_it_could_not_count(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A claim `is_generator` refuses is reported as uncounted, never dropped in silence.

    `docket check` is a separate command, so a store is routinely read before
    it is validated. An unsound `root-cause-of:` is ranked by nothing and
    counted by nothing, so omitting it without a word would hand a reader a
    partial reading as a complete one - the one property
    `.claude/rules/apparatus-standard.md` makes this package refuse.
    """
    store = _drained_cluster(
        tmp_path,
        _clustered("PL-B1B1", "A member still open"),
        _clustered("PL-C2C2", "Another member"),
        _clustered("PL-D3D3", "A third member"),
        _clustered("PL-G4G4", "A head naming an id nothing carries", names="PL-B1B1, PL-N0P3"),
    )

    assert _run("generators", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert "1 generator, 0 drained" in output
    assert "1 item carries a `root-cause-of:` that is not a sound claim" in output
    assert "PL-G4G4" in output


def test_generators_resolves_a_member_id_to_the_cluster_above_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A session holds a member's id, because that is what `next` hands it.

    Requiring the head's id would leave the command answerable only by a
    session that had already found the thing it exists to find.
    """
    store = _drained_cluster(
        tmp_path,
        _clustered("PL-B1B1", "A member that closed", status="done", closed="2026-08-22"),
        _clustered("PL-C2C2", "A member still open"),
        _clustered("PL-D3D3", "A third member, open"),
    )

    assert _run("generators", "PL-C2C2", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert "PL-4040 (done) root cause of 3 items: 1/3 done (2 left)" in output
    # Every member is a line, so counting the marks reproduces both figures
    # above them - `progress_mark`'s reconciliation, kept here too (`PL-VFVW`).
    assert "[x] PL-B1B1" in output
    assert "[ ] PL-C2C2" in output
    assert "[ ] PL-D3D3" in output


_MEMBERS = "PL-B1B1, PL-C2C2, PL-D3D3"
_LIVE = "live - two more captures matched onto this path after the cluster was recorded"
_SPENT = "spent - the parse every member stood on was deleted, so no new one can arrive"


def test_show_on_a_live_head_says_it_is_on_the_tier(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The promotion is invisible from the item file alone.

    A `P2` that outranks every `P1` in the queue has nothing on its own face
    saying so, and `show` is the path a named item arrives on - the one `next`
    never sees, and the one the project owner starts work from.
    """
    store = _cluster(tmp_path, names=_MEMBERS, generator=_LIVE)

    assert _run("show", "PL-4040", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert f"generator: {_LIVE}" in output
    assert "ranked on the generator tier - above every band but P0" in output


def test_show_on_a_spent_head_says_it_ranks_on_its_own_band(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The distinction the drain line above it cannot carry.

    Drain is how much of the damage is repaired; the verdict is whether more
    is still arriving, and a cluster can be fully drained with its mechanism
    running or wholly open with it spent. Only the second decides the rank, so
    a reader shown the first alone would take a recorded generator for a
    ranked one.
    """
    store = _cluster(tmp_path, names=_MEMBERS, generator=_SPENT)

    assert _run("show", "PL-4040", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert f"generator: {_SPENT}" in output
    assert "spent: recorded for the audit, ranked on its own band" in output
    assert "above every band" not in output


def test_show_on_a_head_with_no_verdict_says_the_field_is_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Recorded and unranked, which is the state a session cannot otherwise see.

    Nothing is mis-ranked - the ranking refuses what does not claim `live` -
    so what this catches is the session that recorded a live generator and
    believes the mechanism is now above every safety item in the queue.
    """
    store = _cluster(tmp_path, names=_MEMBERS)

    assert _run("show", "PL-4040", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert "generator: is absent" in output
    assert "ranked on the generator tier" not in output


def test_show_on_a_closed_head_says_it_ranks_on_no_tier(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A dropped head whose own verdict says `live` is ranked by nothing.

    `show` asked the rank predicates, which tested no status, and told the
    reader five closed heads were on the tier - so a mechanism its own verdict
    calls live read as handled, when only an open item's claim can rank it
    (`PL-BBT8`). The plan line made the same claim from the same answer.
    """
    store = _cluster(
        tmp_path, names=_MEMBERS, generator=_LIVE, status="dropped", closed="2026-08-20"
    )
    (tmp_path / "pyproject.toml").write_text('version = "0.2.5"\n', encoding="utf-8")
    (tmp_path / "ROADMAP.md").write_text(WAVE_ROADMAP, encoding="utf-8")

    assert _run("show", "PL-4040", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert f"generator: {_LIVE}" in output
    assert "closed, so on no tier whatever the verdict says" in output
    assert "it is closed, so it ranks nowhere" in output
    assert "ranked on the generator tier" not in output
    assert "above every band" not in output


def _machinery_defect(tmp_path: Path, status: str) -> Path:
    """One `impairs-generators:` item whose claim is sound, at the status given."""
    (tmp_path / "docket.toml").write_text(
        '[docket]\ngenerator_paths = ["a.py"]\n', encoding="utf-8"
    )
    extra = {"closed": "2026-08-20"} if status in ("done", "dropped") else {}
    return _store(
        tmp_path,
        _clustered(
            "PL-5050",
            "The ranking never reads the claim",
            status=status,
            **{"impairs-generators": "recommend never calls the soundness test"},
            **extra,
        ),
    )


@pytest.mark.parametrize(
    ("status", "said"),
    [
        ("ready", "ranked on the generator tier - above every band but P0"),
        ("done", "closed, so on no tier - only an open item's claim ranks there"),
        ("blocked", "blocked, and ranked by nothing: it names no blocker"),
        ("untriaged", "untriaged, so ranked nowhere until triage seats it"),
    ],
)
def test_show_says_a_machinery_defect_ranks_only_while_open(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], status: str, said: str
) -> None:
    """The tier's other entrance, which `show` answered from the claim alone (`PL-BBT8`)."""
    store = _machinery_defect(tmp_path, status)

    assert _run("show", "PL-5050", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert said in output
    assert "UNSOUND" not in output


def _blocked_live_head(tmp_path: Path) -> Path:
    """A live head blocked on one build item, the shape `PL-QFWF` was filed on."""
    return _store(
        tmp_path,
        _clustered(
            "PL-4040",
            "The shared refresh nobody owns",
            names=_MEMBERS,
            generator=_LIVE,
            status="blocked",
            **{"blocked-by": "PL-F5F5"},
        ),
        _clustered("PL-B1B1", "A member of the cluster"),
        _clustered("PL-C2C2", "Another member"),
        _clustered("PL-D3D3", "A third member"),
        _clustered("PL-F5F5", "The build item the head waits on"),
    )


def test_show_on_a_blocker_of_a_blocked_live_head_names_the_head(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The rank is the head's and `blocked-by` is on the head alone, so this is the carrier.

    Without it the plan line told the build item it ranks on its band alone
    while `next` ranked it above every band (`PL-QFWF`).
    """
    store = _blocked_live_head(tmp_path)
    (tmp_path / "pyproject.toml").write_text('version = "0.2.5"\n', encoding="utf-8")
    (tmp_path / "ROADMAP.md").write_text(WAVE_ROADMAP, encoding="utf-8")

    assert _run("show", "PL-F5F5", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert "unblocks PL-4040 on the generator tier: blocked on this item" in output
    assert "it ranks above every band but P0" in output
    assert "ranks on its band alone" not in output


def test_the_digest_says_why_a_blocker_of_a_blocked_head_leads_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A bare `P2` leading the digest reads as a bug in the ranking."""
    assert _run("digest", "--items", str(_blocked_live_head(tmp_path))) == 0

    out = capsys.readouterr().out
    assert "Top: PL-F5F5" in out
    assert "unblocks PL-4040 on the generator tier - ranked above every band but P0" in out


def test_show_on_a_blocked_live_head_says_it_is_blocked_and_names_its_blockers(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The head is startable by nothing, so the rank is its blockers' (`PL-4RK2`).

    `show` said "ranked on the generator tier" of the head itself, and its
    plan line that it ranks above every band, while `next` ranked the build
    item and not the head.
    """
    store = _blocked_live_head(tmp_path)
    (tmp_path / "pyproject.toml").write_text('version = "0.2.5"\n', encoding="utf-8")
    (tmp_path / "ROADMAP.md").write_text(WAVE_ROADMAP, encoding="utf-8")

    assert _run("show", "PL-4040", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert (
        "blocked, so not ranked itself - its rank, above every band but P0, passes to"
        " the open items it waits on: PL-F5F5"
    ) in output
    assert "it is blocked, so it ranks nowhere until it can start" in output
    assert "ranked on the generator tier" not in output
    assert "- it ranks above every band but P0" not in output


def _unranked_live_head(tmp_path: Path) -> Path:
    """A live head behind a chain: its one blocker waits on startable work."""
    return _store(
        tmp_path,
        _clustered(
            "PL-4040",
            "The shared refresh nobody owns",
            names=_MEMBERS,
            generator=_LIVE,
            status="blocked",
            **{"blocked-by": "PL-F5F5, v0.7.0"},
        ),
        _clustered("PL-B1B1", "A member of the cluster"),
        _clustered("PL-C2C2", "Another member"),
        _clustered("PL-D3D3", "A third member"),
        _clustered("PL-F5F5", "The design round", status="blocked", **{"blocked-by": "PL-H1H1"}),
        _clustered("PL-H1H1", "The startable work behind it"),
    )


def test_show_on_a_blocked_live_head_nothing_carries_says_it_is_ranked_by_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Naming the blockers is not enough where none of them can start."""
    assert _run("show", "PL-4040", "--items", str(_unranked_live_head(tmp_path))) == 0

    output = capsys.readouterr().out
    assert (
        "blocked, and ranked by nothing: it waits on PL-F5F5 (blocked), v0.7.0 (a milestone;"
        " the roadmap was not read to say if scoped); startable or in flight behind them:"
        " PL-H1H1."
    ) in output
    assert "write that work into the head's `blocked-by`" in output


def test_next_names_a_live_generator_that_nothing_ranks(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The tier's silent failure, said where a session choosing work looks (`PL-4RK2`)."""
    assert _run("next", "--items", str(_unranked_live_head(tmp_path))) == 0

    out = capsys.readouterr().out
    assert (
        "A live generator that nothing ranks - blocked, and no item it waits on can start:" in out
    )
    assert "  PL-4040 (root cause of 3 items) waits on PL-F5F5 (blocked)" in out
    assert "startable or in flight behind them: PL-H1H1" in out
    assert "Not ranked above - a blocked head's rank passes one edge down" in out


def test_next_is_silent_about_a_blocked_live_head_its_blockers_carry(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The recorded shape `PL-QFWF` fixed: the build item ranks, so nothing is lost."""
    assert _run("next", "--items", str(_blocked_live_head(tmp_path))) == 0

    assert "that nothing ranks" not in capsys.readouterr().out


def _head_blocked_on(tmp_path: Path, blocked_by: str) -> Path:
    """A live head whose `blocked-by` is exactly what is given, and its three members."""
    return _store(
        tmp_path,
        _clustered(
            "PL-4040",
            "The shared refresh nobody owns",
            names=_MEMBERS,
            generator=_LIVE,
            status="blocked",
            **{"blocked-by": blocked_by},
        ),
        _clustered("PL-B1B1", "A member of the cluster"),
        _clustered("PL-C2C2", "Another member"),
        _clustered("PL-D3D3", "A third member"),
    )


def test_next_says_a_scoped_milestone_no_longer_holds_an_unranked_head(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Read from the roadmap, as `docket check` reads it, not assumed unscoped."""
    store = _head_blocked_on(tmp_path, "v0.4.0")
    (tmp_path / "pyproject.toml").write_text('version = "0.2.5"\n', encoding="utf-8")
    (tmp_path / "ROADMAP.md").write_text(WAVE_ROADMAP, encoding="utf-8")

    assert _run("next", "--items", str(store)) == 0

    out = capsys.readouterr().out
    assert (
        "PL-4040 (root cause of 3 items) waits on nothing still open: every blocker its"
        " `blocked-by` names has closed or been scoped"
    ) in out
    assert "not yet scoped" not in out


def test_next_does_not_say_the_blockers_closed_of_a_head_naming_only_itself(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`docket check` refuses the shape; until it is repaired, `next` must not misdescribe it."""
    assert _run("next", "--items", str(_head_blocked_on(tmp_path, "PL-4040"))) == 0

    out = capsys.readouterr().out
    assert "names no blocker in its `blocked-by` but itself" in out
    assert "has closed" not in out


def test_generators_says_a_blocked_live_head_is_not_on_the_tier_itself(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The same claim `show` stopped making, on the cluster summary (`PL-4RK2`)."""
    assert _run("generators", "--items", str(_blocked_live_head(tmp_path))) == 0

    out = capsys.readouterr().out
    assert "still generating, but blocked, so not on the tier itself" in out
    assert "still generating, so on the tier" not in out


def test_generators_does_not_say_a_closed_machinery_defect_ranks(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Still named, as a drained cluster is, and no longer called ranked.

    The line said every sound claim "ranks on the generator tier" and printed
    `(done)` beside one of them (`PL-BBT8`).
    """
    store = _machinery_defect(tmp_path, "done")

    assert _run("generators", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert "1 closed item carries a sound `impairs-generators:` and ranks on no tier" in output
    assert "PL-5050 (done)" in output
    assert "rank on the generator tier" not in output
    assert "ranks on the generator tier" not in output


def _blocked_machinery_defect(tmp_path: Path) -> Path:
    """A machinery defect blocked on one startable item, the shape `PL-Q4DF` was filed on."""
    (tmp_path / "docket.toml").write_text(
        '[docket]\ngenerator_paths = ["a.py"]\n', encoding="utf-8"
    )
    return _store(
        tmp_path,
        _clustered(
            "PL-5050",
            "The ranking never reads the claim",
            status="blocked",
            **{"impairs-generators": "recommend never calls the soundness test"},
            **{"blocked-by": "PL-F5F5"},
        ),
        _clustered("PL-F5F5", "The build item the defect waits on", priority="P3"),
    )


def test_a_blocked_machinery_defect_hands_its_rank_to_what_it_waits_on(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`next` ranks the blocker on the tier, and `show` and `generators` say where it went.

    Before `PL-Q4DF` the rank reached nothing, `show` said "ranked nowhere" and
    `generators` said the blocked defect ranked on the generator tier.
    """
    store = str(_blocked_machinery_defect(tmp_path))

    assert _run("next", "--items", store) == 0
    out = capsys.readouterr().out
    assert "PL-5050, a defect in the generator machinery that is blocked on it" in out

    assert _run("show", "PL-5050", "--items", store) == 0
    out = capsys.readouterr().out
    assert "passes to the open items it waits on: PL-F5F5" in out

    assert _run("generators", "--items", store) == 0
    out = capsys.readouterr().out
    assert "ranks nowhere itself, being blocked or untriaged" in out
    assert "PL-5050 (blocked)" in out
    assert "on the generator tier by `impairs-generators:`" not in out


def test_generators_does_not_list_a_head_as_naming_no_members(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An `impairs-generators:` item that is also a head is a cluster above (`PL-Q4DF`)."""
    (tmp_path / "docket.toml").write_text(
        '[docket]\ngenerator_paths = ["a.py"]\n', encoding="utf-8"
    )
    store = _store(
        tmp_path,
        _clustered(
            "PL-4040",
            "The shared refresh nobody owns",
            names=_MEMBERS,
            generator=_LIVE,
            **{"impairs-generators": "recommend never calls the soundness test"},
        ),
        _clustered("PL-B1B1", "A member of the cluster"),
        _clustered("PL-C2C2", "Another member"),
        _clustered("PL-D3D3", "A third member"),
    )

    assert _run("generators", "--items", str(store)) == 0

    out = capsys.readouterr().out
    assert "PL-4040 3 members" in out
    assert "name no members" not in out and "names no members" not in out


def test_an_untriaged_generator_tier_item_is_not_called_ranked(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`next` offers an untriaged head nowhere, so the table must not call it on the tier."""
    store = _store(
        tmp_path,
        _clustered(
            "PL-4040",
            "The shared refresh nobody owns",
            names=_MEMBERS,
            generator=_LIVE,
            status="untriaged",
        ),
        _clustered("PL-B1B1", "A member of the cluster"),
        _clustered("PL-C2C2", "Another member"),
        _clustered("PL-D3D3", "A third member"),
    )

    assert _run("generators", "--items", str(store)) == 0
    out = capsys.readouterr().out
    assert "still generating, but untriaged, so ranked nowhere until triage seats it" in out
    assert "still generating, so on the tier" not in out

    assert _run("show", "PL-4040", "--items", str(store)) == 0
    out = capsys.readouterr().out
    assert "untriaged, so ranked nowhere until triage seats it" in out
    assert "ranked on the generator tier - above every band but P0" not in out


def test_generators_marks_an_open_head_that_no_longer_ranks(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The audit table is where a recorded generator is counted, so it says which.

    `format_clusters` already names the two sets its count does not reach, so
    the total is honest; from `PL-T7QR` being recorded and ranking are two
    different facts and this is the table where the first is read.
    """
    store = _cluster(tmp_path, names=_MEMBERS, generator=_SPENT)

    assert _run("generators", "--items", str(store)) == 0

    assert "spent, so it ranks on its band" in capsys.readouterr().out


def test_generators_says_nothing_about_a_closed_heads_verdict(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A closed head is startable by nothing, so the clause would decide nothing.

    `CLAUDE.md` retires a check that fires every run without changing a
    decision, and a distinction printed beside every head in a table where all
    eleven are closed is that defect in a report line.
    """
    store = _cluster(tmp_path, names=_MEMBERS, generator=_SPENT, status="done", closed="2026-08-20")

    assert _run("generators", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert "PL-4040" in output
    assert "spent" not in output


def test_show_on_a_head_says_how_much_of_its_cluster_is_open(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`show` has named a member's head since `PL-C97K` and said nothing on the head.

    So the surface a session reaches by naming a generator - the way the
    project owner starts one - was the surface that could not say whether the
    repairs underneath it were still owed.
    """
    store = _drained_cluster(
        tmp_path,
        _clustered("PL-B1B1", "A member that closed", status="done", closed="2026-08-22"),
        _clustered("PL-C2C2", "A member still open"),
        _clustered("PL-D3D3", "A third member, open"),
    )

    assert _run("show", "PL-4040", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert "root cause of 3 items, 2 open - 1 closed since the head closed 2026-08-20" in output
    assert "`docket generators PL-4040` lists them" in output


# --- misread: the fact a head's members misread (`PL-5MYR`) -----------------
#
# Heads were compared with nothing, so one record read by several readers got a
# head per reader. These pin the surfaces that make the comparison one screen:
# the line under each head, the pairs whose clusters overlap, the sorted list,
# and the two `show` paths and the `set` write.

_MISREAD = "Who holds an item now, and whether that holder is still live"


def _overlapping_heads(tmp_path: Path, **third: str) -> Path:
    """Two heads sharing `PL-D3D3` - one stating its misread, one not - and a third apart."""
    return _store(
        tmp_path,
        _clustered(
            "PL-4040",
            "The shared refresh nobody owns",
            names=_MEMBERS,
            generator=_LIVE,
            misread=_MISREAD,
        ),
        _clustered(
            "PL-5050",
            "Another reader of one record",
            names="PL-D3D3, PL-F5F5, PL-G6G6",
            generator=_LIVE,
        ),
        _clustered(
            "PL-6060",
            "A head apart from both",
            names="PL-H7H7, PL-J8J8, PL-K9K9",
            status="done",
            closed="2026-08-20",
            **third,
        ),
        *(
            _clustered(member, f"Member {member}")
            for member in (
                "PL-B1B1",
                "PL-C2C2",
                "PL-D3D3",
                "PL-F5F5",
                "PL-G6G6",
                "PL-H7H7",
                "PL-J8J8",
                "PL-K9K9",
            )
        ),
    )


def test_generators_prints_each_heads_misread_and_the_heads_that_overlap(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The line names the record, the title the reader; the overlap is a hint, not a verdict."""
    store = _overlapping_heads(tmp_path)

    assert _run("generators", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert f"\n      {_MISREAD}\n" in output
    assert "\n      [no misread:] Another reader of one record\n" in output
    assert "The shared refresh nobody owns" not in output
    assert (
        "\n\n  1 pair of heads overlaps - a fact about the two lists, not a verdict that they "
        "share a record; read both `misread:` lines:\n"
        "    PL-4040 and PL-5050 share PL-D3D3\n"
    ) in output
    assert "PL-6060 and" not in output and "and PL-6060" not in output


def test_generators_prints_no_overlap_block_where_no_heads_overlap(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = _cluster(tmp_path, names=_MEMBERS, generator=_LIVE, misread=_MISREAD)

    assert _run("generators", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert _MISREAD in output
    assert "overlap" not in output


def test_generators_misread_sorts_by_the_fact_and_puts_missing_lines_last(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Case-insensitively, so a lower-case fact is not sorted after every capital.

    A plain sort would put `Who ...` ahead of `the ...`; the order is for a
    reader's eye, so two heads naming one record sit together whatever case
    each was typed in. A head stating none is listed last, never left out.
    """
    store = _overlapping_heads(tmp_path)
    (store / "item-1.md").write_text(
        _clustered(
            "PL-5050",
            "Another reader of one record",
            names="PL-D3D3, PL-F5F5, PL-G6G6",
            generator=_LIVE,
            misread="the tree fact a document sentence restates",
        ),
        encoding="utf-8",
    )

    assert _run("generators", "--misread", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert output.startswith(
        "What the members of each of 3 heads misread, sorted by the fact so heads stating "
        "one fact sit together:\n\n"
        "  PL-5050 (ready)  the tree fact a document sentence restates\n"
        f"  PL-4040 (ready)  {_MISREAD}\n"
        "  PL-6060 (done)   [no misread:] - docket check names it\n"
    )
    assert "    PL-4040 and PL-5050 share PL-D3D3" in output


def test_generators_on_a_head_prints_its_misread(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = _overlapping_heads(tmp_path)

    assert _run("generators", "PL-4040", "--items", str(store)) == 0

    assert f"\n  misread: {_MISREAD}\n" in capsys.readouterr().out


def test_show_on_a_head_prints_its_misread_beside_the_verdict(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = _cluster(tmp_path, names=_MEMBERS, generator=_LIVE, misread=_MISREAD)

    assert _run("show", "PL-4040", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert f"  generator: {_LIVE}\n" in output
    assert f"  misread: {_MISREAD}\n" in output
    assert "UNSOUND" not in output


def test_show_on_a_closed_head_with_no_misread_says_the_field_is_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Closed heads owe it too: a closed head's fact is what a capture is compared against."""
    store = _cluster(tmp_path, names=_MEMBERS, status="done", closed="2026-08-20")

    assert _run("show", "PL-4040", "--items", str(store)) == 0

    assert "  misread: is absent, so this head cannot be compared" in capsys.readouterr().out


def test_show_on_a_member_prints_the_misread_of_the_head_explaining_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = _cluster(tmp_path, names=_MEMBERS, generator=_LIVE, misread=_MISREAD)

    assert _run("show", "PL-B1B1", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert (
        "    PL-4040 (ready) root cause of 3 items - The shared refresh nobody owns\n"
        f"      misread: {_MISREAD}\n"
    ) in output


def test_set_writes_a_misread_directly_after_the_verdict(tmp_path: Path) -> None:
    store = _cluster(tmp_path, names=_MEMBERS, generator=_LIVE)

    assert _run("set", "PL-4040", "--misread", _MISREAD, "--items", str(store)) == 0

    assert (
        f"root-cause-of: {_MEMBERS}\ngenerator: {_LIVE}\nmisread: {_MISREAD}\n---\n"
        in _item_text(store)
    )


def test_set_refuses_a_misread_over_the_limit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Validated at write time the way `generator:` is: by what `check` would then add."""
    store = _cluster(tmp_path, names=_MEMBERS, generator=_LIVE)
    before = _item_text(store)

    assert _run("set", "PL-4040", "--misread", "x" * 101, "--items", str(store)) == 1

    assert "runs to 101 characters" in capsys.readouterr().out
    assert _item_text(store) == before


def test_set_refuses_a_blank_misread_rather_than_writing_an_empty_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Read as absent, a blank value added no new error and was written as a success."""
    store = _cluster(tmp_path, names=_MEMBERS, generator=_LIVE)
    before = _item_text(store)

    assert _run("set", "PL-4040", "--misread", "   ", "--items", str(store)) == 1

    assert "is blank" in capsys.readouterr().out
    assert _item_text(store) == before


def test_show_on_a_head_prints_what_is_wrong_with_its_misread_under_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = _cluster(tmp_path, names=_MEMBERS, generator=_LIVE, misread="x" * 101)

    assert _run("show", "PL-4040", "--items", str(store)) == 0

    assert (
        f"  misread: {'x' * 101}\n    UNSOUND - runs to 101 characters" in capsys.readouterr().out
    )


def test_generators_says_which_head_names_which_where_heads_nest(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The pair is ordered by id, so the clause has to carry which head holds the other.

    `PL-4040` names `PL-5050` (the lower id nesting the higher), and
    `PL-6060` names `PL-5050` (the higher nesting the lower), which also
    makes `PL-4040` and `PL-6060` share `PL-5050`. Printed the other way
    round, a nesting line states the containment backwards.
    """
    store = _store(
        tmp_path,
        _clustered("PL-4040", "Outer", names="PL-5050, PL-B1B1, PL-C2C2", misread=_MISREAD),
        _clustered("PL-5050", "Inner", names="PL-D3D3, PL-F5F5, PL-G6G6", misread=_MISREAD),
        _clustered("PL-6060", "Also outer", names="PL-5050, PL-H7H7, PL-J8J8", misread=_MISREAD),
        *(
            _clustered(member, f"Member {member}")
            for member in ("PL-B1B1", "PL-C2C2", "PL-D3D3", "PL-F5F5", "PL-G6G6")
            + ("PL-H7H7", "PL-J8J8")
        ),
    )

    assert _run("generators", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert (
        "\n    PL-4040 names PL-5050\n"
        "    PL-4040 and PL-6060 share PL-5050\n"
        "    PL-6060 names PL-5050\n"
    ) in output


def test_generators_names_both_directions_where_two_heads_name_each_other(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = _store(
        tmp_path,
        _clustered("PL-4040", "One", names="PL-5050, PL-B1B1, PL-C2C2", misread=_MISREAD),
        _clustered("PL-5050", "Other", names="PL-4040, PL-D3D3, PL-F5F5", misread=_MISREAD),
        *(
            _clustered(member, f"Member {member}")
            for member in ("PL-B1B1", "PL-C2C2", "PL-D3D3", "PL-F5F5")
        ),
    )

    assert _run("generators", "--items", str(store)) == 0

    assert "\n    PL-4040 names PL-5050; PL-5050 names PL-4040\n" in capsys.readouterr().out


def test_generators_misread_names_an_unsound_claim_it_could_not_list(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An unsound claim is on no head's line, so leaving it off would pass a part as the whole."""
    store = _store(
        tmp_path,
        _clustered("PL-4040", "A sound head", names=_MEMBERS, generator=_LIVE, misread=_MISREAD),
        _clustered("PL-G4G4", "A head naming an id nothing carries", names="PL-B1B1, PL-N0P3"),
        *(_clustered(member, f"Member {member}") for member in ("PL-B1B1", "PL-C2C2", "PL-D3D3")),
    )

    assert _run("generators", "--misread", "--items", str(store)) == 0

    output = capsys.readouterr().out
    assert f"  PL-4040 (ready)  {_MISREAD}\n" in output
    assert (
        "1 item carries a `root-cause-of:` that is not a sound claim, so it is ranked and "
        "counted as an ordinary item: PL-G4G4"
    ) in output


class TestAskingTheForgeWhichBranchesAreOpen:
    """`flight`'s forge half, and the one way it must never fail.

    A command that could not look and one that looked and found nothing open
    are opposite answers, and the plumbing here is where they would be
    flattened into each other. `None` makes `flight` say "every item closed"
    alone; a list makes it add "and no pull request is open". So the exit
    status is what these assert, rather than the text of the report.
    """

    def _args(self, no_remote: bool = False) -> argparse.Namespace:
        return argparse.Namespace(no_remote=no_remote)

    def test_the_configured_command_supplies_the_branch_names(self, tmp_path: Path) -> None:
        config = with_fields(
            Config(), open_pull_requests_command="printf 'claude/one\nclaude/two\n'"
        )
        ask = cli._open_pull_requests(self._args(), tmp_path, config)
        assert ask is not None
        assert list(ask()) == ["claude/one", "claude/two"]

    def test_a_number_after_the_name_is_read_as_its_pull_request(self, tmp_path: Path) -> None:
        """The number is optional, so a project's own command owes only the name."""
        config = with_fields(
            Config(), open_pull_requests_command="printf 'claude/one 841\nclaude/two\n'"
        )
        ask = cli._open_pull_requests(self._args(), tmp_path, config)
        assert ask is not None
        assert ask() == {"claude/one": 841, "claude/two": None}

    def test_a_command_that_could_not_look_answers_none(self, tmp_path: Path) -> None:
        """Exit non-zero is the contract `tools/open_pull_requests.py` holds to."""
        config = with_fields(Config(), open_pull_requests_command="false")
        ask = cli._open_pull_requests(self._args(), tmp_path, config)
        assert ask is not None
        assert ask() is None

    def test_a_command_that_is_not_there_answers_none(self, tmp_path: Path) -> None:
        config = with_fields(Config(), open_pull_requests_command="no-such-command-anywhere")
        ask = cli._open_pull_requests(self._args(), tmp_path, config)
        assert ask is not None
        assert ask() is None

    def test_a_project_configuring_nothing_has_no_way_to_ask(self, tmp_path: Path) -> None:
        assert cli._open_pull_requests(self._args(), tmp_path, Config()) is None

    def test_no_remote_declines_to_ask_however_it_is_configured(self, tmp_path: Path) -> None:
        config = with_fields(Config(), open_pull_requests_command="printf 'claude/one\n'")
        assert cli._open_pull_requests(self._args(no_remote=True), tmp_path, config) is None


# --- arm: whether a pull request may be armed (`PL-DDYD`) ---------------------

#: The branch every `arm` test asks about, and when its claims are made. The
#: base sits a month earlier, and every read is given `--now` a minute after
#: `ARM_T0`, so no lease is judged against the clock.
ARM_BRANCH = "claude/arm-work-q7x2m4"
ARM_T0 = "2026-09-01T12:00:00+00:00"
ARM_NOW = "2026-09-01T12:01:00+00:00"


def _item_document(identifier: str, status: str = "ready") -> str:
    return f"---\nid: {identifier}\ntitle: {identifier}\nstatus: {status}\n---\n\n**Problem.** x\n"


def _arm_repo(tmp_path: Path) -> tuple[Path, Callable[..., str]]:
    """A clone of a bare `origin` whose `main` holds two items, checked out on `ARM_BRANCH`.

    `main` carries the claim record's marker, so a `Claim:` trailer on the
    branch is read as a claim rather than by the old rules. The returned `git`
    dates every commit it makes at `when`, a month before `ARM_T0` by default.
    """
    from docket.claims import CUTOVER_MARKER

    remote = tmp_path / "origin.git"
    root = tmp_path / "work"
    for target in (["--bare", str(remote)], [str(root)]):
        subprocess.run(
            ["git", "-c", "init.defaultBranch=main", "init", "-q", *target],
            check=True,
            capture_output=True,
        )

    def git(*args: str, when: str = "2026-08-01T12:00:00+00:00") -> str:
        dated = os.environ | {"GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
        done = subprocess.run(
            ["git", *args], cwd=root, check=True, capture_output=True, text=True, env=dated
        )
        return done.stdout

    git("config", "user.email", "t@example.com")
    git("config", "user.name", "T")
    files = {
        "docs/items/PL-B1B1-held.md": _item_document("PL-B1B1"),
        "docs/items/PL-C2C2-other.md": _item_document("PL-C2C2"),
        "docs/PL-D3D3-drafted.md": _item_document("PL-D3D3"),
        CUTOVER_MARKER: "# the claim writer\n",
    }
    for path, text in files.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text, encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "base")
    git("remote", "add", "origin", str(remote))
    git("push", "-q", "-u", "origin", "main")
    git("checkout", "-qb", ARM_BRANCH)
    return root, git


def _arm(root: Path, *extra: str) -> int:
    return main(["arm", "--items", str(root / "docs" / "items"), "--now", ARM_NOW, *extra])


def _commit_file(git: Callable[..., str], root: Path, path: str, text: str, when: str) -> None:
    (root / path).write_text(text, encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", f"edit {path}", when=when)


def _claim_by_hand(git: Callable[..., str], key: str, branch: str, when: str) -> None:
    """A claim commit written the way `bin/docket claim` writes one."""
    git("commit", "-q", "--allow-empty", "-m", f"{key}: start\n\nClaim: {key} {branch}", when=when)


def test_arm_arms_a_branch_carrying_only_item_files_whatever_another_branch_claims(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A capture arms, and a live claim bound to another branch holds nothing here.

    The other branch's claim is on the very item this branch edits, so a
    reader that forgot the claim is bound to its own branch would hold this
    one.
    """
    root, git = _arm_repo(tmp_path)
    git("checkout", "-qb", "claude/rival-k2m9p4", "main")
    _claim_by_hand(git, "PL-B1B1", "claude/rival-k2m9p4", ARM_T0)
    git("push", "-q", "origin", "claude/rival-k2m9p4")
    git("checkout", "-q", ARM_BRANCH)
    _commit_file(git, root, "docs/items/PL-F4F4-new.md", _item_document("PL-F4F4"), ARM_T0)
    _commit_file(
        git, root, "docs/items/PL-B1B1-held.md", _item_document("PL-B1B1", "needs-decision"), ARM_T0
    )

    assert _arm(root) == 0
    out = capsys.readouterr().out
    assert out.startswith(f"arm - {ARM_BRANCH} changes nothing outside docs/items")


@pytest.mark.parametrize(
    "release", ["done", "blocked", "yield"], ids=["closing-the-item", "blocking-it", "yielding-it"]
)
def test_arm_holds_while_a_claim_on_the_branch_is_open_and_arms_once_it_is_released(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], release: str
) -> None:
    """The claim holds whichever push carried it, until one of the routes that end it.

    A queue-only branch - the claim and an item edit - is the shape `PL-QP9Z`
    and `PL-1MCK` each armed while its work went on.
    """
    root, git = _arm_repo(tmp_path)
    _claim_by_hand(git, "PL-B1B1", ARM_BRANCH, ARM_T0)
    held = _item_document("PL-B1B1", "needs-decision")
    _commit_file(git, root, "docs/items/PL-B1B1-held.md", held, "2026-09-01T12:00:30+00:00")

    assert _arm(root) == 1
    out = capsys.readouterr().out
    assert out.startswith(f"hold - {ARM_BRANCH}: a merge would erase its open claim on PL-B1B1")
    assert "keep the pull request a draft" in out

    if release == "yield":
        git("commit", "-q", "--allow-empty", "-m", f"PL-B1B1: yield\n\nYield: PL-B1B1 {ARM_BRANCH}")
    else:
        closed = _item_document("PL-B1B1", release)
        _commit_file(git, root, "docs/items/PL-B1B1-held.md", closed, "2026-09-01T12:00:40+00:00")

    assert _arm(root) == 0
    assert capsys.readouterr().out.startswith(f"arm - {ARM_BRANCH}")


def test_arm_holds_a_lapsed_claim_and_says_how_to_end_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Out of lease is not released: nobody finished the work or handed it back."""
    root, git = _arm_repo(tmp_path)
    _claim_by_hand(git, "PL-B1B1", ARM_BRANCH, "2026-08-20T12:00:00+00:00")

    assert _arm(root) == 1
    out = capsys.readouterr().out
    assert "lapsed with no commit since 2026-08-20" in out
    assert "`bin/docket yield PL-B1B1` ends it" in out


def test_arm_holds_a_branch_changing_paths_outside_the_store_and_names_them(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Work outside the store waits on a read, and a move into the store is still a deletion.

    Read with rename detection, the file moved in from `docs/` prints as one
    path under the store, and the branch would arm with a file gone from
    outside it.
    """
    root, git = _arm_repo(tmp_path)
    git("mv", "docs/PL-D3D3-drafted.md", "docs/items/PL-D3D3-drafted.md")
    git("commit", "-qm", "PL-D3D3: file the drafted item", when=ARM_T0)

    assert _arm(root) == 1
    out = capsys.readouterr().out
    assert out.startswith(f"hold - {ARM_BRANCH}: it changes 1 path outside docs/items")
    assert "docs/PL-D3D3-drafted.md" in out
    assert "keep the pull request a draft" not in out


def test_arm_says_behind_when_the_base_has_moved_past_the_branch(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`main` merges only an up-to-date branch, and auto-merge never brings the base in.

    The base moves on the remote after this checkout last looked, so only the
    fetch `arm` makes first can see it.
    """
    root, git = _arm_repo(tmp_path)
    _commit_file(git, root, "docs/items/PL-F4F4-new.md", _item_document("PL-F4F4"), ARM_T0)
    other = tmp_path / "other"
    subprocess.run(
        ["git", "clone", "-q", str(tmp_path / "origin.git"), str(other)],
        check=True,
        capture_output=True,
    )
    for args in (
        ["-c", "user.email=t@example.com", "-c", "user.name=T", "commit", "-q", "--allow-empty"],
        ["push", "-q", "origin", "main"],
    ):
        extra = ["-m", "elsewhere"] if "commit" in args else []
        subprocess.run(["git", *args, *extra], cwd=other, check=True, capture_output=True)

    assert _arm(root, "--no-fetch") == 0
    capsys.readouterr()

    assert _arm(root) == 1
    out = capsys.readouterr().out
    assert out.startswith("behind 1 - origin/main has 1 commit")
    assert "update_pull_request_branch" in out


def test_arm_answers_unknown_rather_than_arm_from_a_read_it_could_not_complete(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A fetch that failed leaves `behind` unknown, but not a hold that is reason enough alone."""
    root, git = _arm_repo(tmp_path)
    _commit_file(git, root, "docs/items/PL-F4F4-new.md", _item_document("PL-F4F4"), ARM_T0)
    git("remote", "set-url", "origin", str(tmp_path / "gone.git"))

    assert _arm(root) == 2
    assert capsys.readouterr().out.startswith("unknown - `git fetch origin` failed")
    assert _arm(root, "--no-fetch") == 0
    capsys.readouterr()

    _claim_by_hand(git, "PL-B1B1", ARM_BRANCH, ARM_T0)
    assert _arm(root) == 1
    out = capsys.readouterr().out
    assert out.startswith(f"hold - {ARM_BRANCH}: a merge would erase its open claim on PL-B1B1")
    assert "note: `git fetch origin` failed" in out

    git("checkout", "-q", "--detach")
    assert _arm(root, "--no-fetch") == 2
    assert capsys.readouterr().out.startswith("unknown - HEAD is on no branch")


#: The module deciding `arm`'s answer, as the brief names it (`PL-K6B2`).
ARM_GATE = "subprojects/docket/src/docket/arming.py"


def _put(git: Callable[..., str], root: Path, path: str, when: str = ARM_T0) -> None:
    """Commit a new file at `path` on the checked-out branch, making its directory."""
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    _commit_file(git, root, path, "X = 1\n", when)


def test_arm_arms_a_docket_only_pull_request_on_green(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The queue's own tooling arms beside the store, so the hold is left for what needs a read.

    The hold fired on every docket change and was clicked through (`PL-SQTR`).
    The branch is the usual shape of docket work: a module, its test, the
    package's README and the item it closes.
    """
    root, git = _arm_repo(tmp_path)
    for path in (
        "subprojects/docket/src/docket/render.py",
        "subprojects/docket/tests/test_render.py",
        "subprojects/docket/README.md",
    ):
        _put(git, root, path)
    closed = _item_document("PL-B1B1", "done")
    _commit_file(git, root, "docs/items/PL-B1B1-held.md", closed, ARM_T0)

    assert _arm(root) == 0
    out = capsys.readouterr().out
    assert out.startswith(
        f"arm - {ARM_BRANCH} changes nothing outside docs/items and subprojects/docket, "
        "leaves arming.py alone, holds no open claim"
    )


@pytest.mark.parametrize(
    "path",
    [
        "src/anesthesia_sim/core/uptake.py",
        "src/anesthesia_sim/data/agents/sevoflurane.json",
        "tests/unit/test_uptake.py",
        "docs/MODEL.md",
        "README.md",
        "CLAUDE.md",
        "subprojects/docketeer/tool.py",
    ],
)
def test_arm_holds_for_a_read_a_path_outside_the_store_and_the_tooling(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], path: str
) -> None:
    """Everything but the store and the tooling waits on a read, the simulator first of all.

    The branch also changes a docket module, which would arm alone, so the
    hold is the path's own. `subprojects/docketeer/` shares the tooling's
    letters and not its directory.
    """
    root, git = _arm_repo(tmp_path)
    _put(git, root, "subprojects/docket/src/docket/render.py")
    _put(git, root, path)

    assert _arm(root) == 1
    out = capsys.readouterr().out
    assert out.startswith(
        f"hold - {ARM_BRANCH}: it changes 1 path outside docs/items and subprojects/docket, "
        "so its pull request waits on a read\n"
    )
    assert f"\n  {path}\n" in out
    assert "subprojects/docket/src/docket/render.py" not in out
    assert "keep the pull request a draft" not in out


@pytest.mark.parametrize("change", ["edit", "move"])
def test_arm_holds_a_change_to_arming_py_for_a_read_although_it_lies_under_the_tooling(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], change: str
) -> None:
    """The gate cannot loosen itself, by an edit or by moving where the exception points.

    The module is on the base, so a move reads as its deletion beside the new
    file, both under the tooling: read with rename detection, the move would
    print as the new path alone and arm.
    """
    root, git = _arm_repo(tmp_path)
    git("checkout", "-q", "main")
    _put(git, root, ARM_GATE, "2026-08-01T12:00:00+00:00")
    git("push", "-q", "origin", "main")
    git("checkout", "-q", ARM_BRANCH)
    git("merge", "-q", "--ff-only", "main")
    if change == "edit":
        _commit_file(git, root, ARM_GATE, "X = 2\n", ARM_T0)
    else:
        git("mv", ARM_GATE, "subprojects/docket/src/docket/gating.py")
        git("commit", "-qm", "move the gate", when=ARM_T0)

    assert _arm(root) == 1
    out = capsys.readouterr().out
    assert out.startswith(
        f"hold - {ARM_BRANCH}: it changes {ARM_GATE}, the gate itself, "
        "so its pull request waits on a read\n"
    )
    assert "outside docs/items" not in out


def test_arm_names_the_gate_beside_the_paths_outside_the_tooling(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Both reasons are said, and the listed paths are the ones outside, not the gate."""
    root, git = _arm_repo(tmp_path)
    _put(git, root, ARM_GATE)
    _put(git, root, "src/anesthesia_sim/core/uptake.py")

    assert _arm(root) == 1
    out = capsys.readouterr().out
    assert out.startswith(
        f"hold - {ARM_BRANCH}: it changes 1 path outside docs/items and subprojects/docket "
        f"and it changes {ARM_GATE}, the gate itself, so its pull request waits on a read\n"
        "  src/anesthesia_sim/core/uptake.py\n"
    )


def test_the_gate_arm_holds_for_a_read_is_the_module_that_decides_the_answer() -> None:
    """A move of `arming.py` would leave the exception naming a file nothing reads.

    The moved module would then arm on green, which is the gate loosening itself.
    """
    root = Path(__file__).resolve().parents[3]

    assert arming.GATE == ARM_GATE
    assert (root / arming.GATE).resolve() == Path(arming.__file__).resolve()


def _flight_row(out: str, start: str) -> str:
    return next(line for line in out.splitlines() if line.startswith(start))


def test_flight_prints_each_hold_s_kind_and_state_the_lapsed_claims_and_the_unclaimed_work(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-N162`'s slice 5, against real git under the claim record.

    A live claim prints its state and kind on its row. A claim twelve days
    old on an open item has lapsed, holds nothing, and prints as its own row
    under a heading saying so. A `claude/` branch whose commit reaches outside
    the queue with no claim on it is an `unclaimed:` row, although its subject
    leads with an id - attribution, which claims nothing - and `legacy refs:`
    reads 0, because every commit here was made under the record.

    Three branches owe no row, from the review of this slice. The lapsed
    branch did work outside the queue, and a claim counts in any state
    (project owner, 2026-09-24). A capture writing an item and the roadmap
    wrote only the queue. And a capture claimed past its lease names
    an item the base lacks, which is nobody's to start, so it is no lapsed row.
    """
    root, git = _arm_repo(tmp_path)
    _claim_by_hand(git, "PL-B1B1", ARM_BRANCH, ARM_T0)
    _commit_file(git, root, "work.py", "WORK = 1\n", ARM_T0)
    git("checkout", "-qb", "claude/gone-a1b2c3", "main")
    _claim_by_hand(git, "PL-C2C2", "claude/gone-a1b2c3", "2026-08-20T12:00:00+00:00")
    _commit_file(git, root, "gone.py", "GONE = 1\n", "2026-08-20T12:00:00+00:00")
    git("checkout", "-qb", "claude/forgetful-d4e5f6", "main")
    _commit_file(git, root, "forgot.py", "FORGOT = 1\n", ARM_T0)
    git("checkout", "-qb", "claude/capture-g7h8j9", "main")
    (root / "ROADMAP.md").write_text("- PL-F6F6\n", encoding="utf-8")
    _commit_file(git, root, "docs/items/PL-F6F6-later.md", _item_document("PL-F6F6"), ARM_T0)
    git("checkout", "-qb", "claude/capture-k2m9p4", "main")
    _commit_file(
        git,
        root,
        "docs/items/PL-H5H5-new.md",
        _item_document("PL-H5H5"),
        "2026-08-20T12:00:00+00:00",
    )
    _claim_by_hand(git, "PL-H5H5", "claude/capture-k2m9p4", "2026-08-20T12:00:00+00:00")

    argv = ["--items", str(root / "docs" / "items"), "--now", ARM_NOW, "flight", "--no-remote"]
    assert main(argv) == 0
    out = capsys.readouterr().out

    assert re.fullmatch(
        rf"PL-B1B1  {ARM_BRANCH}\s+live  claim  last commit 1 minute ago",
        _flight_row(out, "PL-B1B1"),
    )
    assert "1 claim has lapsed on an item the default branch holds open" in out
    assert re.fullmatch(
        r"PL-C2C2  claude/gone-a1b2c3  lapsed  claim  last commit 12 days ago",
        _flight_row(out, "PL-C2C2"),
    )
    assert "legacy refs: 0" in out
    assert "1 work branch claims nothing" in out
    assert [line for line in out.splitlines() if line.startswith("unclaimed:")] == [
        "unclaimed: claude/forgetful-d4e5f6  last commit 1 minute ago"
    ]
    assert "PL-H5H5" not in out


def test_flight_counts_the_refs_still_holding_by_the_old_rule(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Before the record a subject leading with an id claims it, and `PL-CH3Z` waits on the count.

    `_flight_repo`'s commits predate `CUTOVER_MARKER`, so its branch holds by
    the old rule: the row says `legacy claim`, the ref is counted, and the
    branch is no `unclaimed:` row - the catch skips what was made before a
    session could claim, and the harness's name is outside `claude/` anyway.
    """
    root = _flight_repo(tmp_path, "PL-0001 Do the thing")

    assert main(["--items", str(root / "items"), "--today", "2026-08-23", "flight"]) == 0
    out = capsys.readouterr().out

    assert re.fullmatch(
        rf"PL-0001  {BRANCH}  live  legacy claim  last commit 3 days ago",
        _flight_row(out, "PL-0001"),
    )
    assert "legacy refs: 1 - 1 ref holds an item" in out
    assert "unclaimed:" not in out
    assert "lapsed" not in out


def test_flight_counts_only_legacy_claims_still_live(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A legacy claim past its lease holds nothing, so it no longer needs the old rule either."""
    root = _flight_repo(tmp_path, "PL-0001 Do the thing")

    assert main(["--items", str(root / "items"), "--today", "2026-09-20", "flight"]) == 0
    out = capsys.readouterr().out

    assert "legacy refs: 0 - no ref holds an item" in out


def test_flight_reads_legacy_refs_as_a_floor_where_a_ref_went_unread(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-CH3Z` starts on `legacy refs: 0`, and a truncated clone must not print it.

    `_shallow_pair` is an agent container in miniature: its branch leads with
    an id on commits made before the record, and the ref goes unread, so
    whatever it holds by the old rule is never counted. The zero would be the
    go-ahead to delete that rule over a ref still holding by it.
    """
    work = _shallow_pair(tmp_path)

    assert main(["--items", str(work / "items"), "flight"]) == 0
    out = capsys.readouterr().out

    assert (
        "legacy refs: at least 0 - 1 ref went unread and may hold by the old rule as well "
        f"(origin/{BRANCH})" in out
    )
    assert "nothing here still needs the old rule" not in out


def test_next_and_the_digest_say_what_holds_each_item_they_leave_out(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-N162`'s done-when: the digest and `next` gain each held id's state and kind.

    A status disposition is a decision about an item and a claim is somebody
    working it, and the bare id read the two the same.
    """
    root, git = _arm_repo(tmp_path)
    _claim_by_hand(git, "PL-B1B1", ARM_BRANCH, ARM_T0)
    store = str(root / "docs" / "items")

    assert main(["--items", store, "--now", ARM_NOW, "next"]) == 0
    listed = capsys.readouterr().out
    assert main(["--items", store, "--now", ARM_NOW, "digest"]) == 0
    digest = capsys.readouterr().out

    assert "Excluded, already in flight: PL-B1B1 (live claim)" in listed
    assert re.search(
        r"In flight on a branch, by time since its last commit: PL-B1B1 [^,(]+ \(live claim\)\.",
        digest,
    )
