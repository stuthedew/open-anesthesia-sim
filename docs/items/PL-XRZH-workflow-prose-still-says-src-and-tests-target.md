---
id: PL-XRZH
title: Workflow prose still says src/ and tests/ target Python 3.14, though PL-GLFS moved ruff and mypy to 3.15 and PL-8499 raised requires-python to 3.15: floor_interpreter_guard.py, push_check_guard.py, .claude/hooks/ruff.toml, Makefile comments, quality.yml and docs/apparatus.md
priority: P3
effort: S
status: ready
classes: docs
touches: .claude/hooks/floor_interpreter_guard.py, .claude/hooks/push_check_guard.py, Makefile, .github/workflows/quality.yml, docs/apparatus.md
added: 2026-11-22
payoff: no comment tells a session the source targets a Python version it no longer targets
reenters: PL-8499
---

**Problem.** Workflow prose still says src/ and tests/ target Python 3.14, though PL-GLFS moved ruff and mypy to 3.15 and PL-8499 raised requires-python to 3.15: floor_interpreter_guard.py, push_check_guard.py, .claude/hooks/ruff.toml, Makefile comments, quality.yml and docs/apparatus.md

**Why it matters.** A session reading these comments believes `src/` targets 3.14 and may write or check code against the wrong version.

**Done when.** None of the files named says the source targets 3.14, and each reads the version from `pyproject.toml`'s `requires-python` or names it as 3.15.

**Generator check.** The target version is held in `pyproject.toml` and restated in prose; `PL-8499`, which raised it, should have swept the restatements. Recorded with `reenters`.

**Reproduced 2026-11-23.** 3.14 still appears as the target in `.claude/hooks/floor_interpreter_guard.py`, `.claude/hooks/push_check_guard.py`, `Makefile`, `.github/workflows/quality.yml` and `docs/apparatus.md`; `pyproject.toml` says `>=3.15,<3.16`.
