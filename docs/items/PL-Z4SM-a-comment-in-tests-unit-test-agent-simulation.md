---
id: PL-Z4SM
title: A comment in tests/unit/test_agent_simulation_validation.py still calls the mass-balance threshold 'its release gate', the name PL-8RFG replaced with 'the mass-balance tolerance' in docs/MODEL.md (left alone because open pull request #2121 edits that file)
priority: P3
effort: S
status: done
classes: docs
feature: model-md-structure
milestone: v0.6.20
touches: tests/unit/test_agent_simulation_validation.py
added: 2026-11-16
closed: 2026-11-22
pr: 2235
payoff: A developer reading the agent-balance test finds the threshold under the name docs/MODEL.md uses.
verify: ! grep -qF 'its release gate' tests/unit/test_agent_simulation_validation.py
---

**Problem.** A comment in tests/unit/test_agent_simulation_validation.py still calls the mass-balance threshold 'its release gate', the name PL-8RFG replaced with 'the mass-balance tolerance' in docs/MODEL.md (left alone because open pull request #2121 edits that file)

**Checked 2026-11-22**, at `d4e8200c`. `grep -n "release gate" tests/unit/test_agent_simulation_validation.py` still prints the comment above `DOCUMENTED_ABSOLUTE_TOLERANCE_L`, which says `docs/VERIFICATION.md` § "Mass-balance identity" keeps the halt thresholds "apart from its release gate". That section now calls it "the mass-balance tolerance". `#2121` has merged, so the file is free to edit. The same comment says the test `test_the_accounting_tolerances_are_the_documented_release_tolerances` keeps its old name because a closed item's verification searches for it (`PL-B7ZV`). Since `PL-LFJZ` (`#2182`), nothing runs a closed item's command after its branch merges, so that reason no longer holds. The test checks the halt thresholds, not the mass-balance tolerance, so its current name is the section's "run-time halt thresholds".

**Why it matters.** A developer who reads the comment looks in `docs/MODEL.md` for a "release gate" that the section no longer names, and is given a reason for the test's name that no longer applies.

**Done when.** The comment calls the relative bound "the mass-balance tolerance" and the test's name calls its values the halt thresholds, as `docs/VERIFICATION.md` § "Mass-balance identity" does, and the comment no longer gives the closed item's verification as a reason.

**Generator check.** A one-off. `PL-8RFG` renamed the threshold in `docs/MODEL.md` and left this comment because `#2121` held the file, which is bookkeeping rather than a misread fact.

**Done 2026-11-22.** The comment above `DOCUMENTED_ABSOLUTE_TOLERANCE_L` now says that `docs/VERIFICATION.md` § "Mass-balance identity" keeps the halt thresholds apart from the mass-balance tolerance, and it no longer explains the test's name by a closed item's verification. The test is renamed `test_the_accounting_tolerances_are_the_documented_halt_thresholds`, and the comment that names it follows. Files checked for the old name and the old term: `tests/`, `src/`, `tools/`, `docs/VERIFICATION.md`, `docs/MODEL.md`, `docs/INTERFACE.md` and `docs/PARAMETERS.md`. The old test name is left in `docs/pr-bodies/253.md` and in two item briefs, which record history.
