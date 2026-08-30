---
id: PL-WB0X
title: 'Split simulation_view.py: formatting and chart series are not the view''s job'
priority: P2
effort: M
status: ready
classes: refactor
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/chart_downsampling.py, tests/unit/test_simulation_view.py, docs/MODEL.md
added: 2026-08-30
verify: uv run pytest -k simulation_view
---

**Problem.** `app/simulation_view.py` is 1082 lines: one class, 31 methods, and
a 188-line `__init__` (`:174-362`). It builds every widget, formats every
displayed number, assembles and decimates the chart series, handles eight
control events, refreshes the view, and handles run failure. `core/` is
decomposed along physiological lines — one module per compartment, none over
170 lines — and the view is the one place in `src/` where that discipline
stops.

**Why it matters.** The cohesion cost is ordinary; the safety cost is not.
`_format_percent` (`:1033`) is where displayed precision is decided, and
`docs/MODEL.md`'s "Displayed precision" section is a derivation from the
solver's measured error to the number of digits shown. That derivation
currently terminates in a private static method on a 1082-line Flet class,
which means the one function `docs/MODEL.md` reasons about cannot be read,
cited or tested without loading the whole interface. `CLAUDE.md` treats
presentation correctness as part of safety and requires a displayed value to
be traceable to the transformations that produced it; a formatter buried in a
view class is the weakest link in that chain.

The same argument applies less sharply to the chart series: `_build_chart_series`,
`_refresh_chart_series`, `_decimated_points` and the six module-level sample
accessors (`:134-158`) are a data-shaping concern that already has a sibling
module in `app/chart_downsampling.py`.

**Where.** `app/simulation_view.py` — `__init__` (`:174-362`), the `_build_*`
group (`:438-651`), the chart group (`:134-158`, `:606-833`), the `_handle_*`
group (`:890-943`), and the formatters (`:1019-1082`).

**Approach.** Extract in order of value, smallest first, behavior unchanged:

1. **`app/formatting.py`** — the pure functions: `_format_percent`,
   `_format_subtitle`, `_format_delivered_label`, `_build_metric_value`'s
   initial-value logic. No Flet import. This is the extraction that matters:
   it makes the precision rule directly testable and lets `docs/MODEL.md`
   cite a module rather than a private method.
2. **`app/chart_series.py`** — the six sample accessors, series assembly and
   `_decimated_points`, joining `chart_downsampling.py`.
3. What remains — widget construction, event handling, refresh, failure —
   stays `SimulationView`. Do not split those three apart on principle; they
   are one concern (drive the interface) and separating them would add
   indirection without removing any.

This is a refactor, not a redesign: no displayed value, format or behavior may
change, which is what the existing 63 view tests are for.

**Not a new instruction.** `CLAUDE.md` already holds `src/` to a standard where
"a reader who knows the domain" can follow the code, and already forbids
simulation calculations in UI callbacks. This item is that existing rule
applied to the one module that escaped it, not a new principle.

**Found.** While answering whether this project follows SOLID and whether
`CLAUDE.md` should adopt it as a framework (2026-08-30). The answer to both was
that the existing domain-readability bar is stronger and more decidable — but
this module is the one place where the project genuinely does violate
single-responsibility, by its own standard rather than by an imported one.

**Done when.** The pure formatters live in a Flet-free module with their own
tests, `docs/MODEL.md`'s "Displayed precision" section cites that module, the
chart-series shaping sits beside `chart_downsampling.py`, `simulation_view.py`
holds only interface construction and event handling, and every existing view
test passes unaltered.
