---
id: PL-GLFS
title: Move the pinned interpreter from 3.14 to 3.15: .python-version, ruff target-version and mypy python_version together, now that requires-python admits 3.15
priority: P3
effort: S
status: ready
classes: infra
touches: .python-version, pyproject.toml, uv.lock
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-18 triage pass
added: 2026-10-18
payoff: every pull request tests the newest interpreter the package declares, so a 3.15-only break shows up the day it lands
verify: grep -q '^3.15' .python-version
---

**Problem.** `PL-J0P8` widened `requires-python` to `>=3.14,<3.16`, so the
package now declares that it runs on 3.15. Every run this project makes still
uses 3.14, though. `.python-version` names 3.14.7, `[tool.ruff]
target-version` is `py314` and `[tool.mypy] python_version` is `3.14`. The
only run on 3.15 is `drift.yml`'s monthly interpreter job.

**Evidence so far, 2026-10-18.**

- [Drift run 39159017258](https://github.com/stuthedew/open-anesthesia-sim/actions/runs/39159017258)
  passed 9,352 tests on CPython 3.15.0, with every dependency resolved by
  `uv sync --upgrade`.
- `.venv/bin/mypy --python-version 3.15` (mypy 2.3.1) reported no issues in
  124 source files. That run checks the code against typeshed's 3.15 stubs
  from a 3.14 interpreter. It did not run under a 3.15 interpreter.
- `uv lock` after the widening changed no package version. It added only the
  3.15 wheels, so every pinned dependency already ships for 3.15.
- ruff 0.16.4 accepts `--target-version py315` but warns: "Support for Python
  3.15 is under development and may be unstable. Enable `preview` to remove
  this warning."

**Why it matters.** The declared support is now one minor wider than what CI
tests on every pull request. A 3.15-only break would show up only on the 1st of
the month. Moving the pin closes that gap and keeps the next move one minor
wide.

**Recommendation.** Wait for a ruff release that drops the 3.15 warning, so the
formatter does not need `preview` mode. Then move all three values together in
one pull request, run `uv sync`, and let `quality.yml` test the move.
`tools/ruff.toml` and `subprojects/docket/ruff.toml` override `target-version`
to the bare-`python3` floor and must not change (see the comment above
`[tool.ruff]` in `pyproject.toml`).

**Done when.** A ruff release supports `py315` without `preview`, and
`.python-version`, `[tool.ruff] target-version` and `[tool.mypy]
python_version` name 3.15 together, with `quality.yml` green on the pull
request that moves them. Until that ruff release exists, a session that picks
this item checks for it and leaves the item open.

**Generator check.** Not an instance of a closed head's fact. The three values
already move together by the comment above `[tool.ruff]`.
