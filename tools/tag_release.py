"""Tag the current release on the commit that cut it, where `origin` lacks the tag.

**The failure** (`PL-2FY6`). A release's tag has to sit on the squash-merge
commit that lands its cut on `main`, which does not exist until the release
pull request merges, and no session can push a tag ref (`PL-N936`). So every
cut ended with four commands for the project owner to paste, and an item
recording that they had, closed in a pull request of its own: fifteen of them
from v0.4.21 to v0.5.19.

**The rule is `bin/docket release`'s, not a new one.** The version is the one
`origin/main`'s version file declares, which `release` refuses to cut past
while it is untagged (`release.is_untagged`). Its cut is the commit that added its notes on
`origin/main`, compared with its first parent (`release.CUT_FLAGS`): the lookup
the pasted block made, asked through `vcs.find_cut`.

It changes nothing where `origin/main` adds no notes for the version, which is
a push that is not a cut, or where `origin` already holds the tag on the cut,
which is a second run. It **declines**, tagging nothing and exiting 1, where
git will not answer, where the clone is shallow and its oldest commit would
read as the cut, where the notes were added more than once so no one commit is
the cut, and where `origin` holds the tag on another commit, which a person
settles.

A tag this checkout holds and `origin` does not, a withdrawn tag at a re-used
number that `git fetch` never removes, is deleted before tagging, and only once
`origin` has answered that it lacks the tag (`PL-PNW6`).

Lists by default; `--apply` tags and pushes, then reads the tag back from
`origin` before saying so, because a session's tag push exits as if it landed
and lands nothing (`PL-N936`). `.github/workflows/tag-release.yml` runs it on
each push to `main` that changes a release's notes, with a token that may push
tags; run by hand from a clone, it pushes with that clone's credentials, which
is the project owner's to do. It fetches the default branch first, by the name
`vcs.default_branch` reads (`PL-9KLN`). Standard library only.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.lines import file_text, record_text, split_lines  # noqa: E402
from docket.release import notes_path, version_in  # noqa: E402
from docket.vcs import REMOTE, default_branch, find_cut, is_shallow  # noqa: E402

VERSION_FILE = "pyproject.toml"

#: `git ls-remote --exit-code`'s status where the remote answered and holds no
#: matching ref. Every other failure means it could not be asked, and a tag
#: deleted then would come back from the tag line as a different object.
ABSENT = 2


def _git(args: Sequence[str], root: Path) -> subprocess.CompletedProcess[str]:
    """Git's answer, decoded as written, so a raw `\\r` in a subject stays in it (`PL-0R4M`)."""
    done = subprocess.run(["git", *args], cwd=root, capture_output=True, check=False)
    return subprocess.CompletedProcess(
        done.args, done.returncode, record_text(done.stdout), record_text(done.stderr)
    )


def _failure(done: subprocess.CompletedProcess[str]) -> str:
    """The last line git wrote about a failure, or its exit status where it wrote none."""
    lines = split_lines((done.stderr or done.stdout).strip())
    return lines[-1] if lines else f"exit {done.returncode}"


def held_on(name: str, root: Path, remote: str = REMOTE) -> tuple[str, str]:
    """The commit `remote` holds tag `name` on, `""` where it holds none, and why it could not say.

    Both patterns are asked because `ls-remote` lists an annotated tag's peeled
    commit only under its own `^{}` name (git 2.43.0, measured 2026-09-30); a
    lightweight tag has no peeled line and names its commit directly.
    """
    ref = f"refs/tags/{name}"
    done = _git(["ls-remote", "--exit-code", remote, ref, f"{ref}^{{}}"], root)
    if done.returncode == ABSENT:
        return "", ""
    if done.returncode != 0:
        return "", f"`git ls-remote {remote}` failed: {_failure(done)}"
    named = {
        listed: commit
        for commit, _, listed in (line.partition("\t") for line in split_lines(done.stdout))
    }
    return named.get(f"{ref}^{{}}", named.get(ref, "")), ""


def run(root: Path, *, apply: bool, remote: str = REMOTE, branch: str | None = None) -> int:
    """Tag the version `remote/branch` declares on its cut where `remote` lacks it; the exit status.

    Everything is read from `remote/branch` once fetched, never from the
    working tree: run by hand from a checkout behind it, the tree still
    declares the release before. `branch` is the default branch unless named.
    """
    branch = branch or default_branch(root)
    ref = f"{remote}/{branch}"
    fetched = _git(["fetch", "--quiet", remote, branch], root)
    if fetched.returncode != 0:
        print(f"Declined: `git fetch {remote} {branch}` failed: {_failure(fetched)}")
        return 1
    try:
        version = version_in(file_text(_git(["show", f"{ref}:{VERSION_FILE}"], root).stdout))
    except ValueError as error:
        # Not TOML, which is not the same as declaring no version (`PL-3DD9`).
        print(f"Declined: {ref}:{VERSION_FILE} is not TOML ({error}), so no tag can be named.")
        return 1
    if not version:
        print(f"Declined: {ref} declares no version in {VERSION_FILE}, so no tag can be named.")
        return 1
    name = f"v{version}"
    if is_shallow(root) is not False:
        print(
            "Declined: this clone is shallow, or git will not say, and a shallow"
            " clone's oldest commit reads as adding every file."
        )
        return 1

    notes = notes_path(version)
    cut = find_cut(version, ref, root)
    if not cut.known:
        print(f"Declined: {cut.declined}.")
        return 1
    if not cut.commits:
        print(f"{ref} has no commit adding {notes}, so {name} is not cut there: nothing to tag.")
        return 0
    if not cut.commit:
        added = ", ".join(commit[:9] for commit in cut.commits)
        print(
            f"Declined: {ref} adds {notes} in {len(cut.commits)} commits ({added}),"
            f" so no one of them is {name}'s cut. Tag the one it shipped from by hand."
        )
        return 1

    held, declined = held_on(name, root, remote)
    if declined:
        print(f"Declined: {declined}.")
        return 1
    shown = _git(["log", "-1", "--format=%h %s", cut.commit], root).stdout.strip()
    if held == cut.commit:
        print(f"{name} is already on its cut, {shown}: nothing to do.")
        return 0
    if held:
        print(
            f"Declined: {remote} holds {name} on {held[:9]}, not on its cut, {shown}."
            " Which of the two is right is a person's call, so nothing is tagged."
        )
        return 1

    print(f"{name} goes on its cut, {shown}.")
    if not apply:
        print("Listed only: `--apply` tags it and pushes the tag.")
        return 0
    # Origin has answered that it lacks the tag, so one held here was withdrawn.
    if _git(["rev-parse", "--quiet", "--verify", f"refs/tags/{name}"], root).returncode == 0:
        _git(["tag", "-d", name], root)
    steps = (["tag", "-a", name, cut.commit, "-m", name], ["push", remote, f"refs/tags/{name}"])
    for step in steps:
        done = _git(step, root)
        if done.returncode != 0:
            print(f"Failed: `git {' '.join(step)}`: {_failure(done)}")
            return 1
    # The push's exit status proves nothing: a session's tag push exits as if
    # it landed and lands nothing (`PL-N936`), so ask `remote` what it holds.
    held, declined = held_on(name, root, remote)
    if declined:
        print(f"Pushed {name}, but whether {remote} took it could not be read: {declined}.")
        return 1
    if held != cut.commit:
        print(
            f"Failed: `git push` exited 0 and {remote} does not hold {name} on its cut."
            " A session's tag push is dropped without an error (PL-N936); the workflow's"
            " token, or the project owner's clone, is what lands one."
        )
        return 1
    print(f"Tagged {name} and pushed it to {remote}.")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0])
    parser.add_argument("--apply", action="store_true", help="tag the cut and push the tag")
    args = parser.parse_args(argv)
    return run(ROOT, apply=args.apply)


if __name__ == "__main__":
    sys.exit(main())
