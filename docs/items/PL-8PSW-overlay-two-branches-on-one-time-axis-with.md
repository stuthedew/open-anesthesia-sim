---
id: PL-8PSW
title: Overlay two branches on one time axis, with every curve attributable to its run and its settings
priority: P2
effort: L
status: done
classes: feature, ux
feature: scenario-branching
touches: src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/qt_chart.py, src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/theme.py, tests/unit, tests/integration, docs/MODEL.md
added: 2026-09-06
closed: 2026-09-16
verify: uv run pytest tests/integration/test_qt_chart.py && grep -q 'def test_two_runs_on_one_axis_are_told_apart_by_line_width_and_named_in_text' tests/integration/test_qt_chart.py
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

---

## Session of 2026-09-16: built, with one refinement to `PL-HLD5` and one thing left out

**`touches` was stale and is corrected here.** It named
`app/chart_series.py`, which `PL-25KS` deleted with the Flet chart -
`PL-RWBV` reports this item as one of the seven carrying a path that no longer
exists. The work landed in `app/chart_frame.py` (the cap, the run's width
channel, the fork instant), `app/qt_chart.py` (the pens, the marks, both
legends), `app/dashboard_frame.py` (every word), `app/simulation_view.py` and
`app/run_view.py` (the wiring and the per-run name), `app/theme.py` (the two
new constants) and `app/qt_widgets.py`.

**The one refinement, and it was put to the project owner before it was built.**
`PL-HLD5` chose two width levels on the ground that the distinction is read
locally, "between two curves of the same compartment, which are adjacent by
construction". They are not merely adjacent: `PL-Z3W6` requires a branch to
reproduce its parent element-wise up to the fork, so before the branch point
the two curves **coincide exactly**, and whichever run is drawn thicker hides
the other completely over that stretch. So the narrower curve has to be the one
drawn last and on top, which decides the direction: the **first** run is widened
by `theme.COMPARED_RUN_WIDTH_STEP` and the second keeps the width the single-run
chart draws it at. Widening rather than narrowing also keeps every trace at or
above 2 px - a 1 px antialiased line renders lighter than its declared colour
and would walk into the 3:1 floor against the panel that
`.claude/rules/ui-color.md` treats as an error rather than a tracked shortfall.
`docs/MODEL.md` § "The six compartment traces" and `ROADMAP.md`'s v0.5.0 bullet
both carry it.

**The cap has two enforcement points, deliberately, and they cannot disagree.**
`chart_frame.compared_compartments` is the rule, applied where the frame is
assembled, so what the chart draws is capped whatever route reached the
selection - a legend, a restored layout, or a later view with no legend of its
own. `TraceLegend` applies the *same function* to its boxes, so the checked set
is never over the cap while comparing and the frame's slice is the identity on
everything the legend hands out. Two paths through one rule rather than two
rules. Checking a third compartment drops the longest-standing selection rather
than being refused, because a box that does not respond to a click is the worse
surprise; a bulk `set_shown` has no order of preference to read and falls back
to the table order `compared_compartments` gives.

**The wash-in plot was in scope and is easy to miss.** It draws one trace per
run in one colour and one dash pattern, so two runs there are identical but for
their values - the same failure the compartment chart's cap exists to prevent,
and worse, because nothing at all separates them. It takes the same width step
and its legend names each run.

**`FlowLayout` had to learn to skip a hidden widget.** The legend's per-run
entries are a fixed pool that stands down on a single run, and a hidden widget
still reports a size hint, so without the skip the stood-down entries reserved
width and pushed the row onto a second line.

**What this does not do.** The hover still names the agent and the instant and
not the run (`PL-MN4J`, `needs-decision`): a fourth line amends
`docs/MODEL.md` § "The chart's hover readout", which derives the three-line
form, so it is a decision rather than an omission. `PL-W7H9` - what a branch
comparison asserts - was blocked on this item and is now unblocked. `PL-QRD1`
was blocked on whether a two-run dashboard needs a selector lock: it does not,
because the compartment selection is one control over both runs by construction.

**It lands ahead of its own milestone, at the project owner's direction.**
`ROADMAP.md` places this in v0.5.0 and the project is on v0.4.26; v0.5.0's debt
gate has not cleared and three of the port's own Required-scope items are still
open. The owner asked for this item by id, which `CLAUDE.md`'s
out-of-milestone rule takes as the scope approval - recorded here rather than
left for a later reader to reconstruct from the dates.

**`.claude/rules/ui-areas.md` shaped two decisions** (`PL-LH18`, written the
same session on the owner's instruction that every main UI element is built to
become an area-type widget). The run's name is a value the dashboard hands down
rather than a position the chart reads off its own run list, so a view drawing a
different subset could not rename a run; and `RunView.set_run_name` is named for
naming a view in its own header rather than for naming a run, because that is
what every editor will owe an area. `PL-VN6M` is the one violation found and not
fixed: `TraceLegend` still owns the compartment selection.
