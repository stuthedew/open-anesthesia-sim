---
id: PL-029
title: Surface the ISO 5360 color reference in the interface
priority: P3
effort: S
status: ready
classes: ux, docs
feature: vaporizer-controls
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/theme.py
added: 2026-08-24
---

> **Groomed 2026-09-22 (`PL-Y4YG`): still owed; the surface has moved to Qt.**
> Nothing in the interface reads `standard_color_name`,
> `standard_color_munsell` or `standard_color_pantone` yet;
> `tests/unit/test_theme.py` is their only reader. The badge's writer is now
> `RunView._apply_agent_color_scheme` in `app/run_view.py`:
> `.claude/rules/ui-color.md` makes it the only writer of the ISO 5360
> identity pair and `tools/agent_identity_check.py` reads it to learn the
> identity set, so the name and source belong beside that method rather than
> in a second writer. `touches` names `app/run_view.py` in place of
> `app/simulation_view.py`. The **First step**'s trade-off is now Qt's:
> `setToolTip` is still hover-only, so a tooltip fails **Done when** for touch
> users, and `setAccessibleDescription` is exposed to assistive technology
> through `QAccessible` without being drawn. Visible text, or something a tap
> or a key reveals, is what can pass it.

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
