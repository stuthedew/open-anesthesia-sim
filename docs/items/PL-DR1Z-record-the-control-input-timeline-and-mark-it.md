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
