"""Tests for the one part of `vcs` that actually runs git.

Everything else in `test_vcs.py` injects a runner and asserts the filtering.
`GitRunner` is the plumbing itself - a memo over real subprocess results and a
`git cat-file --batch` standing in for `git show` - so it is proved against real
checkouts here, for the reason `test_vcs.py`'s own header gives: a stub would
test the stub.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from docket.vcs import GitRunner, RefWalk, _run_git, answered


def _git(root: Path, *args: str) -> str:
    done = subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)
    return done.stdout


def _repo(tmp_path: Path, name: str = "repo") -> Path:
    """A real checkout with one commit, built by running real git from `PATH`."""
    root = tmp_path / name
    root.mkdir(parents=True)
    _git(root, "init", "-q", ".")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "T")
    (root / "kept.md").write_text("one\ntwo\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base")
    return root


def _asked_and_ran(runner: GitRunner, subcommand: str) -> tuple[int, int]:
    for cost in runner.profile(RefWalk()).by_subcommand:
        if cost.subcommand == subcommand:
            return cost.asked, cost.ran
    return 0, 0


def test_a_blob_comes_back_exactly_as_git_show_gives_it(tmp_path: Path) -> None:
    """The substitution's whole claim: same object lookup, identical bytes.

    Asserted against `_run_git` rather than against a literal, so the test
    compares the two routes rather than one route against an expectation that
    could be wrong about both.
    """
    root = _repo(tmp_path)
    (root / "odd.md").write_bytes("a\r\nb\nunicode: é\n".encode())
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "odd")
    spec = "HEAD:odd.md"
    with GitRunner() as runner:
        assert runner(["show", spec], root) == _run_git(["show", spec], root)
        assert runner(["show", "HEAD:kept.md"], root) == _run_git(["show", "HEAD:kept.md"], root)


def test_a_path_the_revision_does_not_hold_answers_empty_as_git_show_does(tmp_path: Path) -> None:
    """`cat-file --batch` prints `<spec> missing` on *stdout* where `git show` exits 128.

    Without this the batch would hand every caller the string "HEAD:gone.md
    missing" as the file's content, and `parse_item` would read it as an item.
    `_run_git` turns `git show`'s non-zero exit into the empty string, so the
    batch has to produce the same empty string and every absent-blob path in
    this module keeps working untouched (`PL-0J9K`).
    """
    root = _repo(tmp_path)
    absent = "HEAD:no/such/file.md"
    assert _run_git(["show", absent], root) == ""
    with GitRunner() as runner:
        assert runner(["show", absent], root) == ""


def test_a_revision_naming_a_tree_falls_back_rather_than_returning_raw_bytes(
    tmp_path: Path,
) -> None:
    """`git show` formats a tree; `cat-file --batch` returns the raw object.

    The two disagree completely, so the batch declines anything that is not a
    blob and lets `git show` answer it.

    What this pins is the *answer*, not the guard that produces it: a tree's raw
    bytes carry 20-byte binary hashes and so fail to decode, which sends them
    down the same fallback even with the type check removed. The check is kept
    because a tree that happened to decode would be returned as content, and
    that is worth refusing rather than relying on an encoding accident.
    """
    root = _repo(tmp_path)
    (root / "sub").mkdir()
    (root / "sub" / "inner.md").write_text("x\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "tree")
    with GitRunner() as runner:
        assert runner(["show", "HEAD:sub"], root) == _run_git(["show", "HEAD:sub"], root)


def test_one_read_asked_twice_reaches_git_once(tmp_path: Path) -> None:
    """What the memo is for: every `merge-base` this module issues is asked three times."""
    root = _repo(tmp_path)
    with GitRunner() as runner:
        first = runner(["rev-parse", "HEAD"], root)
        assert runner(["rev-parse", "HEAD"], root) == first
        assert runner(["rev-parse", "HEAD"], root) == first
    assert _asked_and_ran(runner, "rev-parse") == (3, 1)


def test_the_memo_does_not_answer_from_before_a_fetch(tmp_path: Path) -> None:
    """The hazard `PL-MMVF` names, end to end against two real repositories.

    `bin/docket branch` fetches in-process, so a memo keyed on argv alone would
    answer a post-fetch read with the ref as it stood before the fetch - which
    is the one thing this cache must never do. Driven with a real remote that
    really moves, rather than by asserting the clearing rule against itself.
    """
    origin = _repo(tmp_path, "origin")
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, capture_output=True)
    head = ["rev-parse", "origin/HEAD"]
    with GitRunner() as runner:
        before = runner(head, clone)
        (origin / "kept.md").write_text("one\ntwo\nthree\n", encoding="utf-8")
        _git(origin, "commit", "-qam", "moved")
        runner(["fetch", "--quiet", "origin"], clone)
        after = runner(head, clone)
    assert before != after, "the memo answered a post-fetch read from before the fetch"
    assert after.strip() == _run_git(head, clone).strip()


def test_the_batch_process_does_not_outlive_the_runner(tmp_path: Path) -> None:
    """A `cat-file --batch` must be scoped to one command and closed.

    `close()` runs from `main`'s `finally`, so a command that raised still ends
    its batch; this pins that the process is genuinely gone rather than merely
    dereferenced.
    """
    root = _repo(tmp_path)
    runner = GitRunner()
    runner(["show", "HEAD:kept.md"], root)
    started = list(runner._batch.values())
    assert started, "the blob read did not start a batch process"
    runner.close()
    assert all(process.poll() is not None for process in started)
    runner.close()  # idempotent: `main` closes whether or not the command did


def test_a_runner_with_both_behaviours_off_still_answers_identically(tmp_path: Path) -> None:
    """The memo and the batch are optimisations, so switching them off changes nothing.

    This is what makes the profile's `asked` column a true before-count: it is
    the number of processes this command would have spawned without either.
    """
    root = _repo(tmp_path)
    plain = GitRunner(memoize=False, batch_blobs=False)
    with GitRunner() as tuned:
        for argv in (["show", "HEAD:kept.md"], ["rev-parse", "HEAD"], ["show", "HEAD:gone"]):
            assert tuned(argv, root) == plain(argv, root) == _run_git(argv, root)
    assert plain.profile(RefWalk()).processes == plain.profile(RefWalk()).asked


def test_a_missing_blob_does_not_cost_the_batch_for_the_rest_of_the_command(tmp_path: Path) -> None:
    """The `missing` line has to be *read*, not merely survived.

    Mutation-tested 2026-09-16: deleting the `missing` branch leaves every
    caller's answer correct, because an unreadable header drops the batch and
    `git show` answers instead. So correctness alone cannot tell the two apart -
    what it costs is the batch itself, for every later blob in the command, and
    an absent blob is a normal event here rather than a rare one. Asserted as
    the process count, which is the only place the difference shows.
    """
    root = _repo(tmp_path)
    with GitRunner() as runner:
        runner(["show", "HEAD:kept.md"], root)
        assert runner(["show", "HEAD:no/such/file.md"], root) == ""
        runner(["show", "HEAD:kept.md"], root)
        assert runner.profile(RefWalk()).processes == 1, (
            "the missing blob dropped the batch; later reads spawned `git show` again"
        )


def test_one_runner_asked_about_two_checkouts_does_not_confuse_them(tmp_path: Path) -> None:
    """The memo is keyed on the root as well as the argv.

    `rev-parse HEAD` is the same argv in every repository and means something
    different in each, so a key that dropped the root would answer the second
    checkout with the first one's commit. Nothing in this package asks two roots
    in one process today, which is exactly why the key is worth pinning: the
    defect would arrive silently with the first caller that did.
    """
    one = _repo(tmp_path, "one")
    two = _repo(tmp_path, "two")
    (two / "kept.md").write_text("different\n", encoding="utf-8")
    _git(two, "commit", "-qam", "diverge")
    with GitRunner() as runner:
        assert runner(["rev-parse", "HEAD"], one) != runner(["rev-parse", "HEAD"], two)
        assert runner(["show", "HEAD:kept.md"], one) != runner(["show", "HEAD:kept.md"], two)


def test_a_call_git_did_not_answer_is_put_to_git_again(tmp_path: Path) -> None:
    """A silence is not an answer, so the memo does not keep one (`PL-MM7F`).

    The memo exists so that the duplicate questions one command asks are paid
    for once - every `merge-base` this module issues is asked three times, and
    two of the three are removed by remembering (`PL-MMVF`). Storing a
    *failure* inverts that trade rather than extending it: the one fault is
    amortised across the whole command, and the thing that would otherwise make
    a transient fault self-correcting - the next caller asking git again - is
    exactly what the memo takes away.

    Asserted as the `ran` column rather than as the answer, because both calls
    come back a silence either way. Whether git was consulted the second time is
    the entire difference, and the profile is the only place it shows.
    """
    root = _repo(tmp_path)
    argv = ["diff", "--numstat", "HEAD", "refs/heads/gone", "--", "kept.md"]
    with GitRunner() as runner:
        assert not answered(runner(argv, root))
        assert not answered(runner(argv, root))

    assert _asked_and_ran(runner, "diff") == (2, 2), "the memo served a failure as an answer"


def test_a_fault_that_clears_does_not_outlive_itself(tmp_path: Path) -> None:
    """What the retry buys, driven against a fault that really clears.

    The fault `_superseded` meets is a ref deleted - or not yet written - by
    another session between the `for-each-ref` that lists it and the `diff` that
    reads it, so it is transient by nature. The count above pins that git is
    asked again; this pins that asking again is worth something, which the count
    on its own cannot say.
    """
    root = _repo(tmp_path)
    (root / "kept.md").write_text("one\ntwo\nthree\n", encoding="utf-8")
    _git(root, "commit", "-qam", "moved")
    argv = ["diff", "--numstat", "refs/heads/later", "HEAD", "--", "kept.md"]
    with GitRunner() as runner:
        assert not answered(runner(argv, root))
        _git(root, "branch", "later", "HEAD~1")
        assert runner(argv, root).split("\t")[:2] == ["1", "0"], (
            "the memo answered from before the ref existed"
        )
