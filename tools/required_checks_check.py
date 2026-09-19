"""Reconcile the jobs that report a status check on `pull_request` against the required list.

Branch protection matches a required status check by **name**, and that list
lives in repository settings rather than in the tree. So the two sides drift
independently, in two directions, and this repository has been hurt by both:

- **Removing or renaming** a reporting job orphans the requirement named after
  it. Nothing reports it, so every pull request waits forever on a check that
  cannot arrive - pending rather than failing, which does not look like a
  break. `PL-D551` deleting `quality.yml`'s `floor` job did exactly that; it
  cost the project owner a manual merge and cost a session a wrong diagnosis
  (`PL-KPP1`, `#377`).
- **Adding** one creates a check that nothing makes required. `PL-3V8K` split
  the title check out of `checks` into its own job, for a correct and unrelated
  reason, and thereby moved it out from behind the only requirement that had
  been gating it. It stayed ungated for eleven releases, and `#654` merged on a
  failed `pr-title` because of it (`PL-H8YD`).

Until this check, the whole remedy was a comment beside each job key, and both
comments said the same thing: "the required list lives in repository settings,
which no script here can read, so nothing in `make check` or CI will catch the
next one."

**That premise was true of `make check` and false of CI, and it was false for a
narrower reason than anyone had looked for.** `PL-XZD0` was filed expecting the
answer to turn on a credential - `GET /repos/{owner}/{repo}/branches/{branch}/protection`
needs the `administration` permission, which an Actions `GITHUB_TOKEN` can
never hold, because `administration` is not one of the keys a workflow's
`permissions:` block may set. That route is genuinely closed, and `PL-N5WZ` is
this project's recorded dead end on adjacent terrain.

The route that is open needs no credential at all. `GET /repos/{owner}/{repo}/branches/{branch}`
carries `protection.required_status_checks.contexts`, and on a public
repository it answers **unauthenticated**. Measured 2026-09-19 against this
repository with every token stripped from the environment:

    $ env -u GH_TOKEN -u GITHUB_TOKEN curl -s \\
        https://api.github.com/repos/stuthedew/open-anesthesia-sim/branches/main
    "protection": {"required_status_checks": {"contexts": ["checks", "pr-title"], ...

while `.../branches/main/protection` returned 403 `Resource not accessible by
integration` to the same non-admin token in the same minute. So the guard costs
no secret, no permission grant, and no widening of anything - which is what
decided `PL-XZD0` in favour of building it rather than leaving the comments to
stand.

**Both settings surfaces are read, because only one of them holds the answer
today and GitHub is steering the other way.** This repository has one active
ruleset (`Base`, created 2026-08-23) that carries `deletion`, `pull_request`
and `non_fast_forward` rules and **no** `required_status_checks` rule, so the
required contexts live in classic branch protection. Move that setting into the
ruleset - which the GitHub UI encourages - and the classic block would go empty
while the ruleset filled. A check reading only one surface would then report
"nothing is required" and pass, which is the failure `CLAUDE.md` names
explicitly: a check that keeps passing while the guarantee it stands for is
void. So both are read and unioned, and **an empty union is a hard failure**
rather than a quiet pass: a repository whose workflows carry two load-bearing
job names while its settings require nothing is either a real regression or a
blind spot, and neither deserves silence.

**Why it is a step inside `checks` rather than a job of its own.** A new job
reports a new status check, which would itself have to be added to the required
list - the exact trap `PL-H8YD` records. Run as a step, it inherits the
requirement `checks` already carries and adds no name to reconcile. The check
that guards the list is therefore not an entry in it.

**Why it is not wired into `make check`.** Its input is not in the tree. `make
check` runs offline in a bare checkout, and a network call there would be slow,
flaky and wrong-headed; a tool whose answer lives in repository settings is a
CI tool by nature. Run it by hand with `python3 tools/required_checks_check.py`
when changing a job name.

**What it refuses to decide.** Matrix jobs expand into one check per
combination and reusable workflows report as `<caller> / <called>`; this parser
handles neither, and says so and exits non-zero rather than guessing a name.
Likewise an unreachable API is reported as unreachable and fails - distinctly
from a genuine disagreement - rather than passing on the assumption that
nothing has changed. `CLAUDE.md`: prefer an obvious failure to a plausible
answer when correctness cannot be established.

**The escape hatch is declared in the tree, where a reviewer reads it.** A job
that reports a check and is deliberately *not* required carries a
`# not-required: <reason>` line in the comment block above its key. Without one,
the first advisory-only job would make this check fire on every run, which is a
defect in the check rather than a finding - and a check nobody can act on is one
`CLAUDE.md` retires. With one, the exemption is a sentence a reviewer can weigh
instead of a silence.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

API_ROOT = "https://api.github.com"
API_VERSION = "2022-11-28"

# The events that make a job report a status check onto a pull request.
# `push` is deliberately absent: a job triggered only by `push` reports against
# the commit, never against the pull request, so a requirement naming it would
# never be satisfied on a branch. `drift.yml` is the worked example - it runs on
# `schedule` and `workflow_dispatch` and reports on no pull request at all.
PULL_REQUEST_EVENTS = frozenset({"pull_request", "pull_request_target"})

NOT_REQUIRED = re.compile(r"#\s*not-required:\s*(?P<reason>\S.*?)\s*$")


class Undecidable(Exception):
    """The tree holds a shape whose check name this parser will not guess."""


@dataclass(frozen=True)
class ReportingJob:
    """A job that reports a status check onto a pull request."""

    workflow: str
    job_id: str
    check_name: str
    not_required: str | None


def _key_at(line: str, indent: int) -> str | None:
    """Return the mapping key this line opens at `indent`, or None."""
    if len(line) - len(line.lstrip(" ")) != indent:
        return None
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or stripped.startswith("-"):
        return None
    if ":" not in stripped:
        return None
    key = stripped.split(":", 1)[0].strip()
    return key or None


def _triggers(lines: list[str]) -> set[str]:
    """Return the event names in the workflow's `on:` block.

    Three spellings are accepted, which are the three the YAML spec allows and
    the three this repository uses across its history: a block mapping, a flow
    sequence (`on: [push, pull_request]`), and a bare scalar (`on: push`).
    """
    for index, line in enumerate(lines):
        if _key_at(line, 0) != "on":
            continue
        inline = line.strip().split(":", 1)[1].strip()
        if inline.startswith("["):
            return {
                name.strip().strip("'\"") for name in inline.strip("[]").split(",") if name.strip()
            }
        if inline and not inline.startswith("#"):
            return {inline.strip("'\"")}
        events = set()
        for following in lines[index + 1 :]:
            if not following.strip() or following.lstrip().startswith("#"):
                continue
            if len(following) - len(following.lstrip(" ")) == 0:
                break
            key = _key_at(following, 2)
            if key is not None:
                events.add(key)
        return events
    raise Undecidable("no `on:` block at the top level")


def _jobs(lines: list[str], workflow: str) -> list[ReportingJob]:
    """Return every job in the workflow, with the check name it would report."""
    start = None
    for index, line in enumerate(lines):
        if _key_at(line, 0) == "jobs":
            start = index + 1
            break
    if start is None:
        raise Undecidable("no `jobs:` block at the top level")

    jobs: list[ReportingJob] = []
    comment_block: list[str] = []
    current: str | None = None
    display_name: str | None = None
    not_required: str | None = None

    def close() -> None:
        if current is None:
            return
        jobs.append(
            ReportingJob(
                workflow=workflow,
                job_id=current,
                check_name=display_name or current,
                not_required=not_required,
            )
        )

    for line in lines[start:]:
        indent = len(line) - len(line.lstrip(" "))
        if not line.strip():
            comment_block = []
            continue
        if line.lstrip().startswith("#"):
            if indent == 2:
                comment_block.append(line.strip())
            continue
        if indent == 0:
            break
        key = _key_at(line, 2)
        if key is not None:
            close()
            current, display_name = key, None
            not_required = None
            for comment in comment_block:
                match = NOT_REQUIRED.search(comment)
                if match:
                    not_required = match.group("reason")
            comment_block = []
            continue
        comment_block = []
        if current is None:
            continue
        inner = _key_at(line, 4)
        if inner == "name":
            display_name = line.strip().split(":", 1)[1].strip().strip("'\"")
        elif inner == "strategy":
            raise Undecidable(
                f"job `{current}` declares `strategy:` - a matrix expands into one check "
                "per combination, and this parser will not guess those names"
            )
        elif inner == "uses":
            raise Undecidable(
                f"job `{current}` calls a reusable workflow - its checks report as "
                "`<caller> / <called>`, which this parser will not guess"
            )
    close()
    return jobs


def reporting_jobs(workflow_dir: Path) -> list[ReportingJob]:
    """Return every job in the tree that reports a status check onto a pull request."""
    found: list[ReportingJob] = []
    for path in sorted(workflow_dir.glob("*.yml")) + sorted(workflow_dir.glob("*.yaml")):
        lines = path.read_text(encoding="utf-8").splitlines()
        try:
            if not (_triggers(lines) & PULL_REQUEST_EVENTS):
                continue
            found.extend(_jobs(lines, path.name))
        except Undecidable as exc:
            raise Undecidable(f"{path}: {exc}") from exc
    return found


def _get(url: str, token: str | None, attempts: int = 3) -> object:
    """GET a JSON document, retrying a transient failure before giving up.

    The token is optional and buys only rate limit: every endpoint read here
    answers unauthenticated on a public repository. In Actions it is the
    automatic `GITHUB_TOKEN`, which lifts the limit from 60 requests an hour per
    runner IP - shared across every runner - to 1,000 per hour for this
    repository, and that is the whole of what it is for.
    """
    # The URL is always this module's literal API root plus a repo slug.
    request = urllib.request.Request(url)
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", API_VERSION)
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            last = exc
            if attempt + 1 < attempts:
                time.sleep(2**attempt)
    raise RuntimeError(f"could not read {url}: {last}")


def required_contexts(repo: str, branch: str, token: str | None) -> tuple[set[str], list[str]]:
    """Return the required status check names on `branch`, and which surfaces held them.

    Both surfaces are read. Classic branch protection is where this repository
    keeps them today; rulesets are where GitHub's UI now steers, and a migration
    would empty one while filling the other with nothing to announce it.
    """
    contexts: set[str] = set()
    sources: list[str] = []

    branch_doc = _get(f"{API_ROOT}/repos/{repo}/branches/{branch}", token)
    protection: dict[str, object] = {}
    if isinstance(branch_doc, dict):
        protection = branch_doc.get("protection") or {}
    status_checks = protection.get("required_status_checks")
    classic = status_checks.get("contexts") or [] if isinstance(status_checks, dict) else []
    if classic:
        contexts.update(classic)
        sources.append("classic branch protection")

    rules = _get(f"{API_ROOT}/repos/{repo}/rules/branches/{branch}", token)
    from_rulesets: set[str] = set()
    if isinstance(rules, list):
        for rule in rules:
            if not isinstance(rule, dict) or rule.get("type") != "required_status_checks":
                continue
            parameters = rule.get("parameters") or {}
            for check in parameters.get("required_status_checks") or []:
                if isinstance(check, dict) and check.get("context"):
                    from_rulesets.add(check["context"])
    if from_rulesets:
        contexts.update(from_rulesets)
        sources.append("a ruleset")

    return contexts, sources


def reconcile(reporting: dict[str, ReportingJob], required: set[str]) -> list[tuple[str, str]]:
    """Compare the two sets and return `(headline, what it means)` for each disagreement.

    Pure, and deliberately separate from both the parse and the API read: this
    is the decidable half, so it is the half that can be tested without a tree
    or a network.
    """
    problems: list[tuple[str, str]] = []
    exempt = {name for name, job in reporting.items() if job.not_required}

    if not required:
        problems.append(
            (
                "no required status check is set on this branch, by either classic branch "
                "protection or a ruleset",
                "Every job above can go red without blocking a merge. Either the requirement "
                "was removed, or it moved to a surface this check does not read.",
            )
        )
        return problems

    orphaned = sorted(required - set(reporting))
    if orphaned:
        problems.append(
            (
                f"required but reported by no job: {', '.join(orphaned)}",
                "Nothing will ever report these, so every pull request waits on them forever - "
                "pending rather than failing. Rename the job back, or drop the requirement in "
                "settings.",
            )
        )

    ungated = sorted(set(reporting) - required - exempt)
    if ungated:
        problems.append(
            (
                f"reports on a pull request but is not required: {', '.join(ungated)}",
                "These can go red without blocking a merge. Add each to the required list in "
                "settings, or declare a `# not-required: <reason>` above the job key.",
            )
        )

    stale = sorted(exempt & required)
    if stale:
        problems.append(
            (
                f"declared `not-required` but required in settings: {', '.join(stale)}",
                "The comment and the setting disagree. Delete the comment, or drop the "
                "requirement.",
            )
        )

    return problems


def _repo_from_git(root: Path) -> str:
    """Return `owner/name` from the origin remote."""
    try:
        url = subprocess.run(
            ["git", "-C", str(root), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError("no --repo given and no origin remote to read one from") from exc
    match = re.search(r"github\.com[:/]+(?P<slug>[^/]+/[^/]+?)(?:\.git)?/?$", url)
    if not match:
        raise RuntimeError(f"cannot read owner/name out of the origin remote: {url}")
    return match.group("slug")


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY"),
        help="owner/name; defaults to $GITHUB_REPOSITORY, then to the origin remote",
    )
    parser.add_argument(
        "--branch",
        # On a `pull_request` run this is the branch the pull request targets,
        # which is exactly the branch whose protection is about to gate it. Off
        # a pull request there is no such branch, and `main` is the one every
        # trigger and the release process already name.
        default=os.environ.get("GITHUB_BASE_REF") or "main",
        help="the protected branch to read; defaults to $GITHUB_BASE_REF, then to main",
    )
    args = parser.parse_args(argv)

    repo = args.repo or _repo_from_git(root)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    try:
        jobs = reporting_jobs(root / ".github" / "workflows")
    except Undecidable as exc:
        print(f"required-checks: cannot decide what this tree reports - {exc}")
        print(
            "required-checks: reconcile the required list by hand, or teach this parser the shape."
        )
        return 1

    reporting = {job.check_name: job for job in jobs}

    try:
        required, sources = required_contexts(repo, args.branch, token)
    except RuntimeError as exc:
        print(f"required-checks: {exc}")
        print(
            "required-checks: the settings side could not be read, so nothing was compared. "
            "This is not a clean result - re-run it."
        )
        return 1

    print(f"required-checks: {repo} @ {args.branch}")
    for name, job in sorted(reporting.items()):
        mark = f"  (exempt: {job.not_required})" if job.not_required else ""
        print(f"  reports on a pull request: {name}  [{job.workflow}]{mark}")
    held = " and ".join(sources) if sources else "nothing"
    print(f"  required by {held}: {', '.join(sorted(required)) or '(none)'}")

    problems = reconcile(reporting, required)
    for headline, meaning in problems:
        print(f"required-checks: FAIL - {headline}")
        print(f"  {meaning}")
    if problems:
        return 1

    print("required-checks: OK - the two lists agree.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
