---
id: PL-J0P8
title: The tree passes on CPython 3.15.0: drift run 39159017258 ran 9,352 tests green on it, so requires-python's upper bound can move from <3.15
priority: P2
effort: S
status: done
classes: infra
milestone: v0.5.29
touches: pyproject.toml, uv.lock, .github/workflows/drift.yml, ROADMAP.md
added: 2026-10-18
closed: 2026-10-18
pr: 1600
payoff: the package declares the CPython 3.15 support that a green drift run has shown, while every routine run stays on the pinned 3.14
verify: grep -qF 'requires-python = ">=3.14,<3.16"' pyproject.toml && grep -qF 'requires-python = ">=3.14, <3.16"' uv.lock
---

**Problem.** `requires-python` stopped at `<3.15`, but a drift run has shown the tree passes on CPython 3.15.0.

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

**Decided 2026-10-18** (project owner, 2026-10-18, ratified, over moving the
pinned interpreter to 3.15 at the same time). Widen the bound now and keep
3.14 pinned.

**Closed 2026-10-18.** `requires-python` is now `>=3.14,<3.16`. `uv lock`
changed no package version and added only the 3.15 wheels. A mypy run with
`--python-version 3.15` was clean on 124 files. The comments in `drift.yml` and
the toolchain section of `ROADMAP.md` now describe the wider bound. Moving the
pin itself is `PL-GLFS`.
