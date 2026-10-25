---
id: PL-QQGZ
title: CI's quality run grew from a median of about 2 minutes in early September to about 8.7 minutes in the week of 2026-10-12, and its pytest step is 737 s against the 470 s baseline: find what slowed it
priority: P1
effort: M
status: done
classes: perf, infra
feature: defect-review-2026-10
touches: tools/main_ci_status.py, .github/workflows/quality.yml, tests/unit/test_main_ci_status.py
added: 2026-10-19
closed: 2026-10-25
pr: 1771
payoff: every pull request's CI comes back minutes sooner, or the pytest drift warning that opens each session gives its reason and goes quiet
verify: grep -qE '^\*\*Attribution\.' docs/items/PL-QQGZ-*.md
---

**Problem.** CI's quality run grew from a median of about 2 minutes in early September to about 8.7 minutes in the week of 2026-10-12, and its pytest step is 737 s against the 470 s baseline: find what slowed it

**How it was measured.** A defect review on 2026-10-19 read `docs/items` with `docket.store.read_items` and placed each item with `Item.lane(workflow_paths)`. A defect is an item whose `classes` include `defect` or `safety`. An organic defect is one filed before any head's `root-cause-of:` named it and carrying no `reenters:`. The scripts lived in the session's scratchpad and are gone, so this paragraph is the method.

**Evidence.** From `docs/ci-runs.tsv`, successful `quality.yml` pull-request runs took a median of 2.0 minutes in the week of 2026-08-31, 4.2 in the week of 09-21, 6.0 in 09-28, 8.1 in 10-05 and 8.7 in 10-12. That last week came to about 87 CI-hours across pushes and pull requests. The session-start digest of 2026-10-19 reports the pytest step's median over `main`'s last 5 successful runs (#6255 back to #6227) as 737 s, 1.57 times the 470 s `PYTEST_BASELINE_S` in `tools/main_ci_status.py`. About half of the roughly 6,000 tests are apparatus tests: 2,323 under `subprojects/docket/tests`, and about 680 under `tests/` that import no product code.

**Order** (project owner, 2026-10-19, ratified, over leaving it in its band): worked first among this review's items. It is paid on every pull request at a measured cost, which is `CLAUDE.md`'s fourth test for friction that compounds.

**Related.** `PL-ZWQS` (balance the two test parts) and `PL-JWBW` (try the arm64 runner) re-time the split but do not say what slowed it.

**Done when.** The slowdown is attributed to the tests or setup that grew. Then either it is removed, or `PYTEST_BASELINE_S` is re-measured with the reason it grew recorded beside it.

**Why it matters.** Every pull request waits on this run, so each extra minute is paid on every push. The week of 2026-10-12 cost about 87 CI-hours. The digest's drift warning also opens every session until the cause is found or the baseline is re-measured.

**Checked 2026-10-20:** the session-start digest reports the pytest step's median over `main`'s last 5 successful runs (#6423 back to #6415) as 716 s, 1.52 times the 470 s baseline. Record what slowed it under an `**Attribution.**` heading here.

**Generator check.** One-off. This is a measured slowdown, not a misread fact. `PL-ZWQS` and `PL-JWBW` re-time the split, and none of the three explains the growth.

**Attribution.** Measured on 2026-10-25. The step grew because the suite grew. No setup step or fixture slowed down. The simulator's own tests account for about three quarters of the growth, and most of that is the 24-hour reference validation, which `PL-F08Y` already computes once per run.

*The trend on `main`.* Over 700 successful push runs of `quality.yml`, read through the public Actions API, the weekly median of the pytest step (both parts summed after `PL-T9X9`) was 187 s in the week of 2026-09-21, 281 s, 378 s, 509 s, and 695 s in the week of 2026-10-19. The weekly minimum, which a fast runner sets, rose in step: 99 s, 146 s, 205 s, 236 s and 417 s. A runner that grew slower would move the median and not the minimum, so the runners are not the cause.

*The tests, then and now.* The whole suite ran with `pytest -n auto --junitxml` on one 4-core container at three commits. The summed test time is the sum of every test's own time, which removes the effect of how xdist schedules them.

| Commit | Date | Tests | Summed test time | Wall time | Simulator tests | Apparatus tests |
| --- | --- | --- | --- | --- | --- | --- |
| `d2b879ca1` | 2026-09-26 | 4,646 | 480 s | 199 s | 274 s (1,683 tests) | 206 s (2,963 tests) |
| `2251e50c6` | 2026-10-11 | 7,448 | 1,102 s | 460 s | 698 s (2,514 tests) | 404 s (4,934 tests) |
| `48c36b64d` | 2026-10-25 | 10,196 | 1,646 s | 752 s | 1,105 s (3,891 tests) | 541 s (6,305 tests) |

A test counts as a simulator test when it is under `tests/reference/` or `tests/integration/`, or when its module imports `anesthesia_sim`. Every other test, including all of `subprojects/docket/tests`, counts as an apparatus test. From 2026-09-26 to now the summed time rose by 1,166 s. Simulator tests added 831 s of it (71%) and apparatus tests 335 s (29%). Since the 470 s baseline's window (2026-10-11) it rose by 544 s, and simulator tests added 407 s of that (75%).

The modules whose time grew most since 2026-09-26:

- `tests/reference/test_late_washout_against_published_fits.py`, new since then: 362 s over 41 tests. Each 24-hour curve is about 846,000 steps, about 17 s on one core.
- `tests/reference/test_published_wash_in_and_elimination.py`: 45 s to 190 s, as its tests went from 99 to 181.
- `tests/integration/test_controller.py`: 17 s to 151 s, 140 to 209 tests.
- `tests/integration/test_simulation_view.py`: 61 s to 160 s, 193 to 302 tests.
- `tests/unit/test_doc_check.py`: 46 s to 107 s, 312 to 987 tests.
- `subprojects/docket/tests/test_frontmatter_reference.py`, new: 47 s over 5 tests.

These six are 801 s of the 1,166 s rise. Every one of them is coverage added on purpose, so none is a slowdown to remove.

*Setup.* One setup cost was found, and it is not new: every pytest process rewrites the asserts of all 261 test modules, about 13 s of CPU per worker, because the root `conftest.py` turns bytecode writing off (`PL-0MLZ`). It grows with the number of asserts, so it is part of the suite growing. `PL-GQCQ` (each CI worker rewrites every test module's asserts) has the measurement and two ways to cut it. The 74 s before part 2's first line of progress dots in a CI log is not a stall. GitHub stamps a line when it ends, and part 2's first 72 tests include the workers that build the washout curves.

*Not a cause.* Three tests fail at the two older commits in this container: two `test_dark_appearance.py` cases and `test_a_wrapped_mark_row_is_told_apart_from_the_row_below_it`. At 2026-09-26 `test_this_repository_is_clean` also fails, because a worktree is not the repository it checks. They fail fast and change no total by more than a second.

**Disposition.** The growth is deliberate coverage, so `PYTEST_BASELINE_S` in `tools/main_ci_status.py` is re-measured at 695 s, the median over `main`'s 100 successful push runs #6195 to #6627 (2026-10-19 16:20Z to 2026-10-25 01:20Z), with the reason beside it. Over those runs the median of five consecutive runs stayed between 0.79 and 1.15 times 695 s, so the advisory would have stayed silent on all 96 windows. The scripts and junit files lived in the session's scratch space; this section is the method.
