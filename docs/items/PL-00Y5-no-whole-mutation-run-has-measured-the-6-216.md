---
id: PL-00Y5
title: No whole mutation run has measured the 6,216 mutants that PL-19M4 added to the run: every module of layout/, 16 modules of app/ that import no Qt, app_metadata.py and user_files.py have no recorded kill rate and their survivors are unsorted
priority: P2
effort: L
status: ready
classes: test
feature: tests-detect-wrong-values
touches: docs/mutation-testing.md
added: 2026-11-11
payoff: each display and layout module that PL-19M4 brought into the mutation run has a measured kill rate, and each fault its unit tests would miss has a test or an item
verify: grep -q '^| .layout/model.py. |' docs/mutation-testing.md
sweep: survivors of a whole mutation run over the modules PL-19M4 added to the run
---

**Problem.** No whole mutation run has measured the 6,216 mutants that PL-19M4 added to the run: every module of layout/, 16 modules of app/ that import no Qt, app_metadata.py and user_files.py have no recorded kill rate and their survivors are unsorted

**What happens.** `PL-19M4` replaced the hand list of mutated modules with a rule: mutmut mutates every module under `src/` that imports no Qt. The run went from 5,486 mutants to 11,702. The 6,216 added mutants are in `layout/` (3,781), in 16 modules of `app/` (2,374, of which `app/controller.py` holds 1,074), and in `app_metadata.py` and `user_files.py` (61). `docs/mutation-testing.md` § "Baselines" has a kill rate for `core/` and four modules of `app/`, measured on 2026-10-18, and none for the added modules. The gate applies only to lines a branch changes, so the added modules' existing survivors refuse no branch, and nobody has sorted them.

**Why it matters.** The added modules build values a learner reads: which side of a MAC target a reading is on (`app/bookmarks.py`), what an agent cost (`app/agent_cost.py`), the heights and amounts in the compartment schematic (`app/compartment_schematic.py`). A hand probe of 14 one-line faults on 2026-11-11 found three that no test caught, two of them on the edges of a MAC target's band, which `PL-19M4` closed. A whole run finds the rest.

**What to do.** Run every mutant of the added modules against the selected unit tests, and record a baseline in `docs/mutation-testing.md` § "Baselines" with one row for each module. Sort each survivor as § "Read a survivor" says, run each real gap against the whole suite as § "Second tier" says, and file the real gaps under this item's id, grouped by module. `make mutate ARGS=--all` runs all 11,702 mutants. The 2026-10-18 run took about three and a half hours for 2,489, so plan the run for the added modules alone, or in parts, and start it with the Bash tool's `run_in_background`.

**What is known already, from `PL-19M4`'s trial runs on 2026-11-11.** The selected unit tests reach 71 of the 77 mutated functions in `app/controller.py`, and every mutated function of `app/bookmarks.py`, `layout/model.py`, `layout/sizing.py` and `layout/serialization.py`. So the unit tests can kill these mutants, and a survivor there is a candidate gap. Two tests are deselected in the run, and `docs/mutation-testing.md` § "Pitfalls" says what each one hides.

**Done when.** `docs/mutation-testing.md` § "Baselines" holds a dated table with a row for each added module, and each survivor that is a real gap has a test or an item.

**Generator check.** A one-off. It is the measurement that `PL-19M4`'s change of rule left to do, and `PL-19M4` is itself a one-off under `CLAUDE.md`'s rule that a shared fact has one source of truth. No head's `misread:` line states it: `bin/docket generators --misread` was searched on 2026-11-11 for "list", "module", "import", "hand" and "covers" when `PL-19M4` was triaged.
