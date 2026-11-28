---
id: PL-LR03
title: Every mutation run stops before its first mutant, because mutmut 3.8.0 reads pytest's private item._nodeid, which pytest 9.2.0 no longer has, so bin/docket verify --self cannot answer whether the tests catch a mutation on any branch
priority: P1
effort: S
status: done
classes: defect
feature: verify-false-reject
touches: pyproject.toml, uv.lock, docs/mutation-testing.md, tools/diff_mutation.py
added: 2026-11-28
closed: 2026-11-28
filed-pr: 2346
payoff: a session's close-out audit can again say whether the tests catch a mutation of each changed line, instead of rejecting every branch with no answer
---

**Problem.** Every mutation run stops before its first mutant, because mutmut 3.8.0 reads pytest's private item._nodeid, which pytest 9.2.0 no longer has, so bin/docket verify --self cannot answer whether the tests catch a mutation on any branch

**Why it matters.** `bin/docket verify --self` runs the mutation check on every
close-out, and it rejects a branch when the check gives no answer. Since
pytest 9.2.0 entered `uv.lock` on 2026-11-27 (`PL-NV1C`, pull request #2340),
the check has given no answer on any branch, so no close-out could pass it.

**What happened** (found 2026-11-28 on `PL-GWTR`'s branch). mutmut runs the
selected tests once before any mutant, to record which tests call each
function. Its pytest plugin reads each test's id as `item._nodeid`
(`mutmut/runners/harness.py`, `pytest_runtest_teardown`, in 3.8.0). pytest
9.2.0 has no such attribute, so the first test's teardown raised
`AttributeError: 'Function' object has no attribute '_nodeid'`, and mutmut
stopped with "failed to collect stats. runner returned 1". `debug = true` in
`[tool.mutmut]` showed the error; without it the log shows only the spinner.
The same tests passed in mutmut's copy of the tree when run without its plugin.

**Fix.** mutmut 3.8.1 (released 2026-10-28) reads the public `item.nodeid`
there. `pyproject.toml` now pins it and `uv.lock` holds it. Between 3.8.0 and
3.8.1 only five files differ: `runners/harness.py`, `mutation/mutators.py`,
`mutation/file_mutation.py`, `mutation/pragma_handling.py` and
`type_checking.py` (compared file by file, 2026-11-28). The internals that
`tools/diff_mutation.py` calls, in `__main__.py`, `configuration.py`,
`state.py`, `workers/isolation.py`, `utils/file_utils.py`,
`mutation/trampoline.py`, `mutation/data.py` and `mutation/diff_apply.py`, are
the same, so its notes on 3.8.0 still hold.

**Why CI did not catch it.** The `mutation-copy` job runs
`tools/diff_mutation.py --first-step`, which runs the tests in mutmut's copy
without mutmut's plugin, to save the 19 minutes the plugin's record costs
(`first_step` says so). The failure was in that plugin, so the job passed.

**Generator check.** One instance: a pinned tool read a private attribute of a
library that another change upgraded. The `mutation-copy` job's gap is the
mechanism that let it reach `main`, and this fix does not close it: `PL-NZ0R`
records it. mutmut 3.8.1 also leaves an Enum class's `__init__` unmutated,
which may let `app/display_units.py` back into mutation runs: `PL-7YMX`.
`tools/diff_mutation.py`'s `first_step` now names this failure among what it
cannot see.


**Done 2026-11-28.** With mutmut 3.8.1, `uv run --group mutation python
tools/diff_mutation.py --verdict --base origin/main` on `PL-GWTR`'s branch ran
past its first step and returned 41 mutants caught and none uncaught. With
3.8.0 the same command stopped there on three runs that day.

**Documents checked.** `docs/mutation-testing.md`, whose sentence on the pinned
version now says 3.8.1. Its other mentions of 3.8.0 date a run or describe code
that is the same in both releases. `pyproject.toml`'s comments on mutmut, and
`tools/diff_mutation.py`'s `first_step`.
