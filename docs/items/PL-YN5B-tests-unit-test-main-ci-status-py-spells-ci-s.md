---
id: PL-YN5B
title: tests/unit/test_main_ci_status.py spells CI's pytest step with --cov-fail-under=100, which the step has not carried since the suite was split into two parts (PL-T9X9)
priority: P3
effort: S
status: done
classes: test
feature: one-source-of-truth
milestone: v0.6.3
touches: tests/unit/test_main_ci_status.py
added: 2026-10-19
closed: 2026-10-25
pr: 1760
payoff: the test no longer teaches a reader a CI command that was removed
verify: ! grep -qF -- '--cov-branch --cov-fail-under=100"' tests/unit/test_main_ci_status.py
reenters: PL-T9X9
---

**Problem.** tests/unit/test_main_ci_status.py spells CI's pytest step with --cov-fail-under=100, which the step has not carried since the suite was split into two parts (PL-T9X9)

**Why it matters.** The test's docstring says the long step it cuts is `quality.yml`'s pytest step, but the string it builds is that step as it was before `PL-T9X9`. The test still checks the cutting, so it does not give a wrong result. It does teach a reader a CI command that no longer exists.

**Done when.** The fixture reads the pytest step's command from `.github/workflows/quality.yml`, or the docstring stops claiming the string is that step.

**Checked 2026-10-24.** `test_cuts_a_long_unnamed_step_and_says_that_it_cut_it` builds a step ending `--cov-fail-under=100`. `quality.yml`'s step ends `--cov-report= --part 1/2`.

**Generator check.** A re-entry of `PL-T9X9`, closed 2026-10-17. It split the pytest step and left this copy of the old step behind. A configuration fact restated in another file is the shape `PL-SH0W` exists to give one home.
