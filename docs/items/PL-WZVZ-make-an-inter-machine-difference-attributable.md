---
id: PL-WZVZ
title: 'Make an inter-machine difference attributable: which parameter differs, and what it does to the result'
priority: P3
effort: M
status: blocked
classes: safety, anticipated, ux
feature: anesthesia-machine
touches: docs/MODEL.md
blocked-by: PL-TH35, PL-R1WQ
added: 2026-09-02
payoff: stops a learner reading a numerical difference between two machines as a fact about the brand, when it was produced by one named parameter the interface never showed them
---

**Problem.** Once a machine can be chosen (planned-milestone item 1, designed
by PL-FG9D), the same case run on two machines will produce two different
curves. Nothing in the interface would say why. The user sees a trade name and
a different answer, and the difference gets attributed to the brand instead of
to the parameter — a different circuit volume, a different minimum fresh gas
flow — that actually produced it.

**Why it matters.** This is the difference between the machine feature being
educational and being decorative, and it is a presentation-safety issue under
`CLAUDE.md`'s clinical-output standard rather than a nicety. A numerical
difference shown without its cause teaches that machines differ mysteriously,
which is the opposite of the lesson; worse, a trade name attached to an
unexplained difference is a clinical claim about that machine that the model
never made. The correct number with the wrong attribution is still a
presentation failure.

It also protects the modelling work: if a machine's effect on a curve cannot
be traced to a named parameter, that is evidence the abstraction has put
behavior somewhere it should not be, and this surface is where that shows up.

**Two surfaces, and they are not the same one.**

1. **Static, before a run: the comparison table.** The per-machine parameters
   the model uses, machines as columns, one row per parameter, with the value,
   its unit, and its source. Rows come straight from PL-4DCG's survey
   document, which is the single source for them; an unknown value shows as
   unknown rather than blank. This answers "how do these two differ?" without
   running anything, and it is the deliverable the project owner asked for.
2. **Attributed, after a run: the machine as a labelled input.** Planned-
   milestone item 11 (side-by-side comparison on a shared time axis, each
   curve labelled with the run and the settings that produced it) and item 12
   (forking) are already scheduled for v0.5.0 and already do most of this. What
   this item adds is a requirement on them: when two compared runs used
   different machines, the machine must appear as a labelled input *expanded
   into the parameters that differ*, never collapsed to a trade name. If those
   items land first, this half is a constraint on them rather than new work.

**The anti-goal.** The table must not read as a comparison of the machines.
It compares the parameters *this model uses*, which are a small subset of how
two real machines differ. One standing sentence on the surface saying exactly
that, once — not a per-machine list of what is not modelled. PL-4DCG's
rule-out bucket is written once for the survey and is a scope boundary for the
work, not display copy: it does not become rows here.

**Classed `anticipated`** because the concern does not exist until
planned-milestone item 1 is built: there is no machine to pick today, so
nothing is currently misattributing anything. That class is what lets a
`safety` item wait outside the top band (`PL-P909`), and the band is owed
again the moment the item is unblocked.

**Depends on** PL-4DCG for the rows and PL-FG9D for which parameters are
per-machine at all. Neither the table nor the labelling can be built before a
machine exists to select, so this follows planned-milestone item 1; capturing
it now is what stops item 1 shipping a machine picker with no explanation
attached to it.

**Where.** The machine-selection surface in `app/`, and `docs/MODEL.md`
wherever a per-machine parameter enters the model.

**Done when.** Selecting between machines shows the parameters that differ,
their values, units and sources, with unknowns visible as unknown; a
comparison of two runs on different machines names the differing parameters
rather than only the machines; the surface states once that these are the
parameters the model uses and not the whole difference between the machines;
and no per-machine value appears anywhere that is not traceable to PL-4DCG's
survey document.

## Re-pointed, 2026-09-20 (`PL-8G48`): the recorded blockers closed and the item is still not startable

`PL-FG9D` closed as `#748` and `PL-4DCG` as `#742`, so `bin/docket check`
reported this item as ready to promote. **Read against the tree, it is not.**
Both closures are real and neither is the thing this item waits on; what they
removed was the design prerequisite, not the two conditions below. Promoting it
would have put an unbuildable item in front of `bin/docket next` at `P1`, since
leaving `blocked` is what ends the `anticipated` exemption.

**1. There is nothing to select between.**
`src/anesthesia_sim/data/machines/` holds exactly one profile,
`reference_circle_system.json`, and there is no selection surface. Every clause
of `Done when.` above - "selecting between machines", "a comparison of two runs
on different machines" - needs a second machine to exist. `PL-FG9D` answered
planned-milestone item 1 **as a written design** in `docs/machine-abstraction.md`
rather than as code, which `ROADMAP.md` § "What a machine module is, settled
before there are two" states in those terms.

Nothing schedules the implementation. `ROADMAP.md` § "Planned milestones" item 1
is a line of intent, and intent is not scope: no milestone *section* places it,
and the reserved numbers v0.5.0 through v0.9.0 are spent on the branchable case,
the layout, the second screen, the schematic and multi-substance. So there is no
version to name in `blocked-by` either - naming one would assert a placement the
roadmap has not made.

**2. The comparison table is a new display surface, and one is not built yet.**
`ROADMAP.md`'s planned-milestone item 34 carries a standing rule (project owner,
2026-09-17, ratified, over leaving the ordering implied by row position): *"No
new display surface is built before this item"*, because a surface built before
the area system is built against no view contract and is therefore built twice.
Surface 1 above - machines as columns, one row per parameter - is squarely that.

The rule states its own condition and it names items rather than a version: it
"ends when this item's View contract (`PL-TH35`) and view registry (`PL-R1WQ`)
ship". Both are open and placed by v0.6.0. That is the re-point recorded below,
and it follows the pattern § "Behind a design round no milestone section places"
already prescribes for this gate's deferrals - name the item that does the work,
so the entry does not depend on what number the milestone ships under.

**The rule does not reach surface 2, and that matters for what survives.** It
"binds a new surface, not a new value", and this item's second half is a
*requirement on* planned-milestone items 11 and 12 - that a machine appear as a
labelled input expanded into the parameters that differ, never collapsed to a
trade name. That half is a constraint on surfaces those items build, not a new
one, so it is held here only by condition 1.

**Nothing displayed is wrong today and the `anticipated` class still holds.**
One machine, no trade name shown, nothing being misattributed - so this stays
`P3` behind its blockers rather than returning to the debt gate. The band is
owed the moment either condition lifts.
