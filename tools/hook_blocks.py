#!/usr/bin/env python3
"""Copy the guards' local refusal log into the repository, and count what each guard refused.

Every Bash and reply guard under `.claude/hooks/` refuses a call through
`hook_input.deny`, which appends one line to a log outside the checkout
(`PL-SG93`). Nothing else records what a guard blocked, so without this no
guard's cost in defects could be weighed against what it prevented. The
project owner chose this route on 2026-10-25, over deciding from the defect
cost alone.

- `copy` reads the local log and writes each line that no file under
  `docs/hook-blocks/` holds yet to `docs/hook-blocks/<branch>.tsv`, named for
  the branch being recorded. Only the branch's own session writes that file,
  so two branches never write the same file and the copies do not conflict
  when both merge. `bin/docket record` runs it as `docket.toml`'s
  `record_command`, so the lines ride the commit that carries the pull
  request's number.
- `count` prints, for each guard and rule, how many refusals the tracked files
  hold and in how many sessions. It is what `PL-SG93`'s verdicts are read
  from.

A line is the time in UTC to the microsecond, the session id, the guard's name
and the rule that refused, separated by tabs. Two lines alike are one refusal,
so `count` counts each distinct line once, whichever files hold it. The command
is never logged, because a command can carry a token.

**The counts are a floor, and the floor is lowest for the guards that fire
late.** The copy runs at `bin/docket record`, before the closure push, the arm
and the merge. A refusal after it reaches the repository only when a later
record on the same machine copies it. That happens on the owner's Mac and in a
long-running thread's container, but not in a container that ends after one
pull request. So `push-check-guard`, `gate-status-guard` and
`direct-merge-guard` are undercounted most.

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

sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.vcs import head_branch, read_git  # noqa: E402
from hook_input import block_log  # noqa: E402

#: Where the copied lines live in the repository.
BLOCKS_DIR = "docs/hook-blocks"

#: The first line of every copied file.
BLOCKS_HEADER = "time\tsession\tguard\trule"

#: The four fields of a log line.
LINE_FIELDS = 4

#: The characters a branch name may keep in its file name. Each other
#: character, such as the `/` in `claude/x`, becomes `-`.
UNSAFE_RE = re.compile(r"[^A-Za-z0-9_.-]")


def read_lines(text: str) -> list[str]:
    """The log lines in `text` that have the four fields, with the header left out."""
    return [
        line
        for line in text.split("\n")
        if line and line != BLOCKS_HEADER and len(line.split("\t")) == LINE_FIELDS
    ]


def held_lines(root: Path) -> set[str]:
    """Every line that some file under `BLOCKS_DIR` already holds."""
    return {
        line
        for path in sorted((root / BLOCKS_DIR).glob("*.tsv"))
        for line in read_lines(path.read_text(encoding="utf-8"))
    }


def copy(log: Path, root: Path, branch: str) -> list[str]:
    """Copy the lines of `log` that the repository lacks into `branch`'s file.

    A line with no session id is left out: every payload Claude Code sends
    carries one, so such a line came from a guard run by hand. Returns one line
    of report when the file gained lines, or says why nothing was copied.
    """
    if not log.is_file():
        return []
    if not branch:
        return ["hook blocks: HEAD is on no branch, so nothing was copied"]
    held = held_lines(root)
    new = {
        line
        for line in read_lines(log.read_text(encoding="utf-8"))
        if line.split("\t")[1] and line not in held
    }
    if not new:
        return []
    target = root / BLOCKS_DIR / f"{UNSAFE_RE.sub('-', branch)}.tsv"
    mine = set(read_lines(target.read_text(encoding="utf-8"))) if target.is_file() else set()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join([BLOCKS_HEADER, *sorted(mine | new)]) + "\n", encoding="utf-8")
    noun = "refusal" if len(new) == 1 else "refusals"
    return [f"hook blocks: copied {len(new)} {noun} into {target.relative_to(root)}"]


def count(root: Path) -> list[str]:
    """Return one line per guard and rule: its refusals in the tracked files, and its sessions."""
    refusals: Counter[tuple[str, str]] = Counter()
    sessions: dict[tuple[str, str], set[str]] = defaultdict(set)
    for line in held_lines(root):
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
    if args.action == "copy":
        lines = copy(block_log(), root, head_branch(root, read_git))
    else:
        lines = count(root)
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
