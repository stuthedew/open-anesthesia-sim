---
id: PL-4VJG
title: docs/MODEL.md still states that branch and trunk agree to 2.7e-15 over 240 shared columns, but the test's own docstring measured 5.3e-16 over 251 columns on 2026-10-26
status: done
milestone: v0.6.16
touches: docs/MODEL.md
added: 2026-11-05
closed: 2026-11-05
pr: 2042
verify: grep -qF 'was 5.3e-16 on' docs/MODEL.md && ! grep -qF 'is 2.7e-15, a' docs/MODEL.md
---

**Problem.** docs/MODEL.md still states that branch and trunk agree to 2.7e-15 over 240 shared columns, but the test's own docstring measured 5.3e-16 over 251 columns on 2026-10-26

**Fixed 2026-11-05, with `PL-YVL0`.** The sentence now gives the 2026-10-26 measurement, 5.3e-16 over 251 shared columns, as the test's docstring records it, and keeps 2.7e-15 over 240 columns as the figure from before `PL-T5NJ`.

**Generator check.** One measured figure left stale when `PL-T5NJ` moved the chart's columns; the test's docstring held the new figure, and the copy editor and the independent review now catch a document that disagrees with it. No mechanism to fix beyond that.
