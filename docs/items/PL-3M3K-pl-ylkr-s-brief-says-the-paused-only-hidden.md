---
id: PL-3M3K
title: PL-YLKR's brief says the paused-only hidden-mode problem transfers whole to pyqtgraph, and it does not: Qt's hover is a rate-limited scene signal with no per-frame per-point cost, and ScatterPlotItem's tip is a format callable evaluated on hover
priority: P2
effort: S
status: done
closed: 2026-09-14
classes: docs
feature: presentation-safety
touches: docs/items, docs/MODEL.md
added: 2026-09-14
verify: python3 tools/doc_check.py check && grep -qF 'Qt has no such cost to avoid' docs/MODEL.md
---

**Problem.** PL-YLKR's brief says the paused-only hidden-mode problem transfers whole to pyqtgraph, and it does not: Qt's hover is a rate-limited scene signal with no per-frame per-point cost, and ScatterPlotItem's tip is a format callable evaluated on hover

**Where the claim came from and what is wrong with it.** `PL-YLKR` argued that
the port "changes the mechanism, not the design", and that the hidden-mode
problem `PL-KP7H` created "transfers whole, since a paused-only affordance is
equally undiscoverable in either toolkit". The premise is sound and the
conclusion does not follow: the affordance is only paused-only *on Flet*.
`PL-KP7H` withdrew it because Flet's control-tree diff descends into every
point's tooltip object on every frame, which is a per-frame per-point cost that
Qt does not have. A pyqtgraph readout is built either on the scene's own
`sigMouseMoved`, rate-limited through a `SignalProxy`, or on hoverable points
whose `tip` is a format callable evaluated when the pointer arrives — both cost
per pointer event, neither scales with the number of points drawn. So there is
nothing to withdraw after the port, no hidden mode, and no caption needed to
announce one.

**Closed by `PL-YLKR`'s design round**, 2026-09-14. `docs/MODEL.md` § "The
chart's hover readout: what the tooltip may show" → "When it answers" carries
the corrected reasoning, and `PL-YLKR`'s own brief records the correction.

**Its `verify:` postdates the work, and says so rather than implying
otherwise.** This was captured and closed inside one session, so there was no
moment at which the command could be run against a tree without the fix. It is
a specification of the state the correction produces, not a command watched to
fail first.
