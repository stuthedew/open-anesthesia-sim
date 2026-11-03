---
id: PL-BB16
title: 11 of the 29 re-entries in the week of 2026-10-19 were filed on the day the item they re-enter closed; measure whether same-day re-entries are findings filed while the work was done, which PL-04KR separates from a fix that did not hold
priority: P3
effort: S
status: ready
classes: infra
feature: convergence-visibility
touches: docs/items/PL-BB16-11-of-the-29-re-entries-in-the-week-of-2026-10.md
added: 2026-11-03
payoff: the re-entry count that releases print is known to count failed fixes rather than findings made while the work was done, or a follow-up says how to separate them
verify: grep -qE '^[*][*]Same-day re-entries, read' docs/items/PL-BB16*.md
---

**Problem.** 11 of the 29 re-entries in the week of 2026-10-19 were filed on the day the item they re-enter closed; measure whether same-day re-entries are findings filed while the work was done, which PL-04KR separates from a fix that did not hold

**Reproduced 2026-11-03.** Read through `docket.model`'s parser, 33 items filed
from 2026-10-19 to 10-25, in either lane, carry `reenters:`. For 11 of them the
item they re-enter closed on the same day they were filed. Seven of those 11 are
in `one-source-of-truth`: `PL-2T6S`, `PL-3PKN`, `PL-H716`, `PL-PNGQ` and
`PL-S08Z`, among others. `bin/docket inflow` reports 29 re-entries for that
week, which counts the workflow lane only.

**Why it matters.** `PL-04KR` treats a re-entry as evidence that a shipped fix
did not hold. Its own baseline found that every attributed child was filed in
the commit that closed its parent, which is a finding made while the work was
done. A same-day re-entry may be that second kind recorded as the first. If so,
the re-entry count overstates fixes that failed, and a release reads a busy
week as regression.

**Done when.** A paragraph headed `**Same-day re-entries, read <date>.**`
records, for each of the 11 same-day re-entries,
whether it was filed in the commit or pull request that closed the item it
re-enters, or in a later one. It then says whether those filed with the work
should count as re-entries. Where the answer is no, an item is filed for the
change to how `bin/docket inflow` counts them.

**Generator check.** One-off. This is a measurement of how one column reads,
and no item misreads the fact it asks about.
