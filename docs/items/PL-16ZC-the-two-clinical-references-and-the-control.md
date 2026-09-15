---
id: PL-16ZC
title: The two clinical references and the control marks have no show/hide control, though the chart's traces now do
priority: P3
effort: M
status: ready
classes: ux
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py
added: 2026-09-04
verify: uv run pytest tests/integration/test_qt_chart.py && grep -q 'def test_the_references_and_the_control_marks_can_be_hidden_and_shown' tests/integration/test_qt_chart.py
---

> **Not carried by the Qt port** (project owner, 2026-09-10). The port admits
> queued *fixes* in the surface it rewrites, and this is a control that does not
> exist today - new capability by that rule, however small. It stays a queue
> item on its own merits.
>
> **And therefore sequenced past v0.5.0, not clearable before it begins**
> (project owner, 2026-09-14, on `PL-NR2K`). The same rule that keeps this out
> of the port makes building it on Flet first the one piece of open Gate 1 work
> the port throws away whole: the legend table it extends lives in
> `app/simulation_view.py`, which the port's Required scope item 2 rewrites from
> scratch. `blocked-by: PL-G59B` rather than the port's version, because that field means
> *ships with this milestone* through `MilestoneStates.ships_with` and this
> deliberately does not - `PL-G59B` is the chart port, which builds the legend
> and the two references this control would toggle. `ROADMAP.md` Gate 1
> § "Sequenced past v0.5.0" carries the disposition, which is where the
> snapshot rule requires a frozen entry's deferral to be written.
>
> **The decision half is not deferred with it, and can close this item for
> nothing.** "Whether the references and the control marks are hideable at all"
> is a question about what the chart is for, not about a toolkit, and the
> Done-when below already admits an answer that writes no code: if they are not
> hideable, this records the reason and closes. Only the build waits.

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
