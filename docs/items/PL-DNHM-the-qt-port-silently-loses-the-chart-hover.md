---
id: PL-DNHM
title: The Qt port silently loses the chart hover unless something names it: pyqtgraph's ScatterPlotItem defaults hoverable=False, so parity with the Flet build is not the default outcome
priority: P2
effort: S
status: done
closed: 2026-09-14
classes: defect, ux
feature: presentation-safety
touches: docs/items, docs/MODEL.md, ROADMAP.md
added: 2026-09-14
verify: python3 tools/doc_check.py check && grep -qF "ships `hoverable` set to `False`" docs/MODEL.md
---

**Problem.** The Qt port silently loses the chart hover unless something names it: pyqtgraph's ScatterPlotItem defaults hoverable=False, so parity with the Flet build is not the default outcome

**Read from the source, not inferred.**
`pyqtgraph/graphicsItems/ScatterPlotItem.py` sets `'hoverable': False` in its
default options, and a `PlotCurveItem` — a plotted line — carries no hover of
its own at all. So the hover is not something a port inherits and then
customises; it is something a port has to switch on, and a port that says
nothing about it ships without one.

**That makes it a parity failure rather than a deferral.** `v0.5.1`'s
definition of done is "every capability the Flet build has, the Qt build has",
and the Flet build has a hover — `PL-KP7H` shipped it as a paused-only
affordance rather than removing it. Silence in the port is therefore a
learner-visible regression against that milestone's own checkable criterion,
and the kind that no test written for the new build would notice, because
nothing would be asserting on a feature nobody remembered.

**Closed onto two places**, 2026-09-14: `docs/MODEL.md` § "The chart's hover
readout: what the tooltip may show" → "When it answers" states it where the
design is read, and `PL-YVHK` carries it as the build obligation. `ROADMAP.md`
§ "v0.5.1" → "Required scope" item 1 names it in the scope list, which is what
`MilestoneStates.ships_with` reads.

**Its `verify:` postdates the work**, for the same reason `PL-3M3K`'s does:
captured and closed in one session, so it specifies the resulting state rather
than having been watched to fail first.
