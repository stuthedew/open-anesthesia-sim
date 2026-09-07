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

**The encoding, settled 2026-09-07 (`PL-HLD5`); do not re-derive it.** The
paragraph this replaces said run by line style and compartment by colour, which
is the assignment `ROADMAP.md` carried until the same day and which is not
available. Build this instead:

- **Compartment on line style and colour, exactly as the single-run chart draws
  them.** Nothing about a compartment's appearance changes on entering compare
  mode. `docs/MODEL.md` § "The six compartment traces" measures the worst
  trace-against-trace colour pair at 1.01:1 against a 3:1 requirement, so colour
  cannot carry the compartment and line style is the only non-data channel with
  six-category capacity. Handing colour to the run instead would make one
  channel mean two different things either side of a mode change, on the chart
  where a misread is a misread of a clinical value.
- **Run on line width.** Two levels, and the distinction only has to be read
  *locally* - between two curves of the same compartment, which are adjacent by
  construction - rather than decoded across the whole plot.
- **At most two compartments drawn while two branches are shown.** This is the
  load-bearing part rather than a nicety: at six compartments line style,
  colour and width are all already spent (width varies 2 px to 3 px across the
  six), so nothing is free for the run until the cap frees it. It also makes
  "one shared compartment selection across both runs" a constraint the design
  rests on. Two compartments times two runs is four curves.

If two compartments proves too tight once it is built, the fallback is three
with the run moved to direct labelling at each curve's end - position being the
strongest channel and the one that survives every colour-vision deficiency.
Test that rather than assuming it, and do not reach for opacity (it walks into
the 3:1 floor against the panel) or a vertical offset (it falsifies the value
axis). The legend still has to name both dimensions.

**Where.** `simulation_view.py` (after `PL-B9PY`'s decomposition),
`chart_series.py` for the per-run series assembly, `theme.py` for the line
styles.

**Done when.** Two branches draw on one axis with the branch point marked;
every trace's legend entry names its run and its compartment; the compartment
selection applies to both runs at once; and no trace is distinguished from
another by colour alone where the two runs are concerned.
