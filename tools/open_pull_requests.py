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
`left_behind_check.py`'s too, read through `newest` here: every state, that
head, that base, newest first.

**The contract is the exit status, and it is the whole point of the script.**
Exit 0 means the forge was asked and these - possibly none - are the branches
with something open. Exit 1 means it could not be asked, and stdout is then
empty. A caller that conflated the two would read "could not look" as "nothing
is open", which is exactly the confident wrong answer this repository's
apparatus floor refuses: `docket flight` says "every item closed" alone when
this exits 1, and adds "and no pull request is open" only when it exits 0.

**One reading of each pull-request fact, for every tool that asks** (`PL-351H`).
`left_behind_check.py` asked for the newest pull request with its own request
and its own parse, and read an entry carrying no `merged_at` as "closed without
merging", the answer `newest` refuses; `update_armed.py` paged the open listing
where this declined on a full page. So the request is `fetch`, which names why
it failed for the caller that must say so; the listing is `every_page`; and the
newest pull request is `newest`. Each tool reads its own fields off an entry,
and none spells the query, the paging or the merge test again.

Standard library only, like every tool here, so it runs in a bare checkout.
`urllib` is in that library; the token is read from the environment and never
printed. `pr_title_check.py` shares the request code below, and every question
here makes it through `fetch`, which is what keeps one spelling of the token,
the timeout and the failure rule rather than several.
"""

from __future__ import annotations

import argparse
import http.client
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.vcs import (  # noqa: E402
    PULL_CLOSED,
    PULL_MERGED,
    PULL_OPEN,
    REMOTE,
    NewestPullRequest,
    call_git,
    github_slug,
    github_token,
)

#: Where the lookup goes. Named here rather than inline so a test can point it
#: somewhere that is not the network. Every tool that asks GitHub's REST API
#: reads its host from here (`PL-LGDV`).
GITHUB_API = "https://api.github.com"

#: The REST API version every request names in `X-GitHub-Api-Version`, so that
#: GitHub answers in the shape this code reads even after its default moves.
API_VERSION = "2022-11-28"

#: Seconds to wait. Short on purpose: every caller has an answer without this
#: one and is only sharpening it, so a slow forge must cost seconds rather than
#: hold up a check or a report. A timeout is a failure like any other.
LOOKUP_TIMEOUT = 10.0

#: How many pull requests one page of a listing holds: GitHub's maximum.
PAGE = 100

#: Why a listing could not be read, opening `ListingFailed`'s message so a reader
#: and a test can tell them apart without parsing the rest of the sentence.
NO_NETWORK = "no network"
NO_PERMISSION = "no permission"
UNREADABLE_ANSWER = "unreadable"

#: GitHub's answers that refuse this token rather than fail to answer.
_REFUSAL_CODES = (401, 403, 404, 429)

Query = dict[str, str | int]


class ListingFailed(Exception):
    """GitHub could not be asked, or its answer could not be read; `kind` says which."""

    def __init__(self, kind: str, detail: str) -> None:
        super().__init__(f"{kind}: {detail}")
        self.kind = kind


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


def _git(args: list[str], root: Path) -> str:
    """Git's answer in `root`, by `vcs.call_git`, never raising.

    Empty where git said no or gave no answer, which `answered` tells apart for
    a caller that must. Decoded as written, so a raw `\\r` in a record stays in
    it (`PL-0R4M`).
    """
    return call_git(args, root).answer


def origin_url(root: Path = ROOT) -> str:
    """`origin`'s URL in `root`, or "" where git could not name one.

    The one read of the remote's URL, which `repo_slug` parses and
    `headless_worker` clones from (`PL-H5T9`). Git is asked through `_git`.
    """
    return _git(["remote", "get-url", REMOTE], root).strip()


def repo_slug(root: Path = ROOT) -> str | None:
    """`owner/name` for `origin` in `root`, or None when it cannot be read as GitHub's.

    The one reading of which GitHub repository a checkout is, for every tool
    that asks GitHub about it (`PL-LGDV`). Git is asked through `_git`, and its
    answer is parsed by `docket`'s one reading, `vcs.github_slug`, which a
    token-bearing URL does not defeat (`PL-2TV9`). A remote git could not name
    reads as no GitHub repository, as an empty URL does.
    """
    return github_slug(origin_url(root))


def api_request(
    url: str,
    *,
    agent: str,
    token: str | None = None,
    method: str = "GET",
    data: bytes | None = None,
) -> urllib.request.Request:
    """A request to GitHub's REST API at `url`, with the headers every call here sends.

    The one spelling of what GitHub is asked with: the JSON media type, the
    pinned `API_VERSION`, and the token as a bearer where there is one (`PL-LGDV`).
    `agent` names the tool in `User-Agent`, which GitHub requires. Sending and
    reading the answer stay with the caller, since each tool has its own bound
    and its own rule for a failure.
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
        "User-Agent": agent,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(url, data=data, headers=headers, method=method)


def fetch(slug: str, query: Query, listing: str = "pulls") -> list[object]:
    """One page of `slug`'s pull requests as `query` narrows it, or `ListingFailed` saying why not.

    `listing` is the path under the repository that is listed: its pull
    requests by default, or one pull request's timeline for `auto_merge`.

    The one request every question here makes. Its failures are named apart -
    no token or a refusal is `NO_PERMISSION`, nothing answering is
    `NO_NETWORK`, an answer that is not a JSON list is `UNREADABLE_ANSWER` - because
    `left_behind_check.py` must say which; a caller that does the same thing
    with all of them, as this script's own do, catches the one exception.
    """
    token = github_token()
    if not token:
        raise ListingFailed(NO_PERMISSION, "no GH_TOKEN or GITHUB_TOKEN to ask GitHub with")
    request = api_request(
        f"{GITHUB_API}/repos/{slug}/{listing}?{urllib.parse.urlencode(query)}",
        agent="open_pull_requests",
        token=token,
    )
    try:
        with urllib.request.urlopen(request, timeout=LOOKUP_TIMEOUT) as response:
            body = response.read()
    except urllib.error.HTTPError as error:
        if error.code in _REFUSAL_CODES:
            raise ListingFailed(NO_PERMISSION, f"GitHub refused (HTTP {error.code})") from error
        raise ListingFailed(UNREADABLE_ANSWER, f"GitHub answered HTTP {error.code}") from error
    except (OSError, http.client.HTTPException) as error:
        # `URLError`, a timeout, a refused connection: nothing answered. A body
        # cut short raises `IncompleteRead`, which is not an `OSError`.
        raise ListingFailed(NO_NETWORK, f"GitHub could not be reached ({error})") from error
    try:
        payload = json.loads(body)
    except ValueError as error:
        raise ListingFailed(UNREADABLE_ANSWER, "GitHub's answer was not JSON") from error
    if not isinstance(payload, list):
        raise ListingFailed(UNREADABLE_ANSWER, "GitHub's answer was not a listing")
    return payload


def _numbers(page: list[object]) -> list[object]:
    return [entry.get("number") if isinstance(entry, dict) else None for entry in page]


def every_page(read: Callable[[Query], list[object]], query: Query) -> list[object]:
    """Every entry of the listing `query` asks for, read a page at a time with `read`, oldest first.

    **Read to a short page, never stopped at a full one** (`PL-351H`). This
    declined on a full page while `update_armed.py` read the next, so at 100
    open the two disagreed about which pull requests were open. Paging is the
    complete answer; what made the decline safe was that a page read later
    than the one before it can miss an entry, and that is checked instead.

    **Oldest first, so only a close can shift a page**: a pull request opened
    mid-read joins the last page, but one closed shifts every later entry back
    by one, and the entry crossing into a page already read is never seen. So
    a listing that took more than one page reads each page but the last again
    and compares the numbers; any change is `ListingFailed`, since a listing
    missing an entry looks exactly like a complete one. One page - every
    listing here so far - costs one request, as before.
    """
    asked: Query = {**query, "sort": "created", "direction": "asc", "per_page": PAGE}
    pages: list[list[object]] = []
    while not pages or len(pages[-1]) >= PAGE:
        pages.append(read({**asked, "page": len(pages) + 1}))
    for number, page in enumerate(pages[:-1], start=1):
        if _numbers(read({**asked, "page": number})) != _numbers(page):
            raise ListingFailed(
                UNREADABLE_ANSWER, "the listing changed while it was read a page at a time"
            )
    return [entry for page in pages for entry in page]


def open_pull_requests(slug: str, *, head: str | None = None) -> tuple[PullRequest, ...] | None:
    """The open pull requests on `slug`, or None when the forge could not be asked.

    `head` narrows the listing to one branch, which is what a caller holding a
    branch already wants. None is any `ListingFailed`, from `fetch` or from
    `every_page`: every caller here does the same thing with all of them.
    """
    query: Query = {"state": "open"}
    if head:
        query["head"] = f"{slug.split('/')[0]}:{head}"
    try:
        payload = every_page(lambda asked: fetch(slug, asked), query)
    except ListingFailed:
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


def newest(slug: str, branch: str, base: str) -> NewestPullRequest | None:
    """The newest pull request from `branch` into `base`, None where none was ever opened.

    `ListingFailed` is `fetch`'s, and an entry this cannot read is one too,
    `UNREADABLE_ANSWER`: a number that is not one, a state that is neither `open` nor
    `closed`, a `merged_at` that is neither null nor a time - absent included,
    since a merge read as "not merged" is the answer this exists to correct -
    or no head commit. `state` is `merged` where the forge records a merge and
    otherwise its own `open` or `closed`; `head` is the commit the forge names
    as the head, frozen when it closes, so a merged one names the commit its
    merge took whatever the branch gained since (checked on `#793`).
    """
    query: Query = {
        "state": "all",
        "head": f"{slug.split('/')[0]}:{branch}",
        "base": base,
        "sort": "created",
        "direction": "desc",
        "per_page": 1,
    }
    payload = fetch(slug, query)
    if not payload:
        return None
    entry = payload[0]
    if not isinstance(entry, dict):
        raise ListingFailed(UNREADABLE_ANSWER, "GitHub's listing held an entry that is not one")
    number, state = entry.get("number"), entry.get("state")
    merged_at = entry.get("merged_at", False)
    head = entry.get("head")
    sha = head.get("sha") if isinstance(head, dict) else None
    if (
        not isinstance(number, int)
        or state not in (PULL_OPEN, PULL_CLOSED)
        or not (merged_at is None or isinstance(merged_at, str))
        or not isinstance(sha, str)
        or not sha
    ):
        raise ListingFailed(
            UNREADABLE_ANSWER, "GitHub's listing had no number, state, merged_at or head commit"
        )
    merged = PULL_MERGED if merged_at is not None else str(state)
    return NewestPullRequest(number=number, state=merged, head=sha)


def newest_pull_request(slug: str, branch: str, base: str) -> tuple[NewestPullRequest, ...] | None:
    """`newest` as the command prints it: one, `()` for none opened, None where it could not ask.

    `()` is an answer: the forge was asked, and nothing was ever opened from
    the branch.
    """
    try:
        found = newest(slug, branch, base)
    except ListingFailed:
        return None
    return () if found is None else (found,)


#: The timeline events that switch auto-merge on, one per merge method, and
#: the one that switches it off. GitHub's REST timeline names them so.
AUTO_MERGE_ON_EVENTS = frozenset(
    {"auto_merge_enabled", "auto_squash_enabled", "auto_rebase_enabled"}
)
AUTO_MERGE_OFF_EVENT = "auto_merge_disabled"


def auto_merge(slug: str, number: int) -> tuple[str, str] | None:
    """`(STATE, TIME)` for the latest switch of auto-merge on pull request `number`.

    `STATE` is `on` or `off`, and None means it was never switched on.
    `ListingFailed` is `fetch`'s, or an event this cannot read: one with no
    time. The timeline is read whole by `every_page`, oldest first, so the last
    switch found is the latest. The actor is not read, since GitHub names the
    owner's account for a session's switches too (`PL-8TPV`).
    """
    events = every_page(lambda asked: fetch(slug, asked, f"issues/{number}/timeline"), {})
    latest: tuple[str, str] | None = None
    for entry in events:
        if not isinstance(entry, dict):
            raise ListingFailed(
                UNREADABLE_ANSWER, "GitHub's timeline held an entry that is not one"
            )
        event = entry.get("event")
        if event not in AUTO_MERGE_ON_EVENTS and event != AUTO_MERGE_OFF_EVENT:
            continue
        at = entry.get("created_at")
        if not isinstance(at, str) or not at:
            raise ListingFailed(UNREADABLE_ANSWER, f"GitHub's {event} event carried no time")
        latest = ("off" if event == AUTO_MERGE_OFF_EVENT else "on", at)
    return latest


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
    parser.add_argument(
        "--auto-merge",
        type=int,
        metavar="NUMBER",
        help="print `STATE TIME` for the latest switch of auto-merge on pull request NUMBER "
        "instead, `STATE` `on` or `off`, or nothing where it was never switched on",
    )
    args = parser.parse_args(list(argv))
    slug = repo_slug()
    if args.auto_merge is not None:
        if not slug:
            return 1
        try:
            switch = auto_merge(slug, args.auto_merge)
        except ListingFailed:
            return 1
        if switch is not None:
            print(*switch)
        return 0
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
