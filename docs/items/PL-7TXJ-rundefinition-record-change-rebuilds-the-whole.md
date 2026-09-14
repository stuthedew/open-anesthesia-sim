---
id: PL-7TXJ
title: RunDefinition.record_change rebuilds the whole segment tuple per change, and each segment carries a keyframe, so it is the larger of the two unbounded records
status: untriaged
added: 2026-09-14
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

