---
id: PL-VCF0
title: make check fails on a clean main in the cloud container: its default sans-serif is Inter, under which test_a_wrapped_mark_row_is_told_apart_from_the_row_below_it's bare window opens shorter than its wrapped row needs, and PL-K9Z5's legend-checkbox guard fails there as it does on macOS, so bin/docket verify --self REJECTs every correct close-out a thread runs
priority: P2
effort: S
status: done
classes: test, defect
touches: tests/integration/test_simulation_view.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-06
closed: 2026-10-11
pr: 1417
payoff: make check passes on a clean main in a cloud session, so a correct close-out is accepted instead of rejected for a font the host happened to resolve
not-delegable: the proof is the wrap test passing under a host whose sans-serif resolves to Inter while still failing on an unwrapped row; no admitted grep shows that, and a worker's container may resolve a different font
---

**Problem.** make check fails on a clean main in the cloud container: its default sans-serif is Inter, under which test_a_wrapped_mark_row_is_told_apart_from_the_row_below_it's bare window opens shorter than its wrapped row needs, and PL-K9Z5's legend-checkbox guard fails there as it does on macOS, so bin/docket verify --self REJECTs every correct close-out a thread runs

**Measured 2026-10-06** in the Projects thread container closing `PL-CLW5`,
after the Qt libraries were installed. Three tests fail, and they fail the
same way on `origin/main` at `d2310180`, run from a worktree with that tree's
`src/` on `PYTHONPATH`; `main`'s own `quality` run on that commit was green.

- `tests/integration/test_simulation_view.py::test_a_wrapped_mark_row_is_told_apart_from_the_row_below_it`:
  `assert wrapped.text_label.height() >= 2 * ...lineSpacing()` gets 23 against
  30. `fc-match sans-serif` answers `Inter-Regular.otf`; with a
  `FONTCONFIG_FILE` that prefers DejaVu Sans and rejects Inter, it passes. So
  the test holds a wrap that depends on which font the host resolves.
- `tests/integration/test_dark_appearance.py::test_a_legend_checkbox_draws_its_indicator_in_the_theme`,
  both cases: the vacuity guard's `PANEL not in _colours(bare, dark_host)`
  fails, as `PL-K9Z5` records for macOS, and the font override does not
  change it.

`bin/docket verify --self` runs `make check`, so in this container it answers
`REJECT` on a close-out whose own checks all pass, and a thread has to show
the failure is `main`'s before it can say so. The 2026-09-27 measurement in
the shared notes had all 273 Qt tests passing, so the container image has
changed since.

**Reproduced 2026-10-11** on `main` at `16a20a4f` in this session's cloud
container: `fc-match sans-serif` answers `Inter-Regular.otf`, and all three tests
above fail (`3 failed in 3.14s`).

**Diagnosed 2026-10-11: the row wraps under Inter; the window is too short
for it.** Measured offscreen in this container, the first row's text label
against its `heightForWidth` at the width it was given:

| sans-serif | Advance | Text width | `heightForWidth` | Height given | Window height / its `heightForWidth` |
| --- | --- | --- | --- | --- | --- |
| Inter | 363 px | 287 px | 30 (two lines) | 23 | 66 / 81 |
| DejaVu Sans | 393 px | 286 px | 28 (two lines) | 28 | 76 / 76 |

So the 2026-10-06 reading - that the label never wraps under Inter - was wrong:
it wraps under both. The listing is shown as a bare top-level window, and a
window that is never resized opens at a height its size hint works out for a
width of its own choosing, not at its height for the 300 px it was fixed to.
Under DejaVu Sans the two happened to agree; under Inter the window is 15 px
short and the layout takes it out of the rows. The test now sizes the window to
its `heightForWidth`, as `test_qt_chart.py` already does for the legend, and
takes its width from the row's own advance rather than from a pixel count, so
the wrap no longer depends on how wide the host's font is either.

The real dashboard has the same shape in a narrow window, where the sidebar's
rows are given less than their wrap needs: captured as `PL-KX97`.

**Why it matters.** `bin/docket verify --self` runs `make check`, so every
correct close-out in a cloud session currently answers `REJECT`, and each session
has to prove the failure is `main`'s before it can say so. That is a check being
routed around, paid again by every remaining item worked in this container.

**Scope.** The legend-checkbox half is `PL-K9Z5` (the vacuity guard that fails
on macOS), already `ready`; this item is the wrap test, and the two together
clear `make check` here.

**Done when.** `test_a_wrapped_mark_row_is_told_apart_from_the_row_below_it`
wraps its label under any sans-serif the host resolves - including Inter - and
still fails when the row does not wrap.
