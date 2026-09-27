---
id: PL-7TXJ
title: RunDefinition.record_change rebuilds the whole segment tuple per change, and each segment carries a keyframe, so it is the larger of the two unbounded records
priority: P3
effort: M
status: done
classes: perf
feature: scenario-branching
touches: src/anesthesia_sim/core/run_definition.py, tests/unit/test_run_definition.py
added: 2026-09-14
closed: 2026-09-27
pr: 1194
verify: grep -q 'def test_recording_a_change_copies_no_segment_already_recorded' tests/unit/test_run_definition.py && uv run pytest tests/unit/test_run_definition.py
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

[superseded 2026-09-27: the first condition was declined on the measurement
below, and the item closed without replacing the tuple. The second condition
already held, and both it and the growth are pinned by the two tests named
under "Pinned either way".]

## Measured 2026-09-27, before any change

Measured on the tree at `b1ccc844` with the project's Python 3.14 in a cloud
container. Rebuild times are the best of five runs of 200; `record_change` is
the median of 20 calls. The scripts were one-offs and are not kept.

**The rebuild duplicates no keyframe.** The tuple holds references, so
`(*self._segments, new)` copies one 8-byte pointer per segment already
recorded and nothing a segment holds. Checked by identity: after a change,
every earlier segment is the same object it was, and so is its keyframe. A
segment costs about 900 bytes in all (tracemalloc over 2,000 recorded changes,
settings included). Its keyframe is 408 of them: a 48-byte object, a 24-byte
instant, and a nine-entry state tuple of 120 bytes holding nine 24-byte floats.

**What the rebuild costs, against what every change already pays.**

| Segments recorded | Tuple rebuild alone | Whole `record_change` |
| --- | --- | --- |
| 1,000 | 0.005 ms | 1.04 ms |
| 10,000 | 0.057 ms | 1.13 ms |
| 100,000 | 0.53 ms | 2.65 ms |

The floor near 1.0 ms is the matrix exponential that forms the new keyframe,
which any record pays. The rest at 100,000 is the copy plus releasing the old
tuple, about 16 ns per segment already recorded.

**How many changes a run reaches.** `PL-1PSX` measured ten entries per real
second of continuous dragging, and put the reachable extreme at some three
hours of unbroken dragging: about 100,000 changes. A teaching case with a few
dozen adjustments of a second or two each reaches the low thousands, where
the rebuild costs 5 microseconds a change.

**The record's other whole-length readers run per frame, and they are small
too.** Every render tick the fork panel asks for the trunk's fork points,
which `BranchedCase.fork_points_s` builds from `segments` (3.1 ms at
100,000). `_anchored_columns` walks every segment to find the event columns in
its window (2.6 ms at 100,000 segments over 30 days). Both are under 2% of the
200 ms render interval at the extreme, and on these numbers neither is worth
an item. At that density a frame's cost is the two propagators per segment in
view, 368 ms for the 138 events in the last hour, which `docs/MODEL.md`
§ "The run is that record, and every state is derived from it" already
records.

**What a replacement would have to be.** `segments` has to keep handing out
an immutable record: `tests/integration/test_simulation_view.py` compares
`run_segments` before and after an action, and a live view would make those
comparisons pass whatever the action did. With Python's built-in types that
leaves two designs. A list with a cached tuple moves the copy to the first
read after a change, and the fork panel reads the record on every render
tick, so a drag still copies it about once per frame. A persistent sequence
type makes both the append and the snapshot cheap, at the price of a new data
structure in `core/` with its own tests, to save at most 1.6 ms a change after
three hours of dragging.

**What would reopen it.** A path that records on the order of 100,000
changes in one pass. There the rebuild's quadratic sum catches up with the
matrix exponentials: about 80 s against 100 s at 100,000, and eight times
them at a million. Save, load and replay (planned-milestone items 9 and 10)
are where such a path could arrive, and a loader that builds the record in
one pass would avoid it without touching `record_change`.

**Pinned either way.** `test_recording_a_change_copies_no_segment_already_recorded`
checks by identity that each accepted change adds one segment and copies none,
over the 300 changes `PL-1PSX` counted.
`test_a_record_handed_out_is_not_changed_by_later_changes` holds any
replacement to the immutable snapshot this brief asks for, across all three
things `record_change` can do to the open segment.

## Decision 2026-09-27: closed on the measurement

Closed without replacing the tuple (project owner, 2026-09-27, ratified, over
building the replacement the Done-when described). The tuple stays, the two
tests above stay, and `verify:` points at the first of them. A replacement
would add a cache or a new data structure to the record every fork and
keyframe is read from, to save at most 1.6 ms a change after three hours of
unbroken dragging, and no keyframe is duplicated today. The owner agreed the
measurement settled it and said it should have been decided rather than put
to him as a question. If a bulk-recording path arrives, "What would reopen
it" above says when the question comes back.
