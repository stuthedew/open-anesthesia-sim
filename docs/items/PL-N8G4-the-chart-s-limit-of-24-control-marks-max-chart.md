---
id: PL-N8G4
title: The chart's limit of 24 control marks (MAX_CHART_CONTROL_MARKS) and the change list's limit of 12 lines (MAX_LISTED_ADJUSTMENTS) carry no recorded reason: say why each is that number and what changing it would do
priority: P3
effort: S
status: done
classes: defect, docs
touches: src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/dashboard_frame.py, docs/MODEL.md, docs/INTERFACE.md
added: 2026-11-05
closed: 2026-11-16
pr: 2169
payoff: a developer can change either display limit knowing why it is that number and what a learner would gain or lose
verify: ! grep -qF 'No record gives the' docs/INTERFACE.md
---

**Problem.** The chart's limit of 24 control marks (MAX_CHART_CONTROL_MARKS) and the change list's limit of 12 lines (MAX_LISTED_ADJUSTMENTS) carry no recorded reason: say why each is that number and what changing it would do

**Checked 2026-11-09:** `MAX_CHART_CONTROL_MARKS: Final = 24` in `src/anesthesia_sim/app/chart_frame.py` and `MAX_LISTED_ADJUSTMENTS: Final = 12` in `src/anesthesia_sim/app/dashboard_frame.py` have comments that say what each limit does, but not why it is that number. `docs/INTERFACE.md` § "The control-input timeline" says "No record gives the reason for either value (`PL-N8G4`)". `git log -S` finds both values first in the PySide6 ports, `6a823696` (#578) and `ae8fc7bc` (#588), so the trace has to continue under the names they had before.

**Why it matters.** `.claude/rules/plain-writing.md` asks each chosen value for its reason, taken from a record. Without one, a developer cannot tell whether raising either limit still fits the reference window, or what a learner would lose if one were lowered.

**Done when.** Each limit's comment says why it is that number and what changing it would do, from a record: the value's history before the ports, or a measurement at the 1366 by 700 reference window. Where no record is found, the comment says so, and `docs/MODEL.md`'s sentence says what the trace found.

**Generator check.** One-off. Both values predate the rule that asks for a reason, and the `docs/MODEL.md` rewrite `PL-XT53` filed this item as that rule says.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Present. At 817a4d88, `MAX_CHART_CONTROL_MARKS: Final = 24` in `app/chart_frame.py` and `MAX_LISTED_ADJUSTMENTS: Final = 12` in `app/dashboard_frame.py` already stood with no recorded reason. The `docs/MODEL.md` sentence that names the gap came later (ac461fb2), but the gap did not. So the item joins v0.7.0's frozen list.

**Done 2026-11-16.** The clone was unshallowed with `git fetch --unshallow origin`. On the full history, `git log -S MAX_CHART_CONTROL_MARKS` and `git log -S MAX_LISTED_ADJUSTMENTS` both reach back past the PySide6 ports to `fd0d9aab` (`PL-DR1Z`, #301, 2026-09-04). That change introduced both names, at 24 and 12, in the Flet interface's `app/simulation_view.py`, so they never had other names. Its comments say only what each limit does: a pool built at construction and moved between frames, and a fixed panel that counts what it leaves out. Its commit message, the `PL-DR1Z` item and its `docs/MODEL.md` paragraph "Bounds are displayed, not silent" say the same and give no reason for either number. The only other mention of 24 in the record is the `PL-DR1Z` note that parking all 24 pooled marks cost 48 operations a frame, which is a cost of the number and not a reason for it. `grep -rn` over `docs/items`, `docs/WORKING_NOTES.md`, `ROADMAP.md` and `docs/*.md` for both names and for "24 marks" and "12 lines" found nothing else, apart from `PL-0Z35`, which notes that the mark limit does not bound the chart's columns. No measurement at the reference window was taken, because the brief accepts a comment that says no record was found. So each comment now says that no record gives the reason, what the trace found, and what changing the limit would do, read from the code: the mark pool is built per plot and per run in `qt_chart._control_mark_pool`, and the change list sits in the always-visible record column, which `SimulationView` holds as tall as the run rows and scrolls. The sentence in `docs/INTERFACE.md` § "The control-input timeline" now says what the trace found. The brief named `docs/MODEL.md`, but the sentence had moved to `docs/INTERFACE.md` (#2109). Docs checked: `docs/INTERFACE.md`, `docs/MODEL.md` (no remaining mention of either limit) and `docs/ARCHITECTURE.md` (none).
