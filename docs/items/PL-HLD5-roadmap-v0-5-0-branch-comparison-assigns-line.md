---
id: PL-HLD5
title: ROADMAP v0.5.0 branch comparison assigns line style to the run, which leaves the compartment on colour alone
priority: P1
effort: S
status: done
classes: safety, docs
feature: scenario-branching
touches: ROADMAP.md, docs/items/
added: 2026-09-07
closed: 2026-09-07
verify: grep -qF 'the run on line width, and at most two compartments drawn while two' ROADMAP.md && grep -qF 'The encoding, settled 2026-09-07' docs/items/PL-8PSW-overlay-two-branches-on-one-time-axis-with.md
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

**Decided 2026-09-07 by the project owner, on the recommendation below.**
`ROADMAP.md`'s v0.5.0 bullet and `PL-8PSW` both now carry it.

**The assignment: compartment on line style and colour exactly as the
single-run chart draws them, run on line width, at most two compartments drawn
while two branches are shown.** The overlay itself is kept.

**What the candidate list above was missing.** All three options were really
arguments about which channel to *free*, because the six-compartment encoding
already spends every channel a single line has: line style carries the
compartment across six patterns, colour is the second cue, and width is spent
too - `docs/MODEL.md` § "The six compartment traces" gives 3 px for circuit and
alveolar against 2 px for the other four. There is no unspent line-level
channel to give the run at six compartments. That is why the compartment cap is
the load-bearing half of the decision rather than a convenience: capping is what
frees width.

**Why not simply swap the roadmap's two channels.** Run-by-colour would work
arithmetically - colour carries two categories comfortably where it carries six
at 1.01:1 - and was rejected on mode awareness. Colour means "compartment" in
the single-run chart, and making it mean "run" in compare mode would put two
meanings on one channel either side of a mode change, on the chart where a
misread is a misread of a clinical value. `.claude/rules/expert-review.md` names
hidden modes and context-dependent behaviour directly.

**Why the overlay survives, with evidence rather than only the owner's
instinct.** The bullet already recorded the decision against stacked panels
because "the comparison is the whole point of the release". Javed, McDonnel and
Elmqvist measured that shared-space line graphs are the more efficient technique
for comparisons over *small* visual spans, with separate-chart techniques
winning as the span grows - and comparing one compartment against itself under
two settings is a small-visual-span comparison by construction. The citation is
now in the roadmap bullet.

**The fallback, recorded so it is not rediscovered.** If two compartments proves
too tight once built, three works with the run moved to direct labelling at each
curve's end; position is the strongest channel and survives every colour-vision
deficiency. Test it rather than assuming it. Opacity and a vertical offset stay
out, for the reasons in the candidate list above.

**One question this raised and did not answer, filed as `PL-JX0Z`.** Whether
trace-against-trace 3:1 is stricter than SC 1.4.11 actually requires. It is the
premise `PL-GVXP`'s palette search rests on, and it could not be checked from
this environment.
