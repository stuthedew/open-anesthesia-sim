---
id: PL-H2K2
title: Nothing signals a run approaching the supported run length; it advances normally until the step at 24 hours is refused, so the halt arrives with no warning
priority: P2
effort: M
status: ready
classes: ux
feature: presentation-safety
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/controller.py, tests/unit/test_dashboard_frame.py, tests/integration/test_simulation_view.py, tests/integration/test_controller.py
added: 2026-09-07
verify: grep -q 'def test_the_interface_says_the_run_is_approaching_its_supported_length' tests/unit/test_dashboard_frame.py && uv run pytest -q tests/unit/test_dashboard_frame.py tests/integration/test_controller.py
---

**Problem.** Nothing signals a run approaching the supported run length; it
advances normally until the step at 24 hours is refused, so the halt arrives
with no warning.

**Why it matters.** `PL-Y5WR` (halt a run at the supported 24-hour run length)
made the run stop rather than extrapolate, which is the right behaviour — but it
reaches the reader only as a refusal, at the moment it fires. A reader at 23 h
50 min sees a run advancing normally and has no way to tell it is about to stop,
so the halt is as likely to read as a fault as as the model declining to
represent a patient past its declared envelope. `docs/MODEL.md` § "Supported run
length" already requires that those two not be presented alike, and
`require_supported_run_length`'s docstring gives the same reason for raising a
distinct exception type: nothing was miscalculated, and every displayed value is
a completed step's. Presenting the boundary only on arrival leaves the reader to
infer which of the two happened, from a screen that has said nothing about a
boundary until that instant. `.claude/rules/expert-review.md` states the general
form: prefer an interface that prevents the surprise over one that explains it
afterwards.

**Where.** `src/anesthesia_sim/app/simulation_view.py` — the clock is updated at
~2253 from `snapshot.elapsed_s`, the halt message is built at ~2770 from
`format_supported_run_length()`, and the
`isinstance(error, SimulationDomainLimitError)` branch that presents it is at
~3098. `src/anesthesia_sim/app/controller.py:1043` is what raises it.
`src/anesthesia_sim/core/supported_ranges.py` holds
`MAXIMUM_ELAPSED_SIMULATION_TIME_S` and `require_supported_run_length`; no
change is owed there, and the item must not edit it.

**Done when.** A reader can tell that a run is approaching its supported run
length *before* the run reaches it, from the interface rather than from
arithmetic on the clock; the statement takes the limit from
`MAXIMUM_ELAPSED_SIMULATION_TIME_S` rather than from a number written in the
view, so the interface cannot state a limit the model does not enforce; the
existing halt message is unchanged; and
`tests/unit/test_simulation_view.py` carries
`test_the_interface_says_the_run_is_approaching_its_supported_length`.

**Note on the mechanism, which is open.** A warning at a threshold, a persistent
remaining-run-length readout, or stating the limit beside the clock throughout
are all admissible. Prefer whichever adds no mode: a value shown continuously
cannot be missed and cannot fire at the wrong moment, whereas a threshold
warning introduces a state the reader has to notice and a number somebody has to
justify. That is a preference for the implementing session, not a decision this
item is waiting on.

**Re-pointed 2026-09-15, with `PL-25KS`.** The dashboard is on PySide6: what
it says is decided in `app/dashboard_frame.py` (the status word and the notice
banner are `status_word` and `notice` there) and drawn by `app/run_view.py`,
so the warning this item asks for is a claim the frame module states and a
label the run view places. `touches` and `verify:` name those modules and
their tests; the old command ran a Flet test file the port deleted.
