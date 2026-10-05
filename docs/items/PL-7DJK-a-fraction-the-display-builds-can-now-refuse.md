---
id: PL-7DJK
title: A Fraction the display builds can now refuse, and the halt that follows is shown as a failed step, half-drawn, unnamed, or not at all, though no supported setting reaches it
status: untriaged
feature: parse-dont-validate
added: 2026-10-05
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
