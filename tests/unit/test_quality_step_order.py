"""Hold `.github/workflows/quality.yml`'s verify replay to the end of its job (`PL-7K2C`).

No step reads the replay's answer, and it is the most expensive and the most
failure-prone step in the job, so a step after it runs only where the replay
passed. Eleven checks used to, and a replay failure on `main` meant the contrast
audit, the import-boundary, core-vocabulary and glyph checks and the
required-checks reconciliation never ran against that commit.

The steps are split on the indentation the file uses rather than parsed as YAML,
as `test_ci_concurrency.py` reads the same file. A reshaping this split cannot
read fails the first test rather than passing the second.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "quality.yml"

#: A step running the replay, scoped (`--verify-base`) or over the whole store.
_REPLAY = re.compile(r"^\s+(?:- )?run: bin/docket check --verify\b", re.MULTILINE)

#: A line indented less than a step's, which ends the job's step list.
_PAST_THE_STEPS = re.compile(r"^ {0,4}\S")


def _steps(text: str) -> list[str]:
    """The `checks` job's steps in the order the job runs them, each with its own lines."""
    lines = text.splitlines()
    steps_at = lines.index("    steps:", lines.index("  checks:"))
    steps: list[str] = []
    for line in lines[steps_at + 1 :]:
        if _PAST_THE_STEPS.match(line):
            break
        if line.startswith("      - "):
            steps.append(line)
        elif steps and line.startswith("        "):
            steps[-1] += "\n" + line
    return steps


def test_the_split_finds_the_whole_store_replay() -> None:
    """The step `main` runs is where the split looks, so the order test reads something."""
    steps = _steps(WORKFLOW.read_text(encoding="utf-8"))
    whole_store = [step for step in steps if _REPLAY.search(step) and "--verify-base" not in step]
    assert len(whole_store) == 1, f"expected one whole-store replay step among {len(steps)}"


def test_the_whole_store_replay_is_the_last_step_in_the_job() -> None:
    """No step follows either replay step, so a replay failure skips nothing."""
    steps = _steps(WORKFLOW.read_text(encoding="utf-8"))
    first = next(index for index, step in enumerate(steps) if _REPLAY.search(step))
    after = [step.splitlines()[0].strip() for step in steps[first:] if not _REPLAY.search(step)]
    assert not after, f"these run after the verify replay, so its failure skips them: {after}"
