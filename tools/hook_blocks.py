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
  hold, how many bursts they make and in how many sessions. It is what
  `PL-SG93`'s verdicts are read from.

A line is the time in UTC to the microsecond, the session id, the guard's name
and the rule that refused, separated by tabs. Two lines alike are one refusal,
so `count` counts each distinct line once, whichever files hold it. The command
is never logged, because a command can carry a token. Since 2026-11-03 the
gate-status guard's rule names the gate it read, as `status-swallowed:make
check` (`PL-8RGF`).

**A retry is not a second block.** A refused session usually rewrites the call
and tries again within a minute or two, and a false refusal is retried most. On
2026-11-03, 26 of the 125 tracked lines repeated a refusal by the same guard
and rule in the same session less than two minutes earlier (`PL-8RGF`). So
`count` also counts bursts. A refusal less than `BURST_WINDOW_S` after the one
before it, from the same guard and rule in the same session, belongs to that
refusal's burst.

**The counts are a floor, and the floor is lowest for the guards that fire
late.** The copy runs at `bin/docket record`, before the closure push, the arm
and the merge. A refusal after it reaches the repository only when a later
record on the same machine copies it. That happens on the owner's Mac and in a
long-running thread's container, but not in a container that ends after one
pull request. So `push-check-guard` and `gate-status-guard` are undercounted
most.

Standard library only and floor-parseable, like every tool under `tools/`.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / ".claude" / "hooks"))

sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.config import load  # noqa: E402
from docket.vcs import head_branch, read_git  # noqa: E402
from hook_input import block_log  # noqa: E402

#: Where the copied lines live in the repository: `docket.toml`'s `record_dir`,
#: which the claim check also reads, so a branch that only records its number
#: owes no claim for the file this writes (`PL-QLNX`).
BLOCKS_DIR = load(ROOT).record_dir

#: The first line of every copied file.
BLOCKS_HEADER = "time\tsession\tguard\trule"

#: The four fields of a log line.
LINE_FIELDS = 4

#: The longest gap, in seconds, between two refusals that `count` puts in one
#: burst. Two minutes is the window in which `PL-8RGF` found the retries.
BURST_WINDOW_S = 120

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
    if not BLOCKS_DIR:
        return ["hook blocks: docket.toml names no record_dir, so nothing was copied"]
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


def bursts(times: list[datetime]) -> int:
    """How many bursts the refusal times of one guard, rule and session make.

    A refusal starts a new burst unless it comes less than `BURST_WINDOW_S`
    seconds after the refusal before it.
    """
    ordered = sorted(times)
    return 1 + sum(
        1
        for before, after in zip(ordered, ordered[1:], strict=False)
        if (after - before).total_seconds() >= BURST_WINDOW_S
    )


def count(root: Path) -> list[str]:
    """Return one line per guard and rule: its refusals, its bursts and its sessions."""
    times: dict[tuple[str, str], dict[str, list[datetime]]] = defaultdict(lambda: defaultdict(list))
    for line in held_lines(root):
        stamp, session, guard, rule = line.split("\t")
        times[(guard, rule)][session].append(datetime.fromisoformat(stamp))
    if not times:
        return [f"hook blocks: {BLOCKS_DIR} holds no refusals yet"]
    return [
        f"{guard}\t{rule}\t{sum(len(stamps) for stamps in by_session.values())} refusals"
        f"\t{sum(bursts(stamps) for stamps in by_session.values())} bursts"
        f"\t{len(by_session)} sessions"
        for (guard, rule), by_session in sorted(times.items())
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
