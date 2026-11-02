---
id: PL-4R21
title: docs/MODEL.md § 'Independent-solution test' states the 4e-13 tolerance 'over every state, every horizon and every trajectory', but test_the_shipped_step_reaches_the_pinned_reference_horizons holds the pinned 60, 600 and 3600 s horizons to HELD_RUN_ROUNDING_BOUND = 1e-12, which the section never names; the held hour reaches 7.16e-14 for desflurane, above the 5.89e-14 the section's re-measurement over 'the horizons above and every trajectory below' reports as worst (found by PL-F67Q's blind review, 2026-10-25)
priority: P2
effort: S
status: done
classes: docs
feature: stale-source-claims
milestone: v0.6.14
touches: docs/MODEL.md, tests/reference/test_coupled_dynamics.py
added: 2026-10-25
closed: 2026-11-02
pr: 1940
payoff: docs/MODEL.md states the bound each reference horizon is held to and the worst residual the held runs reach
verify: grep -qF 'HELD_RUN_ROUNDING_BOUND' docs/MODEL.md
---

**Problem.** docs/MODEL.md § 'Independent-solution test' states the 4e-13 tolerance 'over every state, every horizon and every trajectory', but test_the_shipped_step_reaches_the_pinned_reference_horizons holds the pinned 60, 600 and 3600 s horizons to HELD_RUN_ROUNDING_BOUND = 1e-12, which the section never names; the held hour reaches 7.16e-14 for desflurane, above the 5.89e-14 the section's re-measurement over 'the horizons above and every trajectory below' reports as worst (found by PL-F67Q's blind review, 2026-10-25)

**Reproduced 2026-10-26.** `docs/MODEL.md` § "Independent-solution test" states
the 4e-13 bound "over every state, every horizon and every trajectory below".
`tests/reference/test_coupled_dynamics.py` defines `HELD_RUN_ROUNDING_BOUND =
1e-12` for the pinned horizons. `docs/MODEL.md` names neither that constant nor
the 7.16e-14 residual the held hour reaches for desflurane. It reports 5.89e-14
as the worst figure measured.

**Why it matters.** `docs/MODEL.md` is the specification a reviewer checks the
verification against. It promises a tighter bound than the test enforces on
the held runs, and it reports a worst case smaller than one the test measures.

**Done when.** The section names `HELD_RUN_ROUNDING_BOUND` and the horizons it
applies to. Its worst-figure sentence covers the held hour, or says why that
run is outside its measurement.

**Closed 2026-11-02.** `docs/MODEL.md` § "Independent-solution test" no
longer says the 4e-13 bound applies at every horizon. A new paragraph names
`HELD_RUN_ROUNDING_BOUND` (1e-12), the 60, 600 and 3600 s horizons it applies
to, and the held hour's worst residual, 7.16e-14 for desflurane in muscle. That
figure was re-measured on 2026-11-02 at 7.1637e-14, unchanged from the
2026-09-07 table. The paragraph gives the bound's basis, 4.6 times the
2.17e-13 subdivision spread. Blind review found that a first draft explained
the larger residual by step count alone. That does not hold, because the 900 s
unperfused load at 0.025 s also takes 36 000 steps and stays smaller, so the
paragraph now says so. The test file's own comments made the same comparison
and are corrected with it, and its "3.2 times its own spread" now reads 4.6.
