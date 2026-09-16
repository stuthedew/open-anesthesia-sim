---
id: PL-16ZC
title: The two clinical references and the control marks have no show/hide control, though the chart's traces now do
priority: P3
effort: M
status: done
classes: ux
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py
added: 2026-09-04
closed: 2026-09-15
pr: 597
verify: python3 tools/doc_check.py check && grep -qF 'Decided 2026-09-15: not hideable' docs/items/PL-16ZC-the-two-clinical-references-and-the-control.md
---

> **Decided 2026-09-15: not hideable, and the question moves to the layout
> system** (project owner, delegating the call). `docs/MODEL.md` § "Minimum
> displayed outputs" already required it - "The chart entries in this list -
> the MAC-awake band, the 1 MAC line, the control marks, and $`F_A/F_I`$ - are
> requirements on the chart itself and are not selectable" - written by
> `PL-CG7J` (#315), the same change that gave the six compartment traces their
> checkboxes, and completed by `PL-RCTQ` (#352) the next day. Hiding a trace is
> safe because that same section separately requires all six compartment values
> in the numeric readouts, which never leave the display; the two references
> have no readout equivalent, so the chart is the only place they exist.
> Nothing is built here and the specification is unchanged.
>
> **The owner's steer is why this closes rather than being built** (project
> owner, 2026-09-15): "I don't see anything about the UI that is close to its
> final form ... not make decisions that fit a rigid (temporary) layout." What
> a reader may take off the display is a property of planned-milestone item
> 34's workspace system rather than a per-element checkbox on one chart, so
> building the control now would bake a choice into a layout item 34 replaces.
> The reason is recorded so the finding is not re-raised against the same
> reasoning.
>
> **The deferral this item carried is discharged, not deleted.** It read
> "sequenced past v0.5.0, not clearable before it begins" (project owner,
> 2026-09-14, on `PL-NR2K`), on the ground that building the control on Flet
> first was the one piece of open Gate 1 work the port throws away whole. Its
> `blocked-by: PL-G59B` was chosen over the port's version precisely so it
> would expire when the chart port landed, which it has - the item promoted to
> `ready` while its prose still said otherwise, which is what `PL-7G5M`
> captured. `ROADMAP.md` Gate 1 § "Sequenced past v0.5.0" is a frozen snapshot
> and stays as written.

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
