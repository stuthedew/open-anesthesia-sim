---
id: PL-DR1Z
title: Record the control-input timeline and mark it on the chart
priority: P1
effort: M
classes: feature, ux
feature: teachable-case
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md
added: 2026-08-25
status: done
closed: 2026-09-04
verify: uv run pytest tests/integration/test_controller.py tests/unit/test_simulation_view.py && grep -q 'def test_a_recorded_change_is_marked_on_the_chart_at_its_own_time' tests/unit/test_simulation_view.py
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

**Raised to `P1` (2026-09-03, `PL-9K7K`).** Not a reassessment of this item on
its own: `PL-ZRSP` (plot the F_A/F_I ratio) is `P1`, science-classed, and now
`blocked-by` this item, because its trace is the textbook wash-in curve only
while inspired concentration is held constant and this timeline is what makes a
mid-run dial change visible. A `P1` waiting on a `P2` is what `docket check`
refuses, and correctly: whatever gates safety-classed work is that work's
schedule. The band follows the dependency rather than a fresh judgment about
this item's own value.

**Closed 2026-09-04.** Recorded in the controller, marked on the chart, listed
beside it, and specified in `docs/MODEL.md` § "The control-input timeline".
Five things the brief did not anticipate, each of which changed the design:

1. **A slider reports continuously while dragged**, so one turn of one control
   reaches the model as a run of settings. The record keeps all of them, because
   the model was stepped under all of them and the reconstruction property is
   what this item is for; the display groups them into one *adjustment*. The
   grouping is exact rather than inferred - `begin_control_adjustment` declares
   the boundary from the input device - because no time threshold survives
   `PL-VM40`'s playback multiplier, which changes how much simulated time one
   drag spans.
2. **A change superseded within one simulation step was never integrated**, so
   recording it would describe a run that did not happen. Changes collapse per
   step, and a change undone within a step leaves no entry.
3. **`set_circuit_volume` is recorded too**, though it has no slider. It changes
   the run, so a timeline omitting it would not reconstruct one; five controls
   rather than the brief's four.
4. **The recorded value is read back off the compartment**, not taken from the
   caller. The core rejects rather than clamps today, so the two agree - but a
   record of what was *asked for* would diverge silently the day that changed.
5. **`→` has no glyph in the Flutter client** and drew as a replacement box, so
   the direction of the change reached the reader as a missing character. Found
   by rendering the running app; no test here would have caught it, since every
   assertion compares strings the same font-less process produced.
   `test_a_rendered_line_uses_only_glyphs_the_interface_can_draw` is the guard.

Verified against the running app (`FLET_FORCE_WEB_SERVER=true
FLET_WEB_NO_CDN=true`, Chromium over the DevTools protocol, per `PL-CQRL`): a
103 s run with four adjustments drew four marks at the right times and listed
them correctly, most recent first.
