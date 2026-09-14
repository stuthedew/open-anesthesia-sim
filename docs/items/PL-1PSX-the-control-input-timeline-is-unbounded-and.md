---
id: PL-1PSX
title: The control-input timeline is unbounded and regrouped in full on every frame
priority: P2
effort: M
status: done
classes: perf
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/control_timeline.py, tests/unit/test_simulation_view.py, tests/unit/test_control_timeline.py, docs/MODEL.md
added: 2026-09-04
closed: 2026-09-14
pr: 563
verify: uv run pytest tests/unit/test_simulation_view.py && grep -q 'def test_the_control_timeline_is_not_regrouped_when_it_has_not_grown' tests/unit/test_simulation_view.py
---

**Problem.** `SimulationController._control_timeline` grows without limit,
and `SimulationView._refresh_view` calls `group_adjustments` over the whole
of it on every frame. Both are the shape PL-011 bounded for the
concentration history and PL-Q197 is removing from the render loop, arriving
in a second record that neither covers.

**Why it matters.** The timeline is bounded by user actions rather than by
run length, which is why this is a `P2` rather than the defect PL-011 was -
a person cannot drag a slider often enough to matter at 1x. The playback
multiplier (PL-SN2C) is what changes the arithmetic: a drag emits settings
at the *event* rate while simulated time advances at the multiplied rate,
so a run played at 60x records many more entries per gesture, and a long
teaching session accumulates them. The per-frame regroup is then O(entries)
work in the render loop, which is exactly the class PL-Q197 measured as the
cause of the stall.

**Where.** `app/controller.py` (the record), `app/simulation_view.py` (the
per-frame call), `app/control_timeline.py` (the grouping).

**Approach.** Two independent halves; the second is worth doing even if the
first is judged unnecessary. Cache the grouping against the timeline's
length rather than recomputing it, since the record is append-only and a
frame that added nothing needs no regroup. Separately, decide whether the
record needs a ceiling at all, and if it does, whether dropping the oldest
entries is acceptable - it breaks the reconstruction property
`docs/MODEL.md` § "The control-input timeline" states, so a ceiling that
drops entries has to say so on the display, the way the chart's mark pool
and the panel's line count already do.

**Done when.** A run with thousands of recorded changes costs a frame no
more than a run with none, and the record's behavior at its limit is either
bounded-and-stated or deliberately unbounded with the reason recorded.

**Decided, 2026-09-14: the grouping is cached, the record is not bounded.**
Both halves were settled by measurement rather than by argument, and one of
the measurements contradicts this brief.

**The brief's stated mechanism is false.** A change is recorded only once
per simulation step - `_record_control_change` collapses a second change to
one control at the same `elapsed_s` - and a step is a property of the tick,
not of simulated time. So a drag records at most one entry per tick however
fast the slider reports, and the playback multiplier does not enter into
it: measured at ten entries per real second of continuous dragging at 1x,
5x, 20x, 60x and 300x alike, and *one* entry for a drag made while the run
is paused. The `PL-SN2C` multiplier therefore changes nothing about how
fast this record grows.

**The per-frame regroup was real, and is fixed.** `group_adjustments` costs
0.88 ms at 1,000 entries, 8.8 ms at 10,000 and 94.6 ms at 100,000, against
a 200 ms `RENDER_INTERVAL_S` - paid every frame, forever, for an answer
identical to the previous frame's on every frame that recorded nothing.
`AdjustmentGrouping` in `app/control_timeline.py` holds the last result and
returns it while the record is unchanged.

**Keyed on the record's identity, not its length, which is what this brief
proposed.** The record is not purely append-only: a control moved twice
inside one step *replaces* the newest entry, same length and different
value. A length-keyed cache would go on serving the superseded grouping, so
the panel would state a setting the run was never computed under - a
presentation-correctness failure under `CLAUDE.md`'s safety standard rather
than a missed optimisation. The record is an immutable tuple the controller
replaces whole, so `is` decides the question exactly and in constant time.
`test_a_superseded_change_is_regrouped_though_the_record_did_not_grow` and
`test_a_change_superseded_within_a_step_reaches_the_panel` were both
confirmed to fail against a length-keyed implementation.

**No ceiling on the record, for two reasons.** Dropping the oldest entries
would retire the beginning of a case, which is the part a learner goes back
to. And it would bound nothing: `RunDefinition._segments` grows one segment
*and one keyframe* per accepted change - measured one-for-one with the
timeline over 300 changes - and is not bounded, so capping the cheaper of
the two structures would cost the display's completeness and buy no memory
bound. At the reachable extreme - some three hours of unbroken dragging -
the record is under 9 MB. Recorded in `docs/MODEL.md` "The control-input
timeline" under "Bounds are displayed, not silent", which is where a reader
meets the display's own ceilings and would ask.

**Not changed: the O(n^2) append.** `_record_control_change` rebuilds the
whole tuple per entry - 0.007 ms at 1,000 entries, 0.05 ms at 10,000, 0.89
ms at 100,000. It is on the input path rather than the render loop and is
paid once per entry rather than once per frame, and a list would give up
the immutability a frozen snapshot rests on. Left alone deliberately; the
numbers are here so a later session need not re-measure to reach the same
conclusion.
