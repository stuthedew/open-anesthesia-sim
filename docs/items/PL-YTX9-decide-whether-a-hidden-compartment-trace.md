---
id: PL-YTX9
title: Decide whether a hidden compartment trace should keep its legend entry or vanish from the legend entirely
priority: P3
effort: S
status: done
classes: ux
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py
added: 2026-09-04
closed: 2026-09-13
verify: uv run pytest tests/unit/test_simulation_view.py -q && python3 -c "import pathlib; t=' '.join(pathlib.Path('src/anesthesia_sim/app/simulation_view.py').read_text().split()); raise SystemExit(0 if 'keeps its line-style words while it is off' in t else 1)"
---

**Problem.** Decide whether a hidden compartment trace should keep its legend
entry or vanish from the legend entirely

**Decision needed — ANSWERED 2026-09-13, see below.** When a reader unchecks a compartment, should its legend
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

**Answered 2026-09-13 (project owner): the entry stays, and what ships today
stands unchanged.** No code behaviour changed; this item is the record that the
difference from `PL-CG7J`'s brief was chosen rather than missed.

**The reasoning, so it is not reopened.** The legend *is* the control, so the
entry has to survive being switched off — it is what switches the trace back
on. Three channels already say the trace is not drawn (unchecked box, empty
swatch, MUTED label), two of them non-colour, which is what `PL-CG7J`'s purpose
clause actually asks for: nothing claims a line is on the plot when it is not.
It is also the interactive-legend convention — plotly and bokeh dim a hidden
series rather than removing it, and Gas Man's own affordance is a labelled
checkbox list.

**The case against is answered rather than conceded.** The objection was that a
MUTED entry reading "Fat (dash-dot)" names a line style nobody is drawing. The
words stay, because this row is a control and a control should say what
switching it on will produce; a reader who has just unchecked Fat is the one
person who needs to know which line will come back. Read as a legend the words
are a small liability, and read as a control they are the point — and the
checkbox settles which of the two it is.

**The third option is rejected on the same ground.** Dropping the style words
while hidden and reserving their width with a spacer would satisfy
`PL-CG7J`'s sentence literally and keep the layout stable, at the cost of a
fourth visual state to keep in step with the other three — for a hazard the
empty swatch has already removed.

**Where it is written down.** `_build_trace_legend_item`'s docstring in
`src/anesthesia_sim/app/simulation_view.py` carries the reasoning, which is
where a future session would go to change the behaviour; `PL-CG7J`'s brief
carries a note beside the sentence it contradicts, so the two now agree.
`test_the_legend_says_exactly_which_traces_are_drawn` is unchanged and remains
correct.
