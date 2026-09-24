---
id: PL-02C4
title: Sweep the 2026-09-19 to 09-23 workflow inflow for generators no head records, including the untriaged captures, at the owner's request
priority: P3
effort: S
status: done
classes: housekeeping
milestone: v0.5.9
touches: docs/items, ROADMAP.md
added: 2026-09-23
closed: 2026-09-23
pr: 963
verify: grep -q 'root-cause-of: PL-58JD, PL-59QW, PL-FD5Q, PL-VFJ3' docs/items/PL-WD5Z-gate-dispositions-are-ids-mentioned-in-roadmap.md
---

**Problem.** The owner asked on 2026-09-23 whether every generator is
recorded, since workflow items were still arriving quickly, and asked for the
untriaged captures to be included. `PL-04KR`'s command, which would answer that,
does not exist, so this pass took its two signals by hand.

**What the pass found.**

- **Inflow is falling.** Non-product filings by day since the 09-19 campaign
  read 97, 75, 69, 44 and 32 (the last a partial day). That is gross inflow,
  which `PL-04KR` rejects as a signal.
- **Re-entry is high.** 14 of the 37 filings from 09-22 and 09-23 that carry a
  `**Generator check.**` line name a closed fix that did not reach them. The
  reading is recorded on `PL-04KR`.
- **One unrecorded cluster, now a head.** `PL-WD5Z` records gate dispositions
  kept as prose in `ROADMAP.md`, over `PL-58JD`, `PL-59QW`, `PL-FD5Q` and
  `PL-VFJ3`.
- **One candidate left unverified.** `PL-MB2W` records claims inferred from
  commit shape, at the altitude of `PL-8FJK`'s and `PL-WNCT`'s closed `live`
  verdicts.
- **Three untriaged captures got a generator check.** `PL-58JD`, `PL-VFJ3`
  and `PL-PZ6T` each carry one. `PL-KWCY` was skipped because it is in flight
  on another branch.

**What stays open.** Closed heads that still carry `generator: live` rank
nowhere and hold no pause. That is `PL-TH9K`, which this pass did not change.
