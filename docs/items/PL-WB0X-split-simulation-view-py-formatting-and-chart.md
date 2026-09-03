---
id: PL-WB0X
title: 'Split simulation_view.py: formatting and chart series are not the view''s job'
priority: P1
effort: M
status: ready
classes: refactor
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/chart_downsampling.py, tests/unit/test_simulation_view.py, docs/MODEL.md
added: 2026-08-30
verify: uv run pytest tests/unit/test_simulation_view.py && test -f tests/unit/test_formatting.py && uv run pytest tests/unit/test_formatting.py && ! grep -q flet src/anesthesia_sim/app/formatting.py
---

**Problem.** `app/simulation_view.py` is 1265 lines: one class, 31 methods, and
a 257-line `__init__` (`:249-505`). It builds every widget, formats every
displayed number, assembles and decimates the chart series, handles eight
control events, refreshes the view, and handles run failure. `core/` is
decomposed along physiological lines — one module per compartment, none over
450 lines — and the view is the one place in `src/` where that discipline
stops.

**Why it matters.** The cohesion cost is ordinary; the safety cost is not.
`_format_percent` (`:1216`) is where displayed precision is decided, and
`docs/MODEL.md`'s "Displayed precision" section is a derivation from the
solver's measured error to the number of digits shown. That derivation
currently terminates in a private static method on a 1265-line Flet class,
which means the one function `docs/MODEL.md` reasons about cannot be read,
cited or tested without loading the whole interface. `CLAUDE.md` treats
presentation correctness as part of safety and requires a displayed value to
be traceable to the transformations that produced it; a formatter buried in a
view class is the weakest link in that chain.

The same argument applies less sharply to the chart series: `_build_chart_series`
(`:745`), `_refresh_chart_series` (`:918`), `_redraw_series` (`:950`) and the
seven module-level sample accessors (`:209-235`) are a data-shaping concern that
already has a sibling module in `app/chart_downsampling.py`.

**Where.** `app/simulation_view.py` — `__init__` (`:249-505`), the `_build_*`
group (`:513-770`), the chart group (`:209-235`, `:745-950`), the `_handle_*`
group (`:1073-1127`), and the formatters (`:1202-1265`).

**Approach.** Two extractions, smallest first, behavior unchanged:

1. **`app/formatting.py`** — the pure functions: `_format_percent`,
   `_format_subtitle`, `_format_delivered_label`, `_build_metric_value`'s
   initial-value logic. No Flet import. This is the extraction that matters:
   it makes the precision rule directly testable and lets `docs/MODEL.md`
   cite a module rather than a private method.
2. **`app/chart_series.py`** — the seven sample accessors, series assembly and
   `_redraw_series`, joining `chart_downsampling.py`.

What remains — widget construction, event handling, refresh, failure — stays
`SimulationView` for now. Do not split those three apart on principle; they are
one concern (drive the interface) and separating them here would add
indirection without removing any. The case for splitting them is v0.5.0's, and
it is `PL-B9PY` (decompose `SimulationView` so two runs can be rendered at
once), which is blocked on this item.

This is a refactor, not a redesign: no displayed value, format or behavior may
change, which is what the existing 75 view tests are for.

**Not a new instruction.** `CLAUDE.md` already holds `src/` to a standard where
"a reader who knows the domain" can follow the code, and already forbids
simulation calculations in UI callbacks. This item is that existing rule
applied to the one module that escaped it, not a new principle.

**Sequencing — what each extraction has to precede.** Both remaining pre-MVP
releases are interface releases on an unchanged model, so essentially all the
work between here and MVP lands in this file.

1. `app/formatting.py` **before `PL-DHV7`** (express compartment concentrations
   in MAC multiples as a display unit). `PL-DHV7` rewrites every formatter and
   adds a second unit to `docs/MODEL.md`'s "Displayed precision" derivation. It
   is `safety`/`science`-classed. Doing it against a Flet-free module with its
   own tests is materially safer than doing it against a private static method
   on a 1265-line view class, and the extraction is `S`.
2. `app/chart_series.py` **before v0.4.0's chart work** — `PL-CC23` (scale the
   vertical axis to the run), `PL-SSBP` (a case-length time base), `PL-ZRSP`
   (the F_A/F_I trace) and `PL-F52R` (the MAC-awake band) all touch series
   assembly, and would otherwise each touch it in its current location.

**Where it belongs on the plan (settled 2026-09-02, project owner).** v0.4.0 —
the teachable case. `ROADMAP.md`'s Required scope for that milestone names this
item and both extractions; the milestone's chart and MAC work is what they
gate, and doing them anywhere later means doing that work twice.

This replaces the three placements this brief previously carried — stage 1
before `PL-DHV7` (v0.4.0), the whole item at Gate 1 (ships inside v0.5.0), and
"a `v0.3.x` patch step" — which could not all hold, and which `PL-4C41` (a brief
can contradict itself about its own sequencing) was filed against. The
resolution was to split rather than to pick: one item cannot sit in two
milestones, so the `SimulationView` decomposition proper left this brief for
`PL-B9PY` and stayed at Gate 1, where v0.5.0's side-by-side comparison of two
branches is what genuinely requires it. `ROADMAP.md`'s Gate 0 section records
the same decision from the gate's side.

**Found.** While answering whether this project follows SOLID and whether
`CLAUDE.md` should adopt it as a framework (2026-08-30). The answer to both was
that the existing domain-readability bar is stronger and more decidable — but
this module is the one place where the project genuinely does violate
single-responsibility, by its own standard rather than by an imported one.

**Done when.** The pure formatters live in a Flet-free module with their own
tests, `docs/MODEL.md`'s "Displayed precision" section cites that module, the
chart-series shaping sits beside `chart_downsampling.py`, and every existing
view test passes unaltered.

**Raised to P1 on 2026-09-02, by the checker rather than by judgment.**
`PL-DHV7` (express concentrations in MAC multiples) and `PL-F52R` (draw the
MAC-awake band) are both `P1` `safety`/`science` items whose briefs state they
come after this one, and they now carry `blocked-by` so `docket next` reads the
sequencing the briefs state (`PL-5WFS`). `_outranks_its_blocker` then refuses a
`P1` waiting on a `P2`: "raise `PL-WB0X` to `P1` or above, because nothing here
can start before it does."

So the band here does not mean this refactor could mislead a clinician. It
means two items that could are waiting on it, which is the one case
`docket.toml`'s note about every `P1` carrying a safety class does not cover.
Dropping it back to `P2` requires unblocking `PL-DHV7` first, or the checker
fails.

**What v0.4.1 does to this (added 2026-09-03).** The extraction itself is
unaffected - it is view-layer only, and v0.4.1 touches no `app/` file for its own
sake. Two artifacts it *relocates* are falsified a release later, and moving a
false comment into a new module is worse than leaving it where it is:

- `_format_percent`'s docstring (`app/simulation_view.py:1220`) justifies the
  two-decimal resolution "against the measured error of the shipped operator
  split". `PL-X9KD` re-derives that resolution from the exact step.
- the `SIMULATION_STEP_S` comment (`:52-59`) names
  `core.uptake_system.MAXIMUM_SIMULATION_STEP_S` as "the operator split's
  applicability domain". `PL-X9KD` decides what that bound now means, or removes
  it.

Both should move as citations of `docs/MODEL.md` § "Displayed precision" and
§ "Supported simulation step" rather than as restatements of their content, which
is what makes the extracted module survive the re-derivation unchanged.

**This item should run before `PL-9SH6`, not after.** `PL-9SH6` renames roughly
300 accessor sites including `app/simulation_view.py`; doing it first lands that
rename inside the 1265-line view class this item exists to split, and this item
then moves renamed code. Running this first shrinks `PL-9SH6`'s app-layer
surface instead. `PL-9SH6`'s Sequencing section does not name this item; it
should.