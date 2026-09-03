---
id: PL-79N5
title: pr_title_check.py is the one tools/ script CI never runs at the declared floor
priority: P3
effort: S
status: ready
classes: infra
feature: dev-tooling
touches: .github/workflows/pr-title.yml, .github/workflows/quality.yml
added: 2026-09-03
verify: uv run pytest tests/unit/test_tools_portability.py && { grep -q pr_title_check .github/workflows/quality.yml || grep -q setup-python .github/workflows/pr-title.yml; }
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

**Checked at triage, 2026-09-03: option 2 works, and needs no flag.** With
`PR_TITLE` unset, `tools/pr_title_check.py` prints "PR_TITLE is not set;
nothing to check" and exits **0** — `main()` returns before it calls
`closes()`. So a bare `python3 tools/pr_title_check.py` line in the `floor`
job is a valid smoke invocation; `--help` is unnecessary. It exercises the
module import at 3.11, including the vendored `docket.model` and `docket.vcs`
imports and the `argparse` setup, and stops there.

It does not reach `closes()` or `leading_ids`, and do not try to make it: the
only way in is to set `PR_TITLE`, which re-runs the real check against a
made-up title, and on a `pull_request` event `origin/main..HEAD` is the
branch's own range — so any branch that closes an item would fail the `floor`
job for a title it was never given. The import-and-argparse smoke is the whole
of what belongs there; `pr-title.yml` runs the behavior.

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
