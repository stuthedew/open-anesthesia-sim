"""Write, review and check the repository's record of each headless worker run.

`tools/headless_worker.py` runs one `claude -p` worker per item on the monthly
API credit. Its output stays on the project owner's Mac, so nothing in the
repository said which items a headless worker did or how their reviews went.
This module owns that record (`PL-87BR`). The owner wants headless work and
chat-session work compared, so a difference in quality between them shows up
in the record (project owner, 2026-10-19).

Each run whose branch reached the remote gets one file,
`docs/worker-runs/<branch without claude/>-<started, %Y%m%dT%H%M%S>.json`. The
runner writes it with `write`, commits it to the worker's branch and pushes
it. One file per run means no two worker branches edit the same file. The
file holds the run's outcome as the runner reports it, without the clone's
local path, plus the run's four token counts. Its `review` starts as `null`.

The session that reviews the branch then runs

    python3 tools/worker_runs.py review <file> --outcome accepted --note "<one line>"

before it opens the pull request. `accepted` means the branch merged as the
worker left it, `fixed` means the reviewer committed fixes first, and
`sent-back` means it was not merged as it stood.

`python3 tools/worker_runs.py check` fails on a record with no review, and on
any field that does not match the format below. `make check` and CI run it,
so a worker's branch cannot go green until its review is written.

Standard library only, like every tool under `tools/`.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.config import load as load_config  # noqa: E402

#: Where the records live, relative to the repository root. `docket.toml`'s
#: `worker_runs_dir` is the one place the folder is spelled, because
#: `docket verify` reads it too, to treat a run's record as a sanctioned edit
#: (`PL-4WFK`).
RECORDS_DIR = Path(load_config(ROOT).worker_runs_dir)
if RECORDS_DIR == Path():
    raise SystemExit("worker-runs: docket.toml names no worker_runs_dir")

#: The run's fields and the JSON types each may hold. `None` stands for `null`.
#: The names match `headless_worker.Run`'s, so the runner copies them across.
RUN_FIELDS: dict[str, tuple[type, ...]] = {
    "item": (str,),
    "model": (str,),
    "effort": (str,),
    "branch": (str,),
    "started": (str,),
    "finished": (str,),
    "exit_code": (int, type(None)),
    "cost_usd": (float, int, type(None)),
    "is_error": (bool, type(None)),
    "subtype": (str, type(None)),
    "turns": (int, type(None)),
    "denials": (int, type(None)),
    "reason": (str, type(None)),
    "input_tokens": (int, type(None)),
    "cache_read_tokens": (int, type(None)),
    "cache_write_tokens": (int, type(None)),
    "output_tokens": (int, type(None)),
}

#: What a review may conclude.
OUTCOMES = ("accepted", "fixed", "sent-back")

#: The fields of a written review.
REVIEW_FIELDS = ("outcome", "note", "reviewed")

BRANCH_PREFIX = "claude/"

#: The one file in the directory that is not a record: it says what the records are.
README = "README.md"


def file_name(branch: str, started: str) -> str:
    """The record's file name, from the run's branch and its start time."""
    moment = datetime.fromisoformat(started)
    return f"{branch.removeprefix(BRANCH_PREFIX)}-{moment:%Y%m%dT%H%M%S}.json"


def run_problems(record: Mapping[str, object]) -> list[str]:
    """What is wrong with a record's run fields, or nothing."""
    found = []
    missing = [name for name in RUN_FIELDS if name not in record]
    extra = sorted(set(record) - set(RUN_FIELDS) - {"review"})
    if missing:
        found.append(f"missing {', '.join(missing)}")
    if extra:
        found.append(f"fields the format does not have: {', '.join(extra)}")
    for name, kinds in RUN_FIELDS.items():
        if name not in record:
            continue
        value = record[name]
        # JSON's true and false load as bool, which Python counts as an int.
        if not isinstance(value, kinds) or (isinstance(value, bool) and bool not in kinds):
            found.append(f"{name} is {json.dumps(value)}, not {_kinds(kinds)}")
    branch = record.get("branch")
    if isinstance(branch, str) and not branch.startswith(BRANCH_PREFIX):
        found.append(f"branch {branch} does not start with {BRANCH_PREFIX}")
    for name in ("started", "finished"):
        value = record.get(name)
        if isinstance(value, str) and _moment(value) is None:
            found.append(f"{name} {value} is not an ISO 8601 time with its UTC offset")
    return found


def review_problems(review: object) -> list[str]:
    """What is wrong with a record's review, or nothing."""
    if review is None:
        return [
            "has no review. Run `python3 tools/worker_runs.py review <file> "
            f'--outcome {"|".join(OUTCOMES)} --note "<one line>"` on the worker\'s branch'
        ]
    if not isinstance(review, dict) or sorted(review) != sorted(REVIEW_FIELDS):
        return [f"review must hold exactly {', '.join(REVIEW_FIELDS)}"]
    found = []
    if review["outcome"] not in OUTCOMES:
        found.append(f"review outcome {json.dumps(review['outcome'])} is not one of {OUTCOMES}")
    note = review["note"]
    if not isinstance(note, str) or not note.strip() or "\n" in note:
        found.append("review note must be one line of text")
    try:
        date.fromisoformat(str(review["reviewed"]))
    except ValueError:
        found.append(f"review date {json.dumps(review['reviewed'])} is not YYYY-MM-DD")
    return found


def write(root: Path, run: Mapping[str, object]) -> Path:
    """Write a new record of `run` under `root` with no review, and return its path.

    Refuses a run whose fields do not match the format, so the runner never
    commits a record that `check` would refuse for anything but its review.
    """
    found = run_problems(run)
    if found or "review" in run:
        raise ValueError(f"not a run record: {'; '.join(found) or 'it already has a review'}")
    path = root / RECORDS_DIR / file_name(str(run["branch"]), str(run["started"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_dump({**{name: run[name] for name in RUN_FIELDS}, "review": None}), "utf-8")
    return path


def review(path: Path, outcome: str, note: str, today: date) -> None:
    """Add the review's outcome to the record at `path`."""
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("review") is not None:
        raise ValueError(f"{path} already has a review; edit the file to change it")
    written = {"outcome": outcome, "note": " ".join(note.split()), "reviewed": today.isoformat()}
    found = run_problems(record) + review_problems(written)
    if found:
        raise ValueError(f"{path}: {'; '.join(found)}")
    path.write_text(_dump({**record, "review": written}), encoding="utf-8")


def check(root: Path) -> tuple[int, list[str]]:
    """How many records are under `root`, and each problem found in them."""
    directory = root / RECORDS_DIR
    paths = sorted(directory.glob("*")) if directory.is_dir() else []
    paths = [path for path in paths if path.name != README]
    found = []
    for path in paths:
        shown = path.relative_to(root).as_posix()
        if path.suffix != ".json" or not path.is_file():
            found.append(f"{shown}: only run records, as .json files, belong here")
            continue
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            found.append(f"{shown}: not JSON ({error})")
            continue
        if not isinstance(record, dict):
            found.append(f"{shown}: not a JSON object")
            continue
        problems = run_problems(record) + review_problems(record.get("review"))
        if not problems and path.name != file_name(record["branch"], record["started"]):
            problems.append(f"should be named {file_name(record['branch'], record['started'])}")
        found += [f"{shown}: {problem}" for problem in problems]
    return len(paths), found


def _moment(text: str) -> datetime | None:
    try:
        moment = datetime.fromisoformat(text)
    except ValueError:
        return None
    return moment if moment.tzinfo is not None else None


def _kinds(kinds: Sequence[type]) -> str:
    names = {str: "text", int: "a whole number", float: "a number", bool: "true or false"}
    return " or ".join("null" if kind is type(None) else names[kind] for kind in kinds)


def _dump(record: Mapping[str, object]) -> str:
    return json.dumps(record, indent=2) + "\n"


def main(argv: Sequence[str] | None = None, *, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="refuse a record with no review or a malformed field")
    reviewing = commands.add_parser("review", help="add a review's outcome to a record")
    reviewing.add_argument("file", type=Path)
    reviewing.add_argument("--outcome", choices=OUTCOMES, required=True)
    reviewing.add_argument("--note", required=True, help="one line on what the review found")
    args = parser.parse_args(argv)
    if args.command == "review":
        try:
            review(args.file, args.outcome, args.note, datetime.now(UTC).date())
        except (OSError, ValueError) as error:
            print(f"worker_runs: {error}", file=sys.stderr)
            return 2
        print(f"Recorded the review of {args.file}: {args.outcome}.")
        return 0
    count, found = check(root)
    if found:
        print(
            f"worker-runs: {len(found)} problem(s) in {RECORDS_DIR}.\n"
            + "".join(f"  {problem}\n" for problem in found)
            + "  Each headless worker run's record needs its review before the "
            "branch merges, so headless and chat work can be compared (PL-87BR).",
            file=sys.stderr,
        )
        return 1
    print(f"worker-runs: {count} record(s) in {RECORDS_DIR}, each reviewed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
