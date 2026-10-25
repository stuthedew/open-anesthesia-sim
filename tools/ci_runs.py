"""Keep `docs/ci-runs.tsv`, the record of this repository's CI runs, from being lost (`PL-4SFQ`).

GitHub deletes a workflow run 90 days after it ran. The model review scores a
closed item partly by the red CI runs on its pull request, and that evidence
would be gone before a 90-day design item is scored. So the review copies the
run history into `docs/ci-runs.tsv`, one row per run, and this tool does the
copying, so that no model retypes a value.

`python3 tools/ci_runs.py refresh` asks GitHub for every run created on or after
the day before the newest row's date, one day at a time, and rewrites the file.
A run already in the file is replaced by what GitHub says now, so a later
attempt updates its row. The one exception is the link to a pull request:
GitHub drops it once the pull request's branch is deleted, so a known link is
kept. A row whose run
GitHub no longer returns is kept, since keeping it is the point of the file. A
run still in progress is left out until a later refresh finds it finished.

GitHub's run listing returns at most 1,000 runs for one query, so each query
covers one day. A day that reaches the cap is refused rather than read short,
because a missing run reads exactly like a run that never happened. On
2026-10-24 the busiest day held 361 runs.

The API is read through `open_pull_requests.api_request`, the one client
`tools/fact_home_check.py` allows.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterable, Sequence
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.vcs import github_token  # noqa: E402

from open_pull_requests import (  # noqa: E402
    GITHUB_API,
    LOOKUP_TIMEOUT,
    PAGE,
    api_request,
    repo_slug,
)

RUNS = ROOT / "docs" / "ci-runs.tsv"

#: The file's columns, in order. `workflow` is the workflow's name, and
#: `pull_requests` the numbers GitHub links to the run, separated by commas.
COLUMNS = (
    "run_id",
    "workflow",
    "run_number",
    "attempt",
    "event",
    "head_branch",
    "head_sha",
    "pull_requests",
    "status",
    "conclusion",
    "created_at",
    "updated_at",
)

#: The most runs GitHub's listing returns for one query, however it is paged.
LISTING_CAP = 1000

Row = dict[str, str]
#: Reads one page of the run listing for a query, returning the decoded JSON.
Reader = Callable[[dict[str, str | int]], dict[str, object]]


class RefreshFailed(Exception):
    """GitHub's answer could not be used, so the file was left as it was."""


def row_of(run: dict[str, object]) -> Row:
    """The file's row for one run as GitHub's listing describes it."""

    linked = run.get("pull_requests")
    entries = linked if isinstance(linked, list) else []
    numbers = [str(entry["number"]) for entry in entries if isinstance(entry, dict)]
    return {
        "run_id": str(run["id"]),
        "workflow": str(run.get("name") or ""),
        "run_number": str(run["run_number"]),
        "attempt": str(run.get("run_attempt") or 1),
        "event": str(run.get("event") or ""),
        "head_branch": str(run.get("head_branch") or ""),
        "head_sha": str(run.get("head_sha") or ""),
        "pull_requests": ",".join(numbers),
        "status": str(run["status"]),
        "conclusion": str(run.get("conclusion") or ""),
        "created_at": str(run["created_at"]),
        "updated_at": str(run.get("updated_at") or ""),
    }


def read_rows(path: Path) -> list[Row]:
    """Every row of the file, or none when it does not exist yet."""

    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != COLUMNS:
            raise RefreshFailed(f"{path} does not have the columns {', '.join(COLUMNS)}")
        return list(reader)


def write_rows(path: Path, rows: Iterable[Row]) -> None:
    """Write the rows in creation order, then by run id, with the header first."""

    ordered = sorted(rows, key=lambda row: (row["created_at"], int(row["run_id"])))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(ordered)


def runs_on(day: date, read: Reader) -> list[dict[str, object]]:
    """Every run GitHub lists as created on `day`, read a page at a time."""

    runs: list[dict[str, object]] = []
    page = 1
    while True:
        answer = read({"created": day.isoformat(), "per_page": PAGE, "page": page})
        listed = answer.get("workflow_runs")
        total = answer.get("total_count")
        if not isinstance(listed, list) or not isinstance(total, int):
            raise RefreshFailed(f"GitHub's listing for {day} was not a run listing")
        if total >= LISTING_CAP:
            raise RefreshFailed(
                f"{day} holds {total} runs, and GitHub lists at most {LISTING_CAP} for one query"
            )
        runs.extend(run for run in listed if isinstance(run, dict))
        if len(listed) < PAGE:
            return runs
        page += 1


def refresh(rows: list[Row], read: Reader, today: date) -> tuple[list[Row], int, int]:
    """The rows with every finished run since the newest row's day added or brought up to date.

    Returns the new rows, the count of runs added and the count updated.
    """

    by_id = {row["run_id"]: row for row in rows}
    newest = max((row["created_at"][:10] for row in rows), default=today.isoformat())
    day = date.fromisoformat(newest) - timedelta(days=1)
    added = updated = 0
    while day <= today:
        for run in runs_on(day, read):
            if run.get("status") != "completed":
                continue
            row = row_of(run)
            known = by_id.get(row["run_id"])
            if known and not row["pull_requests"]:
                # GitHub stops linking a run to its pull request once the head
                # branch is deleted, so an empty link never replaces a known one.
                row["pull_requests"] = known["pull_requests"]
            if known is None:
                added += 1
            elif known != row:
                updated += 1
            by_id[row["run_id"]] = row
        day += timedelta(days=1)
    return list(by_id.values()), added, updated


def github_reader(slug: str) -> Reader:
    """A reader of `slug`'s run listing from GitHub itself."""

    token = github_token()

    def read(query: dict[str, str | int]) -> dict[str, object]:
        url = f"{GITHUB_API}/repos/{slug}/actions/runs?{urllib.parse.urlencode(query)}"
        request = api_request(url, agent="ci_runs", token=token)
        try:
            with urllib.request.urlopen(request, timeout=LOOKUP_TIMEOUT * 3) as response:
                answer = json.loads(response.read())
        except (OSError, ValueError) as error:
            raise RefreshFailed(f"GitHub could not be read ({error})") from error
        if not isinstance(answer, dict):
            raise RefreshFailed("GitHub's answer was not a run listing")
        return answer

    return read


def main(argv: Sequence[str] | None = None) -> int:
    """Refresh the file, print what changed, and exit 1 when it could not."""

    parser = argparse.ArgumentParser(description="keep docs/ci-runs.tsv, the CI run history")
    parser.add_argument("command", choices=("refresh",))
    parser.parse_args(argv)
    slug = repo_slug()
    if slug is None:
        print("ci_runs: origin is not a GitHub repository, so there is no run history to read")
        return 1
    try:
        rows = read_rows(RUNS)
        fresh, added, updated = refresh(rows, github_reader(slug), date.today())
    except RefreshFailed as failure:
        print(f"ci_runs: {failure}; {RUNS.name} was left as it was")
        return 1
    write_rows(RUNS, fresh)
    print(f"ci_runs: {len(fresh)} runs in {RUNS.name}, {added} added and {updated} updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
