---
id: PL-W3Q5
title: app/formatting.py types mac_percent as Percent in two signatures and as a bare float in five others, so one parameter carries two types in one module
priority: P2
effort: S
status: ready
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/formatting.py, tests/unit/test_formatting.py
added: 2026-09-14
verify: uv run pytest tests/unit/test_formatting.py && ! grep -q 'mac_percent: float' src/anesthesia_sim/app/formatting.py
---


**Problem.** app/formatting.py types mac_percent as Percent in two signatures and as a bare float in five others, so one parameter carries two types in one module

**Measured 2026-09-14.** `app/formatting.py` types `mac_percent` as `Percent` in
**two** signatures - `mac_multiple` (`:248`) and `format_mac_multiple`
(`:294`) - and as a bare `float` in **six**: `format_mac_reference` (`:336`),
`:366`, `:439`, `chart_axis_top_percent` (`:485`),
`chart_grid_interval_percent` (`:513`) and `mac_axis_ticks` (`:538`). The brief
above says five; six is what the file holds today.

**Why it matters.** This is the module every displayed concentration passes
through, and `Percent` is not decoration: `PL-BQ46` and `PL-KL2Q` exist because
this project has more than one dimensionless convention and mixing them is how a
fraction gets printed as a percent or the reverse. A parameter carrying two
types in one module means the type is not doing its job anywhere in it - a
caller passing a `Fraction` where a `Percent` is meant type-checks in six of the
eight entry points. `CLAUDE.md` asks for unit-aware types or equivalent
safeguards on exactly these paths.

**Why not `safety`.** No displayed value is currently wrong; every caller passes
the right quantity. What is missing is the guard that would catch it if one
stopped - a latent hole rather than a live defect.

**Done when.** Every `mac_percent` parameter in `app/formatting.py` is typed
`Percent`, `mypy` passes, and no bare `float` remains on that name in the file.
