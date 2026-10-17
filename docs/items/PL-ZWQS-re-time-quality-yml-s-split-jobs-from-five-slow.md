---
id: PL-ZWQS
title: Balance quality.yml's two test parts, whose controller runs are built again when worksteal moves their tests to idle workers, then re-time the split jobs' timeouts and the pytest baseline
priority: P3
effort: M
status: ready
feature: ci-cost
touches: .github/workflows/quality.yml, tools/main_ci_status.py, tests/conftest.py, tests/integration/test_controller.py, tests/reference/test_late_washout_against_published_fits.py, tests/unit/test_worksteal_dealing.py
added: 2026-10-17
payoff: a slow runner's quality run takes about 6 minutes instead of about 8, and its timeouts and drift baseline match what the split jobs take
not-delegable: the end state is a measurement of CI runs on GitHub, which no local command can take
---

**Tabled** (project owner, 2026-10-17: "I want low hanging fruit. Not a new
headache to trouble shoot for two minutes savings"). The split already saves about 2 minutes, and balancing the parts is the troubleshooting the owner declined, so this drops from P2 to P3. Pick it up only if
CI time becomes a problem again.

**Taken up again** (project owner, 2026-10-17: "Can you balance the split
quality ci checks?"). The target is that the two parts finish within about 30 s
of each other, and "don't spend hours optimizing for 5 or 10 seconds".

**Balance is a one-time fix, kept by eye** (project owner, 2026-10-17,
ratified, over automatic balancing with `pytest-split`). New ordinary tests
are dealt round robin between the parts, so they stay even without help. Only
a new costly computation, which always goes to the last part, or growth in part
1's linters moves the balance. The owner will ask when the parts drift apart.
`pytest-split` (https://github.com/jerry-git/pytest-split) balances from a
committed `.test_durations` file that `--store-durations` writes. It was set
aside because it would replace `tests/conftest.py`'s dealing of the costly
tests, and because its durations file goes stale and must be regenerated.

**Problem.** `PL-T9X9` split `quality.yml`'s pytest step into two jobs,
`checks-part-1` and `checks-part-2`, and made `checks` the job that combines
their coverage. Three things in the tree were sized before the split ran on
`main`, and can be re-timed only from its runs:

- Both parts keep the single job's `timeout-minutes: 15`, which was sized
  against that job's longest run of 639 s. Each part now runs about half of
  the work. `checks` has 5 minutes, sized on an estimate of about 30 s.
- `tools/main_ci_status.py`'s `PYTEST_BASELINE_S = 470` is the single step's
  median. The drift line now sums the two parts' pytest steps. The sum should
  sit a little above 470 s, because each part pays its own collection and
  worker start-up. That is inside the line's band, but it is not measured.
- `tests/conftest.py` gives all 46 tests that read a costly computation to
  part 2. On a slow runner the two parts were estimated to finish within about
  20 s of each other.

**The parts are not balanced, measured 2026-10-17.** On the split's first CI
run (run 39062849281), `checks-part-1` took 299 s and `checks-part-2` 487 s,
462 s of it in pytest, so the run took 499 s instead of the estimated 350 to
400 s. A local profile of part 2 (`--durations=25`, 4-core container) found
four setups of the controller runs in `tests/integration/test_controller.py`,
101 s, 57 s, 57 s and 30 s, where `tests/conftest.py`'s dealing expects two.
`worksteal` lets an idle worker take tests from the end of a busy worker's
queue. With half the other tests, part 2's workers run out of work while one
worker is still building the first controller run, so they take the remaining
controller tests and build the runs again. The full suite kept them busy long
enough that this did not happen. Three routes, none measured yet:

- Share the controller runs between workers, as the washout curves are shared
  (`PL-F08Y`), so a test that moved to another worker reads the run instead
  of building it. This changes `tests/integration/test_controller.py`, on the
  owner's read list, and the runs may hold state a test changes.
- Give the part holding the controller tests about two thirds of the other
  tests, so its workers stay busy until the runs are built. This adds a tuned
  share that drifts as tests are added.
- Pin the six tests to one worker with an `xdist_group` mark under
  `--dist loadgroup`. The dealing from `PL-4Z5Y` is built for `worksteal`, so
  this changes how every test is scheduled.

**Why it matters.** The imbalance costs about 3 minutes of every run, and it
is paid on every push to every pull request. A timeout that is too loose lets a hung step hold a runner
for 15 minutes. A baseline a few percent off narrows the band the drift line
reads. Parts that finish far apart lose part of the saving.

**Done when.** Over at least five successful slow-runner runs on `main` after
the split, the median time from the first job's start to the end of `checks`
is recorded here against the single job's 621 s median, with the reason if
the saving is less than 3 minutes. Each `timeout-minutes` is restated from the
longest of those runs, with headroom like the old one's 41%. The parts'
pytest steps are compared, and `PYTEST_BASELINE_S` is re-measured the way its
comment says once 100 runs exist, or kept with the reading that shows it still
fits.

**Generator check.** Follow-up work to a change the owner asked for, not a defect: no reader misread a fact. The numbers were sized before the runs that measure them existed.
