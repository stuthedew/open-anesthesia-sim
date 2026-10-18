---
id: PL-J0P8
title: The tree passes on CPython 3.15.0: drift run 39159017258 ran 9,352 tests green on it, so requires-python's upper bound can move from <3.15
status: untriaged
added: 2026-10-18
---

**Problem.** The tree passes on CPython 3.15.0: drift run 39159017258 ran 9,352 tests green on it, so requires-python's upper bound can move from \<3.15

**Evidence.** [Run 39159017258](https://github.com/stuthedew/open-anesthesia-sim/actions/runs/39159017258)
of `drift.yml`, on 2026-10-18, at `bbfed5fd` on `claude/zealous-cannon-elscr9`.
Its interpreter job reported "Tested past the pin: resolved 3.15.0 against a
pinned 3.14", then passed 9,352 tests and skipped 2. Every dependency resolved
with `--upgrade`. mypy did not run in that job, so whether the typed code is
clean under `python_version = "3.15"` is still unknown.

**Why it matters.** `pyproject.toml` pins `requires-python = ">=3.14,<3.15"`.
The same number appears in `.python-version`, `[tool.ruff] target-version` and
`[tool.mypy] python_version`. The header of `drift.yml` says the point is to
make the move while the gap is one version wide. This is the first run that
gives evidence the move can be made.

**Decision for the project owner.** Whether to widen the bound to `<3.16` now
and keep 3.14 as the pinned interpreter, or to move the pinned interpreter to
3.15 as well. Recommendation: widen the bound now, keep the pinned interpreter
at 3.14 until a mypy run under 3.15 is clean, and then move all four values
together.
