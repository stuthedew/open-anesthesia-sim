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

Standard library only, like every tool here, so it runs in a bare checkout.
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=os.environ.get("PR_BASE", "origin/main"))
    parser.add_argument("--head", default=os.environ.get("PR_HEAD", "HEAD"))
    args = parser.parse_args()

    # The title comes through the environment, never through argv or a shell
    # interpolation: it is attacker-controlled text on a fork pull request, and
    # `${{ github.event.pull_request.title }}` pasted into a `run:` line is the
    # standard GitHub Actions script-injection hole.
    title = os.environ.get("PR_TITLE")
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

    print(
        f"pr-title: this branch closes {', '.join(closing)}, but the title does not "
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
