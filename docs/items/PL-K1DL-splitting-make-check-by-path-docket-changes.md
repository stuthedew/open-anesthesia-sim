---
id: PL-K1DL
title: Splitting make check by path, docket changes against project changes, was measured and rejected
priority: P3
effort: S
status: dropped
classes: session-cost, infra
feature: dev-tooling
touches: Makefile, .github/workflows/quality.yml
reason: >-
  Measured 2026-09-04 and rejected on three counts, all of them numbers rather
  than judgment. The expected saving is about 1.7 s of a 67 s `make check`; the
  real cost is `PL-P3B6`'s verify replay, which a path split does not touch.
  Recorded rather than deleted so the measurement is not re-derived.
closed: 2026-09-04
added: 2026-09-04
---

**Problem.** `subprojects/docket/` is semi-contained and its tests are 40% of
the suite by count (621 of 1532), which invites running docket's checks only for
docket changes and the project's only for project changes. Measured on a
four-core box 2026-09-04, it does not pay.

**Why it matters.** Not as work to do - as a measurement worth keeping. The 40%
figure is real and the inference from it is wrong, so the idea will be had
again.

**Where.** Nowhere; nothing was built. The numbers below are the record.

**Approach.** Rejected on three counts.

*The marginal cost is 4 s, not 27 s.* At `-n auto`: full suite 27.1 / 26.3 s,
`tests/` alone 22.7 / 22.6 s, `subprojects/docket/tests` alone 10.0 s. Docket's
tests are I/O-bound on git subprocesses (serially 33.2 s wall against 8.9 s
user), so xdist packs them into workers idle on the project's CPU-bound tests.
22.7 + 10.0 = 32.7 against 27.1, so splitting makes the both-changed case about
20% *slower*.

*Disjoint changes are rare.* Over the last 60 merged pull requests: 7%
docket-only, 12% project-only, 7% both, and 75% touching neither tree - `docs/`,
`ROADMAP.md`, `CLAUDE.md`, `docs/items/`. Expected saving
0.07 x 17 s + 0.12 x 4.1 s, about 1.7 s of 67 s.

*The boundary is not clean.* `tools/doc_check.py:83-106` imports
`docket.roadmap` and `docket.vcs` at runtime, and seven files under
`tests/unit/` exercise docket: `test_doc_check.py`, `test_tools_portability.py`,
`test_docket_branch_guard.py`, `test_branch_id_check.py`, `test_ignore_check.py`,
`test_docket_digest_hook.py`, `test_pr_title_check.py`. "Docket changed, so skip
the project's checks" would skip the tests that catch docket breaking
`doc_check`.

There is also a correctness argument independent of the numbers: a path-scoped
gate needs a base ref, and `quality.yml`'s `fetch-depth: 0` comment records that
ref-dependent checks silently did not run under depth 1 and turned `main` red
twice. A scoping predicate that quietly answers "nothing changed" is a check
passing while its guarantee is void.

**Done when.** Dropped. `PL-P3B6` carries the change that does pay.
