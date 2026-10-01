---
id: PL-K9Z5
title: The vacuity guard in test_a_legend_checkbox_draws_its_indicator_in_the_theme fails on macOS - a bare checkbox under the dark host draws the theme's #FFFFFF panel colour there too - so the test cannot show PL-7W9N's fix holds on that platform
priority: P2
effort: S
status: ready
classes: defect, ux
feature: platform-palette
touches: tests/integration/test_dark_appearance.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-09-27
payoff: the dark-appearance test proves the legend's checkbox is themed on macOS as well as Linux, instead of failing there undiagnosed
not-delegable: diagnosing it needs a macOS host: the test passes on Linux and in CI and fails only on the owner's Mac
---

**Problem.** The vacuity guard in test_a_legend_checkbox_draws_its_indicator_in_the_theme fails on macOS - a bare checkbox under the dark host draws the theme's #FFFFFF panel colour there too - so the test cannot show PL-7W9N's fix holds on that platform

**Observed, 2026-09-28, not diagnosed.** The full suite ran at `main`
`2149e938` on macOS 27.0 with PySide6 6.11.2 and the offscreen platform, which
`tests/conftest.py` sets. Both cases of the test failed there, `[drawn]` and
`[hidden]`, and on CI they pass.

- The two assertions about the themed box held: its `Base` is `PANEL`, and
  `PANEL` is among the colours it draws.
- The failing one is the guard below them, which says a bare `QCheckBox` in the
  same state must not draw `PANEL`: `assert '#FFFFFF' not in [...]`, the
  sampled colours starting `#323232`.

So on macOS a box that declares nothing still paints the theme's panel colour
somewhere. That makes the second assertion vacuous there: it would pass whether
or not `TraceLegend` themes the indicator.

**Two readings, and the diagnosis decides between them.**

- The guard may be bound to Linux, catching a white that the platform's own
  default palette contributes through a role `dark_host` does not set, such as
  `Light`. Then the product is fine, and the guard needs a colour the platform
  cannot supply.
- Or a bare checkbox on macOS draws white from somewhere the theme fix does not
  reach. Then the legend's indicator may not be themed as `PL-7W9N` intended on
  macOS, the platform whose Dark appearance `PL-DHBX`'s title names.

The first step is to dump the bare box's palette roles, and the pixels where
`#FFFFFF` falls, on macOS.

**Why it matters.** The guard is what makes the test prove anything: a bare checkbox draws no panel colour, so the themed one's panel colour must come from the theme. On macOS it fails, so the test cannot show `PL-7W9N`'s fix holds on the platform whose Dark appearance `PL-DHBX` named, and the suite is red on the owner's machine.

**Done when.** The diagnosis is recorded here - which role or path paints `#FFFFFF` on a bare box on macOS - and either the guard uses a colour that platform cannot supply or the legend's indicator is themed there too, with the test passing on macOS.

**Not reproducible here.** Cloud sessions run Linux, where the test passes.
