---
id: PL-79N5
title: pr_title_check.py is the one tools/ script CI never runs at the declared floor
priority: P2
effort: S
status: done
closed: 2026-09-03

classes: infra
feature: dev-tooling
touches: .github/workflows/pr-title.yml, tests/unit/test_tools_portability.py
added: 2026-09-03
verify: uv run pytest tests/unit/test_tools_portability.py && grep -q 'def test_every_concrete_workflow_pin_is_the_declared_floor' tests/unit/test_tools_portability.py
---

**Problem.** `PL-3V8K` moved the title check out of `quality.yml` into
`.github/workflows/pr-title.yml`, correctly, and dropped `uv` with it because
`tools/pr_title_check.py` is standard library only. The new workflow runs
`python3 tools/pr_title_check.py` directly with no `actions/setup-python`
step, so it executes under whatever interpreter the `ubuntu-latest` runner
image happens to ship.

That leaves this script covered by neither pinned interpreter. It no longer
runs under `.python-version` (which is what `uv run python` gave it inside
`checks`), and it has never run under the 3.11 floor, because
`quality.yml`'s `floor` job invokes `doc_check.py`, `bin/docket check` and
`contrast_check.py` and not this one.

**Why it matters, and how little.** The residual risk is narrow, and the item
should say so rather than overstate it. Syntax is already gated —
`tests/unit/test_tools_portability.py` parses every `tools/` file with
`ast.parse(feature_version=...)`, and the `floor` job imports the same
vendored `docket.model` and `docket.vcs` modules this script depends on when
it runs `bin/docket check` at 3.11. What is left uncovered is a *runtime*
behavior in `pr_title_check.py`'s own body that differs between 3.11 and the
runner's default.

The reason it is worth recording anyway is the reason the `floor` job exists
at all: that job's own header says both portability suites "were
approximating a run CI never performed", and this is a new instance of the
same gap, created by the fix for a different one. The failure mode is also
unpleasant — a title check that errors rather than fails reads as a broken
gate, on the one workflow whose job is to protect squash-merge provenance.

**Two ways to close it, and the second is probably right.**

1. Add `actions/setup-python@v7.0.0` with `python-version: '3.11'` to
   `pr-title.yml`, matching `quality.yml`'s `floor` job. Two lines, and it
   pins the wrong thing if the intent is to test the *current* interpreter.
2. Add `python3 tools/pr_title_check.py --help` (or whatever smoke invocation
   the script supports without `PR_TITLE`) to the `floor` job's list, leaving
   `pr-title.yml` fast and unpinned. This puts the coverage where the other
   three `tools/` scripts already have it, rather than pinning a gate that
   wants to be quick.

Check what the script does with no environment set before choosing 2 — if it
exits non-zero on missing `PR_TITLE`, the smoke invocation needs a flag the
script may not have, and option 1 is the cheaper answer.

**Do not treat this as blocking anything.** It is `P3`-shaped: a small
coverage gap in the workflow apparatus, which `CLAUDE.md` holds to "working
reliably and staying streamlined" rather than to the simulator's standard.

**Found.** #257, 2026-09-03, while merging `main` after `PL-3V8K` landed the
workflow split. This branch had made the same split independently, with a
`setup-python` pin; main's version was taken verbatim as the canonical one and
the pin was not carried across, because doing so would have edited a file that
had just landed under another item. This records the difference instead.

**Done when.** `tools/pr_title_check.py` runs under a named interpreter in
CI — either pinned in `pr-title.yml` or exercised by the `floor` job — and
`quality.yml`'s `floor` header or `pr-title.yml`'s says which and why.

**Closed 2026-09-03** (project owner authorized the fix the same day). Found by
another session and correct: `PL-3V8K` was mine, and dropping `uv` left the
script under neither pinned interpreter. `pr-title.yml` now installs the floor
with `actions/setup-python`, matching `quality.yml`'s `floor` job.

**The fix is two parts, and the second is the one that matters.** Adding the pin
alone would have introduced a *second* hardcoded `3.11` that nothing holds to
`subprojects/docket/pyproject.toml`'s `requires-python` — the same drift one
layer out, and exactly the shape of defect this project keeps closing.
`_ci_floor_pin()` read `quality.yml` alone and asserted exactly one pin *in that
file*, so a pin anywhere else was unheld by construction and would have stayed
green while diverging.

`test_every_concrete_workflow_pin_is_the_declared_floor` now reads every
workflow under `.github/workflows/` and holds each concrete `major.minor` pin to
the declared floor, so a workflow added later is covered without anyone
remembering to come back here. `drift.yml`'s `'3.x'` is deliberately not matched:
that job exists to run on the *newest* interpreter, and holding it to the floor
would invert its purpose.

Verified by breaking it: the pin set to `3.12` fails the new test at
`tests/unit/test_tools_portability.py:229`, and passes restored to `3.11`.
`quality.yml`'s exactly-one-pin invariant is kept unchanged, since its reason is
specific to that file — the `checks` job must set no `python-version`, because
that would set `UV_PYTHON` and override `.python-version`.
