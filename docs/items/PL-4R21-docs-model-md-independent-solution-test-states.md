---
id: PL-4R21
title: docs/MODEL.md § 'Independent-solution test' states the 4e-13 tolerance 'over every state, every horizon and every trajectory', but test_the_shipped_step_reaches_the_pinned_reference_horizons holds the pinned 60, 600 and 3600 s horizons to HELD_RUN_ROUNDING_BOUND = 1e-12, which the section never names; the held hour reaches 7.16e-14 for desflurane, above the 5.89e-14 the section's re-measurement over 'the horizons above and every trajectory below' reports as worst (found by PL-F67Q's blind review, 2026-10-25)
status: untriaged
feature: stale-source-claims
touches: docs/MODEL.md
added: 2026-10-25
---

**Problem.** docs/MODEL.md § 'Independent-solution test' states the 4e-13 tolerance 'over every state, every horizon and every trajectory', but test_the_shipped_step_reaches_the_pinned_reference_horizons holds the pinned 60, 600 and 3600 s horizons to HELD_RUN_ROUNDING_BOUND = 1e-12, which the section never names; the held hour reaches 7.16e-14 for desflurane, above the 5.89e-14 the section's re-measurement over 'the horizons above and every trajectory below' reports as worst (found by PL-F67Q's blind review, 2026-10-25)
