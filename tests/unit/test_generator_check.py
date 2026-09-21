"""Tests for `tools/generator_check.py`, the root-cause candidate advisory.

The script used to return a verdict: a self-generation ratio of `r >= 1.0`,
behind a floor of eight closures, reported as a generator. `PL-VX5H` replaced
the definition - a generator is now the recorded root cause of three or more
items, written on the causing item as `root-cause-of:` - and the ratio does not
measure that. On 2026-09-17 it reported no cluster on this tree while `PL-6ZQY`
had already named six under one root cause.

So what is under test here is mostly what the script *refuses to say*. The
load-bearing tests are `test_a_cluster_below_the_old_closure_gate_is_surfaced`,
which pins the removal of the gate that reported the weed only once it had
seeded, and `test_no_output_calls_anything_a_generator`, which pins the
demotion itself. `test_a_busy_cluster_does_not_read_as_reproducing` stays from
the verdict era: every spawned child is attributed to the item being worked
when it was captured, so counting all of them rates any heavily-worked file a
generator, and the ratio column would be wrong in the direction that flatters.
`test_the_store_clusters_like_any_other_path` pins the removal of the store
paths' exclusion from clustering, whose ground held on the commit axis and not
on this one (`PL-LSR0`).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest
from docket.store import ID_RE

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

import generator_check


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        env={
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t",
            "PATH": "/usr/bin:/bin",
        },
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q", "-b", "main")
    (tmp_path / "docs" / "items").mkdir(parents=True)
    return tmp_path


def _write(
    repo: Path,
    identifier: str,
    *,
    touches: str,
    status: str,
    priority: str = "P2",
    feature: str = "",
    root_cause_of: str = "",
    body: str = "body",
) -> Path:
    path = repo / "docs" / "items" / f"{identifier}-x.md"
    front = [
        f"id: {identifier}",
        f"title: {identifier} title",
        f"priority: {priority}",
        f"status: {status}",
        f"touches: {touches}",
    ]
    if feature:
        front.append(f"feature: {feature}")
    if root_cause_of:
        front.append(f"root-cause-of: {root_cause_of}")
    path.write_text("---\n" + "\n".join(front) + f"\n---\n\n{body}\n", encoding="utf-8")
    return path


def _commit(repo: Path, subject: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", subject)


def _closers(repo: Path, path: str, count: int, *, kids_touch: str) -> None:
    """Close `count` items on `path`, each spawning one child touching `kids_touch`."""
    for n in range(count):
        parent = f"PL-C{n:03d}"
        _write(repo, parent, touches=path, status="done")
        _commit(repo, f"{parent}: capture")
        _write(repo, f"PL-K{n:03d}", touches=kids_touch, status="ready", feature="same")
        _commit(repo, f"{parent}: work that spawned a finding")


def _open_trio(repo: Path, path: str, *, feature: str = "") -> None:
    for identifier in ("PL-8888", "PL-BBBB", "PL-CCCC"):
        _write(repo, identifier, touches=path, status="ready", feature=feature)
    _commit(repo, "PL-8888, PL-BBBB, PL-CCCC: capture three findings")


def test_a_cluster_below_the_old_closure_gate_is_surfaced(repo: Path) -> None:
    """`MIN_CLOSED = 8` reported the weed once it had seeded, so it is gone.

    Three open items sharing a feature and two closures behind them: under the
    old rule this was invisible, which is the failure `PL-VX5H` names.
    """
    _closers(repo, "src/thing.py", 2, kids_touch="docs/other.md")
    _open_trio(repo, "src/thing.py", feature="one-problem")

    found = generator_check.clusters(repo)

    assert [c.path for c in found] == ["src/thing.py"]
    assert found[0].closed == 2
    assert found[0].feature_count == 3


def test_a_cluster_with_no_signal_is_not_surfaced(repo: Path) -> None:
    """Size alone is not a signal: a big file honestly attracts many items."""
    for identifier in ("PL-8888", "PL-BBBB", "PL-CCCC", "PL-DDDD"):
        _write(repo, identifier, touches="src/thing.py", status="ready")
    _commit(repo, "PL-8888, PL-BBBB, PL-CCCC, PL-DDDD: capture four unrelated findings")

    assert generator_check.clusters(repo) == []


def test_a_cluster_under_three_open_items_cannot_host_a_root_cause(repo: Path) -> None:
    for identifier in ("PL-8888", "PL-BBBB"):
        _write(repo, identifier, touches="src/thing.py", status="ready", feature="one-problem")
    _commit(repo, "PL-8888, PL-BBBB: capture two findings")

    assert generator_check.clusters(repo) == []


def test_a_cluster_with_no_closures_declines_the_ratio(repo: Path) -> None:
    """`None`, never `0.00`: a zero would say it was measured and came back clean."""
    _open_trio(repo, "src/thing.py", feature="one-problem")

    found = generator_check.clusters(repo)

    assert found[0].ratio is None
    assert "no closures yet" in generator_check._line(found[0])
    assert not any("r = " in signal for signal in found[0].signals)


def test_a_busy_cluster_does_not_read_as_reproducing(repo: Path) -> None:
    """Children landing elsewhere are captures, not reproduction."""
    _closers(repo, "src/thing.py", 10, kids_touch="docs/other.md")
    _open_trio(repo, "src/thing.py", feature="one-problem")

    found = next(c for c in generator_check.clusters(repo) if c.path == "src/thing.py")

    assert found.ratio == 0.0
    assert not any("not shrinking" in signal for signal in found.signals)


def test_a_cluster_reproducing_into_itself_says_so(repo: Path) -> None:
    _closers(repo, "src/thing.py", 3, kids_touch="src/thing.py")

    found = next(c for c in generator_check.clusters(repo) if c.path == "src/thing.py")

    assert found.ratio == 1.0
    assert any("not shrinking" in signal for signal in found.signals)
    # Two runs against one tree print the same rows in the same order, or the
    # advisory is noise in every diff that touches the store.
    assert found.open_ids == sorted(found.open_ids)


def test_a_cluster_with_nothing_open_is_history_not_friction(repo: Path) -> None:
    """A cluster already closed out is not work anyone can act on."""
    _closers(repo, "src/thing.py", 3, kids_touch="src/thing.py")
    for path in (repo / "docs" / "items").glob("PL-K*.md"):  # not-an-id: a glob, not a literal
        path.write_text(path.read_text().replace("status: ready", "status: done"), encoding="utf-8")
    _commit(repo, "PL-C000: close the children")

    assert generator_check.clusters(repo) == []


def test_a_store_path_with_no_signal_is_not_surfaced(repo: Path) -> None:
    """The store is a path like any other: size alone is not a signal there either."""
    for identifier in ("PL-8888", "PL-BBBB", "PL-CCCC", "PL-DDDD"):
        _write(repo, identifier, touches="docs/items/", status="ready")
    _commit(repo, "PL-8888, PL-BBBB, PL-CCCC, PL-DDDD: capture four unrelated findings")

    assert generator_check.clusters(repo) == []


def test_the_store_clusters_like_any_other_path(repo: Path) -> None:
    """`STORE_PATHS` hid `docs/items` and `docs/WORKING_NOTES.md` from clustering.

    The ground was that every capture would otherwise read as one enormous
    cluster, which is true of the files a commit changes and false of what an
    item declares: 24 and 18 open items declared them when it was measured, and
    13 of `PL-G424`'s 21 members sat there unseen (`PL-LSR0`).
    """
    _closers(repo, "docs/items", 3, kids_touch="docs/items")
    _open_trio(repo, "docs/WORKING_NOTES.md", feature="one-problem")

    found = generator_check.clusters(repo)

    assert sorted(c.path for c in found) == ["docs/WORKING_NOTES.md", "docs/items"]
    assert next(c for c in found if c.path == "docs/items").ratio == 1.0


def test_a_signal_breaks_ties_before_size(repo: Path) -> None:
    """Two clusters equally named as one problem: the one citing itself more leads.

    Size is not a signal, so it cannot outrank one. Measured 2026-09-19, the
    `docs/WORKING_NOTES.md` cluster carrying 8 of `PL-G424`'s members ranked
    ninth on size, behind clusters nobody cited, under a display limit of six.
    """
    for identifier in ("PL-BBB0", "PL-BBB1", "PL-BBB2"):
        _write(repo, identifier, touches="src/big.py", status="ready", feature="one-problem")
    _write(repo, "PL-BBB3", touches="src/big.py", status="ready")
    _open_trio(repo, "src/small.py", feature="another-problem")
    for n in range(3):
        _write(repo, f"PL-S{n:03d}", touches="elsewhere.py", status="ready", body="about PL-8888")
    _commit(repo, "PL-S000, PL-S001, PL-S002: capture three findings")

    found = generator_check.clusters(repo)

    assert [c.path for c in found] == ["src/small.py", "src/big.py"]
    assert found[0].cited == ["PL-8888"]


def test_items_already_inside_a_recorded_root_cause_are_marked(repo: Path) -> None:
    """Marked rather than dropped: a recorded claim can be wrong."""
    _write(repo, "PL-8888", touches="src/thing.py", status="ready", feature="one-problem")
    _write(repo, "PL-BBBB", touches="src/thing.py", status="ready", feature="one-problem")
    _write(
        repo,
        "PL-CCCC",
        touches="src/thing.py",
        status="needs-decision",
        feature="one-problem",
        root_cause_of="PL-8888, PL-BBBB, PL-DDDD",
    )
    _write(repo, "PL-DDDD", touches="elsewhere.py", status="ready")
    _commit(repo, "PL-8888, PL-BBBB, PL-CCCC, PL-DDDD: capture")

    found = next(c for c in generator_check.clusters(repo) if c.path == "src/thing.py")

    assert found.recorded == ["PL-8888", "PL-BBBB", "PL-CCCC"]
    assert "3 already inside a recorded root cause" in generator_check._line(found)


def test_only_open_items_cite(repo: Path) -> None:
    """A closed item's citation is history, not evidence a mechanism still stands."""
    for n, status in enumerate(("done", "done", "done", "ready")):
        _write(
            repo,
            f"PL-S{n:03d}",
            touches="elsewhere.py",
            status=status,
            body="this is about PL-8888",
        )
    _open_trio(repo, "src/thing.py")

    counts = generator_check.citations(repo, {"PL-8888", "PL-BBBB", "PL-CCCC", "PL-S003"})

    assert counts["PL-8888"] == 1


def test_a_capture_commit_spawns_nothing(repo: Path) -> None:
    """A commit leading with the ids it creates is a capture with no parent."""
    _write(repo, "PL-8888", touches="src/thing.py", status="done")
    _write(repo, "PL-BBBB", touches="src/thing.py", status="ready")
    _commit(repo, "PL-8888, PL-BBBB: capture two findings")

    parents = generator_check.creation_parents(repo)
    assert parents["PL-8888"] == set()
    assert parents["PL-BBBB"] == set()


def test_no_output_calls_anything_a_generator(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The demotion itself: it surfaces candidates and claims none of them."""
    _closers(repo, "src/thing.py", 3, kids_touch="src/thing.py")
    _open_trio(repo, "src/thing.py", feature="one-problem")

    assert generator_check.main(["--repo", str(repo)]) == 0

    out = capsys.readouterr().out
    assert "None of these is a generator" in out
    assert "evidence, not causation" in out
    assert "root-cause-of:" in out


#: Anything shaped like an item id in the script's own output. Deliberately
#: looser than `ID_RE`, because what is under test is whether a printed id
#: *matches* that pattern - a candidate regex that could only match a valid id
#: would have nothing to report.
_PRINTED_ID_RE = re.compile(r"PL-[A-Za-z0-9]+")


def test_every_id_the_advisory_prints_is_one_the_store_could_mint(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An example is copied, so an example outside the alphabet teaches a false grammar.

    `store.ID_ALPHABET` is Crockford base32 *minus the vowels*, so `PL-AAAA` is
    an id `new_id` can never produce and `ID_PATTERN` never matches. This script
    printed exactly that literal in the `root-cause-of:` line it offers a
    session to copy, while `docket set --root-cause-of` a directory away printed
    `PL-XXXX,PL-YYYY,PL-ZZZZ` for the same field - two placeholder sets for one
    interface, one of them ungrammatical (`PL-DPY6`).

    It is worth pinning because the failure is silent in both directions. A
    session copying the shape into a fixture reproduces what `PL-GXPP` spent 261
    substitutions removing from the test tree, where an id outside the alphabet
    makes any assertion resting on it pass vacuously; and `generator_check`'s
    own `ID_RE` is looser than the store's, so nothing here would have objected.

    Asserted against `store.ID_RE` rather than a fourth copy of the grammar.
    Restating it is the defect this is next to, not a shortcut around it.
    """
    _closers(repo, "src/thing.py", 3, kids_touch="src/thing.py")
    _open_trio(repo, "src/thing.py", feature="one-problem")

    assert generator_check.main(["--repo", str(repo)]) == 0

    out = capsys.readouterr().out
    printed = sorted(set(_PRINTED_ID_RE.findall(out)))
    assert printed, "no ids in the output at all, so this asserts nothing"

    outside = [i for i in printed if not ID_RE.match(i)]
    assert not outside, (
        "these ids in the advisory's output are outside the alphabet the store mints, "
        "so a session copying one writes an id `ID_PATTERN` can never match: " + ", ".join(outside)
    )


def test_a_historical_three_digit_id_is_cited_like_any_other(repo: Path) -> None:
    """43 of the store's ids are `PL-001`-shaped and `PL-[A-Z0-9]{4}` saw none.

    Measured 2026-09-21: the restated grammar hid 219 citation edges naming one,
    and the signal this prints for the `docs/MODEL.md` cluster read `6 cited by
    3+ open items` where 7 was the answer. The oldest items in the store were
    exactly the ones the advisory under-counted (`PL-KYW3`).
    """
    ids = {"PL-001", "PL-8888", "PL-BBBB", "PL-CCCC"}
    _write(repo, "PL-001", touches="src/a.py", status="ready")
    for identifier in ("PL-8888", "PL-BBBB", "PL-CCCC"):
        _write(repo, identifier, touches="src/a.py", status="ready", body="caused by PL-001")
    _commit(repo, "PL-001, PL-8888, PL-BBBB, PL-CCCC: capture four findings")

    assert generator_check.citations(repo, ids)["PL-001"] == 3


def test_a_commit_leading_with_a_three_digit_id_attributes_what_it_created(repo: Path) -> None:
    """`creation_parents` reads the id off the subject and off the filename.

    Both readers used the same restated grammar, so neither could see one of the
    44 item files whose id is three digits, nor the 6 creation commits that lead
    with one - the whole of the store's early history spawned nothing.
    """
    _write(repo, "PL-001", touches="src/a.py", status="done")
    _commit(repo, "PL-001: capture")
    _write(repo, "PL-8888", touches="src/a.py", status="ready")
    _commit(repo, "PL-001: work that spawned a finding")

    parents = generator_check.creation_parents(repo)

    assert parents["PL-8888"] == {"PL-001"}
    assert parents["PL-001"] == set()
