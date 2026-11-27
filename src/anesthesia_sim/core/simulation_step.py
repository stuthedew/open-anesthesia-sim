"""State the one step that a run takes: one second, with every setting held constant across it.

A run moves forward in whole seconds. `AgentUptakeSystem.advance()` takes one step of
`SIMULATION_STEP_S`, and nothing in the simulator takes a step of any other length. So a run's
simulated time is a whole number of seconds, and its count of completed steps is that number
(`SimulationState.elapsed_s`).

Until `PL-SZ6G` the step was a value that a caller chose from a supported range, 1 ms to 0.1 s,
and the interface ran at 0.1 s. A binary float cannot hold 0.1 exactly. So an instant was a
rounded product, and each place that compared two instants or counted steps needed a rule for
that rounding. `PL-7CY5` counts the six items that came from it and records the decision to
step by whole seconds (project owner, 2026-11-21, ratified, over a step of a tenth of a second
held as a whole count of tenths, and over keeping the float step).

The step is exact at this length, as it is at any length. `matrix_exponential` solves the
governing equations over one second with no truncation error, and the propagator is formed once
for each stretch of constant settings (`AgentUptakeSystem`). What a one-second step costs is
control resolution, and the comment on `SIMULATION_STEP_S` states that cost.

A compartment stepped on its own still takes a step of any supported length, as a plain
`float`. `require_compartment_step` in `core/supported_ranges.py` checks that step.
"""

from __future__ import annotations

from typing import Final

# The one step that `AgentUptakeSystem.advance()` takes, in seconds.
#
# It is a whole number, so that a count of steps is a count of seconds and no
# instant is a rounded product. It is not a bound on the arithmetic. The
# propagator is the exact solution of the governing equations over the
# interval it is given. Its floating-point evaluation was measured across the
# settings envelope for every step from 1e-3 s to 3600 s (`PL-X9KD`). Its error
# is 1e-14 to 2e-12, as an absolute difference in concentration fraction, and
# it does not grow with the step.
#
# What the step sets is control resolution. Every setting is held constant
# across a step, so a control change takes effect at the next whole second and
# is delayed by up to one second. That delay is proportional to the step, with
# no threshold anywhere in it. So this constant is a declared tolerance rather
# than a derived limit, and is recorded here as one.
#
# The tolerance was measured on 2026-11-22 in percentage points (pp) of one
# atmosphere, as the largest difference in any displayed compartment between
# a manoeuvre made on time and the same manoeuvre made one second late. The
# case opening, which is dialling from off to 1 MAC at the reference adult's
# own flows, displaces a compartment by at most 7.3e-2 pp, with desflurane the
# worst agent. In the first hour at 1 MAC, one standard deviation of a single
# measured partition coefficient displaces a compartment by up to 4.0e-2 pp
# (fat), 5.4e-2 pp (vessel-rich), 9.0e-2 pp (blood:gas) or 9.9e-1 pp (muscle)
# (docs/INTERFACE.md "Why the readouts show two decimals"). So an ordinary
# control action's timing error is smaller than the blood:gas and muscle
# uncertainties, larger than the vessel-rich and fat ones, and more than ten
# times smaller than the largest of them.
#
# This tolerance does not cover an abrupt manoeuvre. A ventilator start made
# one second late displaces the alveolar reading by up to 1.3 pp, which is
# more than one standard deviation of any single coefficient moves a readout
# in the first hour. A user who needs a change timed more finely than one
# second cannot have it: the pause, change, resume route in app/playback.py
# also lands on a whole second.
#
# The project owner chose this step on 2026-11-21 (`PL-7CY5`). It replaces a
# step of 0.1 s, chosen on 2026-09-06 (`PL-NBCJ`), whose figures were a tenth
# of these. docs/VERIFICATION.md "Supported simulation step" carries the measurements
# and both decisions.
#
# The figures are per second of delay, and a caller decides how many seconds a
# control change waits (`PL-NBWP`). The shipped interface applies a change at
# the next whole second at 1x and 5x playback. At a faster rate it advances
# several seconds between control opportunities, so its own resolution is that
# many times coarser: 30 s, and up to about 10 pp, at 300x. That is a property
# of the caller's loop and not of this constant. The whole per-rate table is in
# docs/VERIFICATION.md "Supported simulation step", and app/playback.py states which
# grid the interface offers.
#
# Every figure quoted above is measured again from the parameter files at each
# run of tests/reference/test_control_resolution.py (`PL-ZVS7`).
SIMULATION_STEP_S: Final = 1
