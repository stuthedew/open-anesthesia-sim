---
id: PL-7DJK
title: A Fraction the display builds can now refuse, and the halt that follows is shown as a failed step, half-drawn, unnamed, or not at all, though no supported setting reaches it
priority: P1
effort: M
status: done
classes: safety, defect
feature: parse-dont-validate
milestone: v0.5.23
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/run_series.py, src/anesthesia_sim/core/concentration.py, src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/patient.py, tests/integration/test_simulation_view.py, tests/integration/test_controller.py, tests/unit/test_chart_frame.py, tests/unit/test_dashboard_frame.py, docs/ARCHITECTURE.md, docs/MODEL.md
added: 2026-10-05
closed: 2026-10-11
pr: 1408
payoff: when a value the display builds is refused, the screen says the run has stopped and why, instead of reading Running over a frozen, half-drawn chart
verify: grep -q 'def test_a_halt_is_shown_when_the_snapshot_itself_is_refused' tests/integration/test_simulation_view.py
---

**Problem.** Since `PL-4R3W`, `Fraction` and `Percent` check their range when
built, and the display path builds them from values it reads:
`SimulationController.snapshot()` wraps five compartment fractions and
`_compartment_mac_multiples` a state entry (`app/controller.py`);
`RunFrame.percents`, `_hover_value` and the two cursor readouts wrap recorded
fractions (`app/chart_frame.py`); and `off_scale_notice` builds its axis top as
a `Percent` (`app/dashboard_frame.py`). Until `PL-4R3W` each was a `NewType`
cast. Now each can refuse, and the paths a refusal takes were built for a
display that could not:

1. **The halt is not shown when `snapshot()` refuses.**
   `SimulationView._halt_every_run` calls `RunView.present_halt()`, which calls
   `snapshot()` again outside any `try`. With the alveolar amount written
   1.0000001 times its capacity directly and `render_tick` driven offscreen,
   the exception escaped the slot: the controller had failed, but the screen
   read `status: Running | banner: None`, Pause stayed enabled and the chart
   froze. That is the failure `PL-25KS` fixed - a halt presented only through
   the path that failed - arriving by a new route. Main ran on, showing the
   value.
2. **The banner blames a step.** A chart trace patched to 1.0000000000001568
   halts every run with "Simulation stopped — SimulationConfigurationError:
   fraction of 1.0000000000001568 is outside 0 to 1 … the step that failed was
   rolled back and changed nothing." No step failed; a displayed value was
   refused.
3. **The chart is left half-drawn.** In that run the circuit, alveolar,
   mixed-venous and vessel-rich traces were redrawn by the failed frame and
   muscle and fat were not, and the readouts and the wash-in plot stayed on the
   previous frame.
4. **No compartment is named.** No display-path construction passes `name`, so
   a refusal says "fraction of ...", against the convention `Fraction`'s
   docstring states and `_write_state_vector` keeps (`PL-SPN6`).

**Reproduced 2026-10-05**, case 1, on `main` at b67dace8. One `uv run python
-c` under `QT_QPA_PLATFORM=offscreen`: a `SimulationView` over one
`SimulationController`, Start clicked, the alveolar `agent_amount_l` written as
1.0000001 times `gas_volume_l`, then `render_tick()`. It raised out of
`render_tick` - `SimulationConfigurationError: fraction of 1.0000001 is outside
0 to 1, the range a fraction of one atmosphere takes` - and left the controller
at `is_running False` with that failure recorded, while the screen read
`status 'Running' | Pause enabled True | banner shown False`. Unnamed, as
item 4 says: "fraction of", no compartment.

**Why it is not live.** No supported setting computes a fraction outside 0 to
1 - the highest anywhere is 0.18000000000002825, desflurane at its 18% maximum
(`core/concentration.py`) - every write to a compartment goes through a checked
`Fraction`, and an amount written as a fraction times its capacity reads back
no greater than 1, since rounding is monotone. A refusal here needs a future
write that skips every checked path, or a 100% dial no application path sets.
`PL-4R3W`'s close-out review measured all four on 2026-10-05 by writing the
state directly; on main each value was shown and the run went on.

**Settled at `PL-4R3W`'s read.** Until this lands, a refusal on the display
path halts the run rather than drawing the value (project owner, 2026-10-05,
ratified, over drawing it as `main` did), so what is left here is how the halt
is shown, and whether the display re-checks at all.

**What a fix probably wants.** Settle first whether the display should re-check
these at all: `.claude/rules/core-domain.md`'s pattern does not re-check a held
proof, and these arrive as bare floats only because each compartment exposes a
derived `amount / volume`. Where a check stays: present a halt from facts that
cannot fail - `status_word`, `transport` and `notice` read only `is_running`,
`failure_reason` and `supported_limit_reason` - rather than from a fresh
snapshot; build every value a frame draws before drawing any; name each
construction by the quantity it is; and word a refused displayed value as one.

**Settled before building (2026-10-11): the check stays, at the four places a
derived `float` becomes a typed field, because no held proof exists for the
display to reuse.** `.claude/rules/core-domain.md` re-checks no held proof,
and nothing the display builds from holds one: each compartment stores
`agent_amount_l`, and its `partial_pressure_fraction` is the quotient
`agent_amount_l / gas_volume_l` (`core/alveolar.py`, `core/tissue.py`,
`core/blood.py`) - a bare `float` carrying no proof, under the rule's own
second fact about Python. A step builds the `Fraction` once, in
`AgentUptakeSystem._write_state_vector`, and the setter it hands it to stores
the amount, so the proof is spent the moment the value is held;
`state_vector()` reads the quotients back as floats, and a drawn column is
`RunDefinition`'s closed form evaluated at an instant no compartment ever
held. Moving the proof into the compartments - storing the `Fraction`, or
refusing an amount past the capacity where it is written - is a change to
`core/`'s records this brief does not scope, and it would still leave the
drawn columns unproved; the unguarded amount write, which is how case 1 was
reproduced, is captured as its own item. What arrives already proved passes
through unbuilt: the circuit's `inspired_partial_pressure_fraction`, held as
a `Fraction` (`core/circuit.py`), the settings' `Percent`s and flows, and the
agent's MAC and MAC-awake. So the four sites build the type, each naming its
quantity: `snapshot()`'s five quotients and `_compartment_mac_multiples`'s six
state entries (`app/controller.py`), every drawn column at frame assembly
(`app/chart_frame.py`'s `_run_frame`), and the axis top
(`assemble_chart_frame`); `RunFrame.percents`, the hover and the cursor
readouts then read a built `Fraction` and build nothing. The owner's ratified
answer above - a refusal on this path halts the run - is unchanged; what this
settles is that the refusal is raised where the value is first typed, which
is before any frame exists, and that the halt is stated from the controller's
run state, which no compartment value is built for.

**Built (2026-10-11, #1408).** `SimulationController.status()` returns a
`RunStatus` - `is_running`, `supported_limit_reason`, `failure_reason` -
built from the controller's own run-state fields and the run-length guard,
and `SimulationSnapshot` extends it, so `status_word`, `transport` and
`notice` take either and every caller passing a snapshot is unchanged;
`RunView.present_halt` and `set_comparing` read `controller.status()` and
never `snapshot()`. `present_halt` writes `dashboard_frame.halt_notice`,
whose failure wording says no frame of the stopped run could be drawn and
that the chart and the readouts show the frame drawn before the stop;
`refresh` replaces it with `notice`'s on the first frame that draws, so
which banner stands is decided by whether a frame drew rather than guessed
from the reason. `FAILURE_NOTICE_TEMPLATE` no longer claims "the step that
failed was rolled back and changed nothing", which was true only of a step
failure - whose `SimulationNumericalError` already says so - and false of a
setting that raised (`PL-YK2V`) and of a refused displayed value.
`RunFrame.fractions` holds `Fraction`s built in `_run_frame` and
`ChartFrame.axis_top_percent` a `Percent` built in `assemble_chart_frame`,
so the refusal comes before a frame exists and `ConcentrationChart.draw` is
never handed one to half-draw; `percents`, the hover, the cursor readouts
and `off_scale_notice` build nothing. `run_series.COMPARTMENT_FRACTION_NAMES`
carries the six names `_write_state_vector` uses, and the snapshot, the MAC
multiples and the frame name from it.

Tests: `test_a_halt_is_shown_when_the_snapshot_itself_is_refused` and
`test_a_frame_that_refuses_a_drawn_value_moves_no_trace`
(`tests/integration/test_simulation_view.py`; both red on `main` at
103b07d6, the first with the unnamed refusal escaping `render_tick`);
`test_a_halt_no_frame_was_drawn_for_is_worded_as_one_rather_than_as_a_failed_step`
and `test_a_halt_is_stated_from_the_run_status_alone`
(`tests/unit/test_dashboard_frame.py`);
`test_a_drawn_fraction_past_one_atmosphere_is_refused_before_any_frame_exists`,
`test_a_refused_drawn_value_names_its_compartment_as_a_step_would`,
`test_a_frame_holds_built_fractions_so_nothing_drawn_from_it_builds_one` and
`test_an_axis_top_past_one_atmosphere_is_refused_when_the_frame_is_assembled`
(`tests/unit/test_chart_frame.py`); and
`test_a_snapshot_whose_quotient_is_refused_names_the_compartment_and_the_status_answers`
(`tests/integration/test_controller.py`). The pinned failure banner in
`test_refresh_view_reports_a_failed_run_as_stopped_not_paused` is rewritten
for the shorter wording. Two findings filed: `PL-544D`, the unguarded amount
write the reproduction and two of the tests rely on, and `PL-V2HC`, a halted
run whose snapshot refuses cannot change agent, with a coalesced slider
change's `_refresh_against_last_frame` reading the snapshot outside the
gate too.

**Why it matters.** A halt that is not shown is the worst of the four: a
screen reading "Running" with Pause enabled over a failed controller is the
stale-state display `CLAUDE.md`'s safety standard names, and it is the failure
`PL-25KS` fixed for the render path, back by a route that fix did not reach.
The other three mislead the reader who does see the halt - a banner sending
them to a step that did not fail, a chart whose traces stand at two different
instants, a refusal that does not say which compartment. P1 rather than P0
because no supported setting reaches any of them today, as measured above; the
owner's ratified answer that such a refusal halts the run makes the halt's
presentation the whole of what is left.

**Done when.** The implementing session settles whether the display re-checks
these at all, from the code and `.claude/rules/core-domain.md`, and records the
answer and its reason in this brief before building either way. Whichever it
is: a halt is shown from facts that cannot fail - the status word, transport and
banner written without a fresh snapshot - so
`test_a_halt_is_shown_when_the_snapshot_itself_is_refused` in
`tests/integration/test_simulation_view.py`, beside
`test_a_halt_whose_frame_cannot_be_drawn_is_still_shown_on_every_run`, makes
`snapshot()` raise on a running run, drives `render_tick()`, and asserts the
failure is recorded, the status word and banner say so, and Pause and Start are
off; it fails on today's tree. Where a check stays, three more tests in
`tests/unit/test_chart_frame.py` and `tests/unit/test_dashboard_frame.py`, named
by the session, hold the other three: a refused displayed value is worded as
one rather than as a failed step, a frame that cannot be built draws nothing
rather than half of itself, and each construction names its quantity. Where
the check goes, the brief says which types now arrive already proved, and the
unit tests show a compartment's fraction reaching the display without a
second check.
