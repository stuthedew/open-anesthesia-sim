---
id: PL-00Y5
title: No whole mutation run has measured the 6,216 mutants that PL-19M4 added to the run: every module of layout/, 16 modules of app/ that import no Qt, app_metadata.py and user_files.py have no recorded kill rate and their survivors are unsorted
priority: P2
effort: L
status: done
classes: test
feature: tests-detect-wrong-values
milestone: v0.6.24
touches: docs/mutation-testing.md, docs/items/PL-33CG-the-mutation-check-of-a-branch-that-changes.md, tests/unit/, tests/integration/controller/
added: 2026-11-11
closed: 2026-11-23
pr: 2281
payoff: each display and layout module that PL-19M4 brought into the mutation run has a measured kill rate, and each fault its unit tests would miss has a test or an item
verify: grep -qF '| `layout/model.py` | 1,255 / 1,373 (1 timeout) | 91% |' docs/mutation-testing.md
sweep: survivors of a whole mutation run over the modules PL-19M4 added to the run
---

**Problem.** No whole mutation run has measured the 6,216 mutants that PL-19M4 added to the run: every module of layout/, 16 modules of app/ that import no Qt, app_metadata.py and user_files.py have no recorded kill rate and their survivors are unsorted

**What happens.** `PL-19M4` replaced the hand list of mutated modules with a rule: mutmut mutates every module under `src/` that imports no Qt. The run went from 5,486 mutants to 11,702. The 6,216 added mutants are in `layout/` (3,781), in 16 modules of `app/` (2,374, of which `app/controller.py` holds 1,074), and in `app_metadata.py` and `user_files.py` (61). `docs/mutation-testing.md` § "Baselines" has a kill rate for `core/` and four modules of `app/`, measured on 2026-10-18, and none for the added modules. The gate applies only to lines a branch changes, so the added modules' existing survivors refuse no branch, and nobody has sorted them.

**Why it matters.** The added modules build values a learner reads: which side of a MAC target a reading is on (`app/bookmarks.py`), what an agent cost (`app/agent_cost.py`), the heights and amounts in the compartment schematic (`app/compartment_schematic.py`). A hand probe of 14 one-line faults on 2026-11-11 found three that no test caught, two of them on the edges of a MAC target's band, which `PL-19M4` closed. A whole run finds the rest.

**What to do.** Run every mutant of the added modules against the selected unit tests, and record a baseline in `docs/mutation-testing.md` § "Baselines" with one row for each module. Sort each survivor as § "Read a survivor" says, run each real gap against the whole suite as § "Second tier" says, and file the real gaps under this item's id, grouped by module. `make mutate ARGS=--all` runs all 11,702 mutants. The 2026-10-18 run took about three and a half hours for 2,489, so plan the run for the added modules alone, or in parts, and start it with the Bash tool's `run_in_background`.

**What is known already, from `PL-19M4`'s trial runs on 2026-11-11.** The selected unit tests reach 71 of the 77 mutated functions in `app/controller.py`, and every mutated function of `app/bookmarks.py`, `layout/model.py`, `layout/sizing.py` and `layout/serialization.py`. So the unit tests can kill these mutants, and a survivor there is a candidate gap. Two tests are deselected in the run, and `docs/mutation-testing.md` § "Pitfalls" says what each one hides.

**Done when.** `docs/mutation-testing.md` § "Baselines" holds a dated table with a row for each added module, and each survivor that is a real gap has a test or an item.

**Generator check.** A one-off. It is the measurement that `PL-19M4`'s change of rule left to do, and `PL-19M4` is itself a one-off under `CLAUDE.md`'s rule that a shared fact has one source of truth. No head's `misread:` line states it: `bin/docket generators --misread` was searched on 2026-11-11 for "list", "module", "import", "hand" and "covers" when `PL-19M4` was triaged.

**Checked 2026-11-22** against `d4e8200`: still applies. `docs/mutation-testing.md` § "Baselines" still holds only the 2026-10-18 and 2026-10-17 runs, and has no row for `layout/model.py` or any other module that `PL-19M4` added.

**Done 2026-11-23.** Whole runs at `0117c839` (8,721 mutants, 89% killed) and at `c66be832` (8,837, 91%) are in `docs/mutation-testing.md` § "Baselines", with one row for each of the 30 modules that hold mutants. All 1,037 survivors and no-unit-test mutants at `0117c839` were sorted: 386 message only, 222 real gaps, 197 caught by an integration or reference test, 150 equivalent, 41 changed on `main` before their test was written, 20 looks only, 15 unreachable and 6 run while a test module is imported. 210 of the real gaps have one of the 89 test functions this branch adds, in 14 unit test files and 10 controller integration test files. The other 12 point at code to change and are in `PL-8LZS` (a field nothing reads), `PL-PZSF` (fields and branches nothing reads or reaches), `PL-6YDJ` (the join's rounded tolerance test) and `PL-Y6XR` (split sizes not checking the bounds count). The sort also filed `PL-1QX0` (mutmut never runs the test of a function called while a test module is imported), `PL-X106` (a legend test whose expected words come from the code under test), `PL-FKVR` (no per-test time limit), `PL-Z4MP` (the controller's redundant record of time marks it halted on) and `PL-VYN4` (a preview refusal that names a branch).

The second tier first chose each survivor's slower tests from a coverage record made with coverage's default `sys.monitoring` recorder, which on Python 3.15 ties each line only to the first test that ran it in each worker. `trace_legend_label` had 4 contexts that way and 625 with `COVERAGE_CORE=ctrace`, read from coverage 7.15.4's `core.py`, `sysmon.py` and `control.py`. The controller and layout model sorts used the `ctrace` record; the earlier sorts did not, so their 197-kill count is a lower bound, as § "Baselines" says. § "Second tier" now gives the recipe for many survivors and the `COVERAGE_CORE=ctrace` setting, and § "Read a survivor" gains the two kinds this sort needed. The PL-33CG record's sentence about random test order was corrected in passing.

The closing check refused the five skips this branch had added to tests that need something a platform may lack: `time.tzset`, git and a git checkout, a child interpreter whose locale is not UTF-8, and `os.O_DIRECTORY`. Each of those tests now stands in for the platform it needs, so it runs the same on Linux, macOS and Windows. The two encoding tests no longer run a child interpreter, which imports the code with no mutant applied, so mutmut's run could not count them against `write_synced`'s two encoding mutants. Twenty mutants of the four functions, each applied by hand on its own, failed the rewritten test for it.

Docs checked for statements this branch made untrue: `docs/mutation-testing.md` (whole), `docs/ARCHITECTURE.md` § "Tests (`tests/`)", `.claude/rules/test-oracles.md`, and the items filed above. No source file changed, so `docs/MODEL.md`, `docs/INTERFACE.md`, `docs/VERIFICATION.md` and `docs/PARAMETERS.md` were not affected.
