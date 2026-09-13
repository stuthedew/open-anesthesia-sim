---
id: PL-4V6B
title: Decide whether the decision archive should be separated from the work queue
priority: P3
effort: M
status: needs-decision
classes: infra, planning
feature: docket-store
touches: subprojects/docket, docs/items
added: 2026-09-13
---

**Problem.** Decide whether the decision archive should be separated from the work queue
**Why it matters.** `docs/items/` now serves two purposes that pull in
different directions. It is the work queue - what to do next, what is in
flight, what a gate still owes - and it is also the project's decision archive:
several hundred closed and dropped items whose value is the recorded reasoning,
which is what stops a refuted approach being re-proposed. The capture is one
line and does not say which failure it saw, so the first thing the decision has
to settle is what "separated" would mean: separate directories, a separate
rendered view, or only a separate way of reading the same files.

**What is already settled, so the answer starts here rather than from
scratch.** `PL-KM3X` (partition closed item bodies out of the live store) was
dropped on the same day this was captured, on three measured grounds: no
measurable parse cost (76 ms of an 830 ms command whose cost is git); a
partition that would not fix the one real threshold, which is directory entry
count and which a second file per item makes worse; and the shape argument -
this store is cross-referenced (86.1%, 2,773 edges), and cross-referenced
record stores stay flat. The third is not a performance argument and reaches
any split of the files, so moving closed items into their own directory is
already refuted and is in `docs/dead-ends.md`. What `PL-KM3X` does not answer is
whether the archive is a distinct kind of record wanting its own reading
surface, which is what this capture appears to ask.

**Done when.** Either a decision is recorded that the queue and the decision
archive stay one store, with the reasoning added to `docs/dead-ends.md` so the
question is not re-opened a third time; or a mechanism is named that separates
the reading without separating the files, and items are written for it.

**Decision needed.** Does the decision archive get a reading surface of its own, and if so one that does not move the files - given that `PL-KM3X` already refuted moving them?
