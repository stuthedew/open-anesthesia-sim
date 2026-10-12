---
id: PL-K9Z5
title: The vacuity guard in test_a_legend_checkbox_draws_its_indicator_in_the_theme fails on macOS - a bare checkbox under the dark host draws the theme's #FFFFFF panel colour there too - so the test cannot show PL-7W9N's fix holds on that platform
priority: P2
effort: S
status: done
classes: defect, ux
feature: platform-palette
milestone: v0.5.23
touches: tests/integration/test_dark_appearance.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-09-27
closed: 2026-10-11
pr: 1417
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

**Reproducible in the cloud container since its image changed** (`PL-VCF0`,
2026-10-06): both cases fail there, on Linux, as they do on macOS.

**Diagnosed 2026-10-11, in that container: the white is the bare box's label,
not its indicator.** `_HOST_DARK` sets `WindowText` to `#FFFFFF`, which is
PANEL's value, and Fusion draws the box's label `bare` in `WindowText`. Wherever
a glyph covers a whole pixel, that pixel is exactly PANEL. Counted over the
grabbed box, offscreen, against `SE_CheckBoxIndicator`'s rect:

| sans-serif | `#FFFFFF` pixels | In the label | In the indicator |
| --- | --- | --- | --- |
| Inter | 29 | 29 | 0 |
| DejaVu Sans | 1 | 1 | 0 |

So the first of the two readings above holds: the product is fine, and the guard
caught a colour the host's text role supplies through the box's label. Whether
any pixel hits it is a property of the font's rasterisation, which is why it
passed in CI and on the 2026-09-27 container and failed on macOS and here. The
test now samples the indicator's rect alone, on both boxes, so the label is
outside what it reads. A box whose `TraceLegend` declaration is removed still
fails it, in both states.

**Passes on macOS** (project owner, 2026-10-11): `uv run pytest -q
tests/integration/test_dark_appearance.py -k legend_checkbox` on the owner's Mac,
at this branch's `0af74890`, reported `2 passed`. That is the confirmation this
item's **Done when** asks for. The mechanism had been inferred for macOS before
it: the sampled colours the 2026-09-28 run printed start `#323232`, the host
`Window`, which is the same Fusion-under-offscreen rendering seen here, and the
label mechanism needs nothing platform-specific.
