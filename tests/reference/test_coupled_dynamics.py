"""Check the coupled six-state solution against an independent integration.

Mass balance cannot detect a wrong rate. Every internal exchange appears in
the system matrix as a pair of entries whose contributions to the total stored
amount cancel. So the accounting residual stays at the level of rounding whatever
the transfer rates are, including rates that would move the alveolar fraction by
tenths of a percentage point. Conservation is necessary but nowhere near
sufficient, and this module is the check that closes the gap. It re-derives
the governing equations of `docs/MODEL.md` from the parameter files,
integrates them with a fourth-order Runge–Kutta method written from scratch, and
requires the shipped solution to agree with that one.

The independence rule is what makes this a verification rather than a
tautology. `test_oracle_imports_no_solver_from_core` therefore enforces the rule
mechanically rather than leaving it to review: the oracle below may import
the parameter loaders and nothing else from `anesthesia_sim`. Re-deriving an
equation from the specification is evidence. Calling the implementation
under test and comparing it against itself is not.

This module was promoted from the verification harness of the v0.2.0 architecture
review (PL-023). That harness contained the same oracle, but it was run only by hand.
PL-STNV retired the harness once every check it carried had become a closed item,
a reference test, or an open queue entry. The harness now survives only in git
history.
"""

from __future__ import annotations

import ast
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import pytest

from anesthesia_sim.app import formatting
from anesthesia_sim.core.concentration import Fraction, Percent
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

# These factors are declared here rather than imported from `core/units.py` and
# `core/concentration.py`, just as every equation in `_build_derivative` is
# written out here. Agreement is evidence only while the specification is written
# out independently of the code under test. A factor taken from that code would
# check the code against itself (`PL-QRBB`). An operating point gives each control
# in the unit it is set in. The vaporizer dial is in percent, which is how the
# circuit has stored it since `PL-NJPB`. The oracle converts with these factors.
SECONDS_PER_MINUTE = 60.0
PERCENT_PER_UNIT_FRACTION = 100.0

AGENT_IDS = ("sevoflurane", "isoflurane", "desflurane")

# Simulated horizons, each chosen for what it exercises. At 60 s the circuit and
# alveoli are washing in while the tissues are still empty. At 600 s the
# vessel-rich group is approaching its own equilibrium. At 3600 s the run is far
# enough in for muscle and fat to carry a meaningful load. The pinned reference
# states below are computed at these horizons.
#
# 3600 s is also the only run in this module that goes past 900 s, and it gives
# the shipped step's rounding time to accumulate. The residual is rounding added
# once per step, over 36 000 shipped steps in an hour. The endpoint table at
# `HELD_RUN_ROUNDING_BOUND` grows monotonically with the horizon for every agent.
# This comment deliberately does not quote how *many* times the residual grows
# from 60 s to 3600 s. The 60 s residuals are a few units in the last place
# (2.5e-16 to 5.7e-16). A ratio taken against them therefore shows how few bits
# had accumulated by 60 s, not anything about the step. For that reason alone,
# the three agents' ratios spread over an order of magnitude. The absolute table
# is the measurement, and the ratio is not. What does carry information is that
# the worst state moves from the fast circuit compartment to the slow muscle
# compartment, which no trajectory shorter than an hour ever reaches.
# `test_the_shipped_step_reaches_the_pinned_reference_horizons` is the gate that
# covers this. Sampling only the endpoint is right in that gate for the same
# reason: at 3600 s the maximum is at the endpoint, not inside a transient.
HORIZONS_S = (60.0, 600.0, 3600.0)

# The historical operating point. It is kept because the pinned reference states
# below are its solution. 5% is the highest concentration that all three shipped
# vaporizers can deliver (it is isoflurane's maximum), so one dial setting serves
# every agent.
DELIVERED_PERCENT = 5.0
FRESH_GAS_FLOW_L_MIN = 4.0
CIRCUIT_VOLUME_L = 6.0

# These constants restate the model's own supported input ranges instead of
# importing them. The reason is the same as for SHIPPED_STEP_S below: this gate
# should state, in its own file, the domain it claims to cover.
# `test_envelope_limits_match_the_supported_input_ranges` fails when the
# model's ranges and this restatement differ. Without that test, nothing would
# fail when a limit moved. Widening a range would silently enlarge the domain
# these measurements are assumed to cover, and moving any limit would silently
# shrink or stretch the domain this gate covers. PL-042 exists to fix that
# defect. Before PL-0MLQ, these constants were the interface's slider limits.
# The restatement was then checked against `simulation_view`, because the
# interface was the only place the domain was declared.
#
# The minimums matter as much as the maximums, and the same test checks both.
# Two gate trajectories hold a control at zero. `_ventilator_start` holds
# alveolar ventilation at zero. `_unperfused_load_then_dial_off` holds cardiac
# output at zero and then closes the vaporizer. If a minimum were raised above
# zero, the supported-range types would reject those settings, and the
# trajectory would raise an error instead of running. The test named above
# would also fail, and its message says which measurements to re-derive.
# `docs/MODEL.md` § "Supported input ranges" records that zero is supported on
# all four controls, and that this was deliberate (PL-629Z).
MAX_FRESH_GAS_FLOW_L_MIN = 10.0
MAX_ALVEOLAR_VENTILATION_L_MIN = 12.0
MAX_CARDIAC_OUTPUT_L_MIN = 10.0
MIN_FRESH_GAS_FLOW_L_MIN = 0.0
MIN_ALVEOLAR_VENTILATION_L_MIN = 0.0
MIN_CARDIAC_OUTPUT_L_MIN = 0.0
MIN_DELIVERED_CONCENTRATION_PERCENT = 0.0

# The resolution at which every concentration is displayed. It is restated for the
# same reason as the slider limits.
# `test_displayed_resolution_and_shipped_step_match_the_interface` checks it against
# the interface, together with the delivered-concentration minimum.
# `docs/MODEL.md` § "Displayed precision" argues for the choice.
CONCENTRATION_DISPLAY_DECIMALS = 2


@dataclass(frozen=True)
class OperatingPoint:
    """A point in the space of settings the interface can produce.

    The class is frozen so that it can key the reference-solution cache. The four
    fields are exactly the sliders that enter the governing equations. Circuit
    volume is not among them. It is a data-file parameter with no slider, and it
    scales only the circuit equation rather than changing the coupling between
    compartments, which is where a wrong transfer rate would show. PL-GYH2
    records the question of whether it should be a control at all, and what
    range it would need if it became one.
    """

    delivered_percent: float
    fresh_gas_flow_l_min: float
    alveolar_ventilation_l_min: float
    cardiac_output_l_min: float


@dataclass(frozen=True)
class Phase:
    """One leg of a trajectory: settings held for a fixed duration.

    A run of the application is a sequence of these legs, because the settings
    stay the same until someone moves a slider. A gate driven by a phase list
    therefore covers what the application actually produces. One held
    `OperatingPoint` covers only the runs in which nothing is ever changed.
    """

    duration_s: float
    point: OperatingPoint


def _default_operating_point() -> OperatingPoint:
    """The point the pinned reference states were computed at."""

    patient = load_reference_adult_parameters()

    return OperatingPoint(
        delivered_percent=DELIVERED_PERCENT,
        fresh_gas_flow_l_min=FRESH_GAS_FLOW_L_MIN,
        alveolar_ventilation_l_min=patient.default_alveolar_ventilation_l_min,
        cardiac_output_l_min=patient.default_cardiac_output_l_min,
    )


def _max_dial(agent_id: str) -> float:
    """The agent's own vaporizer maximum, in the percent its dial is set in."""

    return load_agent_parameters(agent_id).max_delivered_concentration_percent


def _envelope_corner(agent_id: str) -> OperatingPoint:
    """Return the settings corner where the operator split's error was largest.

    This corner was found by sweeping all four controls, not assumed. Fresh gas
    flow and alveolar ventilation both increase the disagreement with the oracle
    monotonically, up to their slider maxima. Along cardiac output, the
    disagreement has an interior *minimum* near 5 L/min. It rises toward both
    ends, and more toward the upper end. The equations are linear in the
    delivered fraction, so the agent's own vaporizer maximum is its worst dial
    setting. The measurements are recorded in `docs/MODEL.md`
    § "Independent-solution test".

    The sweep was run while the operator split was the shipped method. This
    corner is no longer the worst case by any meaningful margin, and it is now
    kept for the part of the domain it covers. Now that the oracle has converged
    (`ORACLE_STEP_S`), all five gate trajectories measure the same thing at the
    shipped step: accumulated rounding error. That error does not grow with how
    violently the settings move. At the 0.1 s step, four of the five
    trajectories run for 600 s and the unperfused load runs for 900 s. Their
    results all lie within a factor of 1.8 of each other. The unperfused load
    takes the most steps and still reports the smallest error. For desflurane,
    that error peaks at 416.5 s, during the loading phase, while cardiac output
    is zero and every blood and tissue state is still empty. Each figure below
    is measured at the shipped step and is the largest over all states and
    agents. Desflurane has the largest error in every trajectory. Its figures
    are 1.5786e-14 for ordinary use, 1.5377e-14 for this corner, 1.3906e-14 for
    the ventilator start, 1.3427e-14 for held defaults, and 8.7985e-15 for the
    unperfused load.

    This changes what this trajectory is *for*. With the earlier, coarser
    oracle, the corner and the ventilator start reported the largest numbers,
    so they appeared to be the cases that set the gate's tolerance. In fact,
    those numbers were set by how well the coarse oracle could resolve a
    transient. The two trajectories are now kept because they drive settings
    that no other trajectory reaches. They are kept for coverage, not as worst
    cases.

    Monotonicity is measured, not proved. A change to the governing equations
    could move the maximum off this corner. That is why the sweep should be
    re-run, rather than trusted, when the model changes.
    """

    return OperatingPoint(
        delivered_percent=_max_dial(agent_id),
        fresh_gas_flow_l_min=MAX_FRESH_GAS_FLOW_L_MIN,
        alveolar_ventilation_l_min=MAX_ALVEOLAR_VENTILATION_L_MIN,
        cardiac_output_l_min=MAX_CARDIAC_OUTPUT_L_MIN,
    )


def _ventilator_start(agent_id: str) -> tuple[Phase, ...]:
    """Prime the circuit with the ventilator off, then start ventilating.

    This is a manoeuvre that the interface offers and a user performs. The
    vaporizer is open and fresh gas is running while alveolar ventilation is
    still zero. So the circuit fills to the dial setting while the lungs cannot
    take up any of it. Starting ventilation then presents the largest
    circuit-to-alveolar gradient the machine can produce, at the largest
    ventilation it can produce.

    Five minutes is far longer than the circuit needs. At 10 L/min into 6 L,
    the circuit's time constant is 36 s. The first phase therefore ends with
    the circuit saturated, and the scenario does not depend on exactly how
    long that phase ran.
    """

    return (
        Phase(
            300.0,
            OperatingPoint(
                _max_dial(agent_id),
                MAX_FRESH_GAS_FLOW_L_MIN,
                MIN_ALVEOLAR_VENTILATION_L_MIN,
                MAX_CARDIAC_OUTPUT_L_MIN,
            ),
        ),
        Phase(
            300.0,
            OperatingPoint(
                _max_dial(agent_id),
                MAX_FRESH_GAS_FLOW_L_MIN,
                MAX_ALVEOLAR_VENTILATION_L_MIN,
                MAX_CARDIAC_OUTPUT_L_MIN,
            ),
        ),
    )


def _unperfused_load_then_dial_off(agent_id: str) -> tuple[Phase, ...]:
    """Fill the circuit and lungs with no circulation, then restore it and dial off.

    This is the most violent trajectory the four sliders can produce. The reason
    is structural, not clinical. Holding cardiac output at zero lets the circuit
    and alveoli saturate at the dial setting while every blood and tissue
    compartment stays empty. That drives the six states as far apart as they
    can go. The next phase turns perfusion on and the vaporizer off at the same
    moment. Every compartment's equilibrium is then at the opposite extreme from
    where the compartment sits, so all six transients run at once.

    Under the operator split, this trajectory also had the largest error, which
    is why it was added. It no longer does. Since the oracle was refined
    (`ORACLE_STEP_S`), every gate trajectory reports the shipped step's
    accumulated rounding error, and this one reports the smallest of the five.
    For desflurane it is 8.7985e-15, against 1.3906e-14 on `_ventilator_start`
    and 1.5786e-14 on `_ordinary_use`. The docstring of `_envelope_corner` lists
    the figures for all five. The scenario is kept for two reasons. It still sets
    up the widest spread of initial states the interface allows. It is also the
    only gate trajectory that takes cardiac output or the delivered
    concentration to its minimum. `_ventilator_start` is the only other
    trajectory that takes a control to its minimum, and that control is
    alveolar ventilation.

    Zero cardiac output is a supported input. That was decided and recorded,
    not inherited, and `docs/MODEL.md` § "Supported input ranges" gives the
    reasons. The main reason is that reducing cardiac output speeds up
    alveolar wash-in, and zero is the clearest case of that lesson. So this
    trajectory is inside the domain the gate must cover. It is not an edge case
    tolerated at the boundary.

    Even so, the gate does not rest on this trajectory alone.
    `_ventilator_start` above needs no zero-perfusion phase and reports a larger
    error. If a later decision raised the cardiac output slider's minimum above
    zero, this trajectory would be replaced, and the gate would still mean
    something.

    Ten minutes of loading is enough to saturate the circuit and alveoli.
    Extending the loading to twenty minutes changed the measured error
    coefficient by a relative 4e-5. That figure dates from the operator split,
    when the error coefficient itself was the quantity being measured.
    """

    return (
        Phase(
            600.0,
            OperatingPoint(
                _max_dial(agent_id),
                MAX_FRESH_GAS_FLOW_L_MIN,
                MAX_ALVEOLAR_VENTILATION_L_MIN,
                MIN_CARDIAC_OUTPUT_L_MIN,
            ),
        ),
        Phase(
            300.0,
            OperatingPoint(
                MIN_DELIVERED_CONCENTRATION_PERCENT,
                MAX_FRESH_GAS_FLOW_L_MIN,
                MAX_ALVEOLAR_VENTILATION_L_MIN,
                MAX_CARDIAC_OUTPUT_L_MIN,
            ),
        ),
    )


def _ordinary_use(agent_id: str) -> tuple[Phase, ...]:
    """The settings a run starts at, held: 1 MAC and the reference adult's own flows.

    The gate's other trajectories are chosen for where the disagreement is
    worst. This one is chosen for where a reader actually is, so that a claim
    about what the interface displays is not established only at its
    extremes.
    """

    patient = load_reference_adult_parameters()

    return (
        Phase(
            ENVELOPE_HORIZON_S,
            OperatingPoint(
                load_agent_parameters(agent_id).mac_percent,
                FRESH_GAS_FLOW_L_MIN,
                patient.default_alveolar_ventilation_l_min,
                patient.default_cardiac_output_l_min,
            ),
        ),
    )


def _envelope_corner_held(agent_id: str) -> tuple[Phase, ...]:
    """The envelope corner, held for the whole run."""

    return (Phase(ENVELOPE_HORIZON_S, _envelope_corner(agent_id)),)


def _held_default_settings(agent_id: str) -> tuple[Phase, ...]:
    """The reference point, held for the whole run: a trajectory that never turns."""

    del agent_id  # the reference point is the same for every agent

    return (Phase(ENVELOPE_HORIZON_S, _default_operating_point()),)


# The setting-change trajectories the gate drives. They were found by sweeping the
# corners of both phases' settings, and then each axis separately around the
# worst corner. What the sweep showed, and why these two trajectories are kept:
#
#   - The worst disagreement always comes at the first transition after the
#     loading phase saturates. Repeating the cycle three or six times does not
#     raise the peak at all, and shortening the phases lowers it. So the
#     disagreement is bounded rather than accumulating over a run. Re-measured
#     under the exact step, this is still true, and more sharply: on the
#     ventilator start the running maximum at 60 s, 600 s, 1800 s and 3600 s is
#     the same number, reached at about 306 s and never approached again.
#   - Inserting a third phase between the two never beat the pair. The best
#     middle phases were the ones that simply held the loading corner longer.
#   - Every axis is monotone toward the corner used, except cardiac output in
#     the loading phase. That axis is worst at zero, which is the opposite end
#     from the constant-setting corner, where cardiac output is worst at the
#     maximum.
#
# The sweep was run while the split was the shipped method, and its ordering of
# the two scenarios has since reversed (see `_unperfused_load_then_dial_off`).
# So what the sweep establishes now is that these two bracket what a turning
# trajectory does, not which of them is the extreme. Monotonicity is measured,
# not proved. A change to the governing equations could move the maximum off
# these trajectories, so the sweep should be re-run rather than trusted.
SETTING_CHANGE_SCENARIOS = (
    ("ventilator start", _ventilator_start),
    ("unperfused load then dial off", _unperfused_load_then_dial_off),
)

# Every trajectory this module drives. The checks that must pass on all of them,
# not only where the disagreement is worst, use this list.
ALL_GATE_TRAJECTORIES = (
    ("ordinary use", _ordinary_use),
    ("reference point, held", _held_default_settings),
    ("envelope corner, held", _envelope_corner_held),
    *SETTING_CHANGE_SCENARIOS,
)


# This horizon is long enough to contain the worst disagreement anywhere in the
# envelope. At the corner, the worst disagreement occurs early in the wash-in
# transient: at 5.4 s for isoflurane, 6.6 s for sevoflurane and 7.2 s for
# desflurane. The running maximum is unchanged to every digit whether the run
# stops at 60 s, 600 s, 1800 s or 3600 s. The trajectory gates therefore run to
# 600 s and take the maximum over the whole trajectory rather than sampling
# endpoints.
#
# Held *default* settings are the exception, and they are why `HORIZONS_S` still
# has a 3600 s entry. At held defaults nothing transient is happening. The
# residual is rounding that accumulates with the step count, and it keeps growing
# for the whole hour. A maximum taken over 600 s cannot see that growth. Only a
# longer run can, which is what
# `test_the_shipped_step_reaches_the_pinned_reference_horizons` is for.
ENVELOPE_HORIZON_S = 600.0

# SHIPPED_STEP_S is the step the interface runs at
# (`app.dashboard_frame.SIMULATION_STEP_S`). It is restated rather than imported
# so that this reference test stays independent of the application layer.
#
# `test_displayed_resolution_and_shipped_step_match_the_interface` checks the
# restatement, for the same reason it checks the slider limits. This comment
# used to give a different reason, which no longer applies. Under the operator
# split, every measured figure here was a first-order coefficient multiplied by
# this step, so moving the step rescaled all of them. That is not true of the
# exact propagator. It solves each interval exactly, however the interval is
# divided into steps, so it has no coefficient to multiply (`PL-X9KD`).
#
# The step still has to be checked, for two reasons that still apply:
#
#   - This module measures accumulated floating-point rounding. Rounding
#     accumulates with the *number* of steps, not with their size. A 600 s
#     trajectory involves 6 000 roundings at this step and 24 000 at 0.025 s.
#     With the default settings held, the measured residual for sevoflurane
#     grows accordingly: 2.8935e-15 at 0.1 s, 1.3385e-14 at 0.05 s and
#     3.8337e-14 at 0.025 s. Since `PL-B1WW` refined `ORACLE_STEP_S`, the
#     trajectory gates report this same quantity, which is also what
#     `HELD_RUN_ROUNDING_BOUND` measures. The oracle has converged on the
#     transients too. So every figure in this module is the shipped step's own
#     rounding, not just the figure from one gate.
#   - A setting change takes effect only at a step boundary, so the step sets
#     the phase boundaries of every trajectory here. Two of the five
#     trajectories change their settings partway through. If the shipped step
#     moved while this constant did not, those changes would move off the
#     instants at which these measurements were taken.
#
# A second former reason no longer applies either.
# `core.simulation_step.MAXIMUM_SIMULATION_STEP_S` is not derived from anything
# measured here. `docs/MODEL.md` § "Supported simulation step" records that its
# old derivation no longer holds, and that the value is kept unchanged until
# `PL-X9KD` is resolved. Until PL-VP7N, the step was restated here without any
# check at all.
SHIPPED_STEP_S = 0.1

# The oracle's own step, an eighth of the shipped one. It is deliberately not
# 0.1 s, so that agreement can never be an artifact of the two solvers sharing a
# step size. It is also deliberately fine enough to be converged during a fast
# transient, which the oracle was not at 0.05 s (`PL-B1WW`).
#
# **What the coarse oracle cost, and why an eighth rather than a half.** At
# 0.05 s the oracle was converged at held default settings and nowhere else. So
# on the transients that set every gate's worst case, the gate was reporting the
# oracle's own error. The table below splits the worst gate number at that time into
# three parts, at the instant and in the state where it occurred (desflurane,
# ventilator start, alveolar, 307.4 s), against a converged oracle at 0.0015625 s:
#
#     what the gate reported  |shipped(0.1) - oracle(0.05)|   7.7470e-13
#     the oracle's own error  |oracle(0.05) - converged|      7.7562e-13
#     the shipped step's own  |shipped(0.1) - converged|      9.1593e-16
#
# 99.88% of it was the oracle's error. Across the trajectories that set the
# tolerance, the oracle's share ran from 86% to 99.8%. Each halving of the oracle
# step divides the oracle's term by about 2^4, which is the signature of RK4
# truncation rather than of rounding. Under the 0.05 s oracle, the ventilator
# start reported the largest figure. As the oracle step goes from 0.05 to 0.025,
# 0.0125 and 0.00625 s, the gate's maximum on that trajectory falls through
# 7.7377e-13, 4.7351e-14, 1.3906e-14 and 1.2490e-14. It stops falling at 0.0125 s
# because nothing of the oracle's error is left to remove: what remains is the
# shipped step's own rounding. That knee is what sets this constant. 0.025 s was measured and
# rejected, because the oracle still contributes about two thirds of the number
# there.
#
# **What it costs, measured rather than estimated (`PL-B1WW`).** The earlier
# argument against refining said that RK4 time rises fourfold per halving. That
# is true of the RK4 term alone, and it was never measured against the
# deliverable:
#
#     this file, serially                39.5 s -> 79.2 s     (+39.7 s, 2.0x)
#     whole suite, as CI invokes it      43.0 s -> 55.5 s     (+12.5 s, 1.29x)
#
# The file does not take four times as long, because about 25 s of it is not
# oracle work. The suite absorbs even the doubling because
# `.github/workflows/quality.yml` runs `pytest -n $(cpu_count * 2) --dist worksteal`,
# and this module's tests are parametrized across workers. So this module was
# never the critical path on its own. The suite figures are the mean of two paired
# runs on a 4-CPU container at `-n 8`, with the cold first runs discarded.
#
# **Richardson extrapolation was measured and rejected.** It carries two RK4
# streams at h/2 and h/4 and combines them as (16*y_fine - y_coarse)/15. That
# gives a fifth-order oracle at 3x the current oracle cost, against 4x for this
# plain refinement, and it reaches the same lowest value: 1.6029e-14 against
# 1.5786e-14. Both figures are the shipped step's own residual rather than either
# oracle's truncation. Richardson extrapolation would save about a quarter of the
# oracle term, roughly 3 s of CI. The price would be a new mechanism inside the
# one component of this module whose value is that a reviewer can audit it line by
# line against a textbook. Speeding up `_rk4_step` was rejected for the same
# reason. Both are recorded here so that neither is re-derived.
#
# **What moved with it.** The rule in `_oracle_step_for` and this constant have
# to move together, or `test_lockstep_oracle_step_matches_the_pinned_one` fails.
# 0.1 / 8.0 is exactly 0.0125, because division by a power of two is exact in
# binary floating point. `PINNED_REFERENCE_STATES` did *not* need re-pinning: all
# nine pass unchanged under this module's own `rel=1e-9, abs=1e-15`, measured at
# 0.0125 s and again at 0.003125 s. `EXACT_STEP_ORACLE_TOLERANCE` came down with
# it, and that tolerance is now bounded by platform variation rather than by the
# oracle.
ORACLE_STEP_S = 0.0125

# Retired here (`PL-X9KD`): `SPLITTING_ERROR_BOUND_PER_STEP_SECOND = 2.8e-3`,
# `EXACT_SOLUTION_FLOOR = 1e-12`, and the four tests they served. They are
# recorded here rather than simply deleted. "The gate was loosened until it
# passed" and "the gate measured a quantity that no longer exists" look identical
# in a diff, and they are opposite things.
#
# The bound was a first-order splitting coefficient C in an error C·Δt. It was set
# at 1.22 times a measured worst of 2.29e-3 s^-1. The shipped step is now one
# matrix exponential of the whole coupled system, so there is no C. Re-expressed
# as a coefficient, the worst residual reachable anywhere is 7.747e-12 s^-1, and
# the bound sat 3.61e8 times above it. Its three consumers passed with 8.6 to
# 9.7 orders of magnitude of slack, which is not a gate.
#
# `EXACT_SOLUTION_FLOOR` was an escape hatch, the early return that
# `test_shipped_split_error_is_first_order_in_step` took when the error fell below
# what a split could produce. Measured, it fired on all nine parametrizations, so
# that test asserted nothing. It was worse than nothing: with the early return
# removed, all nine would *fail*. The measured step ratios run from 0.147 to 18.6,
# and the assertion required every one of them to lie in (1.9, 2.1). The test's own
# margin to the floor was 1.29x on desflurane's ventilator start. A platform that
# accumulated slightly more rounding would therefore have stopped taking the early
# return and started failing on a true property. The test spent about 25 s of the
# file's 56 s doing that.
#
# What replaced each of them, and what needed a new gate rather than a
# replacement:
#
#   - `test_shipped_split_is_bounded_across_the_settings_envelope` and
#     `test_shipped_split_is_bounded_across_setting_changes` are reproduced
#     exactly by `test_exact_step_matches_the_independent_solution_everywhere`.
#     It uses the same trajectories and the same driver, and it gives the same
#     measured residuals to every printed digit, at the same instants and in the
#     same states. Its tolerance is 6.45 times the worst residual rather than
#     3.61e8 times it. Those two tests were simply deleted: nothing needed to
#     transfer, because nothing was lost.
#   - `test_shipped_split_error_is_first_order_in_step` varied the step over
#     trajectories that *turn*. Its nearest replacement
#     (`test_the_disagreement_does_not_shrink_with_the_step`) did not. That is a
#     real property, not a decorative one: on a turning trajectory the coarsest
#     step is the worst by 10 to 35 times, the opposite of what happens at held
#     settings. The step test now runs the setting-change trajectories too, which
#     is where that property went.
#   - `test_shipped_split_matches_independent_solution` was the only test in the
#     repository that drove the shipped solver past 900 s. That test could not be
#     dropped as cleanup. At 3600 s the residual is two to sixteen times its 600 s
#     value, it sits at the endpoint rather than in a transient, and it is in
#     muscle. Muscle is never the worst state on any of the five surviving
#     trajectories. Retiring the test as written would also have orphaned the
#     3600 s entries of `PINNED_REFERENCE_STATES`, leaving them constraining only
#     the oracle. It survives as
#     `test_the_shipped_step_reaches_the_pinned_reference_horizons`, under
#     `HELD_RUN_ROUNDING_BOUND` below.
#
# The amount by which the shipped exact step may disagree with the oracle. It is
# an absolute difference in any of the six fractions, anywhere on any gate
# trajectory (`PL-GS5X`).
#
# **It is not the retired splitting bound rescaled, and it is a different kind
# of quantity.** That bound was a first-order coefficient C in an error C·Δt,
# which describes a systematic method error that shrinks as the step shrinks. The
# shipped step is now one matrix exponential of the whole coupled system, which
# is the *exact* solution of these equations over the interval. So no method
# error is left to have an order. The residual measured here is floating-point
# accumulation in two independently written solutions. It grows with the
# *number* of steps, and therefore gets slightly worse as the step gets smaller.
# Bounding a coefficient would state the opposite of what is true, so this bound
# is absolute.
#
# **Derived, not inherited.** `PL-P0BB` forbids reusing the ~2e-15 figure, which
# described the old mechanism's accounting residual. The figures below were
# re-measured on 2026-09-07 under the refined `ORACLE_STEP_S`, over every agent
# and every trajectory in `ALL_GATE_TRAJECTORIES`. Each is the worst over the
# whole trajectory rather than at the endpoints, at the shipped 0.1 s step.
# Desflurane is the worst agent on every row:
#
#     ordinary use                            1.5786e-14  (vessel rich)
#     envelope corner, held                   1.5377e-14  (vessel rich)
#     ventilator start                        1.3906e-14  (vessel rich)
#     reference point, held                   1.3427e-14  (vessel rich)
#     unperfused load then dial off           8.7985e-15  (alveolar)
#
# **Note what the trajectories no longer do: separate.** Under the old 0.05 s
# oracle, these figures spread over two orders of magnitude, and the violent
# trajectories carried the large numbers. They now sit within a factor of 1.8 of
# each other. That is because what is left after the oracle's truncation is
# removed is rounding. Rounding is set by the number of steps taken, which is
# 6 000 for each of them, rather than by how far the settings move. A trajectory
# here earns its place by the domain it covers, not by the size of the residual
# it produces.
#
# `test_the_disagreement_does_not_shrink_with_the_step` also drives the same
# trajectories at 0.05 s and 0.025 s. Those runs are where the largest residual
# in this module now occurs, exactly as rounding predicts. The worst anywhere is
# **5.8870e-14**, for desflurane on the ventilator start at the 0.025 s step, in
# the circuit fraction. That is the figure this bound is set against.
#
# **The margin is set by platform variation, not by that figure.** This bound
# constrains accumulated rounding, which is not reproducible between machines. A
# different libm `exp`, or a compiler contracting a multiply and an add into one
# FMA, moves the last bits of both solutions. The proxy used for how far they can
# move is what the *shipped* solution alone does when the same interval is
# subdivided differently. `HELD_RUN_ROUNDING_BOUND` uses the same proxy. The
# comparison runs the same exact propagator over the same phases at 0.1, 0.05 and
# 0.025 s, with no oracle involved, so every difference is the shipped side's own
# accumulation. Measured over all three pairings, all six fractions, every agent
# and every gate trajectory, and sampled at 0.1 s, the largest difference is
# **1.0691e-13**. It is for desflurane on the ventilator start, in the circuit
# fraction at 284.6 s.
#
# That spread is the binding constraint. It is larger than the residual it
# accompanies, which is why this bound is not set tighter. 4e-13 clears the
# worst observed residual by 6.8 times and the subdivision spread by 3.7 times.
# `HELD_RUN_ROUNDING_BOUND` clears its own spread by 3.2 times, so the two bounds
# are now sized by the same rule. The split that the exact step replaced had a
# worst of 2.29e-4 over the same domain at this step. The exact step is nine
# orders of magnitude closer to the independent solution than that, and this
# bound is nine orders below the error of any method that is not exact. The bound
# therefore still fails the moment method error returns, which is the only thing
# it is here to catch.
#
# **What this bound could not do until `PL-B1WW`.** It was 5e-12, set at 6.5
# times a worst of 7.7e-13. That worst was itself 86% to 99.8% the oracle's own
# RK4 truncation. So the bound sat about 320 times above the shipped step's actual
# residual, and a regression that made the exact step a hundred times worse would
# have passed it. Refining the oracle is what makes the measured quantity and the
# quantity of interest the same thing. Tightening this bound is what actually
# delivers the sensitivity: refining the oracle alone, with this constant left at
# 5e-12, would have bought none of it.
#
# This was measured rather than argued, by degrading the shipped step on purpose
# and checking whether each bound notices. Scaling every shipped state by
# (1 + 1e-11) is a relative degradation, which is what a solver that had stopped
# being exact would produce. It takes the worst gate figure to 1.8084e-12. The
# old 5e-12 bound passes that silently. This bound fails it. That is the whole of
# what `PL-B1WW` bought, stated as the smallest defect the gate can now see. A
# 2e-12 relative degradation still passes. So the gate is not sensitive to
# arbitrary degradation, and it is not meant to be: the limit of its sensitivity
# is set by platform variation, as described above.
#
# **The residual is rounding, not truncation, which is why an absolute bound is
# the right shape. The evidence is the absence of a direction, not the absence of
# movement.** Refining the oracle a further eightfold, from 0.0125 s to
# 0.0015625 s, moves the desflurane figures in the table above by at most 11%,
# and it moves them *both ways*: 0.956, 1.008, 0.925, 1.055, 0.895 as ratios of
# the 0.0125 s figure to the 0.0015625 s one, in table order. Truncation cannot
# do that. A residual that still carries RK4 truncation falls by about 2^4 per
# halving and never rises. That is exactly what the 0.05 s oracle did: refining
# it dropped the ventilator start 68-fold, in one direction, on every trajectory
# that turns. What is left at 0.0125 s shifts up or down by a few percent as the
# oracle's own rounding path changes. That is the signature of two independently
# accumulated rounding errors being subtracted. The absence of a one-way fall is
# the check that the oracle is converged everywhere this module drives it.
EXACT_STEP_ORACLE_TOLERANCE = 4e-13

# How much the shipped step alone may accumulate over a run at held settings. It
# is an absolute difference in any of the six fractions at the horizon
# (`PL-X9KD`). It is used by
# `test_the_shipped_step_reaches_the_pinned_reference_horizons`.
#
# **Why this is a second constant rather than a reuse of the tolerance above.**
# The two constants used to measure different quantities. The trajectory gates
# saw the shipped step and the oracle together, and an hour at held settings was
# the one place in this module where the oracle was converged. Since `PL-B1WW`
# refined `ORACLE_STEP_S`, the oracle is converged everywhere. Both constants now
# bound the same thing, the shipped step's own accumulated rounding, and what
# separates them is the run length. Rounding is added once per step. An hour at
# 0.1 s is 36 000 steps, against 6 000 for a gate trajectory. Accordingly, on the
# subdivision spread that sets both margins, the measurements below come out
# about twice the trajectory gates' figures. Folding the two into one constant
# would give the 600 s gates the hour's headroom and throw away the sensitivity
# that this separation buys.
#
# **The derivation.** These figures were re-measured on 2026-09-07 at the
# reference operating point. Each is taken at the endpoint of a horizon in
# `HORIZONS_S`, as the worst over the six fractions. (`PL-D3XX`: the v0.4.7
# venous-pool change moved every figure in the table this replaces, and none of
# them had been re-derived.)
#
#                     60 s                600 s                   3600 s
#     sevoflurane     5.6899e-16 circuit  2.7131e-15 circuit      1.5056e-14 muscle
#     isoflurane      2.4633e-16 circuit  3.9864e-15 vessel rich  1.8395e-14 muscle
#     desflurane      3.5041e-16 circuit  1.3427e-14 vessel rich  7.1637e-14 muscle
#
# The worst is 7.1637e-14, and this bound allows 14.0 times that. The margin is
# set from how far the shipped step's own rounding path can be moved, rather
# than from that figure plus a guess. The identical 3600 s interval was also
# solved at 0.05 s and at 0.025 s instead of 0.1 s. That is the same exact
# propagator over the same interval, subdivided differently, so every difference
# is the shipped side's own accumulation. The answer moves by up to 2.1696e-13,
# taking the maximum over every pair of those three steps, all six fractions and
# all three agents. Isoflurane is the worst, in muscle; desflurane reaches
# 1.4644e-13 and sevoflurane 9.8130e-14. This bound clears that spread by 4.6
# times, which is the room a different libm or a contracted multiply-add needs.
# It does not clear a method error: under any method with an order, the error at
# the coarsest supported step is orders of magnitude above this bound.
#
# The subdivision spread is the larger of the two figures, and the margin is
# deliberately taken over it. A platform that rounds differently moves the
# shipped solution by about as much as re-subdividing the interval does, and
# nothing about the pinned oracle constrains that.
#
# Note the growth signature, because it is what the gate detects. The residual
# grows with run length at a fixed step, monotonically for every agent across the
# three horizons above. It also grows as the step *shrinks*. The worst state
# moves from the circuit to muscle as the slow compartment fills. That is
# rounding accumulating once per step, not truncation. A residual that started
# shrinking with the step would be method error returning, and
# `test_the_disagreement_does_not_shrink_with_the_step` is the test that looks
# for it.
HELD_RUN_ROUNDING_BOUND = 1e-12

# How far apart two compartments may be while the shipped step still inverts
# which of them is displayed as higher. The interface invites an ordinal reading:
# the circuit leads the alveoli, which lead the tissues. That reading is
# misleading only if an inversion happens between two readouts that a reader
# would see as separated. So this constant bounds the gap at which an inversion
# can occur, rather than forbidding inversions outright.
#
# **This value is derived from the absolute bound rather than fitted, and the
# previous value was not.** It used to be 3.0 counts, set at 1.7 times a measured
# 1.73 counts under the operator split. Its arithmetic sanity check was itself
# wrong: it added "half a count of rounding each" on top of two displacements.
# Rounding cannot contribute. The shipped `format_percent` is monotone
# non-decreasing, so it can never produce an ordering opposite to the raw one.
# `test_format_percent_preserves_order` in `tests/unit/test_formatting.py` checks
# that, on the shipped function and across its below-resolution branch
# (`PL-0M7K`). The correct figure for that sanity check was 5.6 counts, not 6.6.
#
# Given monotonicity, the bound follows by arithmetic rather than by measurement.
# Write e = reference - shipped. An inversion of (left, right) needs
# shipped[left] > shipped[right] and reference[left] < reference[right]. By
# monotonicity, both inequalities hold on the raw values too. The gap the test
# measures is then
#
#     reference[right] - reference[left]
#         = (shipped[right] - shipped[left]) + (e[right] - e[left])
#         < e[right] - e[left]  <=  |e[right]| + |e[left]|
#         <= 2 * EXACT_STEP_ORACLE_TOLERANCE
#
# because the first bracket is negative and the gate above bounds every |e|.
# Converting to counts of the last displayed digit gives the expression below:
# 1.0e-7 counts. Measured, the widest gap that any inversion occupies is 0.0,
# because there are no inversions at all over 1 485 000 pair comparisons. The
# largest pairwise differential |e[left] - e[right]| anywhere is 1.104e-12 in
# fraction, or 1.104e-8 counts, which is 9.1 times less than this bound. An
# error-injection sweep confirms the shape: displacing the states by ±ε produces
# a widest inverted gap that approaches 2ε from below at every scale and never
# exceeds it.
#
# **What this test is for, now that the bound follows from the one above.** It
# is not a second, independent bound on the solver. If the absolute gate passes
# and `format_percent` is monotone, this test cannot fail. When the formatter
# stops being monotone, the unit test named above is what fails first. What this
# test adds is the measurement that `docs/MODEL.md` quotes: the readings the
# shipped formatter gives on real trajectories, compared pair by pair. Until
# `PL-0M7K` this test used a test-local `round()` instead, so it could not see
# the formatter at all. The gate keeps its gap-threshold shape rather than
# asserting zero inversions. Crossings really are sampled at gaps smaller than
# the differential: the smallest nonzero true gap seen is 2.354e-15 in fraction,
# below the 1.104e-12 differential. So an inversion is arithmetically possible
# there, and whether a zero-inversion assertion passed would depend on the
# platform.
MAX_INVERTED_GAP_IN_DISPLAY_COUNTS = (
    2.0 * EXACT_STEP_ORACLE_TOLERANCE * 100.0 * 10.0**CONCENTRATION_DISPLAY_DECIMALS
)

# Names this module is allowed to import from `anesthesia_sim`. They are the
# parameter loaders the oracle needs, the system under test, the module that
# declares the input domain this gate measures over, and the view module whose
# displayed resolution and shipped step every figure here is quoted at.
#
# `supported_ranges` and `dashboard_frame` are on this list for two assertions.
# One checks that the limits restated above are still the model's. The other
# checks that the resolution and step they are quoted at are still the
# interface's. Neither import changes the rule that the list enforces: what must
# never be imported is a solver, because comparing the implementation against
# itself proves nothing. A module of constants is not a solver. The oracle itself
# (`_build_derivative`) still uses only the parameter loaders.
#
# `load_reference_circle_system_parameters` is the third loader. It was added with
# the machine parameter file (`PL-4YY1`) and is used by one assertion, which
# checks that the operating point restated above is still the shipped one. It
# reads a JSON document and solves nothing, which is the property this list is
# about.
#
# `SimulationStep` is the type that the system under test accepts for its step
# (`PL-0GJC`). It checks a number against the supported range and solves
# nothing, so it has the property too.
#
# `FreshGasFlow`, `AlveolarVentilation` and `CardiacOutput` are the types that the
# system under test accepts for its three flows (`PL-0YYV`). Each has the same
# property: it checks a number against the supported range and solves nothing.
# The oracle's own operating points stay plain floats. The types are built only
# where `_apply_operating_point` hands a point to the shipped system.
#
# `Percent` is the type that the system under test accepts for its vaporizer dial.
# Since `PL-4R3W` it checks a number against 0 to 100 and solves nothing, so it
# has the property as well. It is built in the same one place.
#
# `Fraction` is the type that `format_percent` takes, and since `PL-0M7K` the
# displayed ordering is read through `format_percent`. It checks a number
# against 0 to 1 and solves nothing. `_displayed_percent` is the one place where
# it is built.
ALLOWED_PACKAGE_IMPORTS = frozenset(
    {
        "AlveolarVentilation",
        "CardiacOutput",
        "Fraction",
        "FreshGasFlow",
        "Percent",
        "load_agent_parameters",
        "load_reference_adult_parameters",
        "load_reference_circle_system_parameters",
        "AgentUptakeSystem",
        "SimulationStep",
        "dashboard_frame",
        "formatting",
        "supported_ranges",
    }
)

# State order for every vector in this module:
# (F_C circuit, F_A alveolar, F_v mixed venous, F_vrg, F_mus, F_fat).
STATE_LABELS = ("circuit", "alveolar", "mixed venous", "vessel rich", "muscle", "fat")

# The independent solution itself, pinned so that a later edit to the oracle
# or to a parameter file cannot quietly move the reference that the shipped core
# is measured against. A failure here is not a failure of the core. It means that
# the oracle or its inputs changed, and the new values must be re-derived and
# reviewed before they are pinned again.
#
# These values were re-derived on 2026-09-07 (`PL-8ZJQ`) from the oracle, not
# from the shipped solver, after `venous_pool_volume_l` moved from 1.0 L to Davis
# and Mapleson's 1.222 L. That is the case this pin exists for: a deliberate
# parameter change fails all nine here first, and that failure forces the review.
# The largest movement is 8.3e-4 relative, in the mixed-venous state.
# That is where a venous-pool change should show, and nowhere else.
PINNED_REFERENCE_STATES: dict[tuple[str, float], tuple[float, ...]] = {
    ("desflurane", 60.0): (
        2.028404136125e-02,
        9.281420915853e-03,
        7.876663535405e-04,
        1.712991053952e-03,
        4.697597715896e-05,
        2.667678019825e-06,
    ),
    ("desflurane", 600.0): (
        4.315734014009e-02,
        3.701331546615e-02,
        2.624076126831e-02,
        3.419351995732e-02,
        2.964053373816e-03,
        1.752741904675e-04,
    ),
    ("desflurane", 3600.0): (
        4.644102032938e-02,
        4.291476330144e-02,
        3.624964893542e-02,
        4.282507191783e-02,
        2.017390576721e-02,
        1.529418023790e-03,
    ),
    ("isoflurane", 60.0): (
        1.979040100781e-02,
        6.424722270858e-03,
        4.911457693498e-04,
        1.043825468899e-03,
        2.349820689350e-05,
        1.148589299382e-06,
    ),
    ("isoflurane", 600.0): (
        3.617208687621e-02,
        2.299235500822e-02,
        1.518165093660e-02,
        1.999176551660e-02,
        1.209506966652e-03,
        6.075357967569e-05,
    ),
    ("isoflurane", 3600.0): (
        4.059930022549e-02,
        3.124202237121e-02,
        2.550585450351e-02,
        3.109232234677e-02,
        1.031870464760e-02,
        6.112932730743e-04,
    ),
    ("sevoflurane", 60.0): (
        2.012553561074e-02,
        8.326553885664e-03,
        5.694784215021e-04,
        1.234707386216e-03,
        2.706958058365e-05,
        1.452557155924e-06,
    ),
    ("sevoflurane", 600.0): (
        4.021622895670e-02,
        3.116010711424e-02,
        2.067189318209e-02,
        2.720937451485e-02,
        1.572056775422e-03,
        8.654143975784e-05,
    ),
    ("sevoflurane", 3600.0): (
        4.421751882173e-02,
        3.846721653957e-02,
        3.142276440079e-02,
        3.835095586380e-02,
        1.246988460300e-02,
        8.038704080644e-04,
    ),
}

Derivative = Callable[[list[float]], list[float]]


def _build_derivative(agent_id: str, point: OperatingPoint) -> Derivative:
    """Build dy/dt for the `docs/MODEL.md` system, from the specification.

    Only the parameter loaders are reused. Every equation below is written
    out from `docs/MODEL.md` § "Governing equations" rather than called from
    the implementation under test. That is what makes agreement between the
    two solutions count as evidence.
    """

    agent = load_agent_parameters(agent_id)
    patient = load_reference_adult_parameters()
    blood_gas = agent.blood_gas_partition_coefficient

    tissues = (
        (
            patient.vessel_rich_volume_l,
            patient.vessel_rich_perfusion_fraction,
            agent.vessel_rich_tissue_gas_partition_coefficient / blood_gas,
        ),
        (
            patient.muscle_volume_l,
            patient.muscle_perfusion_fraction,
            agent.muscle_tissue_gas_partition_coefficient / blood_gas,
        ),
        (
            patient.fat_volume_l,
            patient.fat_perfusion_fraction,
            agent.fat_tissue_gas_partition_coefficient / blood_gas,
        ),
    )

    alveolar_volume_l = patient.alveolar_gas_volume_l
    venous_volume_l = patient.venous_pool_volume_l

    fresh_gas_l_s = point.fresh_gas_flow_l_min / SECONDS_PER_MINUTE
    ventilation_l_s = point.alveolar_ventilation_l_min / SECONDS_PER_MINUTE
    cardiac_output_l_s = point.cardiac_output_l_min / SECONDS_PER_MINUTE
    delivered_fraction = point.delivered_percent / PERCENT_PER_UNIT_FRACTION

    def derivative(state: list[float]) -> list[float]:
        circuit, alveolar, venous = state[0], state[1], state[2]
        tissue_fractions = state[3:]

        # Circuit: fresh-gas exchange plus ventilatory exchange with alveoli.
        d_circuit = fresh_gas_l_s / CIRCUIT_VOLUME_L * (delivered_fraction - circuit) - (
            ventilation_l_s / CIRCUIT_VOLUME_L * (circuit - alveolar)
        )

        # Alveoli: ventilation in, pulmonary uptake out.
        d_alveolar = (
            ventilation_l_s * (circuit - alveolar)
            - cardiac_output_l_s * blood_gas * (alveolar - venous)
        ) / alveolar_volume_l

        # Tissues: perfusion-limited, driven by the arterial fraction, which
        # equals the alveolar fraction.
        d_tissues: list[float] = []
        tissue_outflow = 0.0

        for (volume_l, perfusion, tissue_blood), fraction in zip(
            tissues, tissue_fractions, strict=True
        ):
            flow_l_s = cardiac_output_l_s * perfusion
            d_tissues.append(flow_l_s / (volume_l * tissue_blood) * (alveolar - fraction))
            tissue_outflow += flow_l_s * fraction

        # Venous pool: flow-weighted tissue return, mixed at cardiac output.
        d_venous = (tissue_outflow - cardiac_output_l_s * venous) / venous_volume_l

        return [d_circuit, d_alveolar, d_venous, *d_tissues]

    return derivative


def _rk4_step(derivative: Derivative, state: list[float], step_s: float) -> list[float]:
    """One step of classical fourth-order Runge-Kutta."""

    first = derivative(state)
    second = derivative([a + step_s / 2 * b for a, b in zip(state, first, strict=True)])
    third = derivative([a + step_s / 2 * b for a, b in zip(state, second, strict=True)])
    fourth = derivative([a + step_s * b for a, b in zip(state, third, strict=True)])

    return [
        a + step_s / 6 * (b + 2 * c + 2 * d + e)
        for a, b, c, d, e in zip(state, first, second, third, fourth, strict=True)
    ]


def _integrate_rk4(derivative: Derivative, duration_s: float, step_s: float) -> tuple[float, ...]:
    """Integrate from an empty system with classical fourth-order RK."""

    state = [0.0] * 6

    for _ in range(round(duration_s / step_s)):
        state = _rk4_step(derivative, state, step_s)

    return tuple(state)


@cache
def _reference_state(agent_id: str, duration_s: float, point: OperatingPoint) -> tuple[float, ...]:
    """Return the independent solution, computed once per (agent, horizon, point)."""

    return _integrate_rk4(_build_derivative(agent_id, point), duration_s, ORACLE_STEP_S)


def _empty_shipped_system(agent_id: str) -> AgentUptakeSystem:
    """The implementation under test, empty and at its own defaults."""

    system = AgentUptakeSystem.for_agent(agent_id)
    system.circuit.set_circuit_volume(CIRCUIT_VOLUME_L)

    return system


def _apply_operating_point(system: AgentUptakeSystem, point: OperatingPoint) -> None:
    """Move every slider to `point`, leaving compartment contents untouched.

    This is what the interface does when a slider moves mid-run, and it is
    the only thing that happens at a phase boundary: the settings change,
    the state does not.
    """

    system.set_fresh_gas_flow(FreshGasFlow(point.fresh_gas_flow_l_min))
    system.set_alveolar_ventilation(AlveolarVentilation(point.alveolar_ventilation_l_min))
    system.set_cardiac_output(CardiacOutput(point.cardiac_output_l_min))
    system.set_delivered_concentration_percent(Percent(point.delivered_percent))


def _shipped_system(agent_id: str, point: OperatingPoint) -> AgentUptakeSystem:
    """The implementation under test, configured at one operating point."""

    system = _empty_shipped_system(agent_id)
    _apply_operating_point(system, point)

    return system


def _shipped_states(system: AgentUptakeSystem) -> tuple[float, ...]:
    """Read the six displayed states, in STATE_LABELS order."""

    patient = system.patient

    return (
        system.circuit.inspired_partial_pressure_fraction,
        system.alveoli.partial_pressure_fraction,
        patient.mixed_venous_partial_pressure_fraction,
        patient.vessel_rich.partial_pressure_fraction,
        patient.muscle.partial_pressure_fraction,
        patient.fat.partial_pressure_fraction,
    )


def _run_shipped(
    agent_id: str, duration_s: float, step_s: float, point: OperatingPoint
) -> tuple[float, ...]:
    """Advance the implementation under test to the same simulated time."""

    system = _shipped_system(agent_id, point)

    for _ in range(round(duration_s / step_s)):
        system.advance(SimulationStep(step_s))

    return _shipped_states(system)


def _oracle_step_for(shipped_step_s: float) -> float:
    """An eighth of the step under test.

    The divisor has to meet two needs. Any divisor above one keeps the two
    solvers off a shared step size, so that agreement cannot be an artifact of
    them taking the same stride. A divisor of eight is what makes the oracle
    *converged* at every step this module drives. At the coarsest supported
    shipped step, 0.1 s, it puts the oracle at 0.0125 s, which is where
    refining the oracle stops changing what the gates report (`ORACLE_STEP_S`
    records the series of measurements). The rule was `/ 2` until `PL-B1WW`.
    That rule left the oracle at 0.05 s through transients that needed
    0.0125 s, so 86% to 99.8% of what the trajectory gates reported was the
    oracle's own RK4 truncation rather than the shipped step's error.

    The oracle step scales with the step under test rather than being a fixed
    0.0125 s. So the finer shipped steps in
    `test_the_disagreement_does_not_shrink_with_the_step` get a proportionally
    finer oracle, and the convergence argument still applies at all three.

    At the shipped 0.1 s step this returns `ORACLE_STEP_S`. A trajectory
    driven here and a pinned reference state above are therefore integrated
    identically, and `test_lockstep_oracle_step_matches_the_pinned_one` keeps
    that coincidence true. The two must move together, or that test fails.
    """

    return shipped_step_s / 8.0


def _worst_error_over_phases(
    agent_id: str, phases: Sequence[Phase], shipped_step_s: float = SHIPPED_STEP_S
) -> tuple[float, float, str]:
    """Return the largest disagreement anywhere in the trajectory.

    Both solutions are driven through the same phase list, and both apply a
    phase's settings at the same instant. The shipped system uses the setters
    that the interface calls, and the oracle rebuilds its derivative. The
    comparison therefore measures only the two solvers, not two different
    piecewise schedules.

    Sampling endpoints is not enough here, and neither is one held setting.
    Except at held default settings, the worst disagreement is always inside a
    transient: either the wash-in transient or one that a setting change
    starts. Stepping the two solutions in lockstep and taking the maximum costs
    nothing extra, because the RK4 integration is the expensive part and it
    happens either way.

    Until `PL-X9KD` this function returned `worst_error / shipped_step_s`, and
    a second wrapper multiplied the step back in for the callers that wanted
    the difference. That division gave the first-order coefficient C in an
    error C·Δt, which the exact step does not have. Dividing the exact step's
    residual by the step produces a number that varies with the step for no
    physical reason. The round trip was also not lossless: two of five sampled
    residuals came back a unit in the last place off. So once the last caller
    that wanted C was retired, the division was removed too.

    Returns (absolute error, simulated time of the worst disagreement, state label).
    """

    system = _empty_shipped_system(agent_id)
    reference = [0.0] * 6
    oracle_step_s = _oracle_step_for(shipped_step_s)
    oracle_steps_per_shipped_step = round(shipped_step_s / oracle_step_s)

    worst_error = 0.0
    worst_time_s = 0.0
    worst_label = STATE_LABELS[0]
    step_index = 0

    for phase in phases:
        _apply_operating_point(system, phase.point)
        derivative = _build_derivative(agent_id, phase.point)

        for _ in range(round(phase.duration_s / shipped_step_s)):
            system.advance(SimulationStep(shipped_step_s))

            for _ in range(oracle_steps_per_shipped_step):
                reference = _rk4_step(derivative, reference, oracle_step_s)

            step_index += 1
            error, label = _worst_state_error(_shipped_states(system), tuple(reference))

            if error > worst_error:
                worst_error = error
                worst_time_s = step_index * shipped_step_s
                worst_label = label

    return worst_error, worst_time_s, worst_label


def _worst_state_error(left: tuple[float, ...], right: tuple[float, ...]) -> tuple[float, str]:
    """Return the largest absolute difference and the state it is in."""

    differences = [abs(a - b) for a, b in zip(left, right, strict=True)]
    worst = max(differences)

    return worst, STATE_LABELS[differences.index(worst)]


@pytest.mark.parametrize(("agent_id", "duration_s"), sorted(PINNED_REFERENCE_STATES))
def test_independent_solution_matches_pinned_reference_states(
    agent_id: str, duration_s: float
) -> None:
    """The oracle and its parameter inputs are both unchanged.

    This test is also what lets the bounds below keep narrow margins. Any
    parameter revision fails here first and must be re-derived and reviewed,
    so no bound has to leave room for one.

    These states are the RK4 oracle's own solution, not the shipped solver's.
    That is what makes this a regression gate rather than a self-comparison,
    and re-pinning them from the shipped solver would destroy the gate.

    This docstring once said that `ORACLE_STEP_S` could not be refined without
    re-deriving all nine states. That was assumed rather than measured, and it
    is wrong (`PL-B1WW`): refining the oracle to 0.0125 s and again to
    0.003125 s leaves all nine passing unchanged. The tolerances are the
    reason. `rel=1e-9` on a fraction of order 0.05 allows 5e-11, and refining
    the oracle moves these states by less than 1e-12. The truncation being
    removed is small compared with the tolerance that a pinned regression gate
    must allow if a parameter revision is to be what trips it. This gate
    therefore constrains the parameters and the equations, which is its job,
    and does not constrain the oracle's step.
    """

    assert _reference_state(agent_id, duration_s, _default_operating_point()) == pytest.approx(
        PINNED_REFERENCE_STATES[(agent_id, duration_s)], rel=1e-9, abs=1e-15
    )


@pytest.mark.parametrize("agent_id", AGENT_IDS)
@pytest.mark.parametrize("duration_s", HORIZONS_S)
def test_the_shipped_step_reaches_the_pinned_reference_horizons(
    agent_id: str, duration_s: float
) -> None:
    """The shipped step still lands where the pinned states say it should.

    This is the check that mass balance cannot make: a wrong transfer rate
    leaves the accounting residual untouched but moves these six numbers.

    It is also the only gate here that drives the shipped solver for a full
    hour. Every gate in this module now measures the shipped step's own
    residual. That is because `PL-B1WW` refined `ORACLE_STEP_S`, so the oracle
    is now converged on the transients as well as at held settings. What
    distinguishes this gate is no longer the quantity but the run length. The
    disagreement is rounding accumulated once per step, so it keeps growing
    for as long as the run does. By 3600 s it is about five times its 600 s
    value, for all three agents. None of the trajectory gates can see that
    growth, because they top out at 900 s and take a maximum over a transient.
    By the endpoint the worst state is muscle, which is never the worst state
    on any of the five gate trajectories.

    Sampling the endpoint rather than the whole run is right for the same
    reason: at 3600 s the maximum *is* at the endpoint.

    Retiring this test's predecessor without replacing it would also have
    orphaned the 3600 s entries of `PINNED_REFERENCE_STATES`. The 60 s and
    600 s entries stay tied to the shipped solver through the
    "reference point, held" trajectory, whose inline oracle is bit-identical
    to `_reference_state` at those horizons. Only this test ties the shipped
    solver to the 3600 s entries.
    """

    point = _default_operating_point()
    error, state_label = _worst_state_error(
        _run_shipped(agent_id, duration_s, SHIPPED_STEP_S, point),
        _reference_state(agent_id, duration_s, point),
    )

    assert error <= HELD_RUN_ROUNDING_BOUND, (
        f"{agent_id} at {duration_s:.0f} s diverges from the independent "
        f"solution by {error:.3e} in the {state_label} fraction, above the "
        f"{HELD_RUN_ROUNDING_BOUND:.3e} allowed. The oracle is converged at "
        f"{ORACLE_STEP_S} s, so this residual is the shipped "
        "step's own accumulated rounding and not the oracle's truncation: "
        "exceeding it means the shipped step has stopped solving these "
        "equations exactly, or has started accumulating rounding faster than "
        "once per step."
    )


@pytest.mark.parametrize("agent_id", AGENT_IDS)
@pytest.mark.parametrize(
    ("trajectory_name", "build_phases"),
    ALL_GATE_TRAJECTORIES,
    ids=[name for name, _ in ALL_GATE_TRAJECTORIES],
)
def test_exact_step_matches_the_independent_solution_everywhere(
    agent_id: str, trajectory_name: str, build_phases: Callable[[str], tuple[Phase, ...]]
) -> None:
    """The shipped step is the solution, not an approximation of it (`PL-GS5X`).

    This test replaced two gates that bounded a first-order splitting
    coefficient over the same trajectories. Their bound was eight orders of
    magnitude looser than what the exact step achieves. They still passed and
    still said something true. But a gate that loose cannot tell an exact
    propagator from a merely good approximation of one. So it could not detect
    the regression that matters here, which is any return of method error at
    all. `PL-X9KD` retired those gates once this test had been measured to
    reproduce them exactly: the same trajectories, the same driver, and the
    same residuals to every printed digit, at the same instants and in the
    same states.

    The test covers every agent and every gate trajectory. It takes the
    maximum over the whole run rather than at the endpoint, because outside
    held default settings the worst disagreement is always inside a transient.
    This test cannot see a full hour of held settings.
    `test_the_shipped_step_reaches_the_pinned_reference_horizons` covers that
    case.
    """

    error, at_s, state_label = _worst_error_over_phases(agent_id, build_phases(agent_id))

    assert error <= EXACT_STEP_ORACLE_TOLERANCE, (
        f"{agent_id} on the '{trajectory_name}' trajectory diverges from the "
        f"independent solution by {error:.3e} in the {state_label} fraction at "
        f"{at_s:.1f} s, above the exact step's tolerance of "
        f"{EXACT_STEP_ORACLE_TOLERANCE:.3e}. That tolerance bounds accumulated "
        "rounding between two solutions that agree exactly in exact "
        "arithmetic, so exceeding it means the shipped step has stopped being "
        "an exact solution of the governing equations rather than that it has "
        "become slightly less accurate."
    )


@pytest.mark.parametrize("agent_id", AGENT_IDS)
@pytest.mark.parametrize(
    ("trajectory_name", "build_phases"),
    (("reference point, held", _held_default_settings), *SETTING_CHANGE_SCENARIOS),
    ids=["reference point, held", *(name for name, _ in SETTING_CHANGE_SCENARIOS)],
)
def test_the_disagreement_does_not_shrink_with_the_step(
    agent_id: str, trajectory_name: str, build_phases: Callable[[str], tuple[Phase, ...]]
) -> None:
    """The tolerance above is met at every supported step, not just the shipped one.

    This test does what the retired
    `test_shipped_split_error_is_first_order_in_step` did for the split, but
    inverted. There, the claim was that halving the step halved the error, so
    bounding a coefficient at one step bounded it at all of them. Here, the
    claim is that the step size does not enter. An exact propagator solves the
    same interval exactly however it is subdivided, so the same absolute bound
    must be met at 0.1 s, 0.05 s and 0.025 s alike. A method error of any
    order fails this test by being visibly larger at the coarsest step and
    shrinking as the step shrinks.

    **The setting-change trajectories are here because the retired test ran
    them and this one did not (`PL-X9KD`).** That was the one property of the
    retired test that did not transfer, and it is not decorative. This gate
    drives the largest residual in the module, and it does so at the finest
    step rather than the coarsest.

    **What refining the oracle changed here (`PL-B1WW`).** This docstring used
    to say that held settings were worst at the finest step and turning
    trajectories worst at the coarsest, in opposite directions. Only the first
    half was ever about the shipped step. The second half was about the
    oracle. The oracle ran at half the step under test, so the coarsest
    pairing put it at 0.05 s through a transient that needed 0.0125 s. What
    fell away as the step shrank was the oracle's own truncation, not anything
    the shipped step did. With the oracle at an eighth of the step
    (`_oracle_step_for`), the results are the ones rounding predicts, across
    all nine parametrizations at 0.1, 0.05 and 0.025 s:

      - Eight of the nine are worst at the *finest* step, which takes four
        times as many steps and accumulates four times as much rounding:
        2.8935e-15, 1.3385e-14, 3.8337e-14 for sevoflurane at held settings;
        1.3906e-14, 5.0099e-14, 5.8870e-14 for desflurane's ventilator start,
        which is the largest residual anywhere in this module.
      - Desflurane at held settings is the ninth, and it runs the other way:
        1.3427e-14, 1.1213e-14, 7.8756e-15. It changes by a factor of 1.7,
        rather than by the 4 to 15 that the others grow by. When two
        independently accumulated rounding paths are subtracted, they do not
        have to line up. A factor that small, against a trend that large, is
        the difference shifting by chance and not the step buying accuracy.

    So the only claim this test makes is that no supported step exceeds the
    tolerance. It deliberately does not assert a direction. The ninth row is
    why that restraint is still right, even now that the other eight agree.
    """

    phases = build_phases(agent_id)
    errors = {
        step_s: _worst_error_over_phases(agent_id, phases, step_s)[0]
        for step_s in (0.1, 0.05, 0.025)
    }

    assert max(errors.values()) <= EXACT_STEP_ORACLE_TOLERANCE, (
        f"{agent_id} on the '{trajectory_name}' trajectory exceeds the exact "
        f"step's tolerance of {EXACT_STEP_ORACLE_TOLERANCE:.3e} at some "
        "supported step: "
        + ", ".join(f"{step_s} s -> {error:.3e}" for step_s, error in errors.items())
    )


def test_lockstep_oracle_step_matches_the_pinned_one() -> None:
    """A trajectory and a pinned reference state are integrated identically.

    `_oracle_step_for` takes an eighth of whatever step is under test. At the
    shipped step that is `ORACLE_STEP_S`, the step at which every pinned
    reference state was computed. If the two drifted apart, what the gates
    below measure would move while the pinned states stayed the same. So the
    coincidence is checked rather than only described.

    The equality is exact rather than approximate because 8 is a power of two.
    0.1 is not representable in binary, but dividing whatever double it rounds
    to by 8 only lowers the exponent, and the literal 0.0125 rounds to that
    same scaled value. A divisor of 10 here would need `pytest.approx`, which
    is worth knowing before changing this rule (`PL-B1WW`).
    """

    assert _oracle_step_for(SHIPPED_STEP_S) == ORACLE_STEP_S


def test_envelope_limits_match_the_supported_input_ranges() -> None:
    """The restated limits are still the model's own declared domain.

    Without this test, widening a supported range would silently leave the
    gate measuring only part of the domain it is taken to cover, and nothing
    would fail. That is exactly how the bound first came to be narrower than
    the settings a user could reach.

    The minimums are checked alongside the maximums because two gate
    trajectories hold a control at zero. `_ventilator_start` holds alveolar
    ventilation there, and `_unperfused_load_then_dial_off` holds cardiac
    output there. If a minimum were raised above zero, the supported-range
    types would reject those settings and the trajectory would raise an error.
    This test would fail too, and its message says which measurements to
    re-derive.

    Before PL-0MLQ the comparison was against `simulation_view`'s slider
    limits, because the interface was the only place a supported range was
    written down. `core/supported_ranges.py` now declares the ranges and
    rejects a setting outside them, so this is a check against the model
    itself. `test_the_sliders_span_the_supported_input_ranges`, in the view's
    own suite, checks that the interface offers exactly the same domain.
    """

    from anesthesia_sim.core import supported_ranges

    assert (
        MAX_FRESH_GAS_FLOW_L_MIN,
        MAX_ALVEOLAR_VENTILATION_L_MIN,
        MAX_CARDIAC_OUTPUT_L_MIN,
        MIN_FRESH_GAS_FLOW_L_MIN,
        MIN_ALVEOLAR_VENTILATION_L_MIN,
        MIN_CARDIAC_OUTPUT_L_MIN,
    ) == (
        supported_ranges.MAXIMUM_FRESH_GAS_FLOW_L_MIN,
        supported_ranges.MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
        supported_ranges.MAXIMUM_CARDIAC_OUTPUT_L_MIN,
        supported_ranges.MINIMUM_FRESH_GAS_FLOW_L_MIN,
        supported_ranges.MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
        supported_ranges.MINIMUM_CARDIAC_OUTPUT_L_MIN,
    ), (
        "the model's supported input ranges have changed; re-run the envelope "
        "and trajectory sweeps, update these constants and the bound, and "
        "re-derive the measured figures in docs/MODEL.md"
    )


def test_the_historical_operating_point_is_still_the_shipped_machine_s() -> None:
    """The restated circuit volume and flow are still what a run uses.

    `CIRCUIT_VOLUME_L` and `FRESH_GAS_FLOW_L_MIN` are restated above rather
    than imported, for the same reason as the envelope limits. The pinned
    reference states below are that operating point's solution. Binding the
    two constants to whatever the data file happens to say would let a changed
    file silently re-point this gate at a trajectory it never measured.

    What the restatement needs instead is this test: a statement that the two
    values are still the shipped values, which fails loudly when they stop
    being so. Until `PL-4YY1` there was nothing to compare them against. The
    shipped values were `BreathingCircuit` field defaults, and this file held
    a third unsourced copy of 6.0. They now live in
    `data/machines/reference_circle_system.json`, which is a source a test may
    read. The module docstring's independence rule permits the parameter
    loaders and forbids a solver, and this file is read by a parameter loader.

    A failure here does not mean the file is wrong. It means the shipped
    operating point moved and the pinned states below no longer describe it,
    so they have to be recomputed. The envelope check above gives the same
    instruction, for the same reason.
    """

    from anesthesia_sim.core.parameters import load_reference_circle_system_parameters

    machine = load_reference_circle_system_parameters()

    assert (CIRCUIT_VOLUME_L, FRESH_GAS_FLOW_L_MIN) == (
        machine.circuit_volume_l,
        machine.default_fresh_gas_flow_l_min,
    ), (
        "the shipped circuit volume or fresh gas flow has moved away from the "
        "operating point the pinned reference states below were computed at; "
        "recompute them, or restore the file"
    )


def test_displayed_resolution_and_shipped_step_match_the_interface() -> None:
    """The two interface facts that every figure here is quoted at are unchanged.

    The displayed resolution is checked because
    `test_displayed_ordering_reverses_only_at_a_crossing` measures a property
    of the displayed values and quotes its threshold in counts of the last
    displayed digit. Adding a decimal would change what those counts mean
    without changing anything that test reads. The shipped step is checked for
    two reasons. What this module measures is rounding accumulated once per
    step, and the step is when a setting change takes effect. `SHIPPED_STEP_S`
    explains both reasons, and records that neither is the
    coefficient-times-step reason this docstring used to give.

    The delivered-concentration minimum is checked here rather than with the
    supported ranges above, because it is the only control that the interface
    states in percent while the core's own guard is stated as a fraction.

    The resolution is read from `app/formatting.py`, which declares it. It is
    not read from `app/dashboard_frame.py`, which reads it for the delivered
    dial's slider position. Asserting against the importer would let this
    test pass on an accidental re-export after the declaration moved again
    (PL-WB0X). The minimum and the step are `app/dashboard_frame.py`'s own,
    since `PL-25KS` moved every claim the dashboard makes there.
    """

    from anesthesia_sim.app import dashboard_frame

    assert (
        MIN_DELIVERED_CONCENTRATION_PERCENT,
        CONCENTRATION_DISPLAY_DECIMALS,
        SHIPPED_STEP_S,
    ) == (
        dashboard_frame.MIN_DELIVERED_CONCENTRATION_PERCENT,
        formatting.CONCENTRATION_DISPLAY_DECIMALS,
        dashboard_frame.SIMULATION_STEP_S,
    ), (
        "the interface's displayed resolution or simulation step has changed; "
        "re-run the trajectory sweeps and re-derive the measured figures in "
        "docs/MODEL.md"
    )


def _displayed_percent(fraction: float) -> float:
    """The percent the interface shows for a fraction, read back as a number.

    The reading comes from the shipped `format_percent`, so a display path
    that reordered two values would be measured here (`PL-0M7K`). A reading of
    "<0.01%" means the value is above zero and below the resolution, so it is
    treated as half the resolution. `tests/unit/test_formatting.py` treats it
    the same way.
    """

    reading = formatting.format_percent(Fraction(fraction)).removesuffix("%")
    if reading.startswith("<"):
        return 10.0**-CONCENTRATION_DISPLAY_DECIMALS / 2.0
    return float(reading)


def _display_ordering(displayed: tuple[float, ...], left: int, right: int) -> int:
    """Which of two readouts a reader sees as higher: 1, -1, or 0 for equal."""

    return (displayed[left] > displayed[right]) - (displayed[left] < displayed[right])


@pytest.mark.parametrize("agent_id", AGENT_IDS)
@pytest.mark.parametrize(
    ("trajectory_name", "build_phases"),
    ALL_GATE_TRAJECTORIES,
    ids=[name for name, _ in ALL_GATE_TRAJECTORIES],
)
def test_displayed_ordering_reverses_only_at_a_crossing(
    agent_id: str, trajectory_name: str, build_phases: Callable[[str], tuple[Phase, ...]]
) -> None:
    """No reader is shown two compartments in an order the model does not have.

    The six readouts sit in one row to be read *ordinally*: the circuit leads
    the alveoli, which lead the tissues. An ordinal reading is corrupted only
    if the error flips which of two compartments is displayed as higher. An
    inversion while two compartments are crossing is not a defect, because
    their true gap is then smaller than what the display resolves, and the
    ordering is genuinely ambiguous. An inversion at a gap that a reader would
    call a gradient is a defect, and that is what this test forbids.

    **What this measures, now that its threshold is derived rather than
    fitted.** `MAX_INVERTED_GAP_IN_DISPLAY_COUNTS` follows from
    `EXACT_STEP_ORACLE_TOLERANCE` together with the monotonicity of the
    shipped `format_percent`, which `_displayed_percent` reads. So this test
    can fail only when
    `test_exact_step_matches_the_independent_solution_everywhere` fails or when
    the formatter stops being monotone. `test_format_percent_preserves_order`
    in `tests/unit/test_formatting.py` checks monotonicity over the
    formatter's whole domain. The derivation is written out where the constant
    is defined.

    Measured, there are no inversions at all: zero over 1 485 000 pair
    comparisons. The test keeps its gap-threshold shape rather than asserting
    zero inversions, because crossings really are sampled at gaps below the
    arithmetic bound. The smallest nonzero true gap seen is 2.354e-15 in
    fraction, below the 1.104e-12 worst pairwise differential. So an inversion
    is possible there, and a zero-inversion assertion would turn a different
    libm into a failure.

    `docs/MODEL.md` § "Displayed precision" quotes this test's count of pair
    comparisons. It cites the absolute gate and the unit test as the support
    for its claim that the interface need not mark anything about comparing
    two compartments.
    """

    system = _empty_shipped_system(agent_id)
    reference = [0.0] * 6
    oracle_step_s = _oracle_step_for(SHIPPED_STEP_S)
    resolution_percent = 10.0**-CONCENTRATION_DISPLAY_DECIMALS
    widest_inverted_gap_percent = 0.0
    worst: tuple[float, str, str] | None = None
    step_index = 0

    for phase in build_phases(agent_id):
        _apply_operating_point(system, phase.point)
        derivative = _build_derivative(agent_id, phase.point)

        for _ in range(round(phase.duration_s / SHIPPED_STEP_S)):
            system.advance(SimulationStep(SHIPPED_STEP_S))

            for _ in range(round(SHIPPED_STEP_S / oracle_step_s)):
                reference = _rk4_step(derivative, reference, oracle_step_s)

            step_index += 1
            shipped_displayed = tuple(_displayed_percent(v) for v in _shipped_states(system))
            reference_displayed = tuple(_displayed_percent(v) for v in reference)

            for left in range(len(STATE_LABELS)):
                for right in range(left + 1, len(STATE_LABELS)):
                    shipped_order = _display_ordering(shipped_displayed, left, right)
                    reference_order = _display_ordering(reference_displayed, left, right)

                    # A tie on one side and an order on the other means one
                    # side's display resolves a gap that the other rounds away.
                    # It does not tell a reader that the wrong compartment is
                    # higher.
                    if shipped_order != -reference_order or shipped_order == 0:
                        continue

                    gap_percent = abs(reference[left] - reference[right]) * 100.0

                    if gap_percent > widest_inverted_gap_percent:
                        widest_inverted_gap_percent = gap_percent
                        worst = (
                            step_index * SHIPPED_STEP_S,
                            STATE_LABELS[left],
                            STATE_LABELS[right],
                        )

    widest_in_counts = widest_inverted_gap_percent / resolution_percent
    # `worst` is None only when no inversion was found, and the threshold is
    # positive, so the fallback below can never reach a failure message.
    at_s, left_label, right_label = worst if worst is not None else (0.0, "?", "?")

    assert widest_in_counts <= MAX_INVERTED_GAP_IN_DISPLAY_COUNTS, (
        f"{agent_id} on the '{trajectory_name}' trajectory displays "
        f"{left_label} and {right_label} in the wrong order at {at_s:.1f} s "
        f"while their true gap is {widest_in_counts:.3e} counts of the last "
        f"displayed digit, above the "
        f"{MAX_INVERTED_GAP_IN_DISPLAY_COUNTS:.3e} allowed. The shipped step "
        f"is inverting a gradient rather than resolving a crossing. That gap "
        f"exceeds twice the absolute tolerance the neighbouring gate enforces, "
        f"so either that gate is also failing or format_percent has stopped "
        f"being monotone, which test_format_percent_preserves_order checks; "
        f"docs/MODEL.md's 'Displayed precision' quotes this test's count of "
        f"pair comparisons."
    )


#: Names of calls whose first argument, when it is a literal string, names a
#: module. Listing them lets the check judge a dynamic import that is written out
#: in full, rather than letting it through unchecked.
_DYNAMIC_IMPORTERS = frozenset({"import_module", "__import__"})

_PACKAGE_UNDER_TEST = "anesthesia_sim"


def _reached_by_importing_module(dotted: str) -> frozenset[str]:
    """Return what importing the whole module `dotted` reaches inside the package.

    Args:
        dotted: An absolute module name, as written at the import site.

    Returns:
        The one name that stands for what was reached, or nothing when
        `dotted` names some other package. `import anesthesia_sim.core.x`
        binds `anesthesia_sim` rather than `x`, so the dotted tail is not what
        the importer got hold of. The function therefore returns the
        subpackage, which is the coarsest true description of what the importer
        got. No subpackage is on
        `ALLOWED_PACKAGE_IMPORTS`, which lists names taken *from* a module. A
        bare `import anesthesia_sim` reaches the whole package and is reported
        under the package's own name.
    """
    segments = dotted.split(".")
    if segments[0] != _PACKAGE_UNDER_TEST:
        return frozenset()
    return frozenset({segments[1] if len(segments) > 1 else segments[0]})


def _dynamic_import_target(node: ast.Call) -> str | None:
    """The module a dynamic import names, when the source states it literally.

    Args:
        node: Any call expression.

    Returns:
        The module name, or `None` for anything that reading the source cannot
        settle. That covers a call to something else, a computed name, or a
        relative name, which cannot reach outside the tree doing the importing.
    """
    function = node.func
    if isinstance(function, ast.Attribute):
        called = function.attr
    elif isinstance(function, ast.Name):
        called = function.id
    else:
        return None
    if called not in _DYNAMIC_IMPORTERS or not node.args:
        return None
    first = node.args[0]
    if not (isinstance(first, ast.Constant) and isinstance(first.value, str)):
        return None
    return None if first.value.startswith(".") else first.value


def _package_imports(source: str) -> frozenset[str]:
    """Every name `source` takes from the package under test.

    Args:
        source: A module's text.

    Returns:
        One name per import site, in the same terms that
        `ALLOWED_PACKAGE_IMPORTS` uses. `from anesthesia_sim.x import y`
        contributes `y`, the name it binds. A form that imports a whole module
        contributes what `_reached_by_importing_module` describes. Imports of
        other packages contribute nothing, and so do relative imports, which
        cannot reach `anesthesia_sim` from `tests/`.
    """
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names |= _reached_by_importing_module(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level or node.module is None:
                continue
            if node.module.split(".")[0] == _PACKAGE_UNDER_TEST:
                names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.Call):
            target = _dynamic_import_target(node)
            if target is not None:
                names |= _reached_by_importing_module(target)
    return frozenset(names)


def test_oracle_imports_no_solver_from_core() -> None:
    """Keep this file a verification rather than a tautology.

    The oracle must re-derive the model from parameters alone. Importing any
    solver from `core/`, such as a compartment's exact update or the coupled
    step itself, would make this module compare the implementation against
    itself and pass no matter how wrong the dynamics were.

    The check covers the three forms that name their target in the source:
    `from anesthesia_sim... import x`, `import anesthesia_sim...`, and a
    dynamic import whose argument is a literal string. It does not cover a
    name assembled at runtime, which no reading of the AST can settle. That
    case is left to this docstring and to review. Reading only `ImportFrom`
    left the second and third forms unchecked (`PL-F5GN`), and the second
    assertion below exists to keep that gap from coming back.
    """

    imported_names = _package_imports(Path(__file__).read_text(encoding="utf-8"))

    assert imported_names <= ALLOWED_PACKAGE_IMPORTS, (
        "this module imports "
        f"{sorted(imported_names - ALLOWED_PACKAGE_IMPORTS)} from the package "
        "under test; the independent solution may use the parameter loaders "
        "only"
    )

    # Sources this file must never contain. The check reads this module's own
    # text, so the test asserts on these sources as strings rather than writing
    # one into the module. A real bypass added to prove the point would be a
    # real bypass.
    bypasses = (
        "import anesthesia_sim.core.uptake_system",
        "import anesthesia_sim.core.uptake_system as solver",
        "import anesthesia_sim",
        "from importlib import import_module\nimport_module('anesthesia_sim.core.uptake_system')\n",
    )
    for bypass in bypasses:
        assert not _package_imports(bypass) <= ALLOWED_PACKAGE_IMPORTS, (
            f"{bypass!r} reaches a solver in `core/`, but the independence "
            "check above reports nothing that would fail it"
        )


#: The functions that make up each independent solution, keyed by the file that
#: holds them. Each must exist, so that a rename fails the check instead of
#: leaving it nothing to check.
_ORACLE_FUNCTIONS = {
    "test_coupled_dynamics.py": ("_build_derivative", "_rk4_step", "_integrate_rk4"),
    "test_late_washout_against_published_fits.py": (
        "_open_circuit_system_per_min",
        "_open_circuit_modes",
        "_isolated_time_constants_min",
    ),
}

#: The imported names an oracle may use. The two parameter loaders read data
#: files and solve nothing. The rest are the standard library and numpy, and
#: `Callable` and `dataclass` appear only in a type alias and a decorator.
_ORACLE_IMPORTS = frozenset(
    {
        "Callable",
        "cmath",
        "dataclass",
        "load_agent_parameters",
        "load_reference_adult_parameters",
        "math",
        "numpy",
    }
)

#: Builtins that look up a module or a namespace by name. Any of them would let
#: an oracle get hold of a solver without importing one.
_ORACLE_FORBIDDEN_BUILTINS = frozenset(
    {"__import__", "compile", "eval", "exec", "getattr", "globals", "locals", "vars"}
)


def _module_bindings(tree: ast.Module) -> tuple[dict[str, ast.stmt], frozenset[str]]:
    """The statement that binds each module-level name, and the imported names.

    Args:
        tree: A parsed module.

    Returns:
        A map from each name a top-level function, class or assignment binds
        to the statement that binds it, and the set of names that a top-level
        import binds.
    """
    definitions: dict[str, ast.stmt] = {}
    imported: set[str] = set()
    for statement in tree.body:
        if isinstance(statement, (ast.FunctionDef, ast.ClassDef)):
            definitions[statement.name] = statement
        elif isinstance(statement, (ast.Assign, ast.AnnAssign)):
            targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
            for target in targets:
                for node in ast.walk(target):
                    if isinstance(node, ast.Name):
                        definitions[node.id] = statement
        elif isinstance(statement, (ast.Import, ast.ImportFrom)):
            for alias in statement.names:
                imported.add((alias.asname or alias.name).split(".")[0])
    return definitions, frozenset(imported)


def _without_annotations(tree: ast.Module) -> ast.Module:
    """`tree` with every annotation removed, since none of them ever runs.

    Under `from __future__ import annotations` an annotation is a string that
    nothing evaluates, so a name it mentions is not one the code uses.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.arg):
            node.annotation = None
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            node.returns = None
        elif isinstance(node, ast.AnnAssign):
            node.annotation = ast.Constant(value=None)
    return tree


def _oracle_violations(source: str, roots: Sequence[str]) -> list[str]:
    """Return every way the functions named in `roots` could reach code they must not.

    The walk starts at each root. It follows every module-level function,
    class or assignment that the code it reads refers to, so a helper that
    calls a solver is found as surely as a root that does. Annotations are not
    read, for the reason `_without_annotations` gives.

    Args:
        source: A module's text.
        roots: The names of the oracle's functions in that module.

    Returns:
        One line per violation: a root that is missing, an import statement
        inside the oracle, an imported name not on `_ORACLE_IMPORTS`, a
        builtin on `_ORACLE_FORBIDDEN_BUILTINS`, or a dunder attribute such as
        `__module__`, which names a module without importing it. An empty
        list means the oracle reads parameters and computes the rest itself.
    """
    definitions, imported = _module_bindings(_without_annotations(ast.parse(source)))
    violations: list[str] = []
    visited: set[str] = set()
    pending = list(roots)

    for root in roots:
        if root not in definitions:
            violations.append(f"{root} is not defined in the module")

    while pending:
        name = pending.pop()
        if name in visited or name not in definitions:
            continue
        visited.add(name)

        for node in ast.walk(definitions[name]):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                violations.append(f"{name} imports inside its body")
            elif isinstance(node, ast.Attribute) and node.attr.startswith("__"):
                violations.append(f"{name} reads the attribute {node.attr}")
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if node.id in _ORACLE_FORBIDDEN_BUILTINS:
                    violations.append(f"{name} calls {node.id}")
                elif node.id in definitions:
                    pending.append(node.id)
                elif node.id in imported and node.id not in _ORACLE_IMPORTS:
                    violations.append(f"{name} uses the imported name {node.id}")

    return violations


def test_oracle_bodies_call_no_solver_from_core() -> None:
    """Each independent solution computes the model itself from its parameters.

    `test_oracle_imports_no_solver_from_core` reads what this module imports.
    That cannot settle what an oracle does with an import that the module is
    allowed. This module imports `AgentUptakeSystem` because it is the system
    under test, and the late-washout module imports it to run the model. So
    this check reads the oracle functions themselves, in both files, and
    everything they reach in their own module (`PL-GHT8`).

    An oracle may use the parameter loaders, `math`, `cmath`, `numpy` and its
    own module's helpers. It may not use another imported name, import inside
    its body, read a dunder attribute such as `__module__`, or call a builtin
    that looks up a namespace by name. That closes the three routes that
    reading imports alone leaves open: calling the system under test, reading
    `sys.modules`, and `importlib.import_module(AgentUptakeSystem.__module__)`.
    A name assembled at runtime from strings is still beyond any reading of
    the source, and is left to review.
    """

    directory = Path(__file__).parent
    for file_name, roots in _ORACLE_FUNCTIONS.items():
        source = (directory / file_name).read_text(encoding="utf-8")
        assert _oracle_violations(source, roots) == [], (
            f"an independent solution in {file_name} reaches code it must not: "
            f"{_oracle_violations(source, roots)}"
        )

    # Probes. Each is a small module whose oracle takes one route to a solver,
    # and the check must find every one. They are written as text rather than as
    # code in this module, because a real bypass added to prove the point would
    # be a real bypass.
    loaders = (
        "from anesthesia_sim.core.parameters import load_agent_parameters\n"
        "from anesthesia_sim.core.uptake_system import AgentUptakeSystem\n"
    )
    probes = {
        "the system under test": loaders + "def _build_derivative(agent_id, point):\n"
        "    system = AgentUptakeSystem.for_agent(load_agent_parameters(agent_id))\n"
        "    return system.equation_settings()\n",
        "sys.modules": "import sys\n"
        "def _build_derivative(agent_id, point):\n"
        "    return sys.modules['anesthesia_sim.core.governing_equations']\n",
        "a module named by __module__": loaders + "import importlib\n"
        "def _build_derivative(agent_id, point):\n"
        "    return importlib.import_module(AgentUptakeSystem.__module__)\n",
        "a helper that calls the solver": loaders + "def _helper(agent_id):\n"
        "    return AgentUptakeSystem.for_agent(load_agent_parameters(agent_id))\n"
        "def _build_derivative(agent_id, point):\n"
        "    return _helper(agent_id)\n",
        "an import inside the body": "def _build_derivative(agent_id, point):\n"
        "    from anesthesia_sim.core import uptake_system\n"
        "    return uptake_system\n",
    }
    for route, probe in probes.items():
        assert _oracle_violations(probe, ("_build_derivative",)) != [], (
            f"an oracle that reaches a solver through {route} passes the check"
        )

    allowed = loaders + (
        "import math\n"
        "def _scale(value):\n"
        "    return math.exp(-value)\n"
        "def _build_derivative(agent_id, point):\n"
        "    agent = load_agent_parameters(agent_id)\n"
        "    return _scale(agent.blood_gas_partition_coefficient)\n"
    )
    assert _oracle_violations(allowed, ("_build_derivative",)) == [], (
        "an oracle that reads its parameters and computes the rest itself is refused"
    )
