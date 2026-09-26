"""Refuse a pull request until every item it closes records its own number.

Which pull request closed an item is a fact the merge authors, and for a long
time nothing recorded it when the merge happened: a merge-time write cannot
land, because a push made with `GITHUB_TOKEN` starts no workflow (`PL-N5WZ`),
so `docket check` inferred the number afterwards from the squash subjects on
`main` and then from each item file's own history. Every new shape of history
misled that reading until it got an exception of its own - a UI-generated title
naming no id, a rider closed under another item's subject, a closure split from
its work, a rename, a graft boundary, a queue-only closure - and ten items in
three weeks were that one mechanism (`PL-HMZZ`).

So the number is recorded before the merge instead, by the branch that closes
the item: `bin/docket record N` writes `pr: N` onto every closure the branch
introduces while its pull request is open. This is the guarantee behind that
write, at the one point in the workflow that knows its own number. Every item
closed at `PR_HEAD` and not at `PR_BASE` must record `pr:` equal to
`PR_NUMBER`, or the run fails naming the ids and the command. It runs as a step
of the required `pr-title` job, which already checks out both trees and already
computes what the branch closes, so a merge cannot land between the closure's
push and the number's: the pull request stays red until the number lands, and
the closure still travels in the same commit as its work, which is what keeps
the `PL-D2GW` window shut.

Only `done` closures are held to it. A drop records no `pr`, as the store's
released drops never have, and `docket check` asks nothing of one.

`--discover` is what lets `make check` run this too, exactly as it lets
`pr_title_check.py` run: the number is read from the branch's own open pull
request, and every way that lookup can fail is a silent skip, never a failure
- no token, no network, no remote, a detached HEAD, no pull request open yet.
`make check` has to pass offline and on a branch nobody has opened anything
for. The lookup runs before the tree reads, so a branch with no pull request
pays one request and this speaks only when it has something to say. It reads
the committed tree, so a closure still in the working tree is not seen until
it is committed; the close-out mode runs `record N` before that commit, and
this is what confirms it afterwards.

**A tree git will not read is never compared as an empty one** (`PL-1PBV`),
for the reasons `pr_title_check.py` gives. With the number from `PR_NUMBER`
that exits 1, because the gate cannot answer and must not go green; under
`--discover` it exits 0 like every other way that path can fail, but prints
the reason rather than skipping in silence.

Standard library only, like every tool here, so it runs in a bare checkout.
The tree reads and the pull-request lookup are `pr_title_check.py`'s, imported
rather than spelled again, so the two checks cannot disagree about what a
branch closes.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from open_pull_requests import repo_slug  # noqa: E402
from pr_title_check import GitUnanswered, _branch, closed_items_at, open_pull_request  # noqa: E402


def closures(base: str, head: str) -> dict[str, str]:
    """The done items this branch introduces, as id to the `pr` each records.

    Done at `head` and not closed at `base`, which is `pr_title_check.closes`'s
    comparison narrowed to `done`: an item already closed on the base is
    somebody else's work arriving through a merge, and a number is not owed
    for it. Raises `GitUnanswered` where git cannot read either tree.
    """
    at_base = closed_items_at(base)
    return {
        identifier: item.pr
        for identifier, item in sorted(closed_items_at(head).items())
        if item.status == "done" and identifier not in at_base
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=os.environ.get("PR_BASE", "origin/main"))
    parser.add_argument("--head", default=os.environ.get("PR_HEAD", "HEAD"))
    parser.add_argument(
        "--discover",
        action="store_true",
        help="when PR_NUMBER is unset, read the number from this branch's open "
        "pull request; skip silently if it cannot be read (for `make check`)",
    )
    args = parser.parse_args()

    # Through the environment rather than argv, like the title: `${{ }}` pasted
    # into a `run:` line is the standard Actions script-injection hole, and
    # one spelling of that rule is easier to keep than two.
    given = os.environ.get("PR_NUMBER")
    discovered = given is None and args.discover
    if discovered:
        slug, branch = repo_slug(), _branch()
        found = open_pull_request(slug, branch) if slug and branch else None
        if found is None:
            return 0
        number = found[0]
    elif given is None:
        print("pr-record: PR_NUMBER is not set; nothing to check", file=sys.stderr)
        return 0
    elif not given.strip().isdigit() or int(given) < 1:
        print(
            f"pr-record: PR_NUMBER is {given!r}, which is not a pull request number",
            file=sys.stderr,
        )
        return 1
    else:
        number = int(given)

    try:
        closing = closures(args.base, args.head)
    except GitUnanswered as silence:
        print(
            f"pr-record: git could not read one of the trees at {args.base} and {args.head}, "
            f"so what this branch closes is unknown; not checked.\n"
            f"  {silence}\n"
            f"  Name refs git can resolve - `git fetch origin` where the base is missing.",
            file=sys.stderr,
        )
        return 0 if discovered else 1
    if not closing:
        print("pr-record: this branch closes no item; no number is owed")
        return 0

    owed = {identifier: pr for identifier, pr in closing.items() if pr != str(number)}
    if not owed:
        print(f"pr-record: {', '.join(closing)} record{'s' if len(closing) == 1 else ''} #{number}")
        return 0
    recorded = ", ".join(
        f"{identifier} (records `pr: {pr}`)" if pr else identifier
        for identifier, pr in owed.items()
    )
    print(
        f"pr-record: this branch closes {', '.join(closing)}, but #{number} is not recorded "
        f"on {recorded}.\n"
        f"  The pull request that closed an item is written on the branch, before the merge, "
        f"and nothing recovers it afterwards.\n"
        f"  Run `bin/docket record {number}` on this branch, commit what it wrote, and push.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
