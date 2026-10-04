---
id: PL-0Z0F
title: A test that restates a core constant's value passes while the constant moves, and PL-T5J5 found eight by hand at 48 h: perturb each supported_ranges constant on a schedule and fail a test that breaks without importing it
priority: P3
effort: M
status: blocked
classes: test
feature: one-home-for-constants
touches: tools, .github/workflows/drift.yml, tests
blocked-by: PL-R417
added: 2026-10-03
payoff: a test that copies a supported-range limit instead of importing it is named on the scheduled run, before the limit moves and the copy fails for a reason that is not a defect
verify: grep -q '^  restated-constants:' .github/workflows/drift.yml && grep -q 'def test_a_test_restating_a_constant_is_named_and_one_importing_it_is_not' tests/unit/test_restated_constants.py
---

**Problem.** A test that restates a core constant's value passes while the constant moves, and PL-T5J5 found eight by hand at 48 h: perturb each supported_ranges constant on a schedule and fail a test that breaks without importing it

**Why it matters.** PL-T5J5 found eight tests holding the 24 h limit as text or literal by setting `MAXIMUM_ELAPSED_SIMULATION_TIME_S` to 48 h and reading which tests broke: 9 of 3,670 failed and 8 of the failures were spurious. That method is deterministic and nobody runs it twice. A test that restates a constant passes on every run until the constant moves, then fails for a reason that is not a defect, which is the one kind of failure that trains a session to edit the test rather than the code.

**Premise checked 2026-10-04** on `main` at `48787726`: nothing runs PL-T5J5's method again. `.github/workflows/drift.yml`'s two jobs run the suite against upgraded dependencies and against the newest interpreter, and the two `conftest.py` files read no environment variable for a constant: their `os.environ` lines set git's config, bytecode writing and the Qt platform.

**Shape.** A scheduled job in `.github/workflows/drift.yml`, not `quality.yml`: one full suite per constant is too slow for a gate on every push. For each public constant in `core/supported_ranges.py`, run the suite with the constant replaced by a distinct wrong value (a `conftest.py` fixture reading one environment variable) and collect the failing tests; a failing test that does not import the constant by name is reported. A test that should fail, such as the pin in `tests/unit/test_supported_ranges.py` that asserts the constant equals 86 400 s, imports the name and passes the filter. Standard library plus pytest.

**Done when.** The job runs on its schedule, reports zero restating tests on `main`, and a deliberately restated test on a branch is named in its output. Named at triage, 2026-10-04, so `verify:` can hold it: the job is `restated-constants` in `.github/workflows/drift.yml`, it runs `tools/restated_constants.py`, and `tests/unit/test_restated_constants.py` pins the report with `test_a_test_restating_a_constant_is_named_and_one_importing_it_is_not`, over two fixture tests that both break when a constant moves: the one that copies its value is named, and the one that imports it is not.

**Generator check.** Serves PL-40SJ's family from the tests' side; not a head of its own.

[superseded 2026-10-03: PL-40SJ closed that day, in #1326, and the pause it held did not end with it; the hold below replaces this]
**Decided 2026-10-03: waits for PL-40SJ** (project owner, 2026-10-03, ratified, over lifting the apparatus pause for this item and PL-NH53 while PL-40SJ carries `generator: live`). A new check, so it is built once PL-40SJ, the head of its cluster, has closed and its tool's baseline exists to shape this against; `blocked-by:` records it.

**Held by the generator pause** (triage, 2026-10-04). PL-40SJ's tool and baseline are on `main`, so that half of the wait is over. The pause is not: on `main` at `4ab001b8`, `bin/docket generators` marks `PL-R417` (readers that take one physical line for a whole statement) still generating, and its build is open in #1332. The owner asked for this item's promotion on the two steps the offer named, a `verify:` command and no other live head; the first is done above and the second failed, so `blocked-by:` now names `PL-R417`, keeping the decision above to wait out the pause rather than lift it. Before promoting, check that `bin/docket generators` marks no head "still generating", rather than this list; building it sooner is the owner's call, made by asking (`PL-6Q9L`).
