---
id: PL-HLD5
title: ROADMAP v0.5.0 branch comparison assigns line style to the run, which leaves the compartment on colour alone
status: untriaged
added: 2026-09-07
---

**Problem.** `ROADMAP.md`'s v0.5.0 scope says two branches are overlaid on one
time axis "with the run encoded by line style and the compartment by colour"
(project owner, 2026-09-06; queue item `PL-8PSW` implements it). `PL-GVXP`
closed the next day having established the opposite for this chart: the
compartment cannot be encoded by colour, because it is not a channel that can
carry six categories here.

The arithmetic is in `docs/MODEL.md` § "The six compartment traces". Holding
each trace to 3:1 against the panel caps its luminance at 0.30, so six traces
cannot be more than **1.48** apart pairwise, against SC 1.4.11's 3:1 — and a
search over lightness with each hue and saturation held reaches only 1.28
across four vision models, at the cost of driving four of the six to
near-black. The compartment is currently carried by the line style for exactly
this reason, and the roadmap sentence would hand that channel to the run
instead.

**Why it matters.** A branch comparison is where a misread is most consequential
— the whole point of the release is reading one run against another, so two
curves that should be compared are deliberately drawn adjacent and at similar
values. Six compartments times two runs is twelve curves; taking a value off
the wrong compartment there is a misreading of a clinical quantity, which is
what `CLAUDE.md`'s safety-critical standard treats a misleading plot as.

**This is a design question, not a defect to fix silently.** The sentence
reflects a decision the owner made explicitly, and the goal behind it — that a
reader can tell which run a curve belongs to — is right. What is wrong is only
the channel assignment, and the alternative is not obvious. Candidates, none
costed yet:

1. **Compartment by line style (as now), run by opacity or line weight.** Keeps
   the channel that works where it works. Weight is a weak channel at two
   levels; opacity dims a trace against the panel, which walks straight back
   into the 3:1 floor.
2. **Fewer compartments while comparing.** The chart already has per-compartment
   checkboxes. Two runs times two or three compartments is four to six curves,
   which colour *can* separate — and it is arguably the better lesson anyway.
   Costs the "one shared compartment selection across both runs" the roadmap
   already specifies, or rather makes it load-bearing.
3. **Run by position** — a small vertical offset, or direct labelling at each
   curve's end. Position survives every colour-vision deficiency and greyscale,
   and is the strongest channel available; an offset falsifies the value axis
   and is therefore out, but direct labelling does not.

**Where.** `ROADMAP.md` (the v0.5.0 "two branches are overlaid" bullet);
`docs/items/PL-8PSW-*.md` is the item that would build it;
`docs/MODEL.md` § "The six compartment traces" is the arithmetic;
`.claude/rules/ui-color.md` judgment 3 is the standing rule.

**Done when.** The roadmap bullet names a channel assignment that survives the
six-trace arithmetic, or says explicitly how many compartments may be drawn at
once for colour to be sufficient. The decision is recorded where `PL-8PSW`
will read it.

**Note.** Do not resolve this by re-picking colours. That was measured and
declined in `PL-GVXP`; the ceiling is a property of the bounded luminance axis,
not of the palette.
