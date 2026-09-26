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

**The contract is the exit status, and it is the whole point of the script.**
Exit 0 means the forge was asked and these - possibly none - are the branches
with something open. Exit 1 means it could not be asked, and stdout is then
empty. A caller that conflated the two would read "could not look" as "nothing
is open", which is exactly the confident wrong answer this repository's
apparatus floor refuses: `docket flight` says "every item closed" alone when
this exits 1, and adds "and no pull request is open" only when it exits 0.

Standard library only, like every tool here, so it runs in a bare checkout.
`urllib` is in that library; the token is read from the environment and never
printed. `pr_title_check.py` shares the request code below, which is what keeps
one spelling of the token, the timeout and the failure rule rather than two.
"""

from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
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
    """One open pull request: its number, its title, and the branch it is for."""

    number: int
    title: str
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


def open_pull_requests(slug: str, *, head: str | None = None) -> tuple[PullRequest, ...] | None:
    """The open pull requests on `slug`, or None when the forge could not be asked.

    `head` narrows the listing to one branch, which is what a caller holding a
    branch already wants and costs the same single request.

    None covers every reason there is no answer, and they are deliberately not
    told apart: no token, no network, a proxy refusing, a rate limit, a
    repository this token cannot see, or a malformed body. Every caller does
    the same thing with all of them - says it could not look - so separating
    them would buy a message nobody can act on differently.

    **A full page is one of those reasons.** A listing that comes back at the
    per-page maximum may have more behind it, and the caller's question is
    whether a *particular* branch is absent - which a truncated listing cannot
    answer, while looking exactly like an answer. Declining is the one reading
    that is never wrong. It cannot fire on a `head` listing, which asks about
    one branch and is complete at one entry.
    """
    token = github_token()
    if not token:
        return None
    query: dict[str, str | int] = {"state": "open", "per_page": 1 if head else PAGE}
    if head:
        query["head"] = f"{slug.split('/')[0]}:{head}"
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
    if not isinstance(payload, list):
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
        found.append(PullRequest(number=number, title=title, head=branch))
    return tuple(found)


def main() -> int:
    slug = repo_slug()
    found = open_pull_requests(slug) if slug else None
    if found is None:
        return 1
    for pull_request in found:
        print(f"{pull_request.head} {pull_request.number}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
