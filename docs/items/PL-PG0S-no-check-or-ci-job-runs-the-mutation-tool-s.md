---
id: PL-PG0S
title: No check or CI job runs the mutation tool's first step, so a new unit test that cannot run inside the mutation copy of the tree stops every mutation run until a session next needs one: PL-GP8G's two tests and PL-CTXZ's deselected test, in the week of 2026-11-09
priority: P2
effort: S
status: done
classes: defect
feature: unit-test-review
touches: tools/diff_mutation.py, tests/unit/test_diff_mutation.py, .github/workflows/quality.yml, tests/unit/test_required_checks_check.py, docs/mutation-testing.md, ROADMAP.md
added: 2026-11-11
closed: 2026-11-11
pr: 2131
payoff: a unit test that would stop every mutation run fails its own pull request, so no later session's close-out finds it first
verify: grep -q 'def test_first_step_fails_on_a_test_that_reads_a_file_the_copy_does_not_hold' tests/unit/test_diff_mutation.py
---

**Problem.** No check or CI job runs the mutation tool's first step, so a new unit test that cannot run inside the mutation copy of the tree stops every mutation run until a session next needs one: PL-GP8G's two tests and PL-CTXZ's deselected test, in the week of 2026-11-09

**What happens.** mutmut first runs the selected unit tests inside `mutants/`, a copy of the tree. A unit test that reads a file the copy does not hold, or that lists the functions of a model module, fails there and passes everywhere else. `make check` and `quality.yml` never run that step, so the mutation check stays broken until a session's close-out next needs it. `PL-GP8G` found two such tests that landed on 2026-11-09 and 2026-11-11. `PL-CTXZ`'s branch deselects a third and records that while it ran under mutmut "no mutant was tried on any branch". `PL-R8HY` records that the same first step took about 19 minutes on 2026-11-11 where the tool's docstring says about two and a half.

This is a finding about workflow tooling, so the pause on new workflow mechanisms applies to any new check. Found by the unit-testing review of 2026-11-11.

**Why it matters.** Every item that changes a mutated module runs the mutation check at close-out, and a broken first step leaves each of them with no answer until somebody repairs another branch's test. Three such tests landed in one week, and each was found by a later, unrelated session.

**Done when.** A pull request that adds a simulator unit test which fails in mutmut's copy of the tree fails CI, naming the test.

**Generator pause.** This adds a CI job while `PL-J1ZM`, a workflow-lane generator head, is still generating, which the pause on new workflow mechanisms would otherwise refuse. The project owner's request of 2026-11-11 05:09 UTC, "Address unit testing scheme review weakness issues", names this item's review, and a request from the owner lifts the pause for that request (`CLAUDE.md` § "What this project is").

**Built (2026-11-11).** `tools/diff_mutation.py --first-step` builds the copy as mutmut 3.8.0 does, generates every mutant, and runs the selected simulator unit tests there once with no mutant applied, on every core. It leaves out mutmut's record of which functions each test calls, which is what made the step take about 19 minutes in one process (`PL-R8HY`). A new `mutation-copy` job in `quality.yml` runs it on every pull request that changes more than item files, and `checks` fails unless that job succeeded. Measured in a four-core container at this branch's head: 3,601 tests passed in 2 min 25 s. With `test_bare_numbers.py`'s deselection removed from `[tool.mutmut]`, which is the state `PL-GP8G` fixed, the same run failed on that test and exited 1.

**Generator check.** A one-off. The mechanism, a unit test that passes in the tree and fails in the copy, produced `PL-GP8G`'s two tests and `PL-CTXZ`'s third, and the new job now refuses the next instance in its own pull request.
