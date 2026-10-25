#!/usr/bin/env python3
"""Refuse a model id written outside `docket.toml`'s `[models]` table.

Which model and effort each kind of work uses is one fact, and its home is the
`[models]` table, read through `docket.model_choice` (`PL-0XDM`). The project
owner asked for it on 2026-10-25, after an open item still recommended Fable
5.1, a model nothing here used any more: "Sounds like single source of truth
issue. Make things that say which model and effort to use use a single source
of truth as well". A model id typed into a tool, a skill or a document is a
second copy of that fact, and it goes stale the way that item did.

**One rule, exact.** A model id is a string that `MODEL_ID_RE` matches:
`claude-`, a family name, and version numbers. A tracked file may name one only
if it is `docket.toml`, a record or a test, or is registered in `COPIES` with
the reason it may. A record states what happened, such as the session ledger,
a worker run or a closed item, so it is history rather than a choice. An open
item is read as instructions, so it is held to the rule: that is where the
stale model was. A test's expected value is meant to be independent of the
code it checks.

**What it cannot decide stays a judgment.** It reads ids, not names. "Fable
5.1" or "use Sonnet" in prose passes, and whether such a sentence still tells a
session what to do is for the session that writes it. The aliases Claude Code
reads, such as `model: opus` in `.claude/agents/Explore.md`, are held to the
table by `tools/config_home_check.py`.

Standard library only and floor-parseable, like every tool under `tools/`.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.config import CONFIG_NAME  # noqa: E402
from docket.config import load as load_config  # noqa: E402
from docket.lines import split_lines  # noqa: E402
from docket.model import is_under, parse_item  # noqa: E402
from docket.vcs import tracked_files  # noqa: E402

#: A Claude model id: `claude-`, a family name, then one or more version
#: numbers, the last of which may be a date. This file names no example,
#: because it would be a copy this check refuses.
MODEL_ID_RE = re.compile(r"\bclaude-[a-z]+(?:-\d+)+\b")

#: Where the item store lives. A closed item is a record. An open one is read
#: as instructions, which is how a stale model reached a session, so it is
#: held to the rule like any other file.
ITEMS = "docs/items/"

#: The files and trees that record what happened, and so may name any model.
MODEL_RECORDS = ("docs/session-ledger.tsv", "docs/worker-runs/")

#: Each other file that may name a model id, and why it may.
COPIES = {
    "docs/maintainer.md": (
        "the owner's reference, which records the models overview's prices and the "
        "measurements that chose the table's models"
    ),
    "subprojects/docket/README.md": "the table's format, with an example rule",
    "model-evidence.toml": "a commented example of an evidence entry",
    "subprojects/docket/src/docket/sessions.py": (
        "an example of the context-window suffix that a configured model id carries"
    ),
    "tools/skill_start_eval.py": "a usage example in the docstring",
    "docs/items/PL-6FX6-make-the-first-month-of-api-credit-runs-the.md": (
        "the model-comparison trial's run commands, which name the models it compares"
    ),
}


def problems(root: Path, files: list[str] | None = None) -> list[str]:
    """Return one line for each model id written where it may not be."""

    config = load_config(root)
    table = config.models
    # The test trees, whose expected values are independent copies by design.
    tests = config.collected_test_paths
    if table is None:
        return [f"{CONFIG_NAME} has no [models] table, so no model id has a home"]
    found: list[str] = []
    for path in sorted(tracked_files(root) if files is None else files):
        if path == CONFIG_NAME or is_under(path, tests):
            continue
        source = root / path
        if not source.is_file():
            continue
        try:
            text = source.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        ids = MODEL_ID_RE.findall(text)
        if not ids or is_under(path, MODEL_RECORDS):
            continue
        if path.startswith(ITEMS) and not parse_item(text, Path(path).name).is_open:
            continue
        for model in sorted(set(ids)):
            if path not in COPIES:
                found.append(
                    f"{path}: names {model}; read it from {CONFIG_NAME}'s [models] table, "
                    "or register the file in COPIES with the reason it may"
                )
    return found


def main(argv: list[str] | None = None, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=split_lines(__doc__)[0])
    parser.parse_args(argv)
    found = problems(root)
    for line in found:
        print(line)
    print(f"model homes: {len(found)} errors")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
