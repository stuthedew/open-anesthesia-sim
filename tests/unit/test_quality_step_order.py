"""Hold `quality.yml`'s step order, its jobs to `checks`, and its item-only fast path.

No step reads the replay's answer, and it is the most expensive and the most
failure-prone step in the job, so a step after it runs only where the replay
passed. Eleven checks used to, and a replay failure on `main` meant the contrast
audit, the import-boundary, core-vocabulary and glyph checks and the
required-checks reconciliation never ran against that commit.

The replay runs in `checks-part-1` since `PL-T9X9` split the suite across two
jobs. The required check is `checks`, which needs the other jobs and fails
unless they succeeded. A job left out of its `needs:` would report on a pull
request without gating a merge, while its `# not-required:` line says that
`checks` gates it, so that is held here too.

**The fast path skips only what an item file cannot change** (`PL-DXD4`). A
pull request that changes only item files skips the steps that read only
Python, both parts of the suite and the coverage they feed, and runs the tests
marked `reads_item_store` instead. A wrongly skipped step would fail on `main`
after the merge, so these tests hold three things in every job: a push to
`main` still runs every step, a pull request reaching past the store runs every
step it ran before, and an item-only one skips exactly the listed steps. Each
step's `if:` is evaluated here for each case, and a condition in a form these
tests cannot read fails them.

The steps are split on the indentation the file uses rather than parsed as YAML,
as `test_ci_concurrency.py` reads the same file. A reshaping this split cannot
read fails the first test rather than passing the second.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "quality.yml"

#: A step running the replay, scoped (`--verify-base`) or over the whole store.
_REPLAY = re.compile(r"^\s+(?:- )?run: bin/docket check --verify\b", re.MULTILINE)

#: A line indented less than a step's, which ends the job's step list.
_PAST_THE_STEPS = re.compile(r"^ {0,4}\S")


#: A line opening a job: a key two spaces in.
_JOB = re.compile(r"^  (?P<job>[\w-]+):$", re.MULTILINE)


def _steps(text: str, job: str = "checks-part-1") -> list[str]:
    """`job`'s steps in the order the job runs them, each with its own lines."""
    lines = text.splitlines()
    steps_at = lines.index("    steps:", lines.index(f"  {job}:"))
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


def test_checks_needs_every_other_job() -> None:
    """A job `checks` does not need could fail and still let a pull request merge."""
    text = WORKFLOW.read_text(encoding="utf-8")
    jobs = _JOB.findall(text[text.index("\njobs:\n") :])
    needs = re.search(r"^  checks:\n    needs: \[(?P<needs>[^]]*)\]$", text, re.MULTILINE)
    assert needs is not None, "`checks` should open with a one-line `needs:` list"
    assert sorted(needs["needs"].split(", ")) == sorted(job for job in jobs if job != "checks")


# --- the item-only fast path (`PL-DXD4`) --------------------------------------

#: The two parts, which each ask `bin/docket ci-scope`, and the job that gates them.
_PARTS = ("checks-part-1", "checks-part-2")
_GATE = "checks"

#: Where a step's own key starts: on the step's first line, or on one of its
#: own at the step's indentation. A deeper key, such as a `name:` under
#: `with:`, belongs to the action and not to the step.
_KEY = r"^(?:      - |        )"

#: A step's `if:` condition, its `run:` command or `uses:` action, and its `name:`.
_CONDITION = re.compile(_KEY + r"if: (.+)$", re.MULTILINE)
_RUN = re.compile(_KEY + r"run: (.+)$", re.MULTILINE)
_USES = re.compile(_KEY + r"uses: (.+)$", re.MULTILINE)
_NAME = re.compile(_KEY + r"name: (.+)$", re.MULTILINE)

#: The step that asks the question, found by its `id:`.
_SCOPE_ID = re.compile(_KEY + r"id: scope$", re.MULTILINE)

#: A part's output, which carries its scope step's answer to `checks`.
_OUTPUT = re.compile(
    r"^    outputs:\n      scope: \$\{\{ steps\.scope\.outputs\.scope \}\}$", re.MULTILINE
)

#: The gate's variable, which says whether both parts answered `items`.
_ITEMS_ONLY = re.compile(
    r"^    env:\n      ITEMS_ONLY: \$\{\{ (?P<condition>.+) \}\}$", re.MULTILINE
)

#: One term of a condition: a context compared with a quoted literal. A
#: condition is these terms joined by `&&`.
_TERM = re.compile(r"^(?P<name>[\w.-]+) (?P<operator>==|!=) '(?P<literal>[a-z_]+)'$")

#: The steps an item-only pull request skips in each job, by the start of the
#: name GitHub gives them. A step joins this list only if no item file can
#: change its answer. The workflow's comment above the first part's scope step
#: says why the other tools stay.
SKIPPED_ON_ITEMS = {
    "checks-part-1": (
        "Run uv run ruff format --check .",
        "Run uv run ruff check .",
        "Run uv run mypy",
        "Run uv run python tools/ignore_check.py",
        "Run uv run pytest -n $(python3",
        "Run actions/upload-artifact@",
    ),
    "checks-part-2": ("Run uv run pytest -n $(python3", "Run actions/upload-artifact@"),
    "checks": (
        "Run actions/checkout@",
        "Run astral-sh/setup-uv@",
        "Run uv sync --locked --dev",
        "Run actions/download-artifact@",
        "Run uv run coverage combine",
        "Run uv run coverage report",
    ),
}

#: The fast path's own steps: the question, and the marked tests in the suite's place.
SCOPE_STEP = "which steps this pull request needs"
FAST_PATH_STEP = "the tests that read the item store"


def _job_head(text: str, job: str) -> str:
    """`job`'s lines before its steps, which hold its `needs:`, `outputs:` and `env:`."""
    lines = text.splitlines()
    start = lines.index(f"  {job}:")
    return "\n".join(lines[start : lines.index("    steps:", start)])


def _holds(condition: str, values: dict[str, str]) -> bool:
    """Whether `condition` holds where each context it reads has its value in `values`.

    A term this cannot read, or a context it was not given, fails the test, so
    a condition written another way is read or refused, and never guessed at.
    """
    holds = True
    for term in condition.split("&&"):
        parsed = _TERM.match(term.strip())
        assert parsed is not None, f"this test cannot read the condition {condition!r}"
        name = parsed["name"]
        assert name in values, f"this test does not know {name!r}, in {condition!r}"
        holds = holds and (values[name] == parsed["literal"]) == (parsed["operator"] == "==")
    return holds


def _runs(step: str, values: dict[str, str]) -> bool:
    """Whether a step runs where the contexts its `if:` reads have their values in `values`."""
    found = _CONDITION.search(step)
    return found is None or _holds(found.group(1), values)


def _name(step: str) -> str:
    """The name GitHub shows for a step: its `name:`, or `Run ` and its command or action."""
    named = _NAME.search(step)
    if named is not None:
        return named.group(1)
    for form in (_RUN, _USES):
        found = form.search(step)
        if found is not None:
            return "Run " + found.group(1)
    return step.splitlines()[0].strip()


def _run(
    text: str, event: str, answer: str, second: str | None = None
) -> dict[str, list[tuple[str, bool]]]:
    """Each job's steps by name, and whether each runs, on `event` when `ci-scope` answers `answer`.

    `second`, where given, is the second part's answer instead. The answer
    reaches a part's steps only through a step with `id: scope` that runs on
    `event`, and reaches `checks` only through the output each part declares.
    Where no scope step runs, a later step reads an empty answer, which is what
    GitHub hands it then. `ITEMS_ONLY` is the gate's condition over the two
    outputs, written as GitHub writes a boolean.
    """
    answers = dict(zip(_PARTS, (answer, answer if second is None else second), strict=True))
    values = {"github.event_name": event}
    scopes = {_GATE: ""}
    for part in _PARTS:
        asks = [step for step in _steps(text, part) if _SCOPE_ID.search(step)]
        assert len(asks) == 1, f"{part} should ask `ci-scope` once"
        scopes[part] = answers[part] if _runs(asks[0], values) else ""
        declared = _OUTPUT.search(_job_head(text, part)) is not None
        values[f"needs.{part}.outputs.scope"] = scopes[part] if declared else ""
    gate = _ITEMS_ONLY.search(_job_head(text, _GATE))
    assert gate is not None, "`checks` should set `ITEMS_ONLY` from the parts' answers"
    values["env.ITEMS_ONLY"] = "true" if _holds(gate["condition"], values) else "false"
    return {
        job: [
            (_name(step), _runs(step, {**values, "steps.scope.outputs.scope": scopes[job]}))
            for step in _steps(text, job)
        ]
        for job in (*_PARTS, _GATE)
    }


def _gated(step: str) -> bool:
    """Whether a step's `if:` reads the fast path's answer."""
    found = _CONDITION.search(step)
    return found is not None and any(
        context in found.group(1) for context in ("steps.scope.outputs.scope", "env.ITEMS_ONLY")
    )


def _skippable(text: str, job: str) -> list[str]:
    """The names of `job`'s steps that the fast path can skip: each gated step but its own."""
    gated = [_name(step) for step in _steps(text, job) if _gated(step)]
    return [name for name in gated if name != FAST_PATH_STEP]


def test_the_scope_is_decided_before_any_step_reads_it() -> None:
    """In each part, the scope step comes before every step whose condition reads its answer."""
    text = WORKFLOW.read_text(encoding="utf-8")
    for part in _PARTS:
        steps = _steps(text, part)
        decided = next(index for index, step in enumerate(steps) if _SCOPE_ID.search(step))
        early = [_name(step) for step in steps[:decided] if _gated(step)]
        assert not early, (
            f"in {part}, these read the scope before the step that decides it: {early}"
        )


def test_a_push_to_main_runs_every_step_it_ran_before() -> None:
    """On a push no scope step runs, so no answer can skip a step in any job.

    The answer is given as `items` to show that even that one cannot reach a
    push. Every step the fast path can skip still runs, and the fast path's
    own steps do not, so `main`'s run stays whole.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    push = _run(text, "push", answer="items")

    for job, steps in push.items():
        ran = [name for name, runs in steps if runs]
        skippable = _skippable(text, job)
        assert len(skippable) == len(SKIPPED_ON_ITEMS[job]), (job, skippable)
        assert [name for name in skippable if name not in ran] == [], job
        assert SCOPE_STEP not in ran, job
        assert FAST_PATH_STEP not in ran, job


@pytest.mark.parametrize("answer", ["full", ""], ids=["full", "no-answer"])
def test_a_pull_request_reaching_past_the_store_runs_the_full_job(answer: str) -> None:
    """A `full` answer, or none at all, runs every step a pull request ran before.

    An empty answer is what a later step sees where the scope step wrote
    nothing, so it has to run the whole job too.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    run = _run(text, "pull_request", answer)

    for job, steps in run.items():
        ran = [name for name, runs in steps if runs]
        assert [name for name in _skippable(text, job) if name not in ran] == [], job
        assert FAST_PATH_STEP not in ran, job


def test_an_item_only_pull_request_skips_only_the_steps_no_item_file_can_change() -> None:
    """On `items`, each job skips exactly its listed steps, and the marked tests run instead.

    The steps that read the store, which the item's done-when names, all still
    run in the first part.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    full = _run(text, "pull_request", "full")
    items = _run(text, "pull_request", "items")

    added: dict[str, list[str]] = {}
    for job in full:
        pairs = list(zip(full[job], items[job], strict=True))
        skipped = [name for (name, on_full), (_, on_items) in pairs if on_full and not on_items]
        assert len(skipped) == len(SKIPPED_ON_ITEMS[job]), (job, skipped)
        for name, start in zip(skipped, SKIPPED_ON_ITEMS[job], strict=True):
            assert name.startswith(start), f"{name!r} is skipped in {job} on items"
        added[job] = [name for (name, on_full), (_, on_items) in pairs if on_items and not on_full]
    assert added == {"checks-part-1": [], "checks-part-2": [FAST_PATH_STEP], "checks": []}

    fast_path = next(
        step for step in _steps(text, "checks-part-2") if _name(step) == FAST_PATH_STEP
    )
    assert "-m reads_item_store" in fast_path
    ran = [name for name, runs in items["checks-part-1"] if runs]
    for reader in (
        "Run python3 tools/doc_check.py check",
        "Run uv run python tools/doc_check.py check",
        "Run python3 tools/dead_ends.py check",
        "Run uv run python tools/fixture_id_check.py",
        "Run bin/docket check",
        "verify replay, scoped to what this branch changed",
    ):
        assert reader in ran, f"{reader!r} does not run on an item-only pull request"


@pytest.mark.parametrize(
    ("first", "second"),
    [("items", "full"), ("full", "items"), ("items", ""), ("", "items")],
    ids=["second-full", "first-full", "second-unanswered", "first-unanswered"],
)
def test_checks_combines_coverage_unless_both_parts_answered_items(first: str, second: str) -> None:
    """Where the parts disagree, `checks` runs its coverage steps, which then fail.

    The two parts diff the same merge commit, so they agree in practice. If
    they did not, one part would have skipped its half of the suite on an
    answer the other part did not give. Then `coverage combine` has to run and
    fail on the missing half, rather than let `checks` pass.
    """
    gate = _run(WORKFLOW.read_text(encoding="utf-8"), "pull_request", first, second)[_GATE]
    assert [name for name, runs in gate if not runs] == []
