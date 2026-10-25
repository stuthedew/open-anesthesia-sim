---
id: PL-QQGZ
title: CI's quality run grew from a median of about 2 minutes in early September to about 8.7 minutes in the week of 2026-10-12, and its pytest step is 737 s against the 470 s baseline: find what slowed it
priority: P1
effort: M
status: ready
classes: perf, infra
feature: defect-review-2026-10
touches: tools/main_ci_status.py, .github/workflows/quality.yml, tests/unit/test_main_ci_status.py
added: 2026-10-19
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
