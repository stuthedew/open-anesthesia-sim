---
id: PL-2CS8
title: "Nothing carries roadmap item 24's stated prerequisite: the display constants are scattered across theme.py, simulation_view.py and duplicated core/app defaults, with no item to consolidate them"
priority: P2
effort: M
status: needs-decision
classes: refactor
feature: presentation-safety
touches: src/anesthesia_sim/app/theme.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/main.py, tools/contrast_check.py, tools/agent_identity_check.py, tests/unit
added: 2026-09-08
---

**Problem.** `ROADMAP.md` § "Planned milestones" item 24 names its own
prerequisite — consolidate the UI/display constants "into one settings module
the panel can read from and write to, rather than adding a fourth scattered
location" — and § "Development pathway" Phase 2 orders it *first* of everything
in that phase. No queue item carries it. Two closed items reference it as
future work and neither claims it.

What is actually scattered, measured 2026-09-08:

- `app/theme.py` holds eight colours, three spacing numbers and the three ISO
  5360 agent colours. Everything else is inline in `app/simulation_view.py`:
  about 110 `color=`, 40 size/weight and 30 spacing sites.
- A second, competing constant set lives in `app/simulation_view.py` —
  `COMPACT_PAGE_PADDING`, `COMPACT_PANEL_PADDING`, `COMPACT_PANEL_RADIUS` —
  alongside `METRIC_NAME_SIZE`, `METRIC_QUALIFIER_SIZE`,
  `METRIC_SECONDARY_VALUE_SIZE`, `CHART_HEIGHT`, `WASH_IN_CHART_HEIGHT`,
  `AGENT_SELECTOR_WIDTH`, `LEGEND_SWATCH_WIDTH` and `NEW_CASE_DIALOG_WIDTH`.
- The six chart trace colours (`CIRCUIT_COLOR` through `FAT_COLOR`) are module
  constants in `app/simulation_view.py`, not in `app/theme.py`.
- The gridline and divider grey is the bare literal `"#D9E2EC"`, repeated at
  five sites and defined nowhere.
- `PANEL_PADDING` and `PANEL_RADIUS` in `app/theme.py` are dead — referenced
  from no file in `src/`, `tests/` or `tools/`. The `COMPACT_*` pair
  superseded them.
- `PAGE_PADDING` is applied in `app/main.py` and then overwritten by
  `SimulationView` with `COMPACT_PAGE_PADDING`, so the theme's value never
  reaches the screen at all.

**Why it matters, and why it gets worse rather than staying still.** Phase 2's
own reason is that "every control added before it spreads the same scattered
defaults further", and v0.5.0 is about to add bookmark lists, MAC targets, a
two-run overlay and per-run readouts. It is also the second consumer problem:
the v0.6.0 schematic draws the same six compartments, so `CIRCUIT_COLOR`
through `FAT_COLOR` acquire a reader outside the module that defines them.

Two of the findings above are live defects rather than untidiness. A theme
constant that is silently overwritten is a value a reader of `app/theme.py`
would reasonably believe is in force. A colour that exists only as a repeated
literal is invisible to `tools/contrast_check.py`, which extracts named
constants — so it is unmeasured while the file it sits in reports as checked.

**Where.** `app/theme.py`, `app/simulation_view.py`, `app/main.py`.

**And it reaches two tools, which the obvious `touches` would miss.**
`tools/contrast_check.py` and `tools/agent_identity_check.py` each hardcode
`src/anesthesia_sim/app/theme.py` and `src/anesthesia_sim/app/simulation_view.py`
as the files they parse with `ast`, and `contrast_check` resolves every symbol
named in a `REQUIREMENTS` reason against those two files — so moving a colour
constant to a new module fails `make check` until the tool's file list and the
reasons move with it, in the same commit. `.claude/rules/ui-color.md`
judgment 1 already requires the second half of that; the first half is what a
consolidation adds. This is why `touches` above names `tools/`.

**Decision needed.** Whether the destination is one settings module serving
both the tokens and item 24's user-settable preferences, or a tokens module
now with the preferences store built on it later. The first is what item 24
asks for and risks designing a preferences store before there is a panel to
read it; the second is smaller and risks becoming the fourth scattered
location the roadmap warns against. Also whether the six trace colours move,
given `PL-GVXP` fixed trace separation on dash pattern rather than colour and
`.claude/rules/ui-color.md` judgment 3 turns on where they are read.

**Done when.** No colour, size, spacing or radius literal remains in
`app/simulation_view.py`; `app/theme.py`'s dead constants are gone; the page
padding a reader finds in the theme is the one the page uses; the gridline grey
is a named constant with a declared contrast requirement; and `make check`
passes with both tools reading the new location.
