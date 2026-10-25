"""Set up the blind generalist review passes a simulator branch owes, and print their briefs.

`PL-TCBJ` replayed reviews on ten merged simulator pull requests that later had
a defect filed against them, and `PL-TBQS` on twenty more. One generalist
reviewer, run blind, named about half of what was later filed, as many as a
three-specialist panel. So every simulator pull request gets one blind
generalist pass before it merges, and one that changes the model's code, its
parameter files or `docs/MODEL.md` gets a second (project owner, 2026-10-24,
ratified, `PL-TDV9`). Close-out step 9 in `.claude/skills/docket/modes/close-out.md`
says when the passes run and what happens to their findings.

**How many passes.** `docket.arming.blind_passes` decides it from the paths the
branch changes since it forked from the default branch: none for a branch that
changes no simulator path, two for one that changes a path under
`SECOND_PASS_PATHS`, and one otherwise. A test file under `tests/` that imports
the simulator on neither side of the change is a test of the tooling and owes
nothing, by `docket.arming.tests_the_tooling`, the rule `bin/docket arm` reads.
A test file that will not parse is counted as the simulator's, so a pass is
never skipped on a file nobody could read.

**What "blind" means here.** Each pass gets a directory of its own, outside the
repository, holding only `tree/`, the repository as committed at `HEAD`, and
`tree/REVIEW_DIFF.patch`, the branch's commit messages and its diff from the
fork. The tree comes from `git archive`, so it has no `.git` and the reviewer
cannot read the branch's history, another pass's findings or this session's
notes. `PL-TCBJ` discarded its first control run because its reviewers'
directories held the panel's findings and one reviewer read them. The tree is
what is committed, so commit the work before running this.

**The brief** is `BRIEF`, the generalist brief `PL-TCBJ` ran, as recorded in
that item under "The reviewer brief, as run". Each pass gets it with its own
directory and slug filled in.

Prints how many passes the branch owes, then one brief per pass, separated by
a rule. Exits 0 when it answered, whether or not a pass is owed, and 1 when the
default branch is unknown or git did not answer, since a count taken from a
partial read is not a count. `--count` prints only the number of passes owed.
"""

from __future__ import annotations

import argparse
import sys
import tarfile
import tempfile
from collections.abc import Sequence
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.arming import TESTS, blind_passes, is_test_file, tests_the_tooling  # noqa: E402
from docket.lines import split_lines  # noqa: E402
from docket.vcs import (  # noqa: E402
    GitUnanswered,
    changed_path_args,
    default_base,
    listed_paths,
    read_git,
    resolved,
)

#: The generalist reviewer's brief, as `PL-TCBJ` ran it for its clean control.
#: `{DIR}` is the pass's own directory and `{SLUG}` its short name.
BRIEF = """\
You are the single code reviewer for an open-source anesthesia simulator (inhaled-anesthetic uptake and distribution, with a Qt interface for learners). You are reviewing ONE pull request before it merges.

Your directory is {DIR}. It holds `tree/`, the repository exactly as it stands with this pull request applied, and `tree/REVIEW_DIFF.patch`, the pull request's commit message and diff. Read ONLY inside {DIR}. Do not read any other path on this machine, do not run git, and do not use the network. The project's standards are in `tree/CLAUDE.md`, `tree/.claude/rules/` and `tree/docs/MODEL.md`; read what you need. You may run read-only Python against `tree/` if it helps you check a claim (for example `cd {DIR}/tree && PYTHONPATH=src python3 -c '...'`), but write nothing inside `tree/`.

Your field: General review, with no specialty. Cover whatever matters most in this change: correctness of the model and its units, numerical and state behaviour, and what a clinician or learner sees on screen.

Review the whole diff from your field. Look for faults this change introduces or leaves in the code it adds: wrong results, unhandled cases, state that can go stale or partial, values a learner could misread, and refusals that fail to fire. Do not report style, naming, or documentation polish unless it could mislead a reader about a clinical value. Report only what you would defend to the author; it is better to report three real faults than eight weak ones.

Write at most eight findings, most severe first, in this exact form:

### F<n> [blocking|should-fix|optional] <file path relative to tree/> :: <function, class or symbol>
<two to four plain sentences: what goes wrong, under what input or sequence of actions, and what the user or the model gets as a result>

If you find nothing worth reporting, write the single line `NO FINDINGS`.

Save exactly that text to `{DIR}/findings-{SLUG}.md`, then return exactly the same text as your final answer, with nothing before or after it.
"""  # noqa: E501 - the brief as run, one paragraph per line

#: The file in each pass's tree that holds the branch's commit messages and diff.
DIFF_FILE = "REVIEW_DIFF.patch"


def is_tooling_test(path: str, fork: str, root: Path) -> bool:
    """Whether `path` is a test of the tooling on both sides of the change, which owes no pass.

    A side holding no such file reads as empty, as a test the branch added or
    deleted has nothing on one side. A side that will not parse is not read as
    the tooling's, so the change owes a pass.
    """
    if not path.startswith(TESTS) or not is_test_file(PurePosixPath(path).name):
        return False
    sides = []
    for rev in (fork, "HEAD"):
        held = read_git(["ls-tree", "-z", "--name-only", rev, "--", path], root)
        sides.append(read_git(["show", f"{rev}:{path}"], root) if held.strip("\0") else "")
    try:
        return tests_the_tooling(path, sides)
    except (SyntaxError, ValueError, RecursionError):
        return False


def passes_owed(root: Path, base: str) -> tuple[int, str]:
    """How many passes the branch owes, and the commit it forked from."""
    fork = read_git(["merge-base", base, "HEAD"], root).strip()
    if not fork:
        raise GitUnanswered(f"git gave no merge base of {base} and HEAD")
    changed = listed_paths(
        read_git(changed_path_args("diff", "--name-only", "-z", f"{fork}..HEAD", "--"), root)
    )
    tooling = [path for path in changed if is_tooling_test(path, fork, root)]
    return blind_passes(changed, tooling), fork


def review_diff(root: Path, fork: str) -> str:
    """The branch's commit messages, oldest first, and its diff from the fork."""
    messages = read_git(["log", "--reverse", "--format=commit %H%n%n%B", f"{fork}..HEAD"], root)
    diff = read_git(["diff", f"{fork}..HEAD"], root)
    return messages.rstrip() + "\n\n" + diff


def prepare(root: Path, fork: str, passes: int, out: Path) -> list[Path]:
    """Build one directory per pass under `out`, each holding only the tree and the diff."""
    archive = out / "head.tar"
    read_git(["archive", "--format=tar", "-o", str(archive), "HEAD"], root)
    diff = review_diff(root, fork)
    made = []
    for number in range(1, passes + 1):
        directory = out / f"pass-{number}"
        tree = directory / "tree"
        tree.mkdir(parents=True)
        with tarfile.open(archive) as bundle:
            bundle.extractall(tree, filter="data")
        (tree / DIFF_FILE).write_text(diff, encoding="utf-8")
        made.append(directory)
    archive.unlink()
    return made


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=split_lines(__doc__)[0])
    parser.add_argument("--count", action="store_true", help="print only the passes owed")
    parser.add_argument(
        "--out",
        type=Path,
        help="an empty directory outside the repository to build the passes in "
        "(default: a new temporary directory)",
    )
    args = parser.parse_args(argv)

    base = default_base(ROOT)
    if not resolved(base):
        print(
            "The default branch is unknown, so the branch's changes were not read.", file=sys.stderr
        )
        return 1
    try:
        passes, fork = passes_owed(ROOT, base)
        if args.count:
            print(passes)
            return 0
        if not passes:
            print(
                f"This branch changes no simulator path since {base}, so it owes no blind review."
            )
            return 0
        out = args.out or Path(tempfile.mkdtemp(prefix="blind-review-"))
        out.mkdir(parents=True, exist_ok=True)
        if any(out.iterdir()):
            print(f"{out} is not empty; give an empty directory.", file=sys.stderr)
            return 1
        if out.resolve().is_relative_to(ROOT):
            print(f"{out} is inside the repository; give a directory outside it.", file=sys.stderr)
            return 1
        directories = prepare(ROOT, fork, passes, out)
    except GitUnanswered as error:
        print(f"git did not answer: {error}", file=sys.stderr)
        return 1

    noun = "pass" if passes == 1 else "passes"
    print(
        f"This branch owes {passes} blind generalist review {noun}. Start one subagent per brief."
    )
    for number, directory in enumerate(directories, start=1):
        print(f"\n----- brief for pass {number} -----\n")
        print(BRIEF.format(DIR=directory, SLUG=f"pass-{number}"), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
