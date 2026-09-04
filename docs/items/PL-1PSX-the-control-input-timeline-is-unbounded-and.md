---
id: PL-1PSX
title: The control-input timeline is unbounded and regrouped in full on every frame
status: untriaged
added: 2026-09-04
---

**Problem.** The control-input timeline is unbounded and regrouped in full on every frame

**Why it matters.**

**Where.**

**Done when.**

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
