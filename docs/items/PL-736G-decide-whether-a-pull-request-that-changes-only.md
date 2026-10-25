---
id: PL-736G
title: Decide whether a pull request that changes only apparatus files should also skip the simulator tests that import no apparatus module, which would shorten its CI run by about 85 s more than PL-STM6's skip of the 35 costly tests (found working PL-STM6)
priority: P3
effort: S
status: needs-decision
classes: perf, infra
feature: ci-cost
touches: .github/workflows/quality.yml, tests/conftest.py, subprojects/docket/src/docket/cli.py, docs/apparatus.md, docs/items/PL-STM6-skip-the-46-tests-that-read-a-costly.md
deferred-from: v0.7.0 - filed after the gate froze; a P3 CI cost waiting on the owner's answer
added: 2026-10-25
payoff: a pull request that changes only apparatus files finishes CI about a minute and a half sooner, if the owner chooses the wider skip
---

[superseded 2026-10-25: the design round below narrows the question to the simulator tests that import no apparatus module]
**Problem.** On a pull request that changes only apparatus files, CI could skip all 3,891 simulator tests, 1,105 s of the suite's 1,646 s of test time, rather than only the 35 costly ones that PL-STM6 skips: decide whether it should (found working PL-STM6)

**Evidence.** Measured on 2026-10-25 on one 4-core container at `48c36b64d` with `pytest --junitxml`. A simulator test is one under `tests/reference/` or `tests/integration/`, or one whose module imports `anesthesia_sim`. That is the rule `tools/workflow_paths_check.py` uses for a test file. There were 3,891 simulator tests taking 1,105 s of summed test time, and 6,305 apparatus tests taking 541 s. `PL-STM6` skips the 35 costly tests, 479 s, on a pull request whose every changed path is under `workflow_paths`. Skipping every simulator test there would remove 1,105 s instead, about two thirds of the suite. Of the 236 merges to `main` from 2026-10-18 to 2026-10-25, 99 were such pull requests.

**Why it matters.** On those pull requests, both test parts would shrink to the apparatus tests. The run would then be set by part 1's linters and tree checks, not by pytest, so it would finish perhaps one to two minutes sooner, on about 4 of every 10 pull requests. That is an estimate from summed test time, not a CI measurement.

[superseded 2026-10-25: the design round below shows that the first option's premise is false, and replaces this question, its options and its recommendation]
**Decision needed.** Should a pull request that changes only apparatus files skip every simulator test, and not only the costly ones?

- **Skip them all.** No apparatus file is an input to a simulator test except the root `conftest.py`, which runs inside every test, and `quality.yml`, which says how the suite runs. A change to either that broke a simulator test would most likely break apparatus tests too, which still run. `main`'s push run always runs everything, so a miss shows up on `main` within minutes of the merge, as it does for the item-only fast path.
- **Keep skipping only the costly tests.** Every pull request keeps running the simulator's ordinary tests, so a miss can never reach `main` this way. It costs about a minute more on each such pull request.

**Recommendation:** skip them all. The only inputs the two choices treat differently are the root `conftest.py` and `quality.yml`, and the backstop for both is a run that already happens on every merge. The choice is the owner's because it changes what a pull request proves before it merges.

[superseded 2026-10-25: the design round below replaces this Done-when]
**Done when.** The decision is recorded here. If it is to skip them all, `--skip-costly` becomes a selection of the apparatus tests by the same rule `tools/workflow_paths_check.py` applies, and the median wall time of apparatus pull requests is measured over at least 20 runs.

**Generator check.** One-off. It is a wider version of one optimisation, and no reader misread a fact.

## Design round, 2026-10-25

This round checked the brief against the tree at `ad70226f` and timed the wider skip. What it found changes the question.

**The brief's premise is false.** The brief says no apparatus file is an input to a simulator test except the root `conftest.py` and `quality.yml`. Two simulator tests import `tools/doc_check.py`. Pytest can import it because `pyproject.toml` puts `tools` on pytest's `pythonpath`.

- `tests/unit/test_parameters.py` checks that `doc_check.SOURCE_TIERS` equals the simulator's own `SOURCE_TIERS`. The test exists to catch a change to either copy, the apparatus copy included.
- `tests/unit/test_core_constant_provenance.py` reads `docs/MODEL.md`'s provenance table through `doc_check._provenance_rows`, `doc_check.PROVENANCE_HEADER` and `doc_check.NUMBER_RE`.

From 2026-10-18 to 2026-10-25, 262 pull requests merged to `main`. Of those, 105 changed apparatus files alone, with at least one file outside the store, and 18 of the 105 changed `tools/doc_check.py`. Skipping every simulator test would have skipped both tests on each of those 18 pull requests. Those are the only pull requests on which an apparatus change can break them, so the break would have shown up only on `main`, after the merge. "Skip them all" is therefore set aside.

No other test file under `tests/` that imports `anesthesia_sim` imports a module from `tools/`, `.claude/hooks/` or `subprojects/docket/src/`, the three `pythonpath` entries. No support module under `tests/` does either. Everywhere else, a simulator test names an apparatus path only in a comment or a docstring. This round checked that by scanning every test file's imports and text.

**The safe form of the wider skip.** A test selection is called *safe* when it runs every test that a change could affect (Legunsen, Hariri, Shi, Lu, Zhang and Marinov, "An extensive study of static regression test selection in modern software evolution", FSE 2016, https://mir.cs.illinois.edu/~marinov/publications/LegunsenETAL16StaticRTS.pdf). Selecting by imports is the static, module-level form of that idea. The safe form has three parts:

- On an `apparatus` answer, both parts leave out every test file that imports `anesthesia_sim` and imports no module from a `pythonpath` directory.
- The files are left out before pytest imports them, through the `pytest_ignore_collect` hook. Deselecting them after collection would keep their import cost.
- `bin/docket ci-scope` answers `full` rather than `apparatus` when the diff changes the root `conftest.py` or `quality.yml`, because each of them reaches every test. Of the 105 pull requests above, 3 changed `quality.yml` and 1 changed the root `conftest.py`.

The one input this cannot see is a simulator test that reads an apparatus file as data rather than importing it. No test does that today, and nothing would refuse one that did.

**What it would save.** Each part was timed once on one 4-core container on 2026-10-25, with `-n 8` and coverage, as CI runs it, and with `SKIP_COSTLY_TESTS=1`. "Safe wider skip" means the 75 simulator test files that import no apparatus module were passed to `--ignore`.

| Pytest step | Today's skip | Safe wider skip |
| --- | --- | --- |
| Part 1 | 172 s, 4,126 tests | 62 s, 2,692 tests |
| Part 2 | 236 s, 6,188 tests | 118 s, 4,036 tests |

Three successful apparatus runs on `ubuntu-24.04-arm` had finished since `#1774` merged (runs 40163427755, 40164797752 and 40167192170). Part 1's job took 271 to 287 s, with 127 to 137 s in pytest. Part 2's job took 214 to 218 s, with 184 to 193 s in pytest. So part 1 sets the length of the run today. Scaling each pytest step by its local ratio gives about 195 s for part 1's job and about 120 s for part 2's. That takes about 85 s off the run, before any retuning of `PART_SHARES`. Moving tests from part 1 to part 2 might save about 30 s more. These are estimates from one local run of each part and three CI runs, not a CI measurement.

**What it would cost.** The build needs a collection hook in `tests/conftest.py` that reads each test file's imports through `docket.arming`'s import reader, the new answer rule in `ci-scope`, tests of both, and updates to `docs/apparatus.md` and to `quality.yml`'s comments. There are also two risks. `PL-STM6`'s narrower skip broke the second part of every apparatus pull request for about half an hour on the day it landed (`#1773`, fixed by `#1774`), and a test skipped by mistake gives no signal on its own pull request. The backstop is also weaker than the brief said. `main`'s push run uses `ubuntu-latest`, while pull requests use `ubuntu-24.04-arm`. So a break that shows on only one of the two architectures would first appear on some later product pull request.

**Decision needed.** Should a pull request that changes only apparatus files also skip the simulator tests that import no apparatus module?

- **Keep the current skip, and drop this item.** Apparatus pull requests keep running every simulator test except the 35 costly ones, so what a pull request proves before it merges does not change. `PL-STM6`'s planned retune of `PART_SHARES` may still save about 30 s, because on the three runs above part 1 finished about 60 s after part 2.
- **Build the safe wider skip.** Apparatus pull requests, about 4 in every 10, finish about 85 s sooner, by estimate. On those pull requests, a simulator test whose inputs the change did not touch no longer runs before the merge.

**Recommendation:** keep the current skip and drop this item. The saving is about a minute and a half per run. On 2026-10-17 the owner judged a saving of about that size not worth "a new headache to trouble shoot", and `PL-STM6`'s first version caused exactly that kind of headache on its first day. The choice is still the owner's for two reasons. It changes what a pull request proves before it merges. And the owner has since taken the CI items up again, which may mean CI time is worth more to them now.

The recommendation would be wrong if the saving is worth more than its seconds per run. That would happen if armed pull requests often wait for one another. `main` accepts only an up-to-date branch, so each merge makes every armed pull request behind it bring `main` in and run CI again. A shorter run would then shorten each wait in that line. Nobody has measured how often it happens.

**Done when.** The owner's answer is recorded here. If it is to keep the current skip, the item is dropped, with this round as the reason. If it is to build the safe wider skip, all of the following hold:

- `ci-scope` answers `full` for a diff that changes the root `conftest.py` or `quality.yml`.
- On an `apparatus` answer, both parts leave out every test file that imports `anesthesia_sim` and no module from a `pythonpath` directory, before pytest collects it.
- A test pins that a simulator test importing `doc_check` still runs on that answer.
- The median wall time of apparatus pull requests is measured over at least 20 runs.
