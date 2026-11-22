---
id: PL-MK05
title: The chart's 24 control marks and the change list's 12 lines have no recorded reason (PL-N8G4's trace found none): measure what each limit shows at the 1366 by 700 reference window and record a reason, or a changed value, from that measurement
priority: P3
effort: M
status: ready
classes: ux
feature: interface-matches-its-spec
touches: src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/dashboard_frame.py, docs/INTERFACE.md
added: 2026-11-16
payoff: The number of control changes a learner can see on the chart and in the change list is set by what fits at the reference window, not by an unexplained number.
---

**Problem.** The chart's 24 control marks and the change list's 12 lines have no recorded reason (PL-N8G4's trace found none): measure what each limit shows at the 1366 by 700 reference window and record a reason, or a changed value, from that measurement

**Checked 2026-11-22**, at `d4e8200c`. `grep -n -B2 'MAX_CHART_CONTROL_MARKS: Final\|MAX_LISTED_ADJUSTMENTS: Final' src/anesthesia_sim/app/chart_frame.py src/anesthesia_sim/app/dashboard_frame.py`
printed 24 at `chart_frame.py:199` and 12 at `dashboard_frame.py:393`. The
comments above each, written for `PL-N8G4`, say that no record gives the
reason for the number, and what raising or lowering it would do. No
measurement at the reference window is recorded.

**Why it matters.** Past each limit the chart stops marking a control change
and the panel stops listing one, and both count the rest instead. A learner
reviewing a busy case needs to see the changes that explain a trace. Whether 24
marks and 12 lines show enough of them, at the 1366 by 700 window that
everything must fit, has never been looked at.

**Done when.** The item records what each limit shows at the 1366 by 700
reference window: how many marks the chart can draw before they crowd, and how
many lines the panel shows before it scrolls. Each comment then gives a reason
from that measurement, or the limit is changed to a value the measurement
supports, and `docs/INTERFACE.md` agrees with the code.

**Generator check.** One-off: both numbers were chosen in one change
(`PL-DR1Z`, #301) without a recorded reason, and no other item misreads why a
display limit has the value it has.
