---
id: PL-8PSW
title: Overlay two branches on one time axis, with every curve attributable to its run and its settings
priority: P2
effort: L
status: blocked
blocked-by: PL-TFX5, PL-B9PY
classes: feature, ux
feature: scenario-branching
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/chart_series.py, src/anesthesia_sim/app/theme.py, tests/unit
added: 2026-09-06
---

**Problem.** The chart draws one run. Two branches have to be readable together
on one time axis, with every curve unambiguously attributable to the run and
the settings that produced it - planned-milestone item 11.

**Why it matters.** This is planned-milestone item 11 and the visible half of
the milestone: forking produces the two runs, and this is where a learner
actually reads the difference. A curve that cannot be attributed to its run
makes the comparison worse than no comparison, because it is persuasive and
wrong rather than merely absent.

**Why one chart rather than two panels (project owner, 2026-09-06).** Stacked
panels sharing a time axis force the reader's eye to travel to do the one
comparison the release exists for, and separate vertical scales would make two
curves at the same height mean different things. Superposition is the right
choice when the question is how two series differ.

**The encoding, and the constraint it inherits.** Run by line style,
compartment by colour, one shared compartment selection across both runs, and
the branch point marked. `PL-GVXP` already records that six traces are not
adequately separated by colour alone; doubling to twelve while line style is
spoken for by run identity makes that acute, so a comparison opens with a
small compartment selection rather than all six, and the legend has to name
both dimensions.

**Where.** `simulation_view.py` (after `PL-B9PY`'s decomposition),
`chart_series.py` for the per-run series assembly, `theme.py` for the line
styles.

**Done when.** Two branches draw on one axis with the branch point marked;
every trace's legend entry names its run and its compartment; the compartment
selection applies to both runs at once; and no trace is distinguished from
another by colour alone where the two runs are concerned.
