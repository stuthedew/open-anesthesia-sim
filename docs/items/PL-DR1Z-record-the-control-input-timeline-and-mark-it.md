---
id: PL-DR1Z
title: Record the control-input timeline and mark it on the chart
priority: P2
effort: M
status: ready
classes: feature, ux
feature: teachable-case
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md
added: 2026-08-25
---
**Problem.** The controller records concentrations. Nothing records *why* they
moved. Once a fresh gas flow, vaporizer dial, ventilation or cardiac-output change
has been made, the fact that it was made - and when - is unrecoverable from the run.

**Why it matters.** A curve without its input history is not a result anyone can
check, and the classic exercises in this field are all of the form "change one
thing, look at what happened": overpressure then dial back, drop the flow, halve the
cardiac output. A learner who cannot see where they dialled back cannot read their
own experiment. This is the recording half of `ROADMAP.md` planned-milestone item 8,
which is the prerequisite under items 9 to 12 - and the half that is expensive to
add later, because runs recorded without it stay unrecoverable.

**Where.** `app/controller.py` (alongside `concentration_history`, and on the
snapshot), `app/simulation_view.py` (marks on the chart and a plain list beside it),
`docs/MODEL.md` § "Interface boundary".

**Scope.** Recording only. Replaying the timeline, saving it, and branching from it
are items 9 to 12 and are explicitly out. Each entry is the simulated time the
change took effect, which control, and the old and new values - enough that the run
could be reconstructed by re-applying them, which is the property item 8 needs, not
merely enough to draw a mark.

**Done when.** Every control change during a run is recorded with the simulated time
it took effect and is visible on the chart and in a readable list; a refused setting
records nothing, since it did not take effect; and reset clears the timeline with
the rest of the run's history.

**What v0.4.1 does to this (added 2026-09-03).** The four controls this item
stamps are the forwarding setters on `AgentUptakeSystem`, and two of them are
renamed one release later: `set_delivered_concentration` and the
`delivered_concentration_fraction` it writes become the
`_partial_pressure_fraction` form under `PL-9SH6`, and the circuit fraction
becomes `inspired_` under `PL-3TLK`. Since the timeline entries are recorded as
`(simulated_time, control, value)` tuples rather than a fixed struct, the control
*identifier* is a stored string that will outlive the rename - so pick it from the
domain vocabulary now (`delivered`, not `vaporizer_dial`; `inspired`, not
`circuit`) rather than from the current accessor names, or the recorded history
of every past run carries retired names.

Nothing is invalidated: the recording design, the tuple form and the
nitrous-oxide argument behind it are all independent of v0.4.1.