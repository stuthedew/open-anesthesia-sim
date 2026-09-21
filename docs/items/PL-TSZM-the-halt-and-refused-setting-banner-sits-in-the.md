---
id: PL-TSZM
title: The halt and refused-setting banner sits in the shared notice column with no run attribution, so 'Simulation stopped' and 'the simulation is unchanged and still running its previous setting' read as the dashboard's rather than one run's
priority: P1
effort: S
status: done
classes: defect, safety, ux
feature: two-run-attribution
milestone: v0.5.0
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/dashboard_frame.py, tests/integration/test_simulation_view.py, tests/unit/test_dashboard_frame.py, docs/MODEL.md
added: 2026-09-21
closed: 2026-09-21
pr: 834
payoff: stops a halt or a refused setting on one run reading as the dashboard's, and stops 'the simulation is unchanged' asserting something false of the run it is not about
verify: grep -q 'def test_the_halt_and_refusal_banners_name_their_run' tests/integration/test_simulation_view.py
---

**Problem.** The halt and refused-setting banner sits in the shared notice column with no run attribution, so 'Simulation stopped' and 'the simulation is unchanged and still running its previous setting' read as the dashboard's rather than one run's

**Found 2026-09-21** while fixing `PL-25DD`, which is the same mechanism one
column over, and verified by reading `SimulationView._place_run` and
`RunView.build_notice`.

**Why it matters.** `_holder(self._notice_column, (run.build_notice(),))` puts
one bare `NoticeLabel` per run into a column the runs share, and
`build_notice` returns `self._notice_text` with nothing naming the run beside
it. All three notices it carries assert something about *a* run and name none:

- `FAILURE_NOTICE_TEMPLATE` - "Simulation stopped - {failure_reason}. The
  values shown are the last completed step ... Reset to start a new run."
- `SUPPORTED_LIMIT_NOTICE_TEMPLATE` - "this run reached the supported run
  length of {run_length}".
- `REFUSED_SETTING_NOTICE_TEMPLATE` - "The simulation is unchanged and still
  running its previous setting."

With two runs drawn, a halt on the branch reads as the dashboard having
stopped, and a refusal on one run states that "the simulation" is still on its
previous setting - which is false of the other run. `docs/MODEL.md`'s hazard
table already carries "reading a run halted by a failure as one the user
paused"; unattributed, the distinction it buys is spent.

**Fix.** `dashboard_frame.compared_run_line(line, frame, run_index)` exists and
does exactly this job for the two chart-column lines (`PL-25DD`, `#823`). The
open question is whether a banner takes the same inline prefix or a run chip,
since it is a coloured block rather than a line of text - that is the design
work, and `.claude/rules/ui-reader.md` governs it.

**Measured 2026-09-21**, and it is worse than the item assumed. A banner with
nothing to say is *hidden*, not blank, so the column collapses around it: with
one run halted the display holds a single bold block, and halting run 1 rather
than run 2 moves it by the column's spacing alone - 12 px, with identical
words and nothing on screen to measure the offset against. The chart column's
lines at least render one per run. Here stacking order is not a weak channel,
it is very nearly no channel.

**Built 2026-09-21** as `dashboard_frame.compared_run_notice(notice_text,
run_name)`, written by a new `RunView._write_notice`. Three calls the item left
open, and why they went this way:

- **Not `compared_run_line`, and the reason is `present_halt`.** The banner has
  two writers, and the second states a halt from the snapshot alone with no
  frame, because the frame is what may have failed (`PL-25KS`); `_halt_every_run`
  then swallows the redraw that follows, so on a raise out of the shared render
  path that banner is the last one written. Reading the run count off the frame
  there would drop the attribution in exactly the case this item is about. So
  the name is taken from what the dashboard already gives the run through
  `set_run_name` - the same word `run_label` put on the run's own panel and in
  both legends - and `_run_name` is recorded beside the label rather than read
  back off it.
- **One writer rather than composition at each call site.** `PL-25DD` weighed
  deriving the name inside the formatter and refused it, on one caller held by
  one test. Two callers invert that, and the second is the rarely-exercised
  halt path - which is the one a later edit would forget. `refresh` and
  `present_halt` wrote the identical line before this, so collapsing them into
  `_write_notice` removes the duplication and makes the attribution
  unforgettable in the same move.
- **A colon, where `COMPARED_RUN_LINE_TEMPLATE` uses an em dash.** All three
  notices already open `label — detail` ("Simulation stopped — ...", "Setting
  refused — ..."), so an em-dash prefix puts two in one sentence at different
  depths and the first reads as the banner's own separator with "Run 2" as the
  label. The chart column's lines carry no em dash of their own, which is why
  that template could use one. The colon is the sense
  `OFF_SCALE_NOTICE_TEMPLATE` and `COMPARED_TRACE_LEGEND_CAPTION` already use
  it in. A run *chip* - a second widget beside the banner - was the other
  option named in the item and was refused: it splits one statement across two
  widgets whose visibility must agree, and it leaves `NoticeLabel.notice()`
  returning a warning with no run, which is what the tests and any later
  reader of that text would get.

**Written and removed: a rewrite hung off `set_run_name`**, so the banner would
be renamed the instant the run set changed rather than on the presentation that
follows. It reads like the argument `set_comparing` already makes for the
transport, and it is not the same argument: mutating it away failed no test,
and no scenario could be built that told it from its absence - the fork's own
presentation rewrites every banner, and the Reset that drops a branch clears
the notice outright. A guarantee nothing can fail is not one.
`test_a_banner_standing_when_a_branch_opens_is_named_from_that_frame` holds the
presentation in that role instead.

**`docs/MODEL.md` owed an extension, not a row.** The banner qualifies the
values rather than showing one - "The values shown are the last completed step"
read as the dashboard's says both runs' readouts are frozen at a failed step
when one is still going - so it belongs to the row `PL-25DD` extended, which
enumerates every shared surface that names its run. The halted-versus-paused
row needed nothing: its mitigation is the per-run status words, and those were
never the thing that failed here.

**Done when.** With two runs drawn, each notice says which run it is about by a
channel that does not depend on stacking order, held by
`test_the_halt_and_refusal_banners_name_their_run` in
`tests/integration/test_simulation_view.py`.
