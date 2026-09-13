---
id: PL-1XPX
title: Decide what the readouts show while two branches are displayed
priority: P1
effort: M
status: done
classes: safety, ux
feature: scenario-branching
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/formatting.py, docs/MODEL.md
added: 2026-09-06
closed: 2026-09-13
pr: 535
verify: python3 tools/doc_check.py check && grep -qF 'While two runs are shown, every readout names the run it describes' docs/MODEL.md
---

**Problem.** The readouts name a compartment and show one number each. With two
branches displayed, a number that does not say which run it describes is
ambiguous, and there is more than one defensible way to resolve that.

**Why it matters.** `CLAUDE.md` treats presentation as part of safety: the
correct number with the wrong patient context is still a safety failure, and
"which of the two managements is this" is exactly that context. This is also a
mode-awareness problem - a reader who has forgotten which run is selected reads
a correct number as the other run's.

**Decision needed.** What the readouts show while two branches are displayed.
Three candidates, and they are not equivalent:

- **Both runs, paired per compartment.** No mode, no ambiguity, and the
  difference is readable directly. Doubles the readout block, which already
  wraps at some window widths (`PL-3355`).
- **The selected run only, with the selection stated in the readout block.**
  Keeps the current layout. Introduces a mode, which is the thing
  `.claude/rules/expert-review.md` asks to minimize, and a stale selection is
  invisible.
- **Both runs and their difference.** The most informative and the most
  crowded; a difference readout also needs a stated sign convention or it is
  its own ambiguity.

Whichever is chosen, no readout may show a number without naming its run, and
the answer binds the clinical reference band and the control marks too - both
are per-run.

**Where.** `simulation_view.py`'s readout block, `formatting.py` for whatever
label form the answer needs, `docs/MODEL.md`'s minimum displayed outputs.

**Done when.** The question above is answered and recorded here, and the
displayed-outputs section of `docs/MODEL.md` states what a readout names while
two runs are shown.

## Analysis 2026-09-13: two of the three candidates are already decided elsewhere

Written as the half of this item that does not depend on the owner's answer.
Nothing below changes the interface; the question in **Decision needed** is
still open, narrowed rather than answered.

**`PL-HLD5` is the governing precedent and this item's brief predates it.**
That item settled the *chart's* encoding on 2026-09-07: compartment on line
style and colour exactly as the single-run chart draws them, run on line width,
and **at most two compartments drawn while two branches are shown**. Two things
follow for the readouts.

**First, the second candidate is ruled out on a rule this project has already
applied.** "The selected run only, with the selection stated" is a mode, and
`PL-HLD5` rejected run-by-colour for precisely that - "making it mean 'run' in
compare mode would put two meanings on one channel either side of a mode
change, on the chart where a misread is a misread of a clinical value", citing
`.claude/rules/expert-review.md` on hidden modes and context-dependent
behaviour. The readout version is the stronger case, not the weaker one: colour
would at least change appearance, where a selected-run readout looks identical
whichever run is selected, so a stale selection has no visual signature at all.
`CLAUDE.md`'s "the correct number with the wrong patient context is still a
safety failure" is that sentence exactly. Stating the selection is a warning
after the fact, and `expert-review.md` asks for interfaces that prevent rather
than warn. Recorded as ruled out rather than decided-away - overrule it if the
reasoning does not hold.

**Second, the crowding objection to the first candidate may already be
answered.** The brief says pairing "doubles the readout block, which already
wraps at some window widths (`PL-3355`)". That arithmetic assumed six
compartments. Under `PL-HLD5`'s cap the chart shows two while comparing, and the
roadmap already specifies one shared compartment selection across both runs - so
if the readouts follow the cap, compare mode is *four* entries against today's
six, and pairing costs nothing. Whether they should follow it is the real
question this item now carries, and it is a genuine trade: following keeps one
selection on the screen and loses the six-compartment readout while comparing;
not following puts the chart on two compartments and the readouts on six, which
is two different selections on one screen and a mode-awareness problem of its
own.

**Against the third candidate, and this is a domain point rather than a layout
one.** A difference readout needs a sign convention, which the brief already
names as its own ambiguity. The heavier objection is that the arithmetic
difference of two alveolar fractions is not a quantity with a conventional
clinical reading: anaesthetic depth is reasoned about in MAC multiples and in
time-to-target, not in "these two managements are 0.006 apart", and a readout
that displays a number implies one. `CLAUDE.md` requires displayed precision to
be justified by "practical interpretability", and `expert-review.md` names
ambiguous terminology and false precision as product-level risks. The chart
already carries the comparison continuously, in the axis the reader is looking
at, which is where a difference is legible without being named.

**One constraint on whatever is chosen, which follows from the accessibility
rule rather than from taste.** `PL-HLD5` put the run on line width because
every other line-level channel was spent. Text has no width analogue, so the
run has to be *named* in the readout - a label, not a colour and not position
alone. Colour is spent on compartment, and position alone fails the reader who
has looked away and back, which is the same stale-context failure as the second
candidate. `PL-HLD5`'s own fallback note makes the general point: position
survives every colour-vision deficiency, but it is being relied on here to carry
identity rather than to separate marks.

**Recommendation: the first candidate - both runs, paired per compartment, each
naming its run in text - with the readouts following `PL-HLD5`'s two-compartment
cap while comparing.** The crux the owner has to settle is that second clause,
because it is what decides whether pairing is free or doubles the block.

## Decided 2026-09-13: both runs, paired per compartment, each named in text

**The first candidate, with one clause of the recommendation dropped.**
`docs/MODEL.md` § "Minimum displayed outputs" now states it.

**The second candidate is refused, and not on preference.** Showing the
selected run with the selection stated is a mode, and `PL-HLD5` rejected
run-by-colour on that same ground seven days ago - "making it mean 'run' in
compare mode would put two meanings on one channel either side of a mode
change, on the chart where a misread is a misread of a clinical value". The
readout version is the worse case: colour would at least change appearance,
where a selected-run readout block looks **identical** whichever run is
selected, so a stale selection has no visual signature at all. Stating the
selection warns after the fact; showing both prevents.
`.claude/rules/expert-review.md` asks for the second.

**The third is refused on a domain ground rather than a layout one.** A
difference readout needs a sign convention, which is its own ambiguity - but
the heavier objection is that the arithmetic difference of two alveolar
fractions is not a quantity with a conventional clinical reading. Depth is
reasoned about in MAC multiples and in time-to-target, not in "these two
managements are 0.006 apart", and a displayed number implies a standard
meaning. `CLAUDE.md` requires displayed precision to be justified by practical
interpretability. The chart already carries the comparison continuously.

**The run is named in text.** `PL-HLD5` put the run on line width because every
other line-level channel was spent; text has no width analogue, colour is spent
on the compartment, and position alone fails the reader who looks away and back
- the stale-context failure the whole item is about.

## The cap clause was recommended, approved, and then refused by the specification

**Recorded because the approval was given on a case that had not read this.**
The recommendation put to the project owner was the first candidate *plus* the
readouts following `PL-HLD5`'s two-compartment cap while comparing, and that
clause was named as the crux. It was approved. It is not what landed, and the
reason is not a change of mind.

§ "Minimum displayed outputs" already says, of the six compartment
concentrations: "The chart's compartment traces are the reader's to show and
hide ... and **a required value must not leave the display with the curve that
draws it**." The cap is a colour-capacity limit on the chart - six traces
cannot be separated, two can - and it removes four curves in compare mode.
Under the existing rule the readouts are exactly what must keep those four
values on the display. Capping them too would take four required clinical
readouts off the screen, which is the failure that sentence exists to prevent.

So the crowding objection the cap was meant to answer is answered a different
way: **pair the two runs under one compartment label** rather than adding a
second six-readout block. Six rows, not twelve; the block grows in width, not
in height, and the one-row comparative reading survives. That is what "paired
per compartment" most naturally meant in the first candidate, and the cap was
never needed for it.

**What is still the owner's.** If the readouts *should* follow the chart's cap,
that is an amendment to § "Minimum displayed outputs" - making the six
compartment readouts conditional on compare mode - and it is a change to a
safety requirement rather than a layout choice. It is not made here.

## Not implemented here, and deliberately

No two-run rendering exists yet: `PL-B9PY` decomposes `SimulationView` so two
runs can be drawn, and `PL-8PSW` builds the overlay. This item is the decision
and the requirement, which is what its **Done when** asks for; `PL-TCD1` closing
in v0.4.18 is what made the snapshot able to name which run a value belongs to
at all.

