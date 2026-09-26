"""Bring `main` into every armed pull request it has moved past, so auto-merge can land it.

**The failure** (`PL-S5MF`). Since 2026-09-23 `main` merges a pull request only
once its branch holds `main`'s tip (`PL-6MW8`), and GitHub's auto-merge never
brings the base in. So an armed pull request that `main` moves past waits at
*behind* until somebody clicks *Update branch*, and nothing tells anybody:
`#1115`, the v0.5.12 cut, waited from 18:46 to 19:17 UTC on 2026-09-26 with its
session live and subscribed, because no event reports a branch falling behind.

**The rule.** `.github/workflows/update-armed.yml` runs this on every push to
`main`. An open pull request onto that branch is updated with GitHub's *Update
branch* call, which merges the base in, when all of these hold:

- auto-merge is armed on it, so its author has already said it should merge
  once its checks pass;
- it is not a draft, and it comes from this repository rather than a fork;
- the base is ahead of its head;
- no check the base requires has already failed on its head.

The last is `CLAUDE.md`'s rule for a base merge - once, when `behind` is all
that stops a pull request. A red one would re-run a failing check on every push
to `main`, and fixing it is its session's work. Only required checks count,
because auto-merge waits on nothing else: a failure it ignores must not strand
the pull request here either. Checks still running do not hold one back, since
they would finish on a base that has already moved.

The call carries `expected_head_sha`, so a commit pushed after the read is never
merged over. GitHub refuses the update instead, and the next run reads again.

**Two tokens.** Everything is read with the workflow's own `GITHUB_TOKEN`. The
update is made with `UPDATE_BRANCH_TOKEN`, a fine-grained personal access token
the project owner creates (`docs/maintainer.md`), because an update made with
`GITHUB_TOKEN` "creates workflow runs in an approval-required state" (GitHub
Docs, *Triggering a workflow*): the required checks would wait on a click, which
is the stall again. Without that secret nothing is written, and each pull
request that would have been updated is listed as such.

**What passes and what fails.** Exit 1 means a reading failed or GitHub refused
the token, and nothing after it was tried; the output says which, and for a
refused token it names the permission GitHub asked for. Every reading is taken
before the first update, so a failed one updates nothing. Anything GitHub
answers with 422 - a conflict, a head that moved since the read - is listed and
passes: it is the pull request's to resolve, and failing on it would turn the
run red on every push to `main` until somebody did.

Lists by default, and updates only with the token in the environment. Standard
library only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from open_pull_requests import repo_slug  # noqa: E402
from required_checks_check import required_contexts  # noqa: E402

API = "https://api.github.com"
API_VERSION = "2022-11-28"

#: The secret the update is made with, read from the environment only.
#: `tests/unit/test_update_armed.py` holds the workflow to this spelling, since
#: a misspelt secret reads as an absent one and the run would pass listing.
WRITE_TOKEN = "UPDATE_BRANCH_TOKEN"

#: A check run's conclusions that are a verdict against the pull request.
#: `cancelled` and `action_required` are not: neither says the change is wrong,
#: and the update starts the check again.
FAILED = frozenset({"failure", "timed_out", "startup_failure"})

#: GitHub's largest page. A listing is read page by page until one comes back short.
PAGE = 100

TIMEOUT = 30.0
ATTEMPTS = 3

Emit = Callable[[str], None]


class Declined(Exception):
    """A reading failed, or GitHub refused the token, so nothing more is tried."""


@dataclass(frozen=True)
class Pull:
    """One open pull request, as far as the rule reads it."""

    number: int
    branch: str
    sha: str
    armed: bool
    draft: bool
    fork: bool


@dataclass(frozen=True)
class Answer:
    """One HTTP answer: its status, its decoded body, and the permission header."""

    status: int
    body: object
    accepted: str = ""


def _decoded(raw: bytes) -> object:
    try:
        return json.loads(raw.decode("utf-8"))
    except ValueError:
        return None


def _message(body: object) -> str:
    message = body.get("message") if isinstance(body, dict) else None
    return message if isinstance(message, str) else "no message"


class GitHub:
    """The calls this makes, each with the token it needs."""

    def __init__(
        self, slug: str, read_token: str | None, write_token: str | None, root: str = API
    ) -> None:
        self.slug = slug
        self.read_token = read_token
        self.write_token = write_token
        self.root = root

    def _call(self, method: str, path: str, token: str | None, body: object = None) -> Answer:
        data = None if body is None else json.dumps(body).encode("utf-8")
        request = urllib.request.Request(f"{self.root}{path}", data=data, method=method)
        request.add_header("Accept", "application/vnd.github+json")
        request.add_header("X-GitHub-Api-Version", API_VERSION)
        request.add_header("User-Agent", "update_armed")
        if token:
            request.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                return Answer(response.status, _decoded(response.read()))
        except urllib.error.HTTPError as error:
            accepted = (
                error.headers.get("X-Accepted-GitHub-Permissions", "") if error.headers else ""
            )
            return Answer(error.code, _decoded(error.read()), accepted)

    def get(self, path: str) -> object:
        """The body of a 200 answer, retrying a server or network failure twice."""
        last = ""
        for attempt in range(ATTEMPTS):
            try:
                answer = self._call("GET", path, self.read_token)
            except OSError as error:
                last = str(error)
            else:
                if answer.status == 200:
                    return answer.body
                last = f"HTTP {answer.status}, {_message(answer.body)}"
                if answer.status < 500:
                    break
            if attempt + 1 < ATTEMPTS:
                time.sleep(2**attempt)
        raise Declined(f"GitHub could not be read at {path}: {last}")

    def update_branch(self, number: int, sha: str) -> Answer:
        """Merge the base into pull request `number`, if its head is still `sha`."""
        path = f"/repos/{self.slug}/pulls/{number}/update-branch"
        try:
            return self._call("PUT", path, self.write_token, {"expected_head_sha": sha})
        except OSError as error:
            raise Declined(f"the update of #{number} could not be sent: {error}") from error


def parse_pull(entry: object, slug: str) -> Pull:
    """One entry of GitHub's pull request listing, or Declined where it is not one.

    An entry without `auto_merge` is refused rather than read as unarmed: the
    field is how "armed" is known at all, so its absence is a change in GitHub's
    answer, and reading it as "no" would quietly stop every update.
    """
    head = entry.get("head") if isinstance(entry, dict) else None
    number = entry.get("number") if isinstance(entry, dict) else None
    if (
        not isinstance(entry, dict)
        or not isinstance(head, dict)
        or not isinstance(number, int)
        or "auto_merge" not in entry
    ):
        raise Declined("an entry in GitHub's list of open pull requests could not be read")
    branch, sha, repo = head.get("ref"), head.get("sha"), head.get("repo")
    if not isinstance(branch, str) or not isinstance(sha, str):
        raise Declined(f"GitHub's listing gave #{number} no head branch or commit")
    return Pull(
        number=number,
        branch=branch,
        sha=sha,
        armed=entry["auto_merge"] is not None,
        draft=entry.get("draft") is True,
        fork=not (isinstance(repo, dict) and repo.get("full_name") == slug),
    )


def open_pulls(api: GitHub, base: str) -> list[Pull]:
    """Every open pull request onto `base`."""
    found: list[Pull] = []
    page = 1
    while True:
        query = urllib.parse.urlencode(
            {"state": "open", "base": base, "per_page": PAGE, "page": page}
        )
        payload = api.get(f"/repos/{api.slug}/pulls?{query}")
        if not isinstance(payload, list):
            raise Declined("GitHub's list of open pull requests was not a list")
        found.extend(parse_pull(entry, api.slug) for entry in payload)
        if len(payload) < PAGE:
            return found
        page += 1


def behind_by(api: GitHub, base: str, sha: str) -> int:
    """How many commits `base` has that `sha` does not."""
    payload = api.get(f"/repos/{api.slug}/compare/{urllib.parse.quote(base)}...{sha}")
    behind = payload.get("behind_by") if isinstance(payload, dict) else None
    if not isinstance(behind, int) or behind < 0:
        raise Declined(f"GitHub's comparison of {base} with {sha[:12]} gave no behind_by")
    return behind


def failed_checks(api: GitHub, sha: str, required: set[str]) -> list[str]:
    """The required checks whose latest run on `sha` failed.

    Commit statuses are not read: no required check here reports as one. Were one
    to, a failure in it would be missed, which costs an update the rule meant to
    save and never strands a pull request.
    """
    payload = api.get(f"/repos/{api.slug}/commits/{sha}/check-runs?per_page={PAGE}")
    runs = payload.get("check_runs") if isinstance(payload, dict) else None
    total = payload.get("total_count") if isinstance(payload, dict) else None
    if not isinstance(runs, list) or not isinstance(total, int):
        raise Declined(f"GitHub's check runs for {sha[:12]} could not be read")
    if total > len(runs):
        raise Declined(f"{sha[:12]} has more check runs than one page of GitHub's answer holds")
    return sorted(
        {
            run["name"]
            for run in runs
            if isinstance(run, dict)
            and run.get("name") in required
            and run.get("conclusion") in FAILED
        }
    )


def screen(pull: Pull) -> str | None:
    """Why `pull` is not read further, or None when the rule reads on."""
    if not pull.armed:
        return "not armed"
    if pull.draft:
        return "armed, but a draft"
    if pull.fork:
        return "armed, but from a fork"
    return None


def verdict(behind: int, failed: Sequence[str], base: str) -> str | None:
    """Why an armed pull request is left as it stands, or None when it is updated."""
    if behind == 0:
        return f"level with {base}"
    if failed:
        noun = "check" if len(failed) == 1 else "checks"
        names = ", ".join(repr(name) for name in failed)
        return (
            f"{behind} behind {base}, but required {noun} {names} failed on its head, "
            "which is its session's to fix"
        )
    return None


def outcome(answer: Answer) -> str:
    """What one update answer means, or Declined where GitHub refused the token."""
    if answer.status == 202:
        return "updated"
    if answer.status == 422:
        return f"not updated: GitHub answered {_message(answer.body)!r}"
    needs = (
        f"; GitHub names the permission it needs as {answer.accepted}" if answer.accepted else ""
    )
    raise Declined(
        f"GitHub refused the update with HTTP {answer.status}, {_message(answer.body)}{needs}"
    )


def run(api: GitHub, base: str, required: set[str], emit: Emit) -> None:
    """Read every open pull request onto `base`, then update what the rule says to."""
    pulls = open_pulls(api, base)
    chosen: list[tuple[Pull, int]] = []
    for pull in pulls:
        why = screen(pull)
        if why is None:
            behind = behind_by(api, base, pull.sha)
            failed = failed_checks(api, pull.sha, required) if behind else []
            why = verdict(behind, failed, base)
            if why is None:
                chosen.append((pull, behind))
                continue
        if pull.armed:
            emit(f"#{pull.number} {pull.branch}: {why}")
    unarmed = sum(not pull.armed for pull in pulls)
    emit(f"{unarmed} of {len(pulls)} open pull request(s) onto {base} not armed, so not read")
    for pull, behind in chosen:
        if api.write_token:
            done = outcome(api.update_branch(pull.number, pull.sha))
        else:
            done = f"not updated: no {WRITE_TOKEN}"
        emit(f"#{pull.number} {pull.branch}: {behind} behind {base}, {done}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--base", default="main", help="the branch whose pull requests are read")
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY") or None,
        help="owner/name; defaults to GITHUB_REPOSITORY, then to origin",
    )
    args = parser.parse_args(argv)
    lines: list[str] = []

    def emit(line: str) -> None:
        lines.append(line)
        print(line, flush=True)

    in_actions = os.environ.get("GITHUB_ACTIONS") == "true"
    try:
        slug = args.repo or repo_slug()
        if not slug:
            raise Declined("the repository could not be named from origin; pass --repo owner/name")
        read_token = os.environ.get("GITHUB_TOKEN") or None
        try:
            required, _ = required_contexts(slug, args.base, read_token)
        except RuntimeError as error:
            raise Declined(
                f"the required checks on {args.base} could not be read: {error}"
            ) from error
        run(
            GitHub(slug, read_token, os.environ.get(WRITE_TOKEN) or None), args.base, required, emit
        )
    except Declined as declined:
        lines.append(f"Stopped: {declined}")
        print(f"::error::{declined}" if in_actions else f"Stopped: {declined}", file=sys.stderr)
        _summarize(lines)
        return 1
    _summarize(lines)
    return 0


def _summarize(lines: Sequence[str]) -> None:
    """Put the lines on the run's page, where the owner sees them without opening the log."""
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write("".join(f"- {line}\n" for line in lines))


if __name__ == "__main__":
    raise SystemExit(main())
