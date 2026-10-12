---
id: PL-0FJ8
title: A MAC divisor's positivity is checked in five app/formatting.py functions and by nothing that holds it: AgentParameters admits Percent(0.0) built directly, only the loader's PositivePercent refuses one, and format_mac_reference checks nothing, directly or through another
priority: P1
effort: S
status: done
classes: safety, defect
feature: parse-dont-validate
milestone: v0.5.23
touches: src/anesthesia_sim/core/parameters.py, tests/unit/test_parameters.py
added: 2026-10-11
closed: 2026-10-11
pr: 1424
payoff: a zero or negative MAC is refused when the agent record is built, so no screen can print 1 MAC = 0.0% or divide by it
verify: grep -q 'def test_an_agent_with_a_non_positive_mac_is_refused' tests/unit/test_parameters.py
recurrences: 2026-10-11 PL-HPKK
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

**Reproduced 2026-10-11** on `main` at `16a20a4f`:
`replace(load_agent_parameters("sevoflurane"), mac_percent=Percent(0.0))` builds,
and `format_mac_reference("sevoflurane", Percent(0.0))` returns
`1 MAC sevoflurane = 0.0%`.

**Why it matters.** The MAC reference is the divisor every MAC multiple on screen
is produced with, and `CLAUDE.md` names MAC-equivalent values safety-critical. A
record that admits zero lets the one formatter without its own check print an
impossible reference that looks plausible, and leaves the other five to refuse
at draw time rather than at construction.

**Scope decided at triage, 2026-10-11.** The record refuses it.
`.claude/rules/core-domain.md` § "Where it stops" says a frozen record whose
constructor refuses its own fields is already the parsed type for them, so
`AgentParameters.__post_init__` rejecting a non-positive `mac_percent` is that
rule applied rather than one of two defensible designs. The five formatter checks
stay: the formatters take a bare `Percent`, not the record, and removing them
needs a checked strictly-positive type - the widening that section reserves for
further evidence, and not this item's.

**Done when.** Building `AgentParameters` with a zero or negative `mac_percent`
raises, shown by a unit test; the five formatter checks are unchanged.
