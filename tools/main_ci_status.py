#!/usr/bin/env python3
"""Say when the default branch's last quality run failed, and stay silent otherwise.

`.github/workflows/quality.yml` runs the whole-store `verify:` replay only on
push to `main` — deliberately, because a pull request cannot have changed
whether some *other* item's work merged, and replaying the whole store on every
push to every branch costs more than it buys (`PL-SDHR`). The consequence is
that this class of failure is discovered *after* the merge, on a push nobody is
watching: `main` was red across three consecutive merges with every session
believing the tree was clean, because nothing reads that run (`PL-0ZGK`).

This closes the loop from the other end. Rather than making every branch pay to
prevent the red, one HTTP call at session start reports it once it exists.

**It speaks only when there is something to act on.** A green `main` prints
nothing, and so does every failure of this script's own — no network, no remote,
a remote that is not GitHub, a rate-limited or malformed response. `CLAUDE.md`
is explicit that a check firing every run without changing a decision is a
defect in the check, and this one is read at the top of every session, where a
routine line would train a reader to skim exactly the region a real advisory
appears in.

Two consequences of that rule are worth stating, because both look like gaps:

- **A `cancelled` run is not a verdict.** The workflow cancels superseded runs,
  so the newest completed run on `main` is regularly one that never finished
  judging anything. This reports the newest run that actually *reached* a
  conclusion, which is the most recent real answer about `main`.
- **Silence is not a green tree.** It means "no failing verdict was readable
  from here", which is also what an offline container gets. The line exists to
  surface a red nobody would otherwise see, never to certify a green one.

Standard library only, and parsing at the 3.11 floor `tools/ruff.toml` sets, so
a bare checkout with no virtualenv can run it — from the session-start hook, or
by hand at any moment, which is the half a hook alone cannot give: `main` can
go red *during* a session that started while it was green.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

# This file's own repository, not the caller's working directory: the hook runs
# it from wherever a session started, and `git remote` would otherwise answer
# for a different checkout or for nothing at all.
ROOT = Path(__file__).resolve().parents[1]

API = "https://api.github.com"
WORKFLOW = "quality.yml"
BRANCH = "main"
TIMEOUT_S = 8

# A conclusion that judged the tree. `cancelled` and `skipped` did not, and
# `None` is a run still going.
VERDICTS = ("success", "failure", "timed_out", "startup_failure", "action_required")

_REMOTE = re.compile(r"github\.com[:/]+([^/]+)/(.+?)(?:\.git)?/?$")


def repo_slug(remote_url: str) -> str | None:
    """Return `owner/repo` for a GitHub remote, or None for anything else.

    Both forms this repository is cloned with reach here — `https://github.com/
    owner/repo.git` from CI and containers, `git@github.com:owner/repo.git` from
    a workstation — and a non-GitHub remote returns None so the caller stays
    silent rather than guessing at an API that is not there.
    """
    match = _REMOTE.search(remote_url.strip())
    if match is None:
        return None
    owner, repo = match.group(1), match.group(2)
    return f"{owner}/{repo}" if owner and repo else None


def pick_run(runs: list[object]) -> dict[str, object] | None:
    """Return the newest run that reached a verdict, or None if none did.

    The API returns newest first. Runs that were cancelled or skipped are passed
    over rather than treated as an answer, per the module docstring.

    The parameter is `list[object]` rather than `list[dict]` because this is
    parsed JSON and the API has promised nothing about its shape, which makes
    the `isinstance` below load-bearing rather than defensive.
    """
    for run in runs:
        if isinstance(run, dict) and run.get("conclusion") in VERDICTS:
            return run
    return None


def advisory(run: dict[str, object]) -> str | None:
    """Return the line to print for a run, or None when it says nothing useful.

    Only a non-`success` verdict earns a line. The head sha is included because
    a reader's first question is whether the failure is still `main`'s head or
    something already pushed past.
    """
    conclusion = run.get("conclusion")
    if conclusion == "success":
        return None
    number = run.get("run_number", "?")
    sha = str(run.get("head_sha", ""))[:8] or "?"
    url = run.get("html_url", "")
    return (
        f"main's quality run #{number} on {sha} concluded {conclusion} - "
        f"main is red and no pull request will show it. {url}"
    )


def fetch_runs(slug: str) -> list[object]:
    """Fetch recent completed `quality.yml` runs on the default branch.

    Unauthenticated: this repository is public, so no token is needed and none
    is read, which keeps the script runnable from a bare checkout and keeps a
    credential out of a session-start path.
    """
    url = (
        f"{API}/repos/{slug}/actions/workflows/{WORKFLOW}/runs"
        f"?branch={BRANCH}&event=push&status=completed&per_page=10"
    )
    request = urllib.request.Request(
        url, headers={"Accept": "application/vnd.github+json", "User-Agent": "docket-digest"}
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
        payload = json.load(response)
    runs = payload.get("workflow_runs")
    return runs if isinstance(runs, list) else []


def main() -> int:
    """Print the advisory if there is one. Always exits 0; never blocks a session."""
    try:
        remote = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_S,
            check=True,
            cwd=ROOT,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return 0

    slug = repo_slug(remote)
    if slug is None:
        return 0

    try:
        runs = fetch_runs(slug)
    except (OSError, urllib.error.URLError, ValueError, TimeoutError):
        return 0

    run = pick_run(runs)
    if run is None:
        return 0

    line = advisory(run)
    if line is not None:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
