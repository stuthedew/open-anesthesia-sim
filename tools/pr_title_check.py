"""Refuse a pull request whose title does not lead with the ids it closes.

A squash merge takes its subject from the pull request title, and that subject
is what reaches the default branch. `docket check` reads it to recover which
pull request closed an item, and `docket flight` reads it to know what is in
flight, so a title that names no id is not a style lapse - it destroys
provenance that cannot be reconstructed from anywhere else.

`#220` is the case that produced this check. It was created from the Claude
Code UI, whose generated title named none of the three items it closed. The
squash landed that title verbatim, `docket check` had nothing to recover from,
and `main` went red with three errors that blocked the v0.3.0 release until the
numbers were read off the GitHub UI by hand (`PL-2XTF`).

`PL-2XTF`'s other half made the recovery robust, by falling back to the item's
own file history. This is the half that stops the damage instead of repairing
it: the title is checked while it can still be edited, which is the only moment
anyone can fix it. Both are wanted. Recovery alone leaves the wrong subject on
`main` forever; this check alone leaks whenever a merger retypes the subject in
the squash dialog, which GitHub allows and this cannot see.

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

from docket.model import CLOSED_STATUSES, parse_item  # noqa: E402
from docket.vcs import ITEM_FILE_RE, leading_ids  # noqa: E402

from open_pull_requests import open_pull_requests, repo_slug  # noqa: E402

ITEMS_DIR = "docs/items"


def _git(args: list[str]) -> str:
    """Run git, returning empty output rather than raising.

    Unlike `docket.vcs`, a failure here is not a normal condition - this runs
    in CI against a full checkout - but the empty answer still reads correctly
    at every call site: an unreadable tree closes nothing.
    """
    try:
        result = subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=30, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout if result.returncode == 0 else ""


def _closed_ids_at(ref: str) -> dict[str, str]:
    """Every item closed in that tree, as id to file name."""
    closed: dict[str, str] = {}
    listing = _git(["ls-tree", "-r", "--name-only", ref, "--", ITEMS_DIR])
    for path in listing.splitlines():
        name = path.strip().split("/")[-1]
        if not ITEM_FILE_RE.match(name):
            continue
        text = _git(["show", f"{ref}:{path.strip()}"])
        if not text:
            continue
        item = parse_item(text, name)
        if item.status in CLOSED_STATUSES and item.identifier:
            closed[item.identifier] = name
    return closed


def closes(base: str, head: str) -> list[str]:
    """The ids this branch closes: closed at `head` and not already at `base`.

    Comparing both ends rather than reading the diff is what keeps a rebase or
    a merge of the base from being read as a closure. An item already closed on
    `base` is somebody else's work arriving through the merge, and a title is
    not owed for it.
    """
    return sorted(set(_closed_ids_at(head)) - set(_closed_ids_at(base)))


def _branch() -> str | None:
    """The current branch name, or None on a detached HEAD."""
    name = _git(["rev-parse", "--abbrev-ref", "HEAD"]).strip()
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
    parser.add_argument("--base", default=os.environ.get("PR_BASE", "origin/main"))
    parser.add_argument("--head", default=os.environ.get("PR_HEAD", "HEAD"))
    parser.add_argument(
        "--discover",
        action="store_true",
        help="when PR_TITLE is unset, read the title from this branch's open "
        "pull request; skip silently if it cannot be read (for `make check`)",
    )
    args = parser.parse_args()

    # The title comes through the environment, never through argv or a shell
    # interpolation: it is attacker-controlled text on a fork pull request, and
    # `${{ github.event.pull_request.title }}` pasted into a `run:` line is the
    # standard GitHub Actions script-injection hole.
    title = os.environ.get("PR_TITLE")
    number = None
    if title is None and args.discover:
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

    closing = closes(args.base, args.head)
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
    print(
        f"pr-title: this branch closes {', '.join(closing)}, but {which} does not "
        f"lead with {', '.join(missing)}.\n"
        f"  title: {title}\n"
        f"  The squash-merge subject is taken from this title, and it is what "
        f"`docket check` reads to recover which pull request closed an item.\n"
        f"  Rename the pull request to lead with the ids, comma-separated:\n"
        f"    {', '.join(closing)}: <what it does>",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
