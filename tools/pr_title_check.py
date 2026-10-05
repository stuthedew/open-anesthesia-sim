"""Refuse a pull request whose title does not lead with the ids it closes.

A squash merge takes its subject from the pull request title, and that subject
is what reaches the default branch: the one line of `main`'s history that says
which items a change was about, read by `git log --oneline`, by `docket trend`
and by `filed_with_work`, and the line `CLAUDE.md` asks every commit subject to
open with. A title naming no id lands a subject that says nothing, and a
subject cannot be edited once it has landed.

It is not what provenance rests on, since `PL-HMZZ`. Which pull request closed
an item is recorded on the item before the merge, by `bin/docket record N` on
the closing branch, and `pr_record_check.py` beside this script refuses the
pull request until every closure carries its number; nothing reads a subject
to recover a number any more. This check once carried that weight - `#220`
closed three items under a UI-generated title naming none of them, the squash
landed it verbatim, and `main` went red until the numbers were read off the
GitHub UI by hand (`PL-2XTF`) - and its docstring went on promising provenance
protection after two things had quietly limited it: a merger retyping the
subject in the squash dialog, which GitHub allows and this cannot see, and
auto-merge freezing the subject at the moment it is armed, so a rename made to
satisfy this very check never landed (`PL-M7W1`, on `#868`). Both now cost a
`git log` reader a stale line and nothing else, which is the claim this
docstring is kept to.

Deliberately not checked: whether the title says anything *else* useful, and
whether ids appear that the branch does not close. A pull request may lead with
an id it merely captures, and judging prose is not this tool's business.

`--discover` is what lets `make check` run this too (`PL-J3BB`). In CI the
title arrives in `PR_TITLE`; locally nothing sets it, and until that flag
existed this was the one gate a session could not run before pushing - so its
failures were always found by CI. The failure is not forgetfulness but
sequencing: the title is checked against *what the branch closes*, and a branch
closes more items as it goes, so a title that was right when the pull request
opened stops being right the moment the next item closes on it. Observed on
`#256` and, three times across two occurrences, on `#339`.

With `--discover` the title is read from the branch's own open pull request.
**Every way that can fail is a silent skip, never a failure**: no token, no
network, no remote, a detached HEAD, no pull request open yet. `make check`
has to pass offline and on a branch nobody has opened anything for, and a gate
that fails when it cannot look would be worse than the gap it closes. The
lookup runs *before* `closes()` deliberately - it is one request against
several hundred `git show` calls, so a branch with no pull request pays
milliseconds and this check speaks only when it has something to say.

**Under `--discover` the head is the working tree, not `HEAD`** (`PL-T8PT`,
project owner, 2026-09-27, ratified, over a pre-push hook and over printing the
ids with no verdict). `make check` runs before the commit it vouches for, and
the close-out mode writes a closure in the same commit as its work, so read at
`HEAD` a closure was always one commit short: the run passed, and `pr-title`
failed on the same tree one push later (`#499`, five drops and a close). Read
from disk it is the tree about to be committed, and the set `bin/docket record
N` writes onto. The cost is that the local run answers about the checkout
rather than about what is pushed, so a closure never committed is reported
here and never reaches CI - a true statement about the checkout, and the
failure says where it read. An explicit `--head`, or `PR_HEAD`, still names a
ref, and CI passes no `--discover`, so the merge gate's answer is unchanged.

**A tree git will not read is never compared as an empty one** (`PL-1PBV`).
What a branch closes is the difference between the items closed at two refs,
so an unreadable head read as empty closed nothing and passed any title, and
an unreadable base read as empty made every item the head holds closed this
branch's. Either way the run now says it was not checked. With the title from
`PR_TITLE` that exits 1: `pr-title.yml` checks out both trees on purpose, so
failing to read one there means the gate cannot answer, and it must not go
green. Under `--discover` it exits 0 like every other way that path can fail,
but it prints the reason rather than skipping in silence, because by then there
was a title to check.

Standard library only, like every tool here, so it runs in a bare checkout.
The request itself is `open_pull_requests.py`'s, which `docket flight` also
asks; sharing it keeps one spelling of the token, the timeout and the rule that
every failure is a skip, rather than two that can drift apart.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.lines import file_text, record_text, split_lines  # noqa: E402
from docket.model import CLOSED_STATUSES, Item, parse_item  # noqa: E402
from docket.store import read_items  # noqa: E402
from docket.vcs import ITEM_FILE_RE, default_base, leading_ids  # noqa: E402

from open_pull_requests import open_pull_requests, repo_slug  # noqa: E402

ITEMS_DIR = "docs/items"

#: The head `--discover` reads where no ref is named (`PL-T8PT`): the item files
#: on disk, committed or not. Git refuses a ref name with a space in it, so no
#: ref can be taken for this.
WORKING_TREE = "the working tree"


class GitUnanswered(Exception):
    """A tree read the verdict rests on that did not answer, and the reason.

    Git's reason for a ref, and the disk's for `WORKING_TREE`, which declines
    the same way rather than reading as a tree that closes nothing.
    """


def _git(args: list[str]) -> str:
    """Git's standard output, or `GitUnanswered` where git did not answer.

    Raised rather than returned, because no caller has an answer to give in
    its place. This used to return the empty string on any failure, on the
    ground that "an unreadable tree closes nothing" - which is the claim
    `PL-9RFP` disproved for `verify`, and it was wrong here in both directions
    (`PL-1PBV`, and the module docstring). Any non-zero exit is a failure:
    `ls-tree`, `show` and `rev-parse --abbrev-ref` have no "no" to give, and
    exit 0 whenever they answered at all.

    Decoded as written, so a raw `\\r` in a record stays in it; the one blob
    read translates its own (`PL-0R4M`).
    """
    try:
        result = subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, timeout=30, check=False
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise GitUnanswered(f"`git {args[0]}` could not run: {error}") from error
    if result.returncode != 0:
        stderr = record_text(result.stderr)
        said = next((line.strip() for line in split_lines(stderr) if line.strip()), "")
        raise GitUnanswered(
            f"`git {args[0]}` exited {result.returncode}: {said or 'with nothing on stderr'}"
        )
    return record_text(result.stdout)


def closed_items_at(ref: str) -> dict[str, Item]:
    """Every item closed in that tree, by id, or `GitUnanswered`.

    `ref` is a git ref, or `WORKING_TREE` for the files on disk.
    `pr_record_check.py` reads it too, for what each closure records, so the
    two checks cannot disagree about what a tree holds closed.
    """
    if ref == WORKING_TREE:
        return _closed_on_disk()
    closed: dict[str, Item] = {}
    listing = _git(["ls-tree", "-r", "--name-only", ref, "--", ITEMS_DIR])
    for path in split_lines(listing):
        name = path.strip().split("/")[-1]
        if not ITEM_FILE_RE.match(name):
            continue
        text = file_text(_git(["show", f"{ref}:{path.strip()}"]))
        item = parse_item(text, name)
        if item.status in CLOSED_STATUSES and item.identifier:
            closed[item.identifier] = item
    return closed


def _closed_on_disk() -> dict[str, Item]:
    """Every item closed in the files on disk, by id, or `GitUnanswered`.

    Read through the store's own reader, so the files counted are the ones
    `bin/docket record N` writes onto. A missing directory declines rather than
    reading as a tree that closes nothing, as a ref git cannot read does
    (`PL-1PBV`), and so does a file that cannot be read.
    """
    directory = ROOT / ITEMS_DIR
    if not directory.is_dir():
        raise GitUnanswered(f"`{ITEMS_DIR}` is not on disk in {ROOT}")
    try:
        items = read_items(directory)
    except (OSError, UnicodeDecodeError) as error:
        raise GitUnanswered(f"`{ITEMS_DIR}` could not be read from disk: {error}") from error
    return {
        item.identifier: item
        for item in items
        if item.status in CLOSED_STATUSES and item.identifier
    }


def closes(base: str, head: str) -> list[str]:
    """The ids this branch closes: closed at `head` and not already at `base`.

    Comparing both ends rather than reading the diff is what keeps a rebase or
    a merge of the base from being read as a closure. An item already closed on
    `base` is somebody else's work arriving through the merge, and a title is
    not owed for it.

    It also means neither end may be missing: raises `GitUnanswered` where git
    cannot read either tree, rather than comparing against nothing.
    """
    return sorted(set(closed_items_at(head)) - set(closed_items_at(base)))


def _branch() -> str | None:
    """The current branch name, or None on a detached HEAD or where git cannot say."""
    try:
        name = _git(["rev-parse", "--abbrev-ref", "HEAD"]).strip()
    except GitUnanswered:
        # A skip under `--discover`, the only caller, like every other way the
        # lookup can fail.
        return None
    return name if name and name != "HEAD" else None


def open_pull_request(slug: str, branch: str) -> tuple[int, str] | None:
    """The open pull request for `branch`, as (number, title), or None.

    None covers every reason there is no answer - no token, no network, a
    forge that refused, or simply no pull request open - and they are
    deliberately not told apart, because the caller skips on all of them. The
    one thing that must not happen is a missing answer reading as "checked,
    and fine", which it cannot here: a skip prints nothing and returns 0 rather
    than passing the check.

    A thin call rather than its own request since `PL-Q664`, which gave
    `docket flight` the same question about a different branch.
    """
    found = open_pull_requests(slug, head=branch)
    if not found:
        return None
    return found[0].number, found[0].title


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    # `docket`'s own answer where CI passes no `PR_BASE`, so a clone whose
    # default is `master` compares against it rather than an `origin/main`
    # that does not resolve there (`PL-GNCB`).
    parser.add_argument("--base", default=os.environ.get("PR_BASE") or default_base(ROOT))
    parser.add_argument("--head", default=os.environ.get("PR_HEAD"))
    parser.add_argument(
        "--discover",
        action="store_true",
        help="when PR_TITLE is unset, read the title from this branch's open "
        "pull request; skip silently if it cannot be read; with no --head, read "
        "what the branch closes from the working tree (for `make check`)",
    )
    args = parser.parse_args()
    # A ref where one is named, by `--head` or by CI's `PR_HEAD`; otherwise the
    # local run reads the tree it is about to commit (`PL-T8PT`).
    head = args.head or (WORKING_TREE if args.discover else "HEAD")

    # The title comes through the environment, never through argv or a shell
    # interpolation: it is attacker-controlled text on a fork pull request, and
    # `${{ github.event.pull_request.title }}` pasted into a `run:` line is the
    # standard GitHub Actions script-injection hole.
    title = os.environ.get("PR_TITLE")
    discovered = title is None and args.discover
    number = None
    if discovered:
        # Before `closes()`, which costs a `git show` per item file at both
        # ends of the range. A branch with nothing open pays one request.
        slug, branch = repo_slug(), _branch()
        found = open_pull_request(slug, branch) if slug and branch else None
        if found is None:
            return 0
        number, title = found
    if title is None:
        print("pr-title: PR_TITLE is not set; nothing to check", file=sys.stderr)
        return 0

    try:
        closing = closes(args.base, head)
    except GitUnanswered as silence:
        print(
            f"pr-title: one of the trees at {args.base} and {head} could not be read, "
            f"so what this branch closes is unknown; not checked.\n"
            f"  {silence}\n"
            f"  Name refs git can resolve - `git fetch origin` where the base is missing.",
            file=sys.stderr,
        )
        # A skip under `--discover`, as the module docstring says; the gate
        # that was handed a title fails rather than certify it unread.
        return 0 if discovered else 1
    if not closing:
        print("pr-title: this branch closes no item; no id is owed")
        return 0

    led = {identifier.upper() for identifier in leading_ids(title)}
    missing = [identifier for identifier in closing if identifier.upper() not in led]
    if not missing:
        print(f"pr-title: leads with {', '.join(closing)}")
        return 0

    # The number is named where it is known, because the remedy is a rename of
    # one specific pull request and a session may have several branches behind
    # it. In CI the title arrives without one and the run is already on the
    # pull request it belongs to.
    which = f"#{number}'s title" if number is not None else "the title"
    # Where it read, since under `--discover` that is the checkout rather than
    # anything pushed yet.
    closer = "this checkout" if head == WORKING_TREE else "this branch"
    where = " in its working tree" if head == WORKING_TREE else ""
    print(
        f"pr-title: {closer} closes {', '.join(closing)}{where}, but {which} does not "
        f"lead with {', '.join(missing)}.\n"
        f"  title: {title}\n"
        f"  The squash-merge subject is taken from this title, and it is the one line "
        f"of `main`'s history that says which items this change was about.\n"
        f"  Rename the pull request to lead with the ids, comma-separated:\n"
        f"    {', '.join(closing)}: <what it does>",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
