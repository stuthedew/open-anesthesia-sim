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

**The parts are balanced, measured 2026-10-17** (`#1519`, run 39077752143).
The two 24-hour controller runs now go through `tests/conftest.py`'s
`computed_once` fixture, as the washout curves do, so a worker that `worksteal`
hands a controller test reads the run instead of building it again. An
instrumented local run built each run once. On CI, `checks-part-1` took 324 s,
206 s of it in pytest, and `checks-part-2` took 307 s, 278 s of it in pytest.
The parts finished 17 s apart, against 188 s before. The whole run, from the
first job's start to the end of `checks`, took 343 s, against 499 s on the
split's first run and the single job's 621 s median. One run is one runner, so
this is not yet the five-run median that "Done when" asks for.

**The first part now takes 2 of every 5 ordinary tests** (project owner,
2026-10-17: "it seems less balanced now"). On the run after the merge from
`main` (run 39079652820), `checks-part-1` took 337 s and `checks-part-2` 221 s.
Part 2's pytest step moved by 80 s between the two runs, which is runner speed,
but part 1 finished last on both, by 17 s and by 116 s. Part 1 also runs about
115 s of linters and tree checks outside pytest, which an even split ignores.
So `tests/conftest.py`'s `PART_SHARES` gives part 1 2 of each 5 ordinary tests,
about 35 s of pytest moved to part 2: 3,466 tests against 5,233. With runner
noise near 80 s, one run can still land more than 30 s apart. Retune the one
constant if the median drifts.

**Runner speed sets the gap on a single run, so tuning stops here** (project
owner, 2026-10-17, ratified, over closing `#1523` and keeping the even split).
On `#1523`'s run (39080271618), `checks-part-1` took 186 s and `checks-part-2`
426 s. Part 1's `doc_check` step took 15 s there and 26 to 27 s on the two runs
before, so part 1 had a runner about 1.7 times faster. The single job's medians,
621 s on slow runners and 352 s on fast ones, show the same spread. When one
part gets a fast runner and the other a slow one, the parts finish 2 to 4
minutes apart whatever the split. The 2-in-5 share is kept because it should
help the median, by about 35 s. Judge it by the median of several runs on
`main`, never by a single run. The owner approved merging `#1523` on 2026-10-17.

**Runner speed is confirmed as the cause of the gap, measured 2026-10-18.**
Twelve successful `main` push runs followed `#1519`, from c50b5ce to 81b9176.
Part 2's pytest step had two modes with nothing between them. Three runs took
224 to 228 s and nine took 369 to 480 s. In six of those runs, part 2's job
logs show the same image (`ubuntu-24.04`, version 20261012.334.1), 8 workers
and the same 5,261 to 5,315 tests in both modes. Part 2 started 222 to 226 s
of tests on the three `centralus` runners in that sample. It took 432 to 447 s
on the two `eastus` runners and the one `westcentralus` runner. Six runs are
too few to call the region the cause. Part 1's pytest time tracks its own
`doc_check` step, 119 s at 16 s and 212 s at 27 s. Part 2 finished last on 10
of the 12 runs, the 10 where its runner was slow. The split's median wall time
over the 12 runs is 434.5 s against the single job's 621 s, a saving of about
3.1 minutes. `PL-2N6J` records a second, smaller gap that is the project's own
and not the runner's: part 2 waits 35 to 100 s longer than part 1 before
pytest starts.

**On a larger sample, the gap is the split's and not the runners', measured
2026-10-18.** The sample is every completed `quality.yml` run from 2026-10-17
19:31 UTC to 2026-10-18 22:45 UTC in which both parts' pytest steps passed:
293 runs, pull requests and pushes to `main` together, read from the Actions
API's job and step timings. Each part's runner was sorted into one of three
speed classes by a measure that the part's own split does not affect. Part 1's
`python3 tools/doc_check.py check` step does fixed work, and it took about
16 s, 21 to 22 s or 27 to 28 s, with little in between. Part 2 has no such
step, so its pytest step's own three clusters were used: below 290 s, 290 to
384 s, and 385 s or more. The two parts drew the classes in the same shares,
so GitHub does not hand part 2 the slow runners more often:

| runner class | part 1 | part 2 |
| --- | --- | --- |
| fast | 46 (16%) | 57 (19%) |
| middle | 66 (23%) | 51 (17%) |
| slow | 181 (62%) | 185 (63%) |

The two parts' classes were independent: both parts drew a slow runner in 121
runs, against 114 expected by chance. On runners of the same class, part 2's
pytest step took 1.96 to 2.23 times as long as part 1's (medians 243 s against
124 s on fast runners, 344 s against 154 s on middle ones, 462 s against 209 s
on slow ones). Part 2's job finished last in all 141 runs where both parts
drew the same class. It finished last in 249 of the 293 runs overall. Part 1
finished last only in the 43 runs where part 2 drew a faster runner than part 1.
The median job times were 318 s for part 1 and 460 s for part 2, a gap of
about 140 s against the 30 s target. The 17 s gap measured on `#1519` was one
such lucky pairing: part 1's pytest step took 206 s, the slow class, and part
2's took 278 s, the fast class. So the statement above that runner speed sets
the gap holds for a single run, but the median gap is the split's own.
`PL-2N6J`'s start-up delay in part 2, 76 to 146 s against 33 to 44 s in part
1, falls inside the pytest step and so accounts for roughly 40 to 100 s of the
140 s.

**Tuning resumes, part 2's start-up first** (project owner, 2026-10-18,
ratified, over keeping "runner speed sets the gap, so tuning stops here").
Work `PL-2N6J` first, then re-measure the median job gap over at least 20
runs. Move ordinary tests from part 2 to part 1 only if the gap is still more
than 30 s.

**What is left is the re-timing.** It needs five successful slow-runner runs
on `main` after `#1519` merges, so no branch can do it. The timeouts, the
`checks` job's 5 minutes and `PYTEST_BASELINE_S` stay as they are until then.

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
