---
id: PL-1FPR
title: tests/integration/test_simulation_view.py holds 12,232 lines and 307 tests for a 2,193-line module, and tests/integration/test_controller.py holds 6,443 lines: split each by the behaviour it tests
priority: P3
effort: M
status: ready
classes: refactor
feature: unit-test-review
touches: tests/integration/test_simulation_view.py, tests/integration/test_controller.py, tests/integration
deferred-from: v0.7.0 - it waits on PL-RF2S, which this gate's list does not hold, and splitting the files first would conflict with that item's open branch; it changes no value a learner sees
added: 2026-11-11
payoff: a contributor can find and read the tests of one behaviour of the run screen or the controller without opening a 12,000-line file
verify: grep -q 'Shared constants and helpers for the controller' tests/integration/controller/controller_support.py && grep -q 'Shared constants and helpers for the dashboard' tests/integration/simulation_view/simulation_view_support.py
---

**Problem.** tests/integration/test_simulation_view.py holds 12,232 lines and 307 tests for a 2,193-line module, and tests/integration/test_controller.py holds 6,443 lines: split each by the behaviour it tests

**What happens.** Measured 2026-11-11 at `e084968ac`: `tests/integration/test_simulation_view.py` holds 12,232 lines and 307 test functions, for `src/anesthesia_sim/app/simulation_view.py` at 2,193 lines. `tests/integration/test_controller.py` holds 6,443 lines. `CLAUDE.md` § "What this project is" names "a file nobody wants to open" as one of the slow accumulations that could end the project. Open items already find that tests in the first file check hand-kept lists that miss cases (`PL-B8DL`, `PL-86VL`, `PL-0G2P`), and a file this long makes such a gap harder to see.

**Recommendation.** Split each file by the behaviour its tests check, moving tests without changing them, and keep shared fixtures in a `conftest.py` or a helper module. `PL-RF2S` is changing how the display is written and its tests, so split after it lands.

**Why it matters.** A test file of 12,000 lines is one that nobody reads whole, so a gap in what it checks stays hidden, and every change to the run screen's tests lands in the same file and conflicts with every other branch that touches it.

**Done when.** Each of the two files is split into files that each hold the tests of one behaviour, with no test changed and the same tests collected before and after, and shared fixtures in one helper module or `conftest.py`.

[superseded 2026-11-14] **Blocked on `PL-RF2S` (2026-11-11).** That item rewrites how the run screen is drawn, and its open branch (#2125) changes both files. Splitting first would make that branch's rebase a rewrite. Build this once `PL-RF2S` closes.

**Generator check.** A one-off. Each test was added where the screen's other tests already were, and no rule says when a test file is long enough to split; one item is not enough to say that a rule is missing.
