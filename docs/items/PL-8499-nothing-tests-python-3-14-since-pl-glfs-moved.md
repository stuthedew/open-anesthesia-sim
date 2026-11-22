---
id: PL-8499
title: Nothing tests Python 3.14 since PL-GLFS moved the pin to 3.15, yet requires-python still admits 3.14, so a 3.15-only feature would pass every check and fail at import on 3.14: raise the floor to 3.15 with drift.yml's relaxed copy, or test the floor in CI
priority: P3
effort: S
status: done
classes: defect
milestone: v0.6.20
touches: pyproject.toml, .github/workflows/drift.yml, uv.lock
deferred-from: v0.7.0 - a new problem: PL-GLFS (#2159, 69eb6d3d, 2026-11-13) moved the pins to 3.15 after the freeze and left the floor at 3.14; at 0947408 every pin was 3.14
added: 2026-11-14
closed: 2026-11-22
pr: 2224
payoff: a person installing the simulator on Python 3.14 is refused at install, rather than meeting an import error that no check here could see
verify: grep -qF '>=3.15,<3.16' pyproject.toml
---

**Problem.** Nothing tests Python 3.14 since PL-GLFS moved the pin to 3.15, yet requires-python still admits 3.14, so a 3.15-only feature would pass every check and fail at import on 3.14: raise the floor to 3.15 with drift.yml's relaxed copy, or test the floor in CI

**Checked 2026-11-22.** `pyproject.toml` still says `requires-python = ">=3.14,<3.16"`. Its ruff `target-version` is `py315`, its mypy `python_version` is 3.15, and `.python-version` is 3.15.2. A search of `.github/workflows/` finds 3.14 only in comments, so no job runs the suite on 3.14. At the freeze (`git show 0947408:pyproject.toml`) all three pins were 3.14, so `PL-GLFS` (#2159) opened the gap when it moved them.

**Why it matters.** The package tells an installer that it runs on Python 3.14, while ruff and mypy read the code as 3.15. So code that needs 3.15 would pass every check here and fail on import for someone who installs the simulator on 3.14. That person would meet an import error rather than a refusal to install.

**Recommendation.** Raise the floor to 3.15 in `requires-python` and in the drift job's relaxed copy of the bound. That costs one line in each of two files, where a 3.14 job would add a run to every pull request. Either route is the working session's choice.

**Done when.** Either the package declares 3.15 as the oldest Python it runs on, and the drift job's relaxed bound starts at 3.15 too, or a CI job runs the suite on the oldest Python the package declares.

**Generator check.** The fact misread is the oldest Python the package claims to run on, which `requires-python` states and nothing tests since the pins moved. No head states it. This is a one-off: `PL-GLFS` moved the pins and not the floor.

**Done 2026-11-22.** The floor moved to 3.15: `requires-python = ">=3.15,<3.16"` in `pyproject.toml`, the drift job's relaxed bound `>=3.15` and its comment, and `uv lock` regenerated the lock, which dropped the 3.14 wheels. Files checked for a stated 3.14 floor: `README.md`, `CONTRIBUTING.md`, `docs/ARCHITECTURE.md`, `docs/maintainer.md` and `.github/workflows/`. The remaining 3.14 mentions name PEP 758 syntax that arrived in 3.14, which is still true.
