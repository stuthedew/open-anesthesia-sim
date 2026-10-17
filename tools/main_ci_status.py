#!/usr/bin/env python3
"""Say when the default branch's last quality run failed or was cancelled, and otherwise nothing.

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
nothing while CI's pytest step time stays inside its band (below). A checkout
with no remote, or with a remote that is not GitHub, prints nothing either,
because it has no Actions API to read. `CLAUDE.md` is explicit that a check
firing every run without changing a decision is a defect in the check, and this
one is read at the top of every session, where a routine line would train a
reader to skim exactly the region a real advisory appears in. When the API
cannot be read, because there is no network or the response is rate-limited or
malformed, the verdict lines stay silent and the pytest line says that it could
not compare the time (`PL-YY32`).

Two consequences of that rule are worth stating, because both look like gaps:

- **A `cancelled` run is not a verdict, but one newer than every verdict is
  reported**, and so is one that concluded `action_required`, which ran no step
  to a verdict either (`PL-351H`). The verdict reported is the newest run that
  actually *reached* a conclusion, the most recent real answer about `main`.
  Until `PL-SMN4` every push to `main` shared one concurrency group, so a merge
  arriving while an earlier one was still pending evicted it: 31 of the 257
  completed `main` push runs between 2026-09-05 and 2026-09-16 - 12.1% - were
  cancelled that way. A per-commit group ended the eviction, and none of the
  640 completed from its merge to 2026-10-01 was cancelled, so one now means a
  hand cancellation or a lost runner, and its commit has no whole-store verdict
  at all. Passing over it in silence reported an older commit's verdict as
  `main`'s answer (`PL-JTHW`), so a cancelled run newer than every verdict
  prints a line of its own, naming both runs and asking for a re-run. One older
  than a verdict still prints nothing: the later run checked the whole store
  again on a tree that contains it, so there is nothing to ask for, and a green
  `main` prints nothing.
- **Silence is not a green tree.** It means "no failing verdict, and no
  cancelled run newer than the verdict, was readable from here", which is also
  what a checkout with no GitHub remote gets. The line exists to surface a red
  nobody would otherwise see, never to certify a green one.

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

**It also says when CI's pytest step has drifted from its baseline**
(`PL-YY32`). The pytest step of `quality.yml`'s `checks` job took 48 s on
2026-09-05, about 125 s in mid-September and about 500 s by 2026-10-17. Since
`PL-T9X9` the suite runs in two parts, each the pytest step of its own job, and
the step's time is the sum of the two. Nothing
read the trend, and `PL-H9KW` was filed by feel a month in. So this script takes
the step's median time over `main`'s newest `PYTEST_RUNS` successful runs and
compares it with `PYTEST_BASELINE_S`. It prints a line only when the median
falls outside `PYTEST_BAND`. Above the band, something has slowed the suite.
Below it, the baseline is out of date, and a baseline set too high cannot catch
the next slowdown. The comments on those three constants give the measurements
behind them.

The step's time is in each run's jobs payload, not in the list of runs, so this
line costs `PYTEST_RUNS` more requests at every session start. They are sent at
once, on threads, so they add about the time of one, which was 0.6 s from a
cloud container on 2026-10-17. Every other request here
is paid only when a line will print, but the median is itself the reading, so
it cannot wait for one. When any of the reads fails, the line says so and gives
no figure, because a figure from an earlier read could be out of date.

Standard library only, and parsing at the 3.11 floor `tools/ruff.toml` sets, so
a bare checkout with no virtualenv can run it — from the session-start hook, or
by hand at any moment, which is the half a hook alone cannot give: `main` can
go red *during* a session that started while it was green.
"""

from __future__ import annotations

import http.client
import json
import statistics
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

# This file's own repository, not the caller's working directory: the hook runs
# it from wherever a session started, and `git remote` would otherwise answer
# for a different checkout or for nothing at all.
ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.lines import record_text  # noqa: E402
from docket.vcs import REMOTE, default_branch, github_slug  # noqa: E402

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
TIMEOUT_S = 8

#: The conclusions that are a verdict against a commit, for a workflow run here
#: and for a check run in `update_armed.py`, which imports it (`PL-351H`).
#: `cancelled` and `action_required` are not: neither ran the steps to the end,
#: so neither says the change is wrong. `action_required` sat in `VERDICTS` until
#: then, so a run GitHub held for an action was printed as "main is red" while
#: `update_armed.py` read the same conclusion as not failed.
FAILED = frozenset({"failure", "timed_out", "startup_failure"})

# A conclusion that judged the tree. `skipped` did not, `None` is a run still
# going, and `UNJUDGED` are the two that leave a commit with no verdict at all.
VERDICTS = frozenset({"success"} | FAILED)

# A run that ended without judging the tree, and how the line says so. Newer
# than every verdict, its commit has none, which the line below reports rather
# than letting an older commit's verdict stand as `main`'s (`PL-JTHW`).
UNJUDGED = {"cancelled": "was cancelled", "action_required": "concluded action_required"}

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

# The start of the name GitHub gives each pytest step in `quality.yml`. The steps
# have no `name:`, so GitHub names each `Run ` plus its whole `run:` line. Only
# the start is matched, so a change to the flags after it does not lose a step.
# `tests/unit/test_main_ci_status.py` holds it to the workflow, so naming a
# pytest step fails a test.
PYTEST_STEP_PREFIX = "Run uv run pytest"

#: How many of `main`'s newest successful runs the pytest step's median is taken
#: over. Each run costs a request. Over the 100 runs `PYTEST_BASELINE_S` was
#: measured on, a median of three would have reached the band's lower bound once,
#: at 0.50, while a median of five never went below 0.59 (`PL-YY32`).
PYTEST_RUNS = 5

#: The pytest step's time, in seconds, that the median is compared with. It is
#: the median of the step's time over `main`'s 100 successful push runs from #4906
#: to #5440 (2026-10-11 06:07Z to 2026-10-17 16:07Z), which was 471.5 s. The
#: last 16 of those runs came after `PL-H9KW`'s two test-time changes merged
#: (#1486 and #1487). Their median was 502.5 s, 1.07 times this baseline, so those
#: changes left the step inside the band. When a change moves the step's time on
#: purpose, measure this again the same way: the median over at least the newest
#: 100 successful push runs.
PYTEST_BASELINE_S = 470

#: The band, as fractions of `PYTEST_BASELINE_S`, inside which the line stays
#: silent. About a third of runs land on a runner that finishes the step in about
#: 0.57 of the others' time. The job payload names no machine type, so that cause
#: is inferred. Over the same 100 runs, the median of five consecutive runs ranged
#: from 0.59 to 1.16 times 471.5 s, so the line would have stayed silent on all 96
#: such windows. Read on every fourth run against a baseline set on 2026-09-16,
#: the upper bound would have fired on 2026-09-23, at run #2879. `PL-H9KW` was
#: filed 24 days later.
PYTEST_BAND = (0.5, 1.3)


def repo_slug(remote_url: str) -> str | None:
    """Return `owner/repo` for a GitHub remote, or None for anything else.

    Both forms this repository is cloned with reach here — `https://github.com/
    owner/repo.git` from CI and containers, `git@github.com:owner/repo.git` from
    a workstation — and a non-GitHub remote returns None so the caller stays
    silent rather than guessing at an API that is not there.
    """
    return github_slug(remote_url)


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


def pick_unjudged(runs: list[object]) -> dict[str, object] | None:
    """Return the newest `UNJUDGED` run newer than every verdict, or None.

    Its commit has no whole-store verdict, and whatever `pick_run` answers - or
    the silence of a green answer - is about an older commit, which a reader
    would otherwise take as `main`'s (`PL-JTHW`). Several cancelled above the
    verdict return the newest, because re-running it checks the whole store
    again on a tree that contains the rest.

    A cancelled run *older* than a verdict returns None, which is the
    green-`main`-prints-nothing rule rather than a gap: the later run checked
    the whole store on a tree that contains it, so a re-run would answer
    nothing the verdict has not.
    """
    for run in runs:
        if not isinstance(run, dict):
            continue
        conclusion = run.get("conclusion")
        if conclusion in VERDICTS:
            return None
        if conclusion in UNJUDGED:
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


def _short_sha(run: dict[str, object]) -> str:
    """The run's head commit as a line prints it, or `?` when the payload carries none."""
    return str(run.get("head_sha", ""))[:8] or "?"


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
    sha = _short_sha(run)
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


def unjudged_advisory(cancelled: dict[str, object], verdict: dict[str, object] | None) -> str:
    """The line for an `UNJUDGED` run newer than every verdict, from `pick_unjudged`.

    It names the newest verdict as well as the cancelled run, because which
    commit each answer is about is the reader's whole question. The action is
    a re-run, with one exception the line states rather than detects: a newer
    merge's run still going will answer for the commit too, and the completed
    runs `fetch_runs` asks for cannot show one.
    """
    number = cancelled.get("run_number", "?")
    url = cancelled.get("html_url", "")
    if verdict is None:
        older = "and no run readable here reached one"
    else:
        older = (
            f"and the newest run that reached one, #{verdict.get('run_number', '?')} on "
            f"{_short_sha(verdict)}, checked an older commit"
        )
    ended = UNJUDGED.get(str(cancelled.get("conclusion")), "reached no verdict")
    return (
        f"main's quality run #{number} on {_short_sha(cancelled)} {ended}, so that "
        f"commit has no whole-store verdict, {older}. Re-run it, unless a newer merge's run "
        f"is still going: {url}"
    )


def _instant(value: object) -> datetime | None:
    """Parse a timestamp from the API, or return None when the payload has none."""
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def pytest_seconds(jobs: list[object]) -> float | None:
    """Return the summed time of the run's pytest steps, or None where one cannot be read.

    Since `PL-T9X9` the suite runs in parts, one pytest step in each part's
    job, so the sum is about what the one step took before the split. A run
    from before the split has one step, and its time is read the same way. A
    step that did not end in `success` returns None too. A step that failed or
    was cancelled stopped early, so its time would understate the suite. A job
    whose steps cannot be read returns None, since it may hold a pytest step.
    """
    total = 0.0
    found = False
    for job in jobs:
        steps = job.get("steps") if isinstance(job, dict) else None
        if not isinstance(steps, list):
            return None
        for step in steps:
            if not isinstance(step, dict):
                continue
            name = step.get("name")
            if not isinstance(name, str) or not name.startswith(PYTEST_STEP_PREFIX):
                continue
            if step.get("conclusion") != "success":
                return None
            started = _instant(step.get("started_at"))
            completed = _instant(step.get("completed_at"))
            if started is None or completed is None:
                return None
            total += (completed - started).total_seconds()
            found = True
    return total if found else None


def pytest_declined(reason: str) -> str:
    """Return the line for a pytest time that could not be compared. It never gives a figure."""
    return (
        f"CI's pytest step time was not compared with its {PYTEST_BASELINE_S} s baseline, "
        f"because {reason}."
    )


def pytest_advisory(seconds: list[float], runs: list[dict[str, object]]) -> str | None:
    """Return the line for the pytest step's median, or None while it sits inside the band.

    `seconds` holds the step's time in each of `runs`, which are newest first.
    The band's bounds are inside it, so a median exactly on one is silent.
    """
    median = statistics.median(seconds)
    ratio = median / PYTEST_BASELINE_S
    low, high = PYTEST_BAND
    if low <= ratio <= high:
        return None
    if ratio > high:
        action = (
            "Find what slowed it. If the change is meant, measure a new PYTEST_BASELINE_S "
            "as its comment in tools/main_ci_status.py says."
        )
    else:
        action = (
            "Measure a new PYTEST_BASELINE_S as its comment in tools/main_ci_status.py "
            "says, or the band cannot catch the next slowdown."
        )
    newest, oldest = runs[0], runs[-1]
    return (
        f"CI's pytest step has drifted from its baseline. Its median over main's last "
        f"{len(runs)} successful runs (#{newest.get('run_number', '?')} back to "
        f"#{oldest.get('run_number', '?')}) is {median:.0f} s, which is {ratio:.2f} times "
        f"the {PYTEST_BASELINE_S} s baseline and outside the band of {low} to {high} times. "
        f"{action} {newest.get('html_url', '')}"
    )


def pytest_time_line(slug: str, runs: list[object]) -> str | None:
    """Return the pytest line for this page of runs, or None while the median is in the band.

    It reads the newest `PYTEST_RUNS` runs that concluded `success`, so the
    pytest step ran to its end in every one. With fewer, it declines rather than
    take the median of a smaller set, so the figure always means the same thing.
    """
    successful = [
        run for run in runs if isinstance(run, dict) and run.get("conclusion") == "success"
    ][:PYTEST_RUNS]
    if len(successful) < PYTEST_RUNS:
        return pytest_declined(
            f"only {len(successful)} of main's last {len(runs)} completed runs succeeded, "
            f"and the median needs {PYTEST_RUNS}"
        )
    try:
        with ThreadPoolExecutor(max_workers=PYTEST_RUNS) as pool:
            payloads = list(pool.map(lambda run: fetch_jobs(slug, run.get("id")), successful))
    except NETWORK_FAILURES as error:
        return pytest_declined(f"the Actions API could not be read ({error})")
    seconds: list[float] = []
    for run, jobs in zip(successful, payloads, strict=True):
        time = pytest_seconds(jobs)
        if time is None:
            return pytest_declined(
                f"run #{run.get('run_number', '?')} has a pytest step that did not finish, "
                "or none that could be read"
            )
        seconds.append(time)
    return pytest_advisory(seconds, successful)


def fetch_runs(slug: str) -> list[object]:
    """Fetch recent completed `quality.yml` runs on the default branch.

    The branch is `vcs.default_branch`'s, the one docket compares against,
    rather than a literal of this script's own (`PL-9KLN`).

    Unauthenticated: this repository is public, so no token is needed and none
    is read, which keeps the script runnable from a bare checkout and keeps a
    credential out of a session-start path.
    """
    url = (
        f"{API}/repos/{slug}/actions/workflows/{WORKFLOW}/runs"
        f"?branch={default_branch(ROOT)}&event=push&status=completed&per_page=10"
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
        remote = record_text(
            subprocess.run(
                ["git", "remote", "get-url", REMOTE],
                capture_output=True,
                timeout=TIMEOUT_S,
                check=True,
                cwd=ROOT,
            ).stdout
        )
    except (OSError, subprocess.SubprocessError):
        return 0

    slug = repo_slug(remote)
    if slug is None:
        return 0

    try:
        runs = fetch_runs(slug)
    except NETWORK_FAILURES as error:
        # The verdict lines stay silent, as they always have offline. The pytest
        # line says it could not compare, so its silence still means "inside the
        # band" (`PL-YY32`).
        print(pytest_declined(f"the Actions API could not be read ({error})"))
        return 0

    run = pick_run(runs)

    # First, because it is about a newer commit than any verdict line below it,
    # and whatever that verdict is: under a green one it is the only verdict line.
    cancelled = pick_unjudged(runs)
    if cancelled is not None:
        print(unjudged_advisory(cancelled, run))

    if run is not None:
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

    # Last, because a slow suite matters less than a red `main` or a commit with
    # no verdict.
    time_line = pytest_time_line(slug, runs)
    if time_line is not None:
        print(time_line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
