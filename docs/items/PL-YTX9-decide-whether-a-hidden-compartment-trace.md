---
id: PL-YTX9
title: Decide whether a hidden compartment trace should keep its legend entry or vanish from the legend entirely
priority: P3
effort: S
status: needs-decision
classes: ux
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py
added: 2026-09-04
---

**Problem.** Decide whether a hidden compartment trace should keep its legend
entry or vanish from the legend entirely

**Decision needed.** When a reader unchecks a compartment, should its legend
entry stay on screen showing an off state, or disappear from the legend
altogether?

**Deferred by the project owner, 2026-09-04**, at `PL-CG7J`'s pull request
(#315). Shipped as-is; this records the open question rather than the answer.

**What ships today.** The legend *is* the control: each entry is a checkbox
labelled with its compartment, and a hidden one shows an unchecked box, an
empty swatch and a MUTED label while keeping its width. Three channels say
the trace is off, and the entry is what brings it back.

**What `PL-CG7J`'s brief asked for.** "A hidden trace must also disappear from
any legend, so the chart never labels a line it is not drawing."

**The case for what shipped.** The purpose clause is met - nothing claims a
line is on the plot when it is not - without two lists of six compartments
that agree only while somebody keeps them agreeing, which is the failure the
sentence exists to prevent. It is also the interactive-legend convention
(plotly, bokeh dim a hidden series rather than removing it) and Gas Man's own
affordance is a labelled checkbox list. A vanishing entry needs a separate
control row to bring the trace back, which reintroduces the second list.

**The case against.** A greyed entry reading "Fat (dash-dot)" still names a
line style, and a reader scanning for a dash-dot line may hunt for one that is
not there. Removing the words while keeping the box would answer that, at the
cost of the entry changing width - and a legend row that reflows under the
cursor moves the next checkbox out from under it, which is why the width is
fixed today.

**A third option worth weighing before either.** Keep the entry and drop only
the line-style words when hidden, reserving their width with a spacer, the way
`EMPTY_METRIC_QUALIFIER` holds a readout's baseline. That satisfies the brief
literally and keeps the layout stable, and is the one shape nobody has costed.

**Where.** `simulation_view.py`: `_build_trace_legend_item`,
`_apply_trace_visibility`, and `_CompartmentTrace`'s `checkbox`/`swatch`.
`test_the_legend_says_exactly_which_traces_are_drawn` is what would change
with it.

**Why it matters.** `PL-CG7J`'s brief asked for something the shipped legend
does not do, so the queue currently holds a written requirement the code
contradicts. That is small as a display question and not small as a record: the
next session reading that brief has no way to tell whether the difference was
decided or missed.

**Done when.** The legend's behaviour for a hidden trace is decided and the
decision is written where `PL-CG7J`'s sentence was, so the two agree; if what
ships today stands, this item is what records that it was chosen.
