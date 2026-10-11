---
id: PL-0FJ8
title: A MAC divisor's positivity is checked in five app/formatting.py functions and by nothing that holds it: AgentParameters admits Percent(0.0) built directly, only the loader's PositivePercent refuses one, and format_mac_reference checks nothing, directly or through another
status: untriaged
added: 2026-10-11
---

**Problem.** A MAC divisor's positivity is checked in five app/formatting.py functions and by nothing that holds it: AgentParameters admits Percent(0.0) built directly, only the loader's PositivePercent refuses one, and format_mac_reference checks nothing, directly or through another

**Found 2026-10-11, working `PL-W3Q5`.** `mac_multiple`,
`mac_awake_band_percent`, `chart_axis_top_percent`,
`chart_grid_interval_percent` and `mac_axis_ticks` in `app/formatting.py` each
open with the same `mac_percent must be strictly positive` refusal, and their
docstrings say the loader's `PositivePercent` already makes a non-positive MAC
unreachable from a shipped data file. That holds for the file and for nothing
past it. `AgentParameters.__post_init__` checks only that `mac_percent` was
built as a `Percent`, and a `Percent` admits zero, so
`replace(load_agent_parameters("sevoflurane"), mac_percent=Percent(0.0))`
builds. Measured that day: `mac_multiple` and `chart_axis_top_percent` refuse
the result, and `format_mac_reference` prints `1 MAC sevoflurane = 0.0%`.

**Why a finding rather than a defect.** Nothing but the loader builds an
`AgentParameters` on an application path, so no displayed value is wrong. It is
the shape `.claude/rules/core-domain.md` § "A quantity with a check of its own
is a type, checked once" refuses: one quantity's own check made again by each
function that receives it, with the one that does not check being the way in
nobody guarded.

**What a fix has to decide.** A `Percent` carries no proof of sign, so the five
checks can go only if what reaches them carries one: a checked type for a
strictly positive percent, built where the MAC is parsed and taken by every
divisor parameter, or `AgentParameters` refusing a non-positive MAC (the record
as the parsed type, by that section's "Where it stops") with the five checks
kept, since the formatters would still take a bare `Percent`. The first
re-types the six signatures `PL-W3Q5` just typed; the second closes the hole
and removes nothing.
