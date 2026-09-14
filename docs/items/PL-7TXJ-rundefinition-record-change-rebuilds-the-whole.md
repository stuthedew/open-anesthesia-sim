---
id: PL-7TXJ
title: RunDefinition.record_change rebuilds the whole segment tuple per change, and each segment carries a keyframe, so it is the larger of the two unbounded records
priority: P3
effort: M
status: ready
classes: perf
feature: scenario-branching
touches: src/anesthesia_sim/core/run_definition.py, tests/unit/test_run_definition.py
added: 2026-09-14
verify: uv run pytest tests/unit/test_run_definition.py && grep -q 'def test_recording_many_changes_does_not_rebuild_the_whole_record' tests/unit/test_run_definition.py
---


**Problem.** RunDefinition.record_change rebuilds the whole segment tuple per change, and each segment carries a keyframe, so it is the larger of the two unbounded records

**Where.** `core/run_definition.py`, `record_change` - the segment list is a
tuple rebuilt whole on every accepted change, the same shape `PL-1PSX`
measured on `app/controller.py`'s display timeline.

**Why it may matter more than the one PL-1PSX measured.** The two grow
one-for-one - measured over 300 changes on 2026-09-14 - but a `RunSegment`
carries a *keyframe*, the state at the instant the change took effect, where
a `ControlChange` carries six scalars. So this is the larger structure by
some margin, and it is the one the reconstruction claim rests on, which is
why `PL-1PSX` declined to bound the display record and left this untouched.
`PL-1PSX` measured the tuple rebuild at 0.007 ms per append at 1,000
entries, 0.05 ms at 10,000 and 0.89 ms at 100,000; nobody has measured this
one, nor what a keyframe costs in memory.

**Not obviously worth fixing.** The cost is on the input path rather than in
the render loop and is paid once per change rather than once per frame, and
`PL-1PSX` found the reachable extreme to be some three hours of unbroken
dragging. This is filed so the measurement exists rather than because the
shape is known to be a defect - the first step is to measure a keyframe, not
to replace the tuple. Whatever replaces it has to keep `segments` handing out
an immutable record, which is what lets a caller read the run without being
able to advance it.

**Why it matters.** `record_change` (`core/run_definition.py:334`) rebuilds the
segment tuple on every accepted change, and each segment carries a keyframe - a
full compartment state - so the record grows with the number of control changes
and each addition copies everything before it. That is quadratic work over a
linearly growing record, on the object a branch operation reads. The same
docstring shows the design is already careful about *what* it records - three
kinds of no-op change are dropped - so the cost is in the rebuild rather than in
the recording.

**Measure it before banding it higher.** Nothing here is measured yet, and
`CLAUDE.md`'s standard is to name the number before proposing a change: what
matters is the change count a real teaching case reaches and the copy cost at
that count. A case with a few dozen control changes is not a performance
problem; the item exists because the record is unbounded in principle and
`PL-1PSX` is already the bounding item for the control-input timeline. P3 until
a measurement says otherwise.

**Done when.** A run that records many control changes does not copy the whole
segment record per change, the keyframe per segment is not duplicated by the
rebuild, and `tests/unit/test_run_definition.py` pins the growth - with the
measured before-and-after in the item so the next reader knows what it bought.
