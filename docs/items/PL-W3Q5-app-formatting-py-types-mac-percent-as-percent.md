---
id: PL-W3Q5
title: app/formatting.py types mac_percent as Percent in two signatures and as a bare float in five others, so one parameter carries two types in one module
priority: P2
effort: S
status: done
classes: defect
feature: presentation-safety
milestone: v0.5.23
touches: src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_formatting.py
added: 2026-09-14
closed: 2026-10-11
pr: 1393
verify: ! grep -q 'mac_percent: float' src/anesthesia_sim/app/formatting.py && uv run pytest tests/unit/test_formatting.py
---

**Problem.** app/formatting.py types mac_percent as Percent in two signatures and as a bare float in five others, so one parameter carries two types in one module

**Measured 2026-09-14.** `app/formatting.py` types `mac_percent` as `Percent` in
**two** signatures - `mac_multiple` and `format_mac_multiple` - and as a bare
`float` in **six**: `format_mac_reference`, `mac_awake_band_percent`,
`format_mac_awake_reference`, `chart_axis_top_percent`,
`chart_grid_interval_percent` and `mac_axis_ticks`. The brief above says five;
six is what the file holds today.

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

**Re-confirmed 2026-10-11, at `1ee4e78e`.** Still true, by symbol: the same two
signatures say `Percent` and the same six say `float`. What changed is how far
the fix reaches. `ChartFrame.mac_percent` and `RunFrame.mac_percent` in
`app/chart_frame.py` are typed `float`, though both are built from
`SimulationSnapshot.agent_mac_percent`, a `Percent`. So retyping the six leaves
`mypy` one error, at `dashboard_frame.mac_reference_caption`, which hands
`ChartFrame.mac_percent` to `format_mac_reference`; and the same erasure is why
`chart_frame._hover_value` and `dashboard_frame.off_scale_notice` each rebuild a
`Percent` from the field. Typing the two fields `Percent` clears the error and
both rebuilds, where wrapping the caption's argument would have added a third
(`.claude/rules/core-domain.md` § "A quantity with a check of its own is a
type, checked once"). `touches` widened to the two files.

**Done when.** Every `mac_percent` parameter in `app/formatting.py` is typed
`Percent`, `mypy` passes, and no bare `float` remains on that name in the file.
