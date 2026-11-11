---
id: PL-SGBT
title: The mutation check's comparison of a changed test reruns each mutant whose test module fails to import one at a time on one core: 238 reruns took over 20 minutes for one changed test in tests/unit/test_wash_in.py on 2026-11-11, 182 of them mutants of core/parameters.py
status: untriaged
feature: mutation-run-first-step
added: 2026-11-11
---

**Problem.** The mutation check's comparison of a changed test reruns each mutant whose test module fails to import one at a time on one core: 238 reruns took over 20 minutes for one changed test in tests/unit/test_wash_in.py on 2026-11-11, 182 of them mutants of core/parameters.py

**What was measured.** One run on 2026-11-11, in a four-core container, with `PL-R8HY`'s change to `tools/diff_mutation.py`: `make mutate ARGS=--verdict` with one changed line in `app/wash_in.py::is_wash_in` and one assertion deleted from `tests/unit/test_wash_in.py`. The base compare run tested 3,647 mutants of 12 files in about 10 minutes. mutmut recorded exit status 255 for 238 of them, because the mutant made the test module fail while it was imported: 182 in `core/parameters.py`, 45 in `app/formatting.py` and 11 in `core/supported_ranges.py`. `settle` then ran `tests/unit/test_wash_in.py` whole for each of the 238, one after another in one process, for over 20 minutes. The load average stayed near 1.

**Not yet known.** Whether the reruns can run four at a time, and whether the tool before `PL-R8HY`'s change took as long on the same change.
