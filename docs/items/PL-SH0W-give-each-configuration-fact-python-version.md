---
id: PL-SH0W
title: Give each configuration fact (Python version, paths, commands, timeouts) one home across pyproject.toml, .github/workflows/, the Makefile, docket.toml and the docs, held by a check
priority: P3
effort: S
status: done
classes: infra
feature: one-source-of-truth
touches: pyproject.toml, Makefile, .github/workflows/, tools/, tests/unit/, docs/apparatus.md, docket.toml
blocked-by: v0.6.0, PL-K88Z
added: 2026-10-19
closed: 2026-10-25
pr: 1765
payoff: a configuration fact changed in one file cannot leave another running the old value
verify: grep -q 'config_home_check' Makefile
---

**Problem.** Give each configuration fact (Python version, paths, commands, timeouts) one home across pyproject.toml, .github/workflows/, the Makefile, docket.toml and the docs, held by a check

**Why it matters.** Step 6 of `PL-2LB5` (the one-source-of-truth design round). A configuration fact restated across files drifts silently: one copy changes and the others keep running the old value.

**Done when.** Each configuration fact the inventory (`PL-K88Z`) finds in more than one file has one home that the others read, or a check that fails when a copy differs from its home.

**Generator check.** Not a re-entry: it is a step of `PL-2LB5` (the one-source-of-truth design round), which widens the closed `PL-4S6C` at the project owner's ask, and no open generator head names this shape.

**Closed 2026-10-25.** `tools/config_home_check.py` holds 21 facts, each with the file that holds it and the places that repeat it, and `make check` and `quality.yml`'s floor section run it bare. `PL-K88Z` counted 23. The two counts differ in grouping, not in coverage: the four action pins are four facts here, the five version facts are six (the range and its lower bound are separate), and the three ruff, mypy and `uv sync` commands are counted with the whole-suite run. A copy that the check can no longer find fails too, so a reworded sentence or a renamed key cannot leave it checking nothing. Two copies differ on purpose and are not compared: `drift.yml`'s two `uv sync --upgrade` lines and its `order` job's `-p randomly`. Building it found one more copy, `docket.arming.SECOND_PASS_PATHS`, which repeats `docket.toml`'s `protected_paths`; it is now one of the clinical floor's checked copies. The check also read its own change: adding `duplicate_code_check.py` under `uv run python` failed it until `docs/apparatus.md` counted ten such tools rather than nine.
