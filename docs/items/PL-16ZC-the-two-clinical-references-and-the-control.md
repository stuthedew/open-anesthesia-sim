---
id: PL-16ZC
title: The two clinical references and the control marks have no show/hide control, though the chart's traces now do
priority: P3
effort: M
status: done
classes: ux
feature: teachable-case
milestone: v0.4.26
touches: src/anesthesia_sim/app/simulation_view.py
added: 2026-09-04
closed: 2026-09-15
pr: 597
verify: python3 tools/doc_check.py check && grep -qF 'Decided 2026-09-15: not hideable' docs/items/PL-16ZC-the-two-clinical-references-and-the-control.md
---

> **Decided 2026-09-15: not hideable, and the question moves to the layout
> system** (project owner, 2026-09-15, delegating the call). `docs/MODEL.md` § "Minimum
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

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Sequenced past v0.5.0, so not clearable before it begins", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. This item is also named in paragraphs quoted in the brief of `PL-YVHK`.

> **Deferred past the port, because building it first is the work thrown away — 1.** `PL-16ZC` is a show/hide control for the two clinical references and the control marks (project owner, 2026-09-14, on `PL-NR2K`). It is the mirror image of the five entries carried by the port. It arrives at the same place by the opposite route. Those five are defects the port must not reproduce. This entry is new capability, which § "Completed: v0.4.26" → "Fixes this port carries" excludes "whatever its size". The owner ruled it out on 2026-09-10 for exactly that reason. But the control extends the legend table that `PL-CG7J` built inside `app/simulation_view.py`. Required scope item 2 rewrites all 4 321 lines of that file. So the same rule that keeps the control out of the port also makes it the one piece of open Gate 1 work that would be purely written twice if it were built on Flet first. Its `blocked-by` names `PL-G59B`, the chart port that builds the legend and both references this control would toggle. It does not name the port's version. Naming the version would assert, through `MilestoneStates.ships_with`, that the entry ships with that milestone when it deliberately does not.

> **What is not deferred is the decision.** Saying so is what separates this entry from a parked item. `PL-16ZC` asks whether the references and the control marks should be hideable *at all*. That is a question about what the chart is for. No toolkit answers it, and the item's own Done-when allows it to close without any code being written. That half can be answered any day. Only the build waits. It is the same split taken over `PL-YLKR` on 2026-09-14. That item's design was toolkit-independent and landed on v0.4.x, while its build moved to `PL-YVHK` above.

> **How this was found is worth one line**, because the general version of the proposal is wrong. The project owner asked on 2026-09-14 whether all Flet-related gate entries should be dropped or postponed, now that the interface moves to Qt. The entries were counted, rather than the question being answered from its shape. Of the 23 entries this gate can clear, 13 never touch the interface. 9 of the remaining 10 survive the port or are inputs to it. `PL-JRS3` is item 4 of the port's own Required scope. `PL-LL9Y` is named under § "Decisions the port has to make anyway". `PL-YLKR`'s design is toolkit-independent. `PL-B9PY` ships on Flet in v0.5.0 by the decision recorded in § "Items this port moots or transforms". One entry was left, and it is this one. The general proposal would have suppressed nine real entries to catch it.
