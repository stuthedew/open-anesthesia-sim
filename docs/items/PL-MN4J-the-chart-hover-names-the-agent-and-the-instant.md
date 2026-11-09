---
id: PL-MN4J
title: The chart hover names the agent and the instant but not which run, so a hovered value is unattributed while two runs are drawn
priority: P1
effort: S
status: done
classes: safety, ux
feature: scenario-branching
milestone: v0.4.28
touches: src/anesthesia_sim/app/chart_frame.py, docs/MODEL.md, README.md, tests/unit
added: 2026-09-16
closed: 2026-09-17
pr: 665
verify: grep -qF 'The hover and the run it belongs to' docs/MODEL.md
---

**Problem.** `format_trace_hover` opens "Modelled sevoflurane · 20m8s" and then
gives the compartment and the value. With two runs on one axis the agent is the
same for both - `assemble_chart_frame` refuses a frame whose runs differ on it -
so the readout names everything about the point except the one thing that now
distinguishes it. A reader hovering the alveolar curve at 12 min is told a
number and not which management produced it.

**Why it matters.** `docs/MODEL.md` § "Minimum displayed outputs" already
settles the principle for the readouts: "A concentration that does not say which
management produced it is the correct number under the wrong patient context."
The hover is a displayed concentration under exactly that rule. `PL-8PSW` put
the run's name on the legend and on each run's panel and separated the curves by
line width, so a reader *can* attribute a curve - but a hover box floats away
from the legend, which is the same argument § "The chart's hover readout"
already makes for why the hedge travels with the value rather than being left to
the readout row beside it.

**Decided 2026-09-17** (project owner, ratified, over a fourth line of its own
and over holding line width and the legend to be sufficient): the hover names
the run on line 1, `Modelled sevoflurane · Run 2 · 20m8s`, only while more
than one run is drawn. The counter-argument below - that the pointer is over
one curve - was measured and is false: `nearest_trace_point` keeps the nearest
point across every run, and both runs' fat points sit inside the 12 px radius
over 100% of the shared axis in every management scenario tested, with
43.8-81.4% of those hovers printing different text. `docs/MODEL.md` § "The
hover and the run it belongs to" carries the derivation and the measurement.

**Decision needed.** Whether the hover names the run while more than one is
drawn — and if so, whether as a fourth line or folded into the first — or
whether the curve's own line width and the legend are held to be sufficient and
`docs/MODEL.md` records that instead. It is the project owner's because it
amends § "The chart's hover readout: what the tooltip may show", which derives
the three-line form the hover has today.

**Why `needs-decision` rather than `ready`.** The three-line form is derived in
`docs/MODEL.md` § "The chart's hover readout: what the tooltip may show" and a
fourth line, or a run name folded into the first, is a change to that
specification rather than to its implementation. There is also a real argument
that it is unnecessary: the pointer is over one curve, the curve's width says
which run, and the box costs a line on every hover for a case that only exists
while comparing. The cheapest form - appending the run to the first line only
while more than one run is drawn - is conditional text and may be the answer.

**Where.** `src/anesthesia_sim/app/chart_frame.py` (`format_trace_hover`,
`format_wash_in_hover`, which take a `RunFrame` and so already hold `label`);
`docs/MODEL.md` § "The chart's hover readout".

**Done when.** `docs/MODEL.md` § "The chart's hover readout: what the tooltip
may show" carries a paragraph headed "The hover and the run it belongs to",
saying whether the run is named while more than one is drawn and why. Both
answers write it: that section derives the three-line form, so naming the run
amends it and declining to name the run is a limit on it that a later session
would otherwise re-derive. The `verify:` command names that paragraph rather
than a test, because one outcome adds no test at all.

**Found 2026-09-16** while building `PL-8PSW`, on the docs sweep. Filed rather
than fixed: it changes a specification, which is a decision rather than the
kind of fix `CLAUDE.md`'s fix-now door admits.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "Moved into v0.5.0's own Required scope (project owner, 2026-09-16, ratified, on `PL-R7XK`)". This item is also named in paragraphs quoted in the brief of `PL-KQHN`.

> **One more item from 2026-09-16 was written down here as a deferral, and that was the wrong disposition for it.** The item is `PL-MN4J` (the chart hover names the agent and the instant but not which run). It was captured ten days after this gate was frozen, so the snapshot rule places it in the next gate. It was given priority `P1` because `checks.py` will not give an item of the `safety` class a lower priority.

> **It is `Required scope`, not a deferral** (`PL-R7XK`, project owner, 2026-09-16, ratified - chosen over leaving it deferred here). The reason written for it was sound, and it is carried across to the bullet in § "Required scope" below. The display it concerns exists only in the feature that this milestone builds, so the item cannot be cleared before the compare mode it is about. But that case is what § "Debt inside the milestone's own scope" is for. A deferral is something else. The rule "The gate is a snapshot" makes a `safety` item not deferrable. The two records also say different things about what keeps the item open. A deferral says that the gate has released it. `Required scope` says that this milestone's definition of done still requires it. Only the second is true. Only the second also stops the item from being dropped from v0.5.0 without anyone noticing. The `anticipated` carve-out from `PL-83LS`, described above, does not affect it, because that carve-out covers a different case. v0.5.0 builds the feature that this hazard needs, whereas item 34's findings wait on a milestone two steps further out.
