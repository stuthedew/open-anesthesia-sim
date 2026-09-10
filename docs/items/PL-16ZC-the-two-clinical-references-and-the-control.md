---
id: PL-16ZC
title: The two clinical references and the control marks have no show/hide control, though the chart's traces now do
priority: P3
effort: M
status: needs-decision
classes: ux
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py
added: 2026-09-04
---

> **Not carried by the Qt port** (project owner, 2026-09-10). `v0.5.1` admits
> queued *fixes* in the surface it rewrites, and this is a control that does not
> exist today - new capability by that rule, however small. It stays a queue
> item on its own merits.

**Problem.** `PL-CG7J` gave each of the six compartment traces a checkbox in
the legend. The two clinical references — the MAC-awake band and the 1 MAC
line — and the control marks got none, so the chart's furniture is the one
thing a reader cannot take off it.

**Why it matters, if it does.** The MAC-awake band is a *filled region* across the
whole plot, and the comparison `PL-CG7J` exists to enable is reading two
compartment traces against each other closely. A band lying across both is
exactly what would be in the way. The control marks are vertical rules
crossing every trace, which is why they are drawn first; on a case with a
dozen adjustments they are the densest thing on the chart.

**Why it might not.** Gas Man has checkboxes for its traces and not for its
furniture, so this is an extension rather than the reference implementation's
own affordance. And the references carry a labelling obligation the traces do
not — `docs/MODEL.md` § "Interface boundary" requires a reference to state the
value and divisor it was drawn from and the trace it is read against — so
hiding one has to hide its legend row and its provenance line with it, or the
panel states the provenance of a mark that is not on the plot. That is the
work here, and it is why this is not simply four more checkboxes.

**Where.** The same table `PL-CG7J` built. The references and marks are
deliberately *not* members of `_plotted_series` — they read no sample — so
they need their own record rather than joining that one.

**Decision needed.** Whether this is wanted at all. A chart whose every element
is optional is a chart with no stated content, and the references exist to
stop a trace being read without its clinical anchor.

**Done when.** The project has decided whether the references and the control
marks are hideable at all. If they are, hiding one takes its legend row and its
provenance line with it, so no panel states the provenance of a mark that is not
on the plot; if they are not, this item records the reason and closes.
