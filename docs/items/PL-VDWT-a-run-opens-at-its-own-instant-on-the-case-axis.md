---
id: PL-VDWT
title: A run opens at its own instant on the case axis, not at zero: three members found on 2026-09-14 and closed by 2026-09-27
priority: P3
effort: S
status: done
classes: defect
feature: defect-review-2026-10
touches: docs/items
added: 2026-10-25
closed: 2026-10-25
pr: 1783
payoff: the audit records that a run's opening instant was one mechanism behind three defects
verify: grep -qE '^generator: spent' docs/items/PL-VDWT-*.md
root-cause-of: PL-3LZB, PL-59WB, PL-7TBQ
generator: spent - all three came from one review on 2026-09-14, none filed since 2026-09-27, and case instants now have a checked type of their own (PL-CN5S)
misread: Where a run opens on the case axis: at its own instant, not at zero
---

**Problem.** A run opens at its own instant on the case axis, not at zero: three members found on 2026-09-14 and closed by 2026-09-27

**The fact the members misread.** Once a run can open at a branch's instant, its own start is not zero. Each member assumed it was:

- `PL-3LZB`: `RunDefinition`'s lower bound was the literal 0.0, so a definition opening later answered from its last segment.
- `PL-59WB`: `chart_time_base.fit_to_run` took a case instant as a run length.
- `PL-7TBQ`: `has_recorded_run` read `elapsed_s > 0.0`, so a new branch counted as recorded.

**Why it is spent.** All three came from one review of the branching work on 2026-09-14, and none has been filed since 2026-09-27. Case instants now have a checked type of their own (`PL-CN5S`, under `parse-dont-validate`).

**Why it matters.** The audit of where product defects come from needs each shared cause recorded, so that a recurrence is recognised as one.

**Done when.** This head records its members and why it is spent.

**Generator check.** Recorded for the audit by `PL-R4Y2`'s defect review.
