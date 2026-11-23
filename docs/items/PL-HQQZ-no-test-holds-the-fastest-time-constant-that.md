---
id: PL-HQQZ
title: No test holds the fastest time constant that docs/MODEL.md prints, 5.83 s at an alveolar ventilation of 9.32 L/min
priority: P2
effort: S
status: done
classes: defect
feature: model-spec-accuracy
milestone: v0.6.21
touches: docs/MODEL.md, tests/unit/test_governing_equations.py
blocked-by: PL-SZ6G
deferred-from: v0.7.0 - captured after the freeze by the check of docs/MODEL.md against the code; it changes no displayed value, and it is not safety or science
added: 2026-11-21
closed: 2026-11-22
pr: 2237
payoff: the fastest time constant that docs/MODEL.md compares the step with is computed by a test, so a change that moves it fails instead of leaving the old figure in print
tests: tests/unit/test_governing_equations.py::test_the_fastest_time_constant_is_the_one_the_model_document_prints
---

**Problem.** No test holds the fastest time constant that docs/MODEL.md prints, 5.83 s at an alveolar ventilation of 9.32 L/min

**Why it matters.** § "Supported simulation step" judges the step against this figure. With no test, a change to the alveolar equation or to the supported ranges moves the fastest time constant, and the document keeps the old figure.

**Found by.** `PL-RMNP`, the check of `docs/MODEL.md` against the code, on 2026-11-21. The figures are true: the check reproduced a minimum of 5.83379 s, flat across 9.32, 9.325 and 9.33 L/min.

**The gap.** § "Time constants" prints 5.83 s as the fastest time constant any supported setting gives, at an alveolar ventilation of 9.32 L/min, and § "Supported simulation step" compares the step with it. No file under `src/`, `tests/` or `tools/` holds either figure, and they are not in the section's table, so the table's test does not cover them. The search that found them is recorded only in the closed item `PL-JDX0`.

`PL-SZ6G` (a run's time as a whole number of seconds) rewrites the comparison that uses the 5.83 s: a 1 s step is about a sixth of it. Write the test after that merges. `PL-H94Q` (hold the numeric paragraphs of § "Numerical method" to tests) covers a different section.

**Done when.** A test re-derives the fastest time constant and the ventilation it occurs at from the model's own matrix, and the paragraph names the test.

**Generator check.** Filed by `PL-RMNP` (the check of `docs/MODEL.md` against the code), a sweep that the owner asked for. The fact it misreads is whether a `docs/MODEL.md` sentence about what the model computes matches what it computes, which the head `PL-B6YV` (a document sentence about what the model computes, checked against the code) already states. It is counted under the sweep and is not a new head.

**Checked 2026-11-22** against `d4e8200`: still applies. No file under `src/`, `tests/` or `tools/` holds 5.83 s, and `docs/MODEL.md` prints it twice in § "Alveolar gas" and twice in § "Supported simulation step", where the one-second step is now compared with it ("about a sixth"). The blocker `PL-SZ6G` closed with #2180, so the test can be written now. The brief misnames the setting: § "Alveolar gas" gives 9.32 L/min as the cardiac output, with 10 L/min of fresh gas and 12 L/min of ventilation, and it says the figure is isoflurane's. The test should find all three flows and the agent.

**Done 2026-11-22**, on `claude/project-thread-v9awbd` from `c0e9861e`. `test_the_fastest_time_constant_is_the_one_the_model_document_prints` in `tests/unit/test_governing_equations.py` repeats the search that `docs/VERIFICATION.md` § "The alveolar gas equation in the code" describes, on the shipped `build_system_matrix`: a grid of 11 fresh gas flows, 13 ventilations and 21 cardiac outputs over the supported ranges for each agent, then a golden-section search along cardiac output within one grid spacing of the grid's fastest point. It holds the agent, the three flows and the time constant to the figures `docs/MODEL.md` § "Time constants" prints, at the precision printed. It runs in about 0.5 s. It is not a regression test, so it passes on `c0e9861e` as well; it fails when a change moves any printed figure.

The search found a different last digit for the cardiac output. The minimum is 5.833790 s at 9.3252 L/min, which rounds to 9.33, not the 9.32 that `docs/MODEL.md` printed. The time constant at 9.32 and at 9.33 L/min differs from the minimum by less than 0.00001 s (5.833794 s and 5.833793 s), so two decimals of cardiac output were false precision. `docs/MODEL.md` now says "about 9.3 L/min", the test holds the cardiac output to one decimal, and `docs/VERIFICATION.md` § "The alveolar gas equation in the code" gives the refined value, explains the rounding and names the test. The 5.83 s is unchanged. Measured with `/tmp/claude-0/s/tau.py`, a scratch copy of the same search: `uv run python /tmp/claude-0/s/tau.py` printed `argmin 9.325212429530918 ... 5.833790469681773`.

Files checked: `docs/MODEL.md`, `docs/VERIFICATION.md`, `docs/PARAMETERS.md`, `docs/INTERFACE.md` and `tests/`, by `grep -rn "5\.83\|9\.32"`. The only other mention is `docs/VERIFICATION.md` § "Control timing at the one-second step", whose 5.83 s and 16 % per step still hold.
