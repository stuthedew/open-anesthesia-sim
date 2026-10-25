---
id: PL-M81V
title: .claude/hooks/floor-interpreter-guard.sh says pyproject.toml declares requires-python >=3.14,<3.15, but PL-J0P8 widened it to <3.16
priority: P3
effort: S
status: done
classes: docs
feature: one-source-of-truth
touches: .claude/hooks/floor-interpreter-guard.sh
added: 2026-10-19
closed: 2026-10-25
pr: 1760
payoff: the hook's reason for existing is stated against the Python range the project actually allows
verify: ! grep -qF '">=3.14,<3.15"' .claude/hooks/floor-interpreter-guard.sh
reenters: PL-J0P8
---

**Problem.** .claude/hooks/floor-interpreter-guard.sh says pyproject.toml declares requires-python >=3.14,\<3.15, but PL-J0P8 widened it to \<3.16

**Why it matters.** The hook's comment explains why the guard exists by quoting the Python versions `pyproject.toml` allows. The quote is now wrong, so a reader deciding whether the guard is still needed reasons from a range the project no longer has.

**Done when.** The comment points at `pyproject.toml`'s `requires-python` instead of quoting it, or quotes the current range.

**Checked 2026-10-24.** `.claude/hooks/floor-interpreter-guard.sh` says `">=3.14,<3.15"`, and `pyproject.toml` says `requires-python = ">=3.14,<3.16"`.

**Generator check.** A re-entry of `PL-J0P8`, closed 2026-10-18. It widened `requires-python` and left this copy behind. A configuration fact restated in another file is the shape `PL-SH0W` exists to give one home.
