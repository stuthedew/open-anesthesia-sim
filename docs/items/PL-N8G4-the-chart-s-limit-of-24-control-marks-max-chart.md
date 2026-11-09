---
id: PL-N8G4
title: The chart's limit of 24 control marks (MAX_CHART_CONTROL_MARKS) and the change list's limit of 12 lines (MAX_LISTED_ADJUSTMENTS) carry no recorded reason: say why each is that number and what changing it would do
priority: P3
effort: S
status: ready
classes: defect, docs
touches: src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/dashboard_frame.py, docs/MODEL.md
added: 2026-11-05
payoff: a developer can change either display limit knowing why it is that number and what a learner would gain or lose
verify: ! grep -qF 'No record gives the' docs/MODEL.md
---

**Problem.** The chart's limit of 24 control marks (MAX_CHART_CONTROL_MARKS) and the change list's limit of 12 lines (MAX_LISTED_ADJUSTMENTS) carry no recorded reason: say why each is that number and what changing it would do

**Checked 2026-11-09:** `MAX_CHART_CONTROL_MARKS: Final = 24` in `src/anesthesia_sim/app/chart_frame.py` and `MAX_LISTED_ADJUSTMENTS: Final = 12` in `src/anesthesia_sim/app/dashboard_frame.py` have comments that say what each limit does, but not why it is that number. `docs/MODEL.md` § "The control-input timeline" says "No record gives the reason for either value (`PL-N8G4`)". `git log -S` finds both values first in the PySide6 ports, `6a823696` (#578) and `ae8fc7bc` (#588), so the trace has to continue under the names they had before.

**Why it matters.** `.claude/rules/plain-writing.md` asks each chosen value for its reason, taken from a record. Without one, a developer cannot tell whether raising either limit still fits the reference window, or what a learner would lose if one were lowered.

**Done when.** Each limit's comment says why it is that number and what changing it would do, from a record: the value's history before the ports, or a measurement at the 1366 by 700 reference window. Where no record is found, the comment says so, and `docs/MODEL.md`'s sentence says what the trace found.

**Generator check.** One-off. Both values predate the rule that asks for a reason, and the `docs/MODEL.md` rewrite `PL-XT53` filed this item as that rule says.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Present. At 817a4d88, `MAX_CHART_CONTROL_MARKS: Final = 24` in `app/chart_frame.py` and `MAX_LISTED_ADJUSTMENTS: Final = 12` in `app/dashboard_frame.py` already stood with no recorded reason. The `docs/MODEL.md` sentence that names the gap came later (ac461fb2), but the gap did not. So the item joins v0.7.0's frozen list.
