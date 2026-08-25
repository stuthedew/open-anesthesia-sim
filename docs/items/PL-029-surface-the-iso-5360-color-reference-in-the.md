---
id: PL-029
title: Surface the ISO 5360 color reference in the interface
priority: P3
effort: S
status: ready
classes: ux, docs
feature: vaporizer-controls
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/theme.py
added: 2026-08-24
---

**Problem.** `AgentColorScheme` records `standard_color_name`,
`standard_color_munsell`, and `standard_color_pantone` for every agent, but
nothing in the interface reads them. A user sees a colored badge with no
indication that the color reproduces a cited standard rather than being
decoration.
**Why it matters.** Not a correctness defect — the provenance is recorded in
`app/theme.py` and `docs/MODEL.md`. But a simulator that deliberately
reproduces a real safety feature teaches more when it says so: a learner who
does not already know the ISO 5360 color convention cannot learn it from an
unlabeled colored badge.
**Where.** `app/simulation_view.py` (header badge and dropdown),
`app/theme.py`.
**First step.** Decide the surface. A tooltip on the badge is cheapest and
adds no persistent clutter, but tooltips are invisible to touch users and
usually to screen-reader users.
**Done when.** The agent's standard color name and its ISO 5360 source are
discoverable from the interface without reading the source, and the chosen
surface works for keyboard and touch users.
