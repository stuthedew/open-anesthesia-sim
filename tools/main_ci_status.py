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

- **A `cancelled` run is not a verdict.** This reports the newest run that
  actually *reached* a conclusion, which is the most recent real answer about
  `main`. That skip used to carry more than it looks: until `PL-SMN4` every
  push to `main` shared one concurrency group, so a merge arriving while an
  earlier one was still pending evicted it, and 31 of the 257 completed `main`
  push runs between 2026-09-05 and 2026-09-16 - 12.1% - were passed over here
  for that reason alone. A per-commit group ended the eviction, so a cancelled
  run on `main` now means a hand cancellation or a lost runner. Those are still
  passed over in silence, and the commit behind one has no whole-store verdict
  at all: `PL-JTHW`.
- **Silence is not a green tree.** It means "no failing verdict was readable
  from here", which is also what an offline container gets. The line exists to
  surface a red nobody would otherwise see, never to certify a green one.

**The line names the failing step, and that is the whole of what `PL-T83R`
changed.** Attributed over all 819 completed `main` push runs from 2026-08-22
to 2026-09-20, the 109 failures fall almost entirely into one step:

| first failing step | runs | share |
| --- | --- | --- |
| `verify replay, the whole store` | 93 | 85.3% |
| `bin/docket check` (the bare floor-section run) | 14 | 12.8% |
| the pytest/coverage line | 1 | 0.9% |
| no job ran (startup failure) | 1 | 0.9% |

Reading the error text back out of each run's log agrees with that split
exactly: 93 are `checks.py`'s "open but its `verify:` command already passes",
14 are "marked done but records no `pr`", and the one pytest failure is
`test_this_repository_records_a_disposition_for_every_open_debt_item`, which
asserts on `ROADMAP.md` rather than on the simulator. **Not one of the 109 was
a defect in `src/`.**

In every one of the 93, the bare `bin/docket check` step earlier in the *same
job* passed, as did `ruff`, `mypy` and the full suite at 100% branch coverage.
The bare run is the same store validation without `--verify`, so a failure at
the replay and not at it isolates the cause to the one report `--verify` adds:
an open item whose own `verify:` command has flipped to passing. The tree was
not broken in any of the 93. Over the window `PL-T83R` was filed on it was 73
of 74 - the tree was never broken for the thirty-seven hours `main` was red,
the store was.

So the old line - which named no step - asked every reader to tell those 93
from the 16 that were something else by opening the run, and a container whose
egress policy blocks GitHub's log storage cannot open it at all. Naming the step
is one extra request, paid only on the runs that were already going to print a
line, and it separates "stop, the tree is broken" from "an item wants closing".
It is about 330 ms in practice, and its worst case is a second `TIMEOUT_S` -
so a session start reading a red `main` can wait 16 s rather than 8 s before the
line appears, and spends two of the 60 requests an hour an unauthenticated
caller gets rather than one. Both ceilings are paid only in the case the reader
most needs the answer, and never on a green `main`, which is every session start
but a few.

**Why the rate itself is left alone.** Over the narrower window `PL-T83R` was
filed on - 2026-09-05 to 2026-09-16, holding 74 of the 109 failures above -
`main` failed on 32.7% of the pushes that reached a verdict, which reads like a
check firing so often that nobody could act on it. It is an artifact of counting merges: the 74
failures are 8 episodes, and 2 of them - 37.7 h and 44.3 h - hold 87% of the
red time, because merges keep arriving while `main` is red. Each of those two
ended in a single cheap commit (`#432` closed two items whose work had landed;
`#493` rewrote one command that did not discriminate). What was wrong was the
time to green, not the count. Suppressing the class would have cost every one
of the 93 findings, all of which were real and all of which somebody later
fixed, so the rate is accepted and the line made precise instead.

Standard library only, and parsing at the 3.11 floor `tools/ruff.toml` sets, so
a bare checkout with no virtualenv can run it — from the session-start hook, or
by hand at any moment, which is the half a hook alone cannot give: `main` can
go red *during* a session that started while it was green.
"""

from __future__ import annotations

import http.client
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

# This file's own repository, not the caller's working directory: the hook runs
# it from wherever a session started, and `git remote` would otherwise answer
# for a different checkout or for nothing at all.
ROOT = Path(__file__).resolve().parents[1]

# Every way a read of the API can fail, and it is a named tuple rather than an
# inline one because both call sites have to catch the same set: a gap in either
# loses the line. `urllib.error.URLError`, `HTTPError`, `TimeoutError` and
# `ConnectionResetError` are all `OSError`; `json.JSONDecodeError` is a
# `ValueError`. `http.client.HTTPException` is neither, which is the one worth
# writing down - a body GitHub cuts short raises `IncompleteRead`, a bare
# `Exception` subclass, and it would otherwise escape both.
NETWORK_FAILURES = (OSError, ValueError, http.client.HTTPException)

API = "https://api.github.com"
WORKFLOW = "quality.yml"
BRANCH = "main"
TIMEOUT_S = 8

# A conclusion that judged the tree. `cancelled` and `skipped` did not, and
# `None` is a run still going.
VERDICTS = ("success", "failure", "timed_out", "startup_failure", "action_required")

# The name `.github/workflows/quality.yml` gives the whole-store replay step,
# which is the one step whose failure is a fact about the queue rather than
# about the tree. Matched as a literal because that is what the API returns;
# `tests/unit/test_main_ci_status.py` holds it to the workflow file, so a rename
# there fails a test rather than silently dropping this back to the plain line.
REPLAY_STEP = "verify replay, the whole store"

# The name GitHub derives from the bare `- run: bin/docket check` line, which
# has no `name:` of its own. It is the same store validation without `--verify`,
# and it runs earlier in the same job on the same tree, so its *passing* is what
# narrows a replay failure to the one report `--verify` adds. Held to the
# workflow by a test alongside `REPLAY_STEP`.
BARE_CHECK_STEP = "Run bin/docket check"

# `skipped` is every step after the failure, and `cancelled` is a job that lost
# its runner. Neither names a cause, and printing them would bury the one that
# does. `timed_out` is a failure but not an answer - a step the 15-minute job
# timeout killed says nothing about what it would have found - so it is read as
# a failure and never as grounds for the queue reading below.
#
# Whether GitHub reports a timeout-killed step as `timed_out` or as `cancelled`
# is an assumption rather than an observation: all 93 recorded replay failures
# concluded `failure`, so the case has never occurred here. It is handled in the
# direction that costs a sentence rather than the one that prints a false one -
# under either answer the queue reading is withheld, since `cancelled` is not in
# this tuple and so the replay does not read as the only failing step.
STEP_FAILURES = ("failure", "timed_out")

# What a step whose name the payload does not carry is called. A name that is
# not a string would otherwise be dropped, and dropping one *failing* step turns
# two failures into the single failure the queue reading is conditioned on -
# manufacturing the one shape that licenses the strongest sentence here.
UNNAMED_STEP = "(a step whose name could not be read)"

# A step with no `name:` is named by GitHub after its whole `run:` line, and
# `quality.yml`'s pytest line is 150 characters of shell. Printed whole at the
# top of a session it buries the run number and the URL either side of it, so it
# is cut - visibly, with an ellipsis, because a shell command truncated to look
# complete is worse than one that says it was cut. 70 keeps every named step in
# the workflow whole; only the unnamed `run:` lines reach it.
STEP_WIDTH = 70

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


def step_conclusions(jobs: list[object]) -> tuple[tuple[str, str], ...]:
    """Every step's (name, conclusion), in the order CI ran them.

    Empty for a payload this cannot read - a run whose jobs were never created,
    a shape the API has promised nothing about, a job that was cancelled. The
    caller degrades to the unattributed line rather than guessing, because the
    fact that `main` is red is already established by the time this is asked and
    must not be lost to a failure of the enrichment.

    A step carrying no readable name still takes a row, under `UNNAMED_STEP`.
    Leaving it out would shorten the failing set, and the length of that set is
    exactly what `advisory` conditions its strongest sentence on.
    """
    out: list[tuple[str, str]] = []
    for job in jobs:
        if not isinstance(job, dict):
            continue
        steps = job.get("steps")
        if not isinstance(steps, list):
            continue
        for step in steps:
            if not isinstance(step, dict):
                continue
            conclusion = step.get("conclusion")
            if not isinstance(conclusion, str):
                continue
            name = step.get("name")
            out.append((name if isinstance(name, str) else UNNAMED_STEP, conclusion))
    return tuple(out)


def failing_steps(steps: tuple[tuple[str, str], ...]) -> tuple[str, ...]:
    """The names of the steps that did not pass, in run order."""
    return tuple(name for name, conclusion in steps if conclusion in STEP_FAILURES)


# GitHub appends one of these per `uses:` action, to run its cleanup, and names
# it `Post ` plus the step it follows. They are skipped along with everything
# else below a failure, and counting them inflates the number the line prints:
# measured across the 93 recorded replay failures, every one carries exactly two,
# so an unfiltered count says six to eleven where the truth is four to nine.
# A step of this repository's own that began with `Post ` would be excluded too,
# and that error runs the safe way - it under-counts what was skipped, where the
# bug being fixed over-counted it.
_CLEANUP_PREFIX = "Post "


def unrun_after(steps: tuple[tuple[str, str], ...], name: str) -> int:
    """How many of the job's own steps after `name` never ran, its failure skipping them.

    Load-bearing rather than decoration. `quality.yml` puts four to nine checks
    *below* the replay - `contrast_check`, `import_boundary_check`,
    `core_vocabulary_check` and `glyph_check` among them, all of which read
    `src/` and `app/` - and a failing step skips every one. So a replay failure
    leaves those unrun, and a line that called the tree clean on the strength of
    the steps above it would be claiming a guarantee nobody checked.

    The number is printed, so it is the repository's own steps rather than every
    skipped row: `_CLEANUP_PREFIX` says why.
    """
    for index, (step, _) in enumerate(steps):
        if step == name:
            return sum(
                1
                for later, c in steps[index + 1 :]
                if c == "skipped" and not later.startswith(_CLEANUP_PREFIX)
            )
    return 0


def _quoted(step: str) -> str:
    """One step name, quoted and cut to `STEP_WIDTH` with the cut made visible."""
    if len(step) <= STEP_WIDTH:
        return f'"{step}"'
    return f'"{step[: STEP_WIDTH - 1].rstrip()}..." (cut)'


def _is_queue_failure(run: dict[str, object], steps: tuple[tuple[str, str], ...]) -> bool:
    """Whether the replay failing is attributable to an item's own `verify:` command.

    Three conditions, and every one is read from this run rather than assumed
    from the base rate:

    1. the run itself concluded `failure`, not `timed_out` or anything else;
    2. the replay is the *only* step that did not pass, and it `failure`d rather
       than being killed by the job timeout - a hung command says nothing about
       what it would have found;
    3. `bin/docket check` ran earlier in the same job, on the same tree, and
       passed. That is the whole of the argument: the bare run is the same store
       validation without `--verify`, so it has already ruled out every store
       error that does not need the flag, and what is left is the one report the
       flag adds.

    Any of the three missing and the caller names the steps and interprets
    nothing.
    """
    if run.get("conclusion") != "failure":
        return False
    if failing_steps(steps) != (REPLAY_STEP,):
        return False
    if any(name == REPLAY_STEP and conclusion != "failure" for name, conclusion in steps):
        return False
    return any(name == BARE_CHECK_STEP and conclusion == "success" for name, conclusion in steps)


def advisory(run: dict[str, object], steps: tuple[tuple[str, str], ...] = ()) -> str | None:
    """Return the line to print for a run, or None when it says nothing useful.

    Only a non-`success` verdict earns a line. The head sha is included because
    a reader's first question is whether the failure is still `main`'s head or
    something already pushed past; `steps` answers the second, which is whether
    this is the tree or the queue.

    **The queue reading never claims the tree is clean**, and that distinction is
    the point rather than a hedge. What can be said is that the replay was the
    only step that failed and that the checks above it passed. What cannot is
    that the tree is sound, because the replay's own failure skipped every check
    below it - `unrun_after` counts them and the line says so, so a reader is
    never handed a green they did not get.
    """
    conclusion = run.get("conclusion")
    if conclusion == "success":
        return None
    number = run.get("run_number", "?")
    sha = str(run.get("head_sha", ""))[:8] or "?"
    url = run.get("html_url", "")
    head = f"main's quality run #{number} on {sha} concluded {conclusion}"
    if _is_queue_failure(run, steps):
        unrun = unrun_after(steps, REPLAY_STEP)
        tail = (
            f" The {unrun} step(s) below it were skipped, so they are unrun rather than green."
            if unrun
            else ""
        )
        return (
            f'{head} at "{REPLAY_STEP}", the only step that failed; `bin/docket check` passed '
            "above it on the same tree, so this is an open item's `verify:` command that has "
            "flipped to passing rather than the tree. `bin/docket check --verify` reproduces "
            f"it here.{tail} {url}"
        )
    failed = failing_steps(steps)
    where = f" at {', '.join(_quoted(name) for name in failed)}" if failed else ""
    return f"{head}{where} - main is red and no pull request will show it. {url}"


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


def fetch_jobs(slug: str, run_id: object) -> list[object]:
    """Fetch one run's jobs, for the names of the steps that failed.

    A second request, and it is paid only on a run that is already going to
    print a line - never on a green `main`, which is every session start but a
    few. Unauthenticated like `fetch_runs`, and for the same reason.
    """
    url = f"{API}/repos/{slug}/actions/runs/{run_id}/jobs?per_page=50"
    request = urllib.request.Request(
        url, headers={"Accept": "application/vnd.github+json", "User-Agent": "docket-digest"}
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
        payload = json.load(response)
    jobs = payload.get("jobs")
    return jobs if isinstance(jobs, list) else []


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
    except NETWORK_FAILURES:
        return 0

    run = pick_run(runs)
    if run is None:
        return 0

    # Asked only once the verdict is known to be a failure, and swallowed
    # separately from the fetch above: by this point `main` is red and the
    # reader is owed that whether or not the attribution can be read.
    steps: tuple[tuple[str, str], ...] = ()
    if run.get("conclusion") != "success":
        try:
            steps = step_conclusions(fetch_jobs(slug, run.get("id")))
        except NETWORK_FAILURES:
            steps = ()

    line = advisory(run, steps)
    if line is not None:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
