#!/usr/bin/env python3
"""Copy the guards' local refusal log into the repository, and count what each guard refused.

Every Bash and reply guard under `.claude/hooks/` refuses a call through
`hook_input.deny`, which appends one line to a log outside the checkout
(`PL-SG93`). Nothing else records what a guard blocked, so without this no
guard's cost in defects could be weighed against what it prevented. The
project owner chose this route on 2026-10-25, over deciding from the defect
cost alone.

- `copy` reads the local log and writes each session's lines to
  `docs/hook-blocks/<session id>.tsv`, keeping any lines the file already
  holds. One file per session means two branches never append to the same
  file, so the copies do not conflict when both merge. `bin/docket record`
  runs it as `docket.toml`'s `record_command`, so the lines ride the commit
  that carries the pull request's number.
- `count` prints, for each guard and rule, how many refusals the tracked files
  hold and in how many sessions. It is what `PL-SG93`'s verdicts are read
  from.

A line is the time in UTC, the session id, the guard's name and the rule that
refused, separated by tabs. The command is never logged, because a command can
carry a token. A session whose container ends before it records a pull request
loses its lines, so the counts are a floor, not a total.

Standard library only and floor-parseable, like every tool under `tools/`.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / ".claude" / "hooks"))

from hook_input import block_log  # noqa: E402

#: Where the copied lines live in the repository.
BLOCKS_DIR = "docs/hook-blocks"

#: The first line of every copied file.
BLOCKS_HEADER = "time\tsession\tguard\trule"

#: The four fields of a log line.
LINE_FIELDS = 4

#: A session id that is safe to use as a file name. A line whose session does
#: not match is reported and left out of the copy.
SESSION_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")

#: The file name for refusals whose payload carried no session id.
NO_SESSION = "no-session"


def read_lines(text: str) -> list[str]:
    """The log lines in `text` that have the four fields, with the header left out."""
    return [
        line
        for line in text.split("\n")
        if line and line != BLOCKS_HEADER and len(line.split("\t")) == LINE_FIELDS
    ]


def copy(log: Path, root: Path) -> list[str]:
    """Copy each session's lines from `log` into its file under `BLOCKS_DIR`.

    Returns one line of report for each file that gained lines, and one for
    each session id that could not be a file name.
    """
    if not log.is_file():
        return []
    by_session: dict[str, set[str]] = defaultdict(set)
    report: list[str] = []
    for line in read_lines(log.read_text(encoding="utf-8")):
        session = line.split("\t")[1] or NO_SESSION
        if not SESSION_RE.match(session):
            report.append(
                f"hook blocks: skipped a line whose session id {session!r} is not a file name"
            )
            continue
        by_session[session].add(line)
    directory = root / BLOCKS_DIR
    for session, lines in sorted(by_session.items()):
        target = directory / f"{session}.tsv"
        held = set(read_lines(target.read_text(encoding="utf-8"))) if target.is_file() else set()
        new = lines - held
        if not new:
            continue
        directory.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "\n".join([BLOCKS_HEADER, *sorted(held | lines)]) + "\n", encoding="utf-8"
        )
        noun = "refusal" if len(new) == 1 else "refusals"
        report.append(f"hook blocks: copied {len(new)} {noun} into {target.relative_to(root)}")
    return report


def count(root: Path) -> list[str]:
    """Return one line per guard and rule: its refusals in the tracked files, and its sessions."""
    refusals: Counter[tuple[str, str]] = Counter()
    sessions: dict[tuple[str, str], set[str]] = defaultdict(set)
    for path in sorted((root / BLOCKS_DIR).glob("*.tsv")):
        for line in read_lines(path.read_text(encoding="utf-8")):
            _, session, guard, rule = line.split("\t")
            refusals[(guard, rule)] += 1
            sessions[(guard, rule)].add(session)
    if not refusals:
        return [f"hook blocks: {BLOCKS_DIR} holds no refusals yet"]
    return [
        f"{guard}\t{rule}\t{refusals[key]} refusals\t{len(sessions[key])} sessions"
        for key in sorted(refusals)
        for guard, rule in (key,)
    ]


def main(argv: list[str] | None = None, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("action", choices=("copy", "count"))
    args = parser.parse_args(argv)
    lines = copy(block_log(), root) if args.action == "copy" else count(root)
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
