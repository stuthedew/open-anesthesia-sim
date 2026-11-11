---
id: PL-R8HY
title: The mutation run's first step took about 19 minutes on a four-core container on 2026-11-11, where tools/diff_mutation.py's docstring says about two and a half: the same 3,576 unit tests ran in 2 min 59 s outside mutmut
priority: P2
effort: M
status: ready
classes: perf, infra
touches: tools/diff_mutation.py, docs/mutation-testing.md, tests/unit/test_diff_mutation.py, tests/unit/test_line_splits.py
deferred-from: v0.7.0 - captured after the freeze; a close-out audit cost in the workflow lane, not safety or science, which its band ranks rather than the gate
added: 2026-11-11
payoff: a session that closes an item with a change to a mutated module waits less before its first mutant runs, or the two documents state the wait it will really have
verify: ! grep -qF 'about two' tools/diff_mutation.py && ! grep -qF 'five minutes on a four-core container' docs/mutation-testing.md
---

**Problem.** The mutation run's first step took about 19 minutes on a four-core container on 2026-11-11, where tools/diff_mutation.py's docstring says about two and a half: the same 3,576 unit tests ran in 2 min 59 s outside mutmut

**What was measured.** One run, on 2026-11-11, on `origin/main` at `7c5a8418b` with `PL-GP8G`'s fix to `[tool.mutmut]` applied, in a four-core cloud container. Found while checking that fix.

- `make mutate` with one changed function (`app/wash_in.py::is_wash_in`, 2 mutants) started at about 03:25 UTC and finished at about 03:45 UTC. Generating the mutants took 5 s and running the 2 mutants took about 6 s (mutmut printed 0.33 mutations a second). The rest, about 19 minutes, was mutmut's first step, "Running stats", in which it runs the selected unit tests once and records which functions each test calls. The load average stayed at 1.0, so the step ran in one process.
- The same test files, with the same two tests deselected, ran outside mutmut in one process in 2 min 59 s (3,576 passed). Command: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest @selected-tests.txt -q -p no:cacheprovider --deselect tests/unit/test_supported_range_edges.py::test_each_guard_admits_only_what_its_functions_compute`, where `selected-tests.txt` is the copy that the run wrote into `mutants/`.

So recording the calls made the tests about six times slower in this run. The docstring of `tools/diff_mutation.py` says "A fresh run costs about two and a half minutes of coverage collection before the first mutant", and `docs/mutation-testing.md` says "A run took about five minutes on a four-core container. Half of that time went on finding which tests reach which function."

**Why it matters.** Every run pays this step before its first mutant, because every run starts with an empty `mutants/`. That includes the run inside `bin/docket verify`, which each item that changes a mutated module makes at close-out.

**Not yet known.** Whether a second run measures the same. Whether the time grew with the number of unit tests or with mutmut's version. Which tests take most of it: the slowest outside mutmut was 4.7 s, and no single test explains 16 minutes. Whether the stopped run that preceded this one left anything that slowed it (its processes were killed first, and the load average says no).

**Cause, found 2026-11-11.** Measured in a four-core container on `origin/claude/pl-gp8g-5hq69c` at `fadda8f70`, which is `origin/main` at `7c5a8418b` with `PL-GP8G`'s fix. The three experiments ran at the same time as one another and as a second full run, so each time below is longer than it would be alone.

1. **Each call to a mutated function goes through mutmut's wrapper, and the selected tests make 218 million such calls.** mutmut 3.8.0 replaces every function in the files that `only_mutate` names with a wrapper (`mutmut/mutation/trampoline.py`). The wrapper looks up the mutant under test in `os.environ` and then calls the original function or a mutant. In the first step it also records the call. The 3,575 selected tests took 219 s on plain source, 517 s through the wrapper when it only forwards, and 1,027 s when it records. That is about 1.4 microseconds a call to forward and about 3.5 to record. 60% of the calls go to three modules that check inputs: `core/checked_number.py` (70 million), `core/validation.py` (38 million) and `core/supported_ranges.py` (23 million). 79% come from six test files that step a simulation: `test_chart_frame.py`, `test_compartment_schematic.py`, `test_agent_cost.py`, `test_numerical_envelope_sweep.py`, `test_run_definition.py` and `test_bookmarks.py`. Three of those were added after 2026-10-17, when the two stated times were written: `test_numerical_envelope_sweep.py` on 2026-10-26, `test_compartment_schematic.py` on 2026-11-01 and `test_agent_cost.py` on 2026-11-02. mutmut has been pinned at 3.8.0 since the tool landed, so its version did not change.
2. **A plain `make mutate` runs the selected tests twice before its first mutant, not once.** After "Running stats", mutmut runs the tests of the mutants it was asked for once more with no mutant applied ("Running clean tests"). The tool passes one glob for each changed function, such as `anesthesia_sim.app.wash_in.x_is_wash_in__mutmut_*`. mutmut 3.8.0's `tests_for_mutant_names` matches a glob against function names, which do not end in `__mutmut_N`, so it finds no test and runs every selected test. `--verdict` passes mutant names, which mutmut looks up directly, so `bin/docket verify` pays the second pass only for the tests that reach the changed functions. The 19 minutes this item reports was both passes.

The script that took these measurements is `driver.py` in the session's scratch directory, which is not kept. It runs pytest in a copy of `mutants/` as mutmut's `run_stats` does, with mutmut's own wrapper in forwarding mode, in recording mode, and in recording mode with a counter around `record_trampoline_hit`.

**Done when.** The step's time is measured a second time and its cause is named. Then either the step is made shorter, or the two documents give the measured time.
