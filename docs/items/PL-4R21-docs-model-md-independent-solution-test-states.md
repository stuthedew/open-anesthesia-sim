---
id: PL-4R21
title: docs/MODEL.md § 'Independent-solution test' states the 4e-13 tolerance 'over every state, every horizon and every trajectory', but test_the_shipped_step_reaches_the_pinned_reference_horizons holds the pinned 60, 600 and 3600 s horizons to HELD_RUN_ROUNDING_BOUND = 1e-12, which the section never names; the held hour reaches 7.16e-14 for desflurane, above the 5.89e-14 the section's re-measurement over 'the horizons above and every trajectory below' reports as worst (found by PL-F67Q's blind review, 2026-10-25)
priority: P2
effort: S
status: ready
classes: docs
feature: stale-source-claims
touches: docs/MODEL.md
added: 2026-10-25
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
