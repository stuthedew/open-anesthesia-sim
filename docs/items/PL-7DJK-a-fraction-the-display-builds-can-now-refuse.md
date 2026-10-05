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
