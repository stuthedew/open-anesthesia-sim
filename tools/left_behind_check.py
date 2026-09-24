"""Name the commits a branch carries past the head its merged pull request merged.

**The failure.** A pull request merges; the session pushes one more commit to
the same branch. Nothing merges a merged pull request a second time, so the
commit lands nowhere, and nothing says so: no conflict, no red check, and the
branch and the pull request both read as merged. `#284` is the recorded
instance, and `claude/recurrence-signal-feature-3hnynt` was carrying another
when this was written: one commit pushed after `#793` merged.

**The invariant, and why it is exact** (`PL-VV4D`). A pull request merges the
head it was opened against, and GitHub freezes `refs/pull/<n>/head` there when
it closes. So the only question is whether the branch's tip descends from that
head. Equal, or behind it, means nothing was left behind. A descendant means
exactly the commits between them were, less any the default branch already
holds and any merge commit, which brings the base in and adds no work. Nothing
here compares file content, so a squash, a rename, two sessions writing the
same lines, and a base that rewrote the file afterwards cannot confound it. All
of those have fooled `vcs.orphaned` (`PL-JHJ3`, `PL-5TRV`, `PL-XLQ5`).

**Except a change that landed another way, which ancestry cannot see.** A
commit pushed after the merge whose change then reached the default branch
through a *different* pull request - a port of a fix, which the drive-to-green
rules prescribe for a red base - descends from the frozen head and is merged by
nothing, yet nothing is lost. So each commit past the head is also put to
`vcs.change_landed`, which replays it onto the base and asks whether that
changes anything (`PL-GHHW`, `PL-PXZ3`). One held there is not left behind:
the branch reads as clear, and the clearance names the pull request that
landed it. `vcs.orphaned` reads the same test, so the two checks cannot
disagree about a port.

**What it needs, and what it says when it cannot have it.** Git holds no record
of which pull request came from which branch, so that mapping comes from
GitHub's pull-request listing, which needs a token. The frozen head is read from
`refs/pull/<n>/head` with `git ls-remote`, not fetched. Where either cannot be
read the check declines, and names the reason. It never goes quiet, because
silence is how it reports a clean answer. The three conditions `PL-R808` names:

- **no network**: GitHub, or `origin`, could not be reached;
- **no permission**: no token, or GitHub refused the request;
- **no such ref**: the pull request merged but its `refs/pull/<n>/head` is gone.
  GitHub deletes that ref on request, and this repository asked it to for
  `#297`-`#386` (`PL-0SCG`, `PL-LF2C`). A missing ref never reads as "nothing
  left behind".

Which of the first two a git failure falls under is read from git's own error
text. That choice sets only the wording: every failure declines.

**Beside `vcs.orphaned`, never instead of it** (`PL-BHVM`, 2026-09-19). That
check compares content, and it runs in a bare checkout with no network. This
one runs only where GitHub answers. So each branch gets this check's answer
where it has one, and `orphaned`'s wherever it does not. Where the two disagree,
this one wins and the disagreement is printed, because a reader holding both
answers needs to know which to believe.

Wired into `.claude/hooks/docket-digest.sh`, so each session start reads it. It
prints nothing when every branch is clear, and otherwise one line per finding,
per decline and per disagreement. `--all` also lists every branch it read and
the verdict for each. It always exits 0, like the digest's other tools. Standard
library only, so a bare checkout can run it.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from open_pull_requests import GITHUB_API, LOOKUP_TIMEOUT, repo_slug  # noqa: E402

#: Seconds for one git call. `ls-remote` is the only one that touches the
#: network, and it answered in 0.6 s for 839 pull refs when this was written.
GIT_TIMEOUT = 30.0

#: The prefixes a decline opens with, one per condition, so a reader and a test
#: can tell them apart without parsing the rest of the sentence.
NO_NETWORK = "no network"
NO_PERMISSION = "no permission"
NO_SUCH_REF = "no such ref"
UNREADABLE = "unreadable"

#: Phrases in git's error text that mean the remote refused, not that it could
#: not be reached. Anything else is read as a network failure. Both decline.
_REFUSALS = (
    "returned error: 401",
    "returned error: 403",
    "returned error: 404",
    "Authentication failed",
    "Permission denied",
    "Repository not found",
    "terminal prompts disabled",
)


class Declined(Exception):
    """The check could not read what it compares; the message says which part."""


@dataclass(frozen=True)
class Git:
    """One git call's exit status and output, both streams kept."""

    code: int
    out: str
    err: str


Runner = Callable[[list[str]], Git]


def git_runner(root: Path) -> Runner:
    """Run git in `root`, never prompting for credentials and never raising."""

    def run(args: list[str]) -> Git:
        env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        try:
            done = subprocess.run(
                ["git", *args],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=GIT_TIMEOUT,
                check=False,
                env=env,
            )
        except subprocess.TimeoutExpired:
            return Git(124, "", f"git {args[0]} timed out after {GIT_TIMEOUT:.0f} s")
        except OSError as error:
            return Git(127, "", str(error))
        return Git(done.returncode, done.stdout, done.stderr)

    return run


@dataclass(frozen=True)
class Remote:
    """What `origin` holds right now: its default branch, branch tips, frozen heads."""

    default: str
    heads: dict[str, str]
    frozen: dict[int, str]


def read_remote(run: Runner) -> Remote:
    """One `ls-remote` for the default branch, every branch tip and every pull head.

    Read from the remote rather than from this checkout's tracking refs, which
    are only as fresh as the last fetch. A tip newer than that fetch is caught
    per branch, in `examine`, rather than compared stale.
    """
    done = run(["ls-remote", "--symref", "origin", "HEAD", "refs/heads/*", "refs/pull/*/head"])
    if done.code != 0:
        first = (done.err.strip().splitlines() or ["no error text"])[0]
        kind = NO_PERMISSION if any(mark in done.err for mark in _REFUSALS) else NO_NETWORK
        raise Declined(f"{kind}: git ls-remote origin failed ({first})")
    default = ""
    heads: dict[str, str] = {}
    frozen: dict[int, str] = {}
    for line in done.out.splitlines():
        value, _, ref = line.partition("\t")
        if value.startswith("ref: ") and ref == "HEAD":
            default = value.removeprefix("ref: refs/heads/")
        elif ref.startswith("refs/heads/"):
            heads[ref.removeprefix("refs/heads/")] = value
        elif ref.startswith("refs/pull/") and ref.endswith("/head"):
            number = ref.removeprefix("refs/pull/").removesuffix("/head")
            if number.isdigit():
                frozen[int(number)] = value
    if not default or default not in heads:
        raise Declined(f"{UNREADABLE}: origin did not name its default branch")
    return Remote(default=default, heads=heads, frozen=frozen)


@dataclass(frozen=True)
class PullRequest:
    """The newest pull request from one branch into the default branch."""

    number: int
    state: str
    merged: bool


Lookup = Callable[[str], "PullRequest | None"]


def github_lookup(slug: str, base: str) -> Lookup:
    """Ask GitHub for the newest pull request from a branch into `base`.

    The request is `open_pull_requests.py`'s, with every state and one result.
    The listing is newest first, so that result is the one whose head the
    branch was last merged at, or the open one now carrying it. What differs is
    the failure: that script folds every failure into "could not look", and this
    one separates them into the conditions its caller must name.
    """
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    owner = slug.split("/")[0]

    def lookup(branch: str) -> PullRequest | None:
        if not token:
            raise Declined(f"{NO_PERMISSION}: no GH_TOKEN or GITHUB_TOKEN to ask GitHub with")
        query = urllib.parse.urlencode(
            {
                "state": "all",
                "head": f"{owner}:{branch}",
                "base": base,
                "sort": "created",
                "direction": "desc",
                "per_page": 1,
            }
        )
        request = urllib.request.Request(
            f"{GITHUB_API}/repos/{slug}/pulls?{query}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "left_behind_check",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=LOOKUP_TIMEOUT) as response:
                body = response.read()
        except urllib.error.HTTPError as error:
            if error.code in (401, 403, 404, 429):
                raise Declined(f"{NO_PERMISSION}: GitHub refused (HTTP {error.code})") from error
            raise Declined(f"{UNREADABLE}: GitHub answered HTTP {error.code}") from error
        except OSError as error:
            # `URLError`, a timeout, a refused connection: nothing answered.
            raise Declined(f"{NO_NETWORK}: GitHub could not be reached ({error})") from error
        return _pull_request(body)

    return lookup


def _pull_request(body: bytes) -> PullRequest | None:
    """The one entry a listing holds, or None where it holds none."""
    try:
        payload = json.loads(body)
    except ValueError as error:
        raise Declined(f"{UNREADABLE}: GitHub's answer was not JSON") from error
    if not isinstance(payload, list):
        raise Declined(f"{UNREADABLE}: GitHub's answer was not a listing")
    if not payload:
        return None
    entry = payload[0]
    number = entry.get("number") if isinstance(entry, dict) else None
    state = entry.get("state") if isinstance(entry, dict) else None
    if not isinstance(number, int) or state not in ("open", "closed"):
        raise Declined(f"{UNREADABLE}: GitHub's listing had no number or state")
    return PullRequest(number=number, state=state, merged=entry.get("merged_at") is not None)


@dataclass(frozen=True)
class Commit:
    """One commit left behind: its hash, committer date and subject."""

    sha: str
    date: str
    subject: str


@dataclass(frozen=True)
class Verdict:
    """What one branch was found to carry.

    `left` is the finding, and a verdict with commits in it is the only kind
    printed as one. `landed` holds the commits past the merged head whose
    change the default branch took another way, each beside the pull request
    or commit that took it; they are not the finding. `clear` says why nothing
    was left behind, for `--all` and for the disagreement line. `declined`
    says why the branch could not be read.
    """

    branch: str
    number: int | None = None
    left: tuple[Commit, ...] = ()
    clear: str = ""
    declined: str = ""
    landed: tuple[tuple[Commit, str], ...] = ()


def _has_commit(sha: str, run: Runner) -> bool:
    return run(["cat-file", "-e", f"{sha}^{{commit}}"]).code == 0


def landed_through(sha: str, base: str, run: Runner) -> str:
    """How the default branch took `sha`'s change another way, or "" where it has not.

    `vcs.change_landed` is the test, and it is `vcs.orphaned`'s too, so the two
    checks give one answer about a port (`PL-GHHW`). Every failure reads as not
    landed - an unimportable `docket`, a conflict, a git older than 2.40 - so the
    commit stays a finding, which is what this check printed before the test
    existed. A pull request is named where the landing commit is a squash
    merge's, and the commit otherwise.
    """
    try:
        from docket.vcs import change_landed
    except Exception:  # a broken import must cost the clearance, never the finding
        return ""

    def call(args: list[str], _root: Path) -> str:
        done = run(args)
        return done.out if done.code == 0 else ""

    landing = change_landed(sha, base, ROOT, runner=call)
    if landing is None:
        return ""
    number = landing.pull_request
    return f"#{number}" if number is not None else landing.commit[:9]


def examine(
    branch: str, tip: str, base: str, remote: Remote, lookup: Lookup, run: Runner
) -> Verdict:
    """Compare one branch tip against the head its newest pull request merged.

    `base` is the default branch's tip. Commits it holds are never reported.
    """
    if not _has_commit(tip, run):
        return Verdict(branch, declined=f"tip {tip[:9]} is not in this checkout; git fetch origin")
    on_base = run(["merge-base", "--is-ancestor", tip, base]).code
    if on_base == 0:
        return Verdict(branch, clear="already on the default branch")
    if on_base != 1:
        return Verdict(branch, declined=f"{UNREADABLE}: git could not compare it with the base")
    pull = lookup(branch)
    if pull is None:
        return Verdict(branch, clear="no pull request was opened from it")
    number = pull.number
    if pull.state == "open":
        return Verdict(branch, number, clear=f"#{number} is open on it")
    if not pull.merged:
        return Verdict(branch, number, clear=f"#{number} closed without merging")
    head = remote.frozen.get(number)
    if head is None:
        return Verdict(
            branch,
            number,
            declined=f"{NO_SUCH_REF}: #{number} merged, but refs/pull/{number}/head no longer "
            "resolves, so the head it merged cannot be read",
        )
    if head == tip:
        return Verdict(branch, number, clear=f"#{number} merged at its tip")
    # A clone that is not shallow holds every ancestor of every commit it holds,
    # so a head it lacks is not an ancestor of the tip. `check` refuses a
    # shallow clone before any branch is examined.
    past = run(["merge-base", "--is-ancestor", head, tip]).code if _has_commit(head, run) else 1
    if past == 1:
        return Verdict(branch, number, clear=f"it does not descend from the head #{number} merged")
    if past != 0:
        return Verdict(
            branch, number, declined=f"{UNREADABLE}: git could not compare it with #{number}"
        )
    listed = run(["log", "--no-merges", "--format=%H%x1f%cs%x1f%s", tip, f"^{head}", f"^{base}"])
    if listed.code != 0:
        return Verdict(branch, number, declined=f"{UNREADABLE}: git could not list its commits")
    left = tuple(
        Commit(sha, date, subject)
        for sha, date, subject in (
            line.split("\x1f", 2) for line in listed.out.splitlines() if line
        )
    )
    if not left:
        return Verdict(branch, number, clear=f"only merges of the base since #{number} merged")
    through = {commit.sha: landed_through(commit.sha, base, run) for commit in left}
    landed = tuple((commit, through[commit.sha]) for commit in left if through[commit.sha])
    left = tuple(commit for commit in left if not through[commit.sha])
    if not left:
        where = ", ".join(sorted({how for _, how in landed}))
        return Verdict(
            branch,
            number,
            clear=f"the {len(landed)} commit(s) pushed after #{number} merged landed through "
            f"{where}",
            landed=landed,
        )
    return Verdict(branch, number, left=left, landed=landed)


@dataclass(frozen=True)
class Report:
    """Every branch's verdict, or the one reason none could be read."""

    verdicts: tuple[Verdict, ...] = ()
    declined: str = ""


def check(root: Path, *, run: Runner | None = None, lookup: Lookup | None = None) -> Report:
    """Read every branch on `origin` except its default branch.

    Declines whole where nothing can be compared: a remote that is not
    GitHub's, a shallow clone, a remote that will not answer, or a base this
    checkout has not fetched. A failure of the GitHub lookup also declines the
    whole report, since every branch shares one token and one route to GitHub.
    """
    run = run or git_runner(root)
    slug = repo_slug()
    if slug is None:
        return Report(declined=f"{UNREADABLE}: origin is not a GitHub repository")
    shallow = run(["rev-parse", "--is-shallow-repository"])
    if shallow.code != 0 or shallow.out.strip() != "false":
        return Report(declined="this checkout is shallow, so ancestry past its boundary is unknown")
    try:
        remote = read_remote(run)
    except Declined as declined:
        return Report(declined=str(declined))
    base = remote.heads[remote.default]
    if not _has_commit(base, run):
        return Report(
            declined=f"{remote.default} {base[:9]} is not in this checkout; git fetch origin"
        )
    lookup = lookup or github_lookup(slug, remote.default)
    branches = sorted(name for name in remote.heads if name != remote.default)

    def one(name: str) -> Verdict:
        return examine(name, remote.heads[name], base, remote, lookup, run)

    try:
        with ThreadPoolExecutor(max_workers=8) as pool:
            verdicts = tuple(pool.map(one, branches))
    except Declined as declined:
        return Report(declined=str(declined))
    return Report(verdicts=verdicts)


def orphaned_branches(root: Path) -> frozenset[str] | None:
    """The branches `vcs.orphaned` reports, or None where it could not answer.

    A failure here costs only the agreement clause. The findings above it are
    this check's own and are printed either way.
    """
    from docket.vcs import orphaned

    try:
        report = orphaned(root)
    except Exception:  # the comparison is a courtesy; it must not take the findings down
        return None
    if not report.known:
        return None
    return frozenset(branch.ref.removeprefix("origin/") for branch in report.branches)


def lines(report: Report, orphaned: frozenset[str] | None, *, every: bool = False) -> list[str]:
    """The digest's lines: findings, declines and disagreements. Clear branches say nothing."""
    if report.declined:
        return [
            f"left-behind: not checked - {report.declined}. vcs.orphaned's content "
            "comparison is the only answer this session has."
        ]
    out: list[str] = []
    for verdict in report.verdicts:
        if verdict.left:
            newest = verdict.left[0]
            more = f", +{len(verdict.left) - 1} more" if len(verdict.left) > 1 else ""
            if orphaned is None:
                agreement = "vcs.orphaned could not answer"
            elif verdict.branch in orphaned:
                agreement = "vcs.orphaned agrees"
            else:
                agreement = "vcs.orphaned does not report it, and this ref comparison wins"
            out.append(
                f"left-behind: {verdict.branch} carries {len(verdict.left)} commit(s) pushed "
                f"after #{verdict.number} merged, which nothing will merge: {newest.sha[:9]} "
                f"{newest.subject} ({newest.date}){more}; {agreement}."
            )
        elif verdict.declined:
            out.append(f"left-behind: {verdict.branch} not checked - {verdict.declined}.")
        elif orphaned is not None and verdict.branch in orphaned:
            out.append(
                f"left-behind: vcs.orphaned reports {verdict.branch}, but {verdict.clear}, "
                "so no merged pull request left work on it; this ref comparison wins."
            )
    if any(verdict.left for verdict in report.verdicts):
        out.append(
            "left-behind: open a pull request from the branch to land them, or delete the "
            "branch if they landed another way. `python3 tools/left_behind_check.py --all`."
        )
    if every:
        for verdict in report.verdicts:
            said = verdict.declined or verdict.clear or f"{len(verdict.left)} commit(s) left behind"
            out.append(f"  {verdict.branch}: {said}")
            out.extend(
                f"    {commit.sha[:9]} {commit.date} {commit.subject}" for commit in verdict.left
            )
            out.extend(
                f"    {commit.sha[:9]} {commit.date} {commit.subject} - landed through {how}"
                for commit, how in verdict.landed
            )
    return out


def main(argv: list[str]) -> int:
    """Print the digest's lines. Always exits 0; never blocks a session."""
    try:
        report = check(ROOT)
        compared = orphaned_branches(ROOT) if report.verdicts else None
        for line in lines(report, compared, every="--all" in argv):
            print(line)
    except Exception as error:  # a crash must decline, not go quiet
        # The hook discards stderr, and an empty stdout reads as "every branch
        # is clear". So a bug here must still print, or it would look like that.
        print(
            f"left-behind: not checked - the check itself failed ({type(error).__name__}: {error})."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
