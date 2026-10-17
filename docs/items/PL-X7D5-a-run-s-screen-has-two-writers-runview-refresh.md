---
id: PL-X7D5
title: A run's screen has two writers - RunView.refresh from a drawn frame and RunView.present_halt from a hand-picked subset of controller state - and nothing owes a frame when the run changes outside present, so each widget missing from the subset, and each path that stops or changes a run without a frame, leaves the screen stating an old run: the cause of PL-1YDD, PL-DTJQ, PL-MMNX, PL-T995, PL-G3K7 and PL-0LG6 (found at the 2026-10-17 triage pass)
priority: P1
effort: L
status: ready
classes: safety, refactor
feature: every-control-restates-the-halt
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/dashboard_frame.py, docs/ARCHITECTURE.md, docs/MODEL.md, tests/integration/test_simulation_view.py, tests/unit/test_dashboard_frame.py
added: 2026-10-17
payoff: a halted or self-stopped run states itself on every widget as the controller holds it, and a widget added later is checked by default rather than remembered
verify: grep -q 'def test_every_run_state_widget_reads_alike_on_a_drawn_run_and_a_halted_one' tests/integration/test_simulation_view.py
root-cause-of: PL-1YDD, PL-DTJQ, PL-MMNX, PL-T995, PL-G3K7, PL-0LG6, PL-85LJ
generator: live - four reviews of the run view in ten days (PL-V2HC's, PL-85LJ's, PL-Y2SL's, PL-VN6M's) each found a widget or stop path the halt list or a frame request missed, and each widget added later is another
misread: Which widgets state a run's current state, and that each is restated on every path that changes it
---

**Problem.** A run's screen has two writers - RunView.refresh from a drawn frame and RunView.present_halt from a hand-picked subset of controller state - and nothing owes a frame when the run changes outside present, so each widget missing from the subset, and each path that stops or changes a run without a frame, leaves the screen stating an old run: the cause of PL-1YDD, PL-DTJQ, PL-MMNX, PL-T995, PL-G3K7 and PL-0LG6 (found at the 2026-10-17 triage pass)

**The mechanism, read 2026-10-17.** `RunView.refresh` writes every widget a
run shows from a drawn frame and its snapshot. `RunView.present_halt`, the one
writer that runs when no frame can draw, writes a list chosen by hand: the
status word, the transport, the notice banner, and since `PL-85LJ` the four
setting controls. Nothing states which widgets say what the run currently is,
so each one left off that list stays on the last frame after a halt
(`PL-1YDD` the agent identity, `PL-DTJQ` the control-change panel, `PL-MMNX`
the fork panel, which `_halt_every_run` never reaches). And nothing makes a
frame owed when a run changes outside `SimulationView.present`, so a path that
stops or changes a run without asking for one leaves every widget behind
(`PL-T995` a run stopping itself in `RunView.step_tick`, `PL-0LG6`
`SimulationView.add_run`, and `PL-G3K7` the legend written ahead of a frame
that then fails). `PL-85LJ`, closed, was the first member: its fix added one
more entry to the hand-picked list, which is why the list kept producing.

**Not members.** `PL-08SS`, `PL-F2T2` and `PL-M3M2` share the feature but not
the fact: each is slot code that reads the snapshot, or lets a raise out,
outside the halt gate, which is where the halt is stated rather than which
widgets it restates.

**Why it matters.** `PL-T995` is reachable today: a learner's own bookmark
halt leaves the screen reading "Running" with Pause live and a clock one step
behind, which is the stale-state presentation failure `CLAUDE.md`'s
safety-critical standard names. The rest need a failing frame, but each review
of this view finds another widget the list missed, and every widget or stop
path added later is another place to miss, so fixing the members one at a time
pays the same review again.

**Decision needed.** What shape makes "every widget states the run as it is"
true by construction rather than by a list. **Recommended:** one record per
run of what its screen states that is not a compartment value (status,
transport, notice, agent identity, settings, control timeline, fork offer),
built from the controller without a snapshot, and written by both `refresh`
and `present_halt` through one method, so a widget is added to the record or
is not on screen; and every path that changes a run's state outside `present`
- a self-stop in `step_tick`, `add_run`, a request that changes the selection
- asks for a coalesced frame, so the record is restated on the next tick.
[superseded 2026-10-17: the frame request per path was replaced by the design
round's half two, answered below - `render_tick` compares each run's record
and the run count against what was last written; and the fork offer is
restated by `_halt_every_run` at the dashboard rather than carried in the
per-run record.] The
alternative, keeping the two writers and a test that enumerates the widgets,
catches an omission only where the test's list is itself complete, which is
the list that has already failed. The choice is internal structure and is the
design round's to take; it reaches every member's code, so the round puts the
size and the risk of breaking the run view to the owner before building.

**Done when.** The shape answered below is built, in its two pull requests,
and four things hold:

- **The frame owed by a change.** `SimulationView.render_tick` draws whenever
  a displayed run's `SimulationController.record()` or the run count differs
  from what was last written. `PL-T995` (both its cases) and `PL-0LG6` close
  under it in the first pull request, each with the regression test its brief
  names. A frame that keeps failing is attempted once, not every tick.
- **One writer for the run-state widgets.** `RunView._write_statement` writes
  them from a pure `dashboard_frame.run_statement`. `refresh` and
  `present_halt` both call it, and `present_halt` calls it with
  `controller.record()`. The halt statement is on screen before the one write
  that can raise.
- **The dashboard's members.** `_halt_every_run` restates the fork panel,
  guarded, and the legend is handed the drawn frame's selection. `PL-1YDD`,
  `PL-DTJQ`, `PL-MMNX` and `PL-G3K7` close under these, each with its named
  regression test. `PL-G3K7`'s Done when is rewritten to the legend-from-frame
  form when it is claimed.
- **The default-include guard.**
  `test_every_run_state_widget_reads_alike_on_a_drawn_run_and_a_halted_one`
  in `tests/integration/test_simulation_view.py` compares every widget
  attribute of a `RunView` drawn by a frame with one halted with every frame
  failing, in equal states. The only exceptions are a `FRAME_WIDGETS` table,
  each entry named against its reason and held live in both directions.

The halt passage in `docs/ARCHITECTURE.md` describes the new shape.

**Generator check.** A generator: one fact - which widgets state a run's
current state, and that each is restated on every path that changes it -
misread by six open items and one closed, with no head's `misread:` stating it
(`bin/docket generators --misread`, 2026-10-17). Live, because four reviews in
ten days (`PL-V2HC`'s, `PL-85LJ`'s, `PL-Y2SL`'s and `PL-VN6M`'s) each handed
it new members.

**Design round requested 2026-10-17** (project owner, in the triage session):
claim this item, read its members' briefs (`PL-1YDD`, `PL-DTJQ`, `PL-MMNX`,
`PL-T995`, `PL-G3K7`, `PL-0LG6`), run the round from the marked
recommendation, and put the refactor's size and risk to the owner before
building anything.

**Design round, 2026-10-17.** Run from the marked recommendation, after reading
the six members' briefs and `RunView.refresh`, `present_halt`, `step_tick`,
`_write_settings`, `SimulationView.present`, `render_tick`, `_refresh_view`,
`_refresh_fork_panel`, `_halt_every_run`, `add_run` and
`_handle_compartment_request`. The fact the members misread has two halves,
and the design makes each one structural.

*Half one: which widget is written from what.* Every widget a run shows sits
in exactly one of two groups, decided by whether stating it needs a
compartment value:

- **Run-state widgets**, stated from what the run holds: the status word, the
  transport, the agent identity (`_apply_agent_color_scheme`'s six controls,
  the selector's index, the chip, the subtitle and the substance heading), the
  four dials, the control-change panel, and the notice banner.
- **Frame widgets**, stated from the drawn frame and its snapshot: the
  readout row (its clock included, which stays with the readouts it was read
  with, so no row pairs one instant's clock with another's values), the
  accounting panel, the off-scale line and the wash-in line.

Four parts build that split:

1. **A record to state from.** `controller.py` gains `RunRecord(RunSettings)`,
   which takes `control_timeline` up from `SimulationSnapshot`.
   `SimulationSnapshot` then extends `RunRecord`, and
   `SimulationController.record()` builds one from no compartment value, as
   `status()` and `settings()` do. This is the third layer of the existing
   `RunStatus` -> `RunSettings` -> `SimulationSnapshot` ladder.
2. **A pure statement of the run.** `dashboard_frame.py` gains a frozen
   `RunStatement` and a pure `run_statement(record, ...)` that builds it.
   `substance_heading` takes a `RunSettings`.
3. **One writer.** `RunView._write_statement` is the only writer of the
   run-state widgets. `refresh` calls it with the snapshot it drew from and
   the frame's undrawn marks. `present_halt` calls it with
   `controller.record()`, no undrawn marks, and `halt_notice`.
4. **A test that defaults to including widgets.** It puts two runs in equal
   states side by side: one drawn by a frame, and one halted with every frame
   failing. It then compares every widget attribute on the two `RunView`s,
   except those named in a `FRAME_WIDGETS` table, each named against its
   reason. That table is held live in both directions, as
   `FOREGROUND_NOT_DECLARED` is.

That test's default is the point. A widget added later is checked unless
someone declares it frame-bound, so leaving it out fails the suite. The
alternative the brief already refused was a list of the widgets to restate,
which passes silently when it is incomplete.

*Half two: a frame is owed whenever a run's record changes.* This is **one
change from the marked recommendation**, put to the owner below. Rather than
every path that changes a run outside `present` asking for a frame,
`render_tick` compares each displayed run's `controller.record()`, and the run
count, against what was last written. It draws when they differ.

- **What it covers.** That comparison covers `PL-T995` (a self-stop on a mark,
  or on arrival at the supported run length, changes the status) and `PL-0LG6`
  (`add_run` changes the count). It also covers any later path - a scripted
  scenario event fired inside `advance`, say - without that path being named
  anywhere.
- **What stays as it is.** Discrete actions still present at once, so they
  stay instant. The comparison is the floor, not the trigger.
- **How it is stored.** The record is stored when `_write_statement` writes
  it, `present_halt` included. A frame that keeps failing is therefore not
  retried every tick.
- **What it costs.** It reads only what `status()` already reads, so it
  builds no compartment value and cannot raise for one. It runs once per
  0.2 s tick (`RENDER_INTERVAL_S`) on a paused dashboard, which today does
  no work.
- **Why not per-path requests.** A request in `step_tick` and a
  `present(True)` in `add_run`, as `PL-T995`'s and `PL-0LG6`'s briefs
  propose, is two lines. It is also the list shape this generator came from:
  the next stop path has to remember to ask.

*The dashboard's own two members.* `_halt_every_run` restates the fork panel
from the case (`PL-MMNX`), guarded so that the restatement cannot raise out of
the halt path, and falls back to a withdrawn offer when it does raise. The
legend is made a frame widget (`PL-G3K7`): `_refresh_view` hands it the
selection the drawn frame was assembled from, after both plots draw, instead
of `_handle_compartment_request` handing it the new one ahead of the frame.
That replaces `PL-G3K7`'s own recommendation, to have `present` report whether
it drew and roll the selection back. That recommendation was a triage call,
not the owner's. It is again the list shape, since every later handler that
changes the selection would have to remember to roll back. `PL-G3K7`'s verify
test still reads the same, and its Done when is rewritten when the build
claims it.

*Size.*

- **Source.** Four files, about 250-300 changed lines:
  - `controller.py`: `RunRecord` and `record()`, about 50 lines.
  - `dashboard_frame.py`: `RunStatement` and `run_statement`, about 100.
  - `run_view.py`: the writer, plus `refresh` and `present_halt` rewritten
    around it, about 100.
  - `simulation_view.py`: the comparison, the fork-panel restatement and
    the legend's move, about 60.
- **Tests.** About 500-600 lines:
  - each member's named regression test, `PL-T995`'s through the real timers;
  - the equivalence test;
  - a pure unit test of `run_statement`;
  - edits to the existing halt tests that pin the old subset.
- **Docs.** The halt passage of `docs/ARCHITECTURE.md`, which cites
  `present_halt` and `render_tick`.
- **Not touched.** No model, equation or displayed value's computation.
- **Shipping.** Two pull requests, both held for the owner's read because they
  change `src/` and `tests/`:
  - First, half two alone. It fixes `PL-T995`, the one member a learner
    reaches today (P1, safety), and `PL-0LG6`, about 40 source lines and 120
    test lines.
  - Then half one and the dashboard members (`PL-1YDD`, `PL-DTJQ`,
    `PL-MMNX`, `PL-G3K7`), with the equivalence test.

*Risk, highest first.*

1. **Two ordering contracts become one.** `present_halt` writes the status
   word, transport and banner before anything that can raise
   (`setting_readouts`, `PL-25KS`, `PL-7DJK`, `PL-85LJ`). `refresh` writes the
   agent colour first and the banner last. One writer needs one order: agent
   colour, then everything that cannot raise, banner included, then the
   dials. Getting this wrong recreates `PL-7DJK`, a failed controller under
   a screen reading "Running". The existing tests for those three items are
   the guard, and they stay unchanged.
2. **The comparison must not become a loop.** If the record were stored only
   when a frame draws, a frame that keeps failing would be retried and the
   dashboard re-halted every 0.2 s. Storing it in the writer prevents that,
   and the half-two tests drive a failing frame through the real timers to
   check it.
3. **Tests pinning the old subset.** About 22 halt and timer tests in
   `tests/integration/test_simulation_view.py` exercise these paths. The
   success path is meant to behave identically, so edits should be
   confined to tests that assert a widget stays stale after a halt. How many
   do is not known until the suite runs.
4. **Static checks that read method bodies.** `tools/agent_identity_check.py`
   reads the identity set off `_apply_agent_color_scheme` and
   `_write_transport`. Both are kept as they are and called from the writer.
5. **When the legend hears of a change.** `compartment_selection_changed` now
   fires after a frame draws rather than on the click. The legend is its one
   subscriber, and on the success path both happen inside the same call.

**Recommended:** build it as above, in the two pull requests, the comparison
included. The alternative is to fix each member as its own brief says (each
`S`). That is about 150 lines in all, but it is the hand-kept list this item
was recorded to end, and the four reviews that found the members are the
evidence it does not hold.

**Answered 2026-10-17, both questions as recommended** (project owner,
2026-10-17, ratified, "Agree with recs"):

1. **The refactor**, in two pull requests, chosen over the six members fixed
   one at a time as their briefs say.
2. **The `render_tick` comparison** of each run's record and the run count,
   chosen over the marked recommendation's frame request on every path that
   changes a run outside `present`.

The Done when above is written for these answers. The build claims this item
afresh and starts with the first pull request, half two: `PL-T995` and
`PL-0LG6`.

**Build, first pull request, 2026-10-17.** The first pull request is built
and up for the owner's read. `PL-T995` and `PL-0LG6` close under it. It
adds four things:

- **`RunRecord(RunSettings)`** in `app/controller.py`, which carries
  `control_timeline`. `SimulationSnapshot` now inherits that field rather
  than declaring it.
- **`SimulationController.record()`**, built from no compartment value.
- **`RunView.owes_a_frame`**, which compares `record()` with the record the
  view last wrote.
- **The new `render_tick` condition.** It draws while a run runs, while a
  frame is owed, while the run count differs from the count last drawn, or
  while any run owes a frame.

Four details were taken here that the design round placed later or left open:

- `present_halt` reads `controller.record()` once and writes from it. The
  Done when puts that in the second pull request's `_write_statement`. It is
  taken now so that the record stored is exactly the one written.
- `RunRecord.run_record()` projects a snapshot onto its record. Dataclass
  equality compares like classes only, so a `SimulationSnapshot` never
  equals the `RunRecord` it extends.
- The run count is stored at the top of `_refresh_view`, at the attempt
  rather than on success, so a failing frame is not retried every tick.
  `refresh` and `present_halt` store the record the same way.
- The supported-run-length test shortens the span by monkeypatching
  `supported_ranges.maximum_step_count`. The real timers cannot reach 24 h in
  a test, and stepping there first takes about 27 s.

What remains is the second pull request: `_write_statement` with the
`RunStatement` builder, the four dashboard members, and the default-include
guard. Until then this item stays `ready`, with its claim yielded.
