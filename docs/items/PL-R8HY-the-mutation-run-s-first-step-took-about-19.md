---
id: PL-R8HY
title: The mutation run's first step took about 19 minutes on a four-core container on 2026-11-11, where tools/diff_mutation.py's docstring says about two and a half: the same 3,576 unit tests ran in 2 min 59 s outside mutmut
status: untriaged
added: 2026-11-11
---

**Problem.** The mutation run's first step took about 19 minutes on a four-core container on 2026-11-11, where tools/diff_mutation.py's docstring says about two and a half: the same 3,576 unit tests ran in 2 min 59 s outside mutmut

**What was measured.** One run, on 2026-11-11, on `origin/main` at `7c5a8418b` with `PL-GP8G`'s fix to `[tool.mutmut]` applied, in a four-core cloud container. Found while checking that fix.

- `make mutate` with one changed function (`app/wash_in.py::is_wash_in`, 2 mutants) started at about 03:25 UTC and finished at about 03:45 UTC. Generating the mutants took 5 s and running the 2 mutants took about 6 s (mutmut printed 0.33 mutations a second). The rest, about 19 minutes, was mutmut's first step, "Running stats", in which it runs the selected unit tests once and records which functions each test calls. The load average stayed at 1.0, so the step ran in one process.
- The same test files, with the same two tests deselected, ran outside mutmut in one process in 2 min 59 s (3,576 passed). Command: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest @selected-tests.txt -q -p no:cacheprovider --deselect tests/unit/test_supported_range_edges.py::test_each_guard_admits_only_what_its_functions_compute`, where `selected-tests.txt` is the copy that the run wrote into `mutants/`.

So recording the calls made the tests about six times slower in this run. The docstring of `tools/diff_mutation.py` says "A fresh run costs about two and a half minutes of coverage collection before the first mutant", and `docs/mutation-testing.md` says "A run took about five minutes on a four-core container. Half of that time went on finding which tests reach which function."

**Why it matters.** Every run pays this step before its first mutant, because every run starts with an empty `mutants/`. That includes the run inside `bin/docket verify`, which each item that changes a mutated module makes at close-out.

**Not yet known.** Whether a second run measures the same. Whether the time grew with the number of unit tests or with mutmut's version. Which tests take most of it: the slowest outside mutmut was 4.7 s, and no single test explains 16 minutes. Whether the stopped run that preceded this one left anything that slowed it (its processes were killed first, and the load average says no).

**Done when.** The step's time is measured a second time and its cause is named. Then either the step is made shorter, or the two documents give the measured time.
