---
id: PL-LKX7
title: docs/INTERFACE.md § "Displayed precision" says a maximized 1280 px screen opens the readout row on seven columns (measured 2026-09-27), but that predates the region's 0.82/0.18 split: at 1366 px the region's 1320 px leaves the readouts 1073 px, so a 1280 px screen's 1234 px likely leaves about 1000 px, below the 1005 px that seven across needs
priority: P2
effort: S
status: done
classes: defect
feature: interface-areas
touches: docs/INTERFACE.md, tests/integration/test_simulation_view.py, docs/items/PL-92XM-at-a-1280-px-window-the-control-change-record.md, docs/items/PL-6XPZ-below-about-1366-px-of-window-width-the-control.md
added: 2026-11-04
closed: 2026-11-14
pr: 2156
payoff: a reader on a 1280 px laptop sees all seven readouts in one row, or the model specification says plainly that the row opens on four there
verify: grep -rq 'def test_a_1280_px_window_opens_one_run_s_readout_row_on_seven_columns' tests/integration
reenters: PL-4FBP
---

**Problem.** docs/INTERFACE.md § "Displayed precision" says a maximized 1280 px screen opens the readout row on seven columns (measured 2026-09-27), but that predates the region's 0.82/0.18 split: at 1366 px the region's 1320 px leaves the readouts 1073 px, so a 1280 px screen's 1234 px likely leaves about 1000 px, below the 1005 px that seven across needs

**Read at triage, 2026-11-04.** `docs/MODEL.md` now says that whether a
maximized 1280 px screen opens on seven columns has no test yet, and names this
item. Measured with the integration tests' `_shown_view` and offscreen font on
`main` at `f369249fa`: a region 1320 px wide leaves the readout row 1073 px and
opens on seven, matching the section's 1366 px paragraph. A region 1234 px wide,
which is what the section says a maximized 1280 px screen gives, leaves the row
1002 px. That is 3 px short of the 1005 px that seven across needs, so the row
opens on four.

**Why it matters.** On a 1280 px laptop all seven readouts stay on screen, but
on two lines, so comparing the compartments needs a scan rather than one glance.
The owner's ratified decision of 2026-09-27 (`PL-Z4K6`), taken over raising the
window fraction to 0.85, rested in part on a maximized 1280 px screen opening on
seven. The record column added later (`PL-F2YS`) took that outcome away.

**Done when.** A test pins what a maximized 1280 px screen opens on, and
`docs/INTERFACE.md` states that outcome in place of "has no test yet".
**Recommendation:** restore seven across. The row is 3 px short, and the
2026-09-27 decision chose its route partly for this outcome. Where seven cannot
be restored without making the control-change record harder to read, state the
four-column outcome. Either way, all seven values stay on screen, so under the
owner's rule of 2026-10-18 this placement is the working session's call.

**Generator check.** An instance of `PL-4FBP`'s fact, the link between a
document sentence and the tree fact it restates, filed after the head closed.
The 1280 px sentence restated a measurement, and the change of layout in
`PL-F2YS` updated the 1366 px paragraph beside it but not this one.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. `docs/MODEL.md` at `817a4d88` already said a 1280 px screen gives about 1234 px, beside the 0.82 share that `simulation_view.py` already used.

**Disposition under PL-BLN0 (2026-11-09).** PL-BLN0 is the head over the
sentences that went stale when the code they restated changed. It binds every
paragraph of `docs/ARCHITECTURE.md` and of the last chapter of
`docs/interface-provenance.md` to the code it describes, and leaves the free
prose of `docs/MODEL.md` outside that binding, for the reason its brief gives.
This item's sentence is in that free prose, and correcting it also needs a new
measurement in the running app, so it stays its own item.

**Built 2026-11-14.** The row already opens seven across on a 1280 px window,
so nothing in the layout changed. Measured with `_shown_view` on `main` at
`26dba5d`: a 1280 px window gives the region 1248 px, not the 1234 px of
2026-09-27, and the readout column at least 1014 px, 9 px more than the 1005 px
that seven across needs. Compare mode gives the same. A 1366 px window now
gives the region 1334 px, where `PL-F2YS` measured 1320 px on 2026-10-18. Both
older figures are 14 px narrower than today's, which matches a vertical scroll
bar beside the region. Which change removed it was not traced. The
recommendation to restore seven across therefore needed no lever.

`test_a_1280_px_window_opens_one_run_s_readout_row_on_seven_columns` pins the
outcome, beside the 1366 px test. `docs/INTERFACE.md` § "The readout row's width
condition" states it for the reader and updates both windows' figures in the
note for developers.

**Found while measuring.** The readout column's width at 1280 px moved between
runs: 1014 px with a clean checkout and 1028 px with uncommitted changes. The
transport row's minimum width includes the version badge, whose text gains
".dirty", and the run rows cannot narrow below it, so the record column loses
the difference. That is `PL-6XPZ`'s mechanism, and `bin/docket new` recorded
it as a recurrence (`PL-92XM`). The readout row seats seven in both states.

**Docs swept.** `docs/INTERFACE.md` (this section and the note for developers),
`docs/MODEL.md` (no 1280 px sentence remains since `PL-CTXZ` moved the
interface sections), `README.md` (no window-width figures).
