---
id: PL-WZVZ
title: 'Make an inter-machine difference attributable: which parameter differs, and what it does to the result'
priority: P3
effort: M
classes: safety, ux
blocked-by: PL-FG9D
status: blocked
feature: anesthesia-machine
touches: docs/MODEL.md
added: 2026-09-02
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
