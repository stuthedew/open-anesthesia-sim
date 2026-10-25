#!/usr/bin/env python3
"""Refuse a block of code copied between two modules, against a baseline that only shrinks.

Copied logic is the third shape of a second copy, after a copied value and
restated configuration: two modules that make one rule each in their own
words, so a fix to one leaves the other giving the old answer (`PL-VWXL`).
pylint's duplicate-code check (`R0801`) already finds such blocks, so this
runs it over `PYLINT_TREES` with every other pylint message off, and compares what it
reports with `ALLOWED_BLOCKS`.

`ALLOWED_BLOCKS` counts the blocks pylint reports for each pair of modules. A pair
above its count fails, and so does a pair below it, so the baseline is lowered
in the change that removes a copy and never stays above what the tree holds.
It is keyed by the pair rather than by line numbers, so an edit that only
moves a block does not fail.

pylint's own settings decide what counts as a copy: four or more similar
lines, with comments, docstrings, imports and signatures ignored. Whether two
similar blocks are one rule or two that happen to look alike stays a judgment.
Where they are two, the remedy is to say so in the code until they no longer
match, not to raise the baseline.

It needs pylint, a `dev` dependency, so it runs under `uv run python`.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: The trees pylint reads: the simulator, the tools and docket.
PYLINT_TREES = ("src", "tools", "subprojects/docket/src")

#: The pylint arguments that leave only the duplicate-code check running.
PYLINT_ARGS = ("--disable=all", "--enable=duplicate-code", "--output-format=json")

#: Blocks pylint reports for each pair of modules, as the tree stood when the
#: check landed. The one entry is `PL-VWXL`'s last: the venous pool and a
#: tissue group make the same capacity check when a partition coefficient is
#: written, and clearing it means editing `core/`.
ALLOWED_BLOCKS: Mapping[tuple[str, str], int] = {
    ("anesthesia_sim.core.blood", "anesthesia_sim.core.tissue"): 1
}

#: A module and line span in an `R0801` message, such as `==tissue:[179:187]`.
_SPAN_RE = re.compile(r"^==(?P<module>[\w.]+):\[(?P<start>\d+):(?P<end>\d+)\]$", re.MULTILINE)


def pairs(messages: Sequence[Mapping[str, object]]) -> Counter[tuple[str, str]]:
    """Count the `R0801` blocks in pylint's JSON output by the pair of modules they join.

    Raises:
        ValueError: a duplicate-code message names other than two modules,
            so this cannot say which pair it joins.
    """

    found: Counter[tuple[str, str]] = Counter()

    for message in messages:
        if message.get("symbol") != "duplicate-code":
            continue

        modules = sorted({span["module"] for span in _SPAN_RE.finditer(str(message["message"]))})

        if len(modules) != 2:
            raise ValueError(f"a duplicate-code message names {modules}, not two modules")

        found[(modules[0], modules[1])] += 1

    return found


def run_pylint(root: Path) -> list[dict[str, object]]:
    """Return pylint's messages for `PYLINT_TREES` under `root`.

    Raises:
        RuntimeError: pylint did not run, or printed something other than JSON.
    """

    done = subprocess.run(
        [sys.executable, "-m", "pylint", *PYLINT_ARGS, *PYLINT_TREES],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    try:
        messages = json.loads(done.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"pylint exited {done.returncode} without JSON output: {done.stderr.strip()}"
        ) from error

    if not isinstance(messages, list):
        raise RuntimeError(f"pylint printed {type(messages).__name__}, not a list of messages")

    return messages


def compare(
    found: Mapping[tuple[str, str], int], baseline: Mapping[tuple[str, str], int] = ALLOWED_BLOCKS
) -> list[str]:
    """Return one line for each pair whose count differs from its baseline."""

    lines = []

    for pair in sorted(set(found) | set(baseline)):
        count, allowed = found.get(pair, 0), baseline.get(pair, 0)
        first, second = pair

        if count > allowed:
            lines.append(
                f"{first} and {second}: {count} copied block(s), and the baseline allows "
                f"{allowed}. Read the shared rule from one module; the baseline does not grow."
            )
        elif count < allowed:
            lines.append(
                f"{first} and {second}: {count} copied block(s), below the baseline of "
                f"{allowed}. Lower `ALLOWED_BLOCKS` to {count}, so the count stays a ratchet."
            )

    return lines


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="path to the repository")
    args = parser.parse_args(argv)
    found = pairs(run_pylint(args.root.resolve()))
    lines = compare(found)

    for line in lines:
        print(line, file=sys.stderr)

    print(
        f"duplicate code: {sum(found.values())} copied block(s) against a baseline of "
        f"{sum(ALLOWED_BLOCKS.values())}, {len(lines)} errors"
    )
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main())
