---
id: PL-BB16
title: 11 of the 29 re-entries in the week of 2026-10-19 were filed on the day the item they re-enter closed; measure whether same-day re-entries are findings filed while the work was done, which PL-04KR separates from a fix that did not hold
priority: P3
effort: S
status: done
classes: infra
feature: convergence-visibility
touches: docs/items/PL-BB16-11-of-the-29-re-entries-in-the-week-of-2026-10.md
added: 2026-11-03
closed: 2026-11-14
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

**Same-day re-entries, read 2026-11-14.** I read the 11 items through
`docket.model`'s parser. For each, `git log --diff-filter=A` gave the commit
that added the re-entering item, and the closed item's `pr:` field, checked
against `git log -S 'status: done'`, gave the pull request that closed it. The
repository squash-merges, so one commit is one pull request. Eight were filed
with the closing work and three were filed later.

1. `PL-2T6S` re-enters `PL-JS6P`: filed with the work, both in #1782.
2. `PL-3PKN` re-enters `PL-S08Z`: filed with the work, both in #1802.
3. `PL-646J` re-enters `PL-YV90`: filed with the work, both in #1721.
4. `PL-7FPD` re-enters `PL-CZXN`: filed with the work, both in #1728.
5. `PL-H57W` re-enters `PL-CZXN`: later. `PL-CZXN` closed in #1728, and
   `PL-H57W` was added about three hours later by #1744, the triage of
   `PL-7FPD`'s gaps.
6. `PL-H716` re-enters `PL-3PKN`: filed with the work, both in #1810.
7. `PL-PNGQ` re-enters `PL-N4FP`: filed with the work, both in #1738.
8. `PL-S08Z` re-enters `PL-MM3Q`: later. `PL-MM3Q` closed in #1762, and
   `PL-S08Z` was added about five hours later by #1781.
9. `PL-TBX9` re-enters `PL-PNSV`: filed with the work, both in #1835.
10. `PL-TLPH` re-enters `PL-9JHM`: later. `PL-9JHM` closed in #1616, merged at
    20:40 CDT on 2026-10-18, which is 2026-10-19 in UTC, and `PL-TLPH` was added
    by #1688 about 23 hours later.
11. `PL-YV90` re-enters `PL-TLPH`: filed with the work, both in #1688.

The eight filed with the work should not count as re-entries. `PL-04KR` counts a
re-entry as evidence that a shipped fix did not hold. A filing added by the pull
request that closed its parent was known before that fix shipped, so the fix
cannot have failed to reach it. It records a gap found while building, which is
the filed-while-working kind that `PL-04KR`'s baseline found in all 623 of its
parent-child links. Two of the eight form a chain in `one-source-of-truth`:
`PL-S08Z`'s pull request filed `PL-3PKN`, whose pull request filed `PL-H716`.
Each fix found the next copy of the same fact, so counting both as failed fixes
would read a thorough sweep as regression. The three filed later are
genuine re-entries by `PL-04KR`'s definition, since each was found after the fix
it names had merged. So the same-day count of 11 overstates fixes that did not
hold by eight. `PL-C47M` is filed for the change to how `bin/docket inflow`
counts them.
