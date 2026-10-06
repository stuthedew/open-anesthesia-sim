---
id: PL-VCF0
title: make check fails on a clean main in the cloud container: its default sans-serif is Inter, under which test_a_wrapped_mark_row_is_told_apart_from_the_row_below_it never wraps its label, and PL-K9Z5's legend-checkbox guard fails there as it does on macOS, so bin/docket verify --self REJECTs every correct close-out a thread runs
status: untriaged
added: 2026-10-06
---

**Problem.** make check fails on a clean main in the cloud container: its default sans-serif is Inter, under which test_a_wrapped_mark_row_is_told_apart_from_the_row_below_it never wraps its label, and PL-K9Z5's legend-checkbox guard fails there as it does on macOS, so bin/docket verify --self REJECTs every correct close-out a thread runs

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
