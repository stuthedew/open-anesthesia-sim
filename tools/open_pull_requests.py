"""Print the branch name of every open pull request, and its number, one per line.

`bin/docket flight` reports an item as in flight from a branch that carries it,
and cannot tell a live session from a branch nobody will merge; it says so, and
leaves the age to separate them. One case is not the age's to decide. A branch
whose every item is already closed and which nobody has opened a pull request
for is *finished* work that has stalled - nothing is being worked there and
nothing is being reviewed - and until `PL-Q664` it was reported to every
session as "in flight ... do not start these again". `claude/hopeful-allen-tetrje`
sat that way with two closed items and ten item files existing nowhere else,
and surfaced three hours later only because the project owner asked whether the
feature had been built.

`docket` decides the first half from the branch's own item files. This is the
second half, and since `PL-7TVT` it is also the pull-request clause on every row
`flight` prints: a branch outlives its session, so an age alone reads a pull
request waiting on review as somebody's live work. The number follows the
branch name, so the row can say which pull request rather than send the reader
to look it up. It lives here rather than in `subprojects/docket/` for the
reason `main_ci_status.py` does: that package answers from a bare checkout with
no network and knows nothing about GitHub, and it should stay that way. Which
forge a project uses is not a fact about its queue, so the package asks a
command named in `docket.toml` and this repository points that setting here.

**`--newest BRANCH BASE` asks what became of a branch's newest pull request**,
for `docket branch` and `docket arm` through `newest_pull_request_command`
(`PL-8BR0`). A squash lands none of a branch's commits by hash, and a branch
that carried only item files leaves no content `docket` may take for merge
evidence (`PL-JBRC`), so a merged pull request read as work still to merge and
the next capture on its branch landed nowhere. It prints `NUMBER STATE HEAD` -
`STATE` one of `open`, `merged` or `closed`, `HEAD` the commit the forge names
as the pull request's head, which GitHub freezes when it closes - or nothing
where no pull request was ever opened from the branch. The listing is
`left_behind_check.py`'s: every state, that head, that base, newest first.

**The contract is the exit status, and it is the whole point of the script.**
Exit 0 means the forge was asked and these - possibly none - are the branches
with something open. Exit 1 means it could not be asked, and stdout is then
empty. A caller that conflated the two would read "could not look" as "nothing
is open", which is exactly the confident wrong answer this repository's
apparatus floor refuses: `docket flight` says "every item closed" alone when
this exits 1, and adds "and no pull request is open" only when it exits 0.

Standard library only, like every tool here, so it runs in a bare checkout.
`urllib` is in that library; the token is read from the environment and never
printed. `pr_title_check.py` shares the request code below, and both questions
here make it through `_listing`, which is what keeps one spelling of the token,
the timeout and the failure rule rather than several.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.vcs import github_slug, github_token  # noqa: E402

#: Where the lookup goes. Named here rather than inline so a test can point it
#: somewhere that is not the network.
GITHUB_API = "https://api.github.com"

#: Seconds to wait. Short on purpose: every caller has an answer without this
#: one and is only sharpening it, so a slow forge must cost seconds rather than
#: hold up a check or a report. A timeout is a failure like any other.
LOOKUP_TIMEOUT = 10.0

#: How many open pull requests one listing may describe. GitHub's maximum, and
#: a full page is treated as a failure below rather than as a complete answer.
PAGE = 100


@dataclass(frozen=True)
class PullRequest:
    """One open pull request: its number, its title, the branch it is for, and its base.

    `base` is empty where GitHub's answer carried none; the branch sweep, the
    one caller that reads it, declines on that rather than read it as no base.
    """

    number: int
    title: str
    head: str
    base: str = ""


@dataclass(frozen=True)
class NewestPullRequest:
    """The newest pull request from one branch into one base, and what became of it.

    `state` is `merged` where the forge records a merge and otherwise its own
    `open` or `closed`. `head` is the commit the forge names as the pull
    request's head: frozen when it closes, so a merged one names the commit
    its merge took whatever the branch gained since (checked on `#793`).
    """

    number: int
    state: str
    head: str


def _git(args: list[str]) -> str:
    """Run git from the repository root, returning empty output rather than raising."""
    try:
        result = subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=30, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout if result.returncode == 0 else ""


def repo_slug() -> str | None:
    """`owner/name` for `origin`, or None when it cannot be read as GitHub's.

    Parsed by `docket`'s one reading, `vcs.github_slug`, which a token-bearing
    URL does not defeat (`PL-2TV9`).
    """
    return github_slug(_git(["remote", "get-url", "origin"]))


def _listing(slug: str, query: dict[str, str | int]) -> list[object] | None:
    """One page of `slug`'s pull requests as `query` narrows it, or None where it could not ask.

    The one request every question here makes. None covers every reason there
    is no answer, and they are deliberately not told apart: no token, no
    network, a proxy refusing, a rate limit, a repository this token cannot
    see, or a body that is not a JSON list. Every caller does the same thing
    with all of them - says it could not look - so separating them would buy a
    message nobody can act on differently.
    """
    token = github_token()
    if not token:
        return None
    request = urllib.request.Request(
        f"{GITHUB_API}/repos/{slug}/pulls?{urllib.parse.urlencode(query)}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "open_pull_requests",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=LOOKUP_TIMEOUT) as response:
            payload = json.load(response)
    except (OSError, ValueError):
        # `URLError` and `HTTPError` are both `OSError`; a body that is not
        # JSON raises `ValueError`. Nothing else should escape a GET.
        return None
    return payload if isinstance(payload, list) else None


def open_pull_requests(slug: str, *, head: str | None = None) -> tuple[PullRequest, ...] | None:
    """The open pull requests on `slug`, or None when the forge could not be asked.

    `head` narrows the listing to one branch, which is what a caller holding a
    branch already wants and costs the same single request. `_listing` says
    what None covers.

    **A full page is one of those reasons.** A listing that comes back at the
    per-page maximum may have more behind it, and the caller's question is
    whether a *particular* branch is absent - which a truncated listing cannot
    answer, while looking exactly like an answer. Declining is the one reading
    that is never wrong. It cannot fire on a `head` listing, which asks about
    one branch and is complete at one entry.
    """
    query: dict[str, str | int] = {"state": "open", "per_page": 1 if head else PAGE}
    if head:
        query["head"] = f"{slug.split('/')[0]}:{head}"
    payload = _listing(slug, query)
    if payload is None:
        return None
    if head is None and len(payload) >= PAGE:
        return None
    found: list[PullRequest] = []
    for entry in payload:
        if not isinstance(entry, dict):
            return None
        number, title = entry.get("number"), entry.get("title")
        branch = entry.get("head", {}).get("ref") if isinstance(entry.get("head"), dict) else None
        if not isinstance(number, int) or not isinstance(title, str) or not isinstance(branch, str):
            return None
        target = entry.get("base", {}).get("ref") if isinstance(entry.get("base"), dict) else None
        base = target if isinstance(target, str) else ""
        found.append(PullRequest(number=number, title=title, head=branch, base=base))
    return tuple(found)


def newest_pull_request(slug: str, branch: str, base: str) -> tuple[NewestPullRequest, ...] | None:
    """The newest pull request from `branch` into `base`: one, `()` where none was opened, or None.

    None is `_listing`'s refusal, and an entry this cannot read is one too: a
    number that is not one, a state that is neither `open` nor `closed`, a
    `merged_at` that is neither null nor a time - absent included, since a
    merge read as "not merged" is the answer this exists to correct - or no
    head commit. `()` is an answer: the forge was asked, and nothing was ever
    opened from the branch.
    """
    query: dict[str, str | int] = {
        "state": "all",
        "head": f"{slug.split('/')[0]}:{branch}",
        "base": base,
        "sort": "created",
        "direction": "desc",
        "per_page": 1,
    }
    payload = _listing(slug, query)
    if payload is None:
        return None
    if not payload:
        return ()
    entry = payload[0]
    if not isinstance(entry, dict):
        return None
    number, state = entry.get("number"), entry.get("state")
    merged_at = entry.get("merged_at", False)
    head = entry.get("head")
    sha = head.get("sha") if isinstance(head, dict) else None
    if (
        not isinstance(number, int)
        or state not in ("open", "closed")
        or not (merged_at is None or isinstance(merged_at, str))
        or not isinstance(sha, str)
        or not sha
    ):
        return None
    merged = "merged" if merged_at is not None else state
    return (NewestPullRequest(number=number, state=merged, head=sha),)


def main(argv: Sequence[str] = ()) -> int:
    parser = argparse.ArgumentParser(
        description="Print every open pull request's branch and number, one per line."
    )
    parser.add_argument(
        "--newest",
        nargs=2,
        metavar=("BRANCH", "BASE"),
        help="print `NUMBER STATE HEAD` for the newest pull request from BRANCH into BASE "
        "instead, or nothing where none was ever opened",
    )
    args = parser.parse_args(list(argv))
    slug = repo_slug()
    if args.newest is not None:
        branch, base = args.newest
        newest = newest_pull_request(slug, branch, base) if slug else None
        if newest is None:
            return 1
        for pull in newest:
            print(f"{pull.number} {pull.state} {pull.head}")
        return 0
    found = open_pull_requests(slug) if slug else None
    if found is None:
        return 1
    for pull_request in found:
        print(f"{pull_request.head} {pull_request.number}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
