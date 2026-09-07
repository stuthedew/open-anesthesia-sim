"""Check the coupled six-state solution against an independent integration.

Mass balance cannot detect a wrong rate. Every internal exchange appears in
the system matrix as a pair of entries whose contribution to the total stored
amount cancels, so the accounting residual stays at rounding whatever the
transfer rates are — including rates that would move the alveolar fraction by
tenths of a percentage point. Conservation is necessary and nowhere near
sufficient, and this module is the check that closes the gap: it re-derives
the governing equations of `docs/MODEL.md` from the parameter files,
integrates them with a from-scratch fourth-order Runge–Kutta, and requires the
shipped solution to agree with that one.

The independence rule is what makes this verification rather than a
tautology, so `test_oracle_imports_no_solver_from_core` enforces it
mechanically rather than leaving it to review: the oracle below may import
the parameter loaders and nothing else from `anesthesia_sim`. Re-deriving an
equation from the specification is evidence; calling the implementation
under test and comparing it against itself is not.

Promoted from the v0.2.0 architecture review's verification harness (PL-023),
where the same oracle was written but ran only by hand. That harness was
retired by PL-STNV once every check it carried had become a closed item, a
reference test, or an open queue entry; it survives in git history alone.
"""

from __future__ import annotations

import ast
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import pytest

from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

SECONDS_PER_MINUTE = 60.0

AGENT_IDS = ("sevoflurane", "isoflurane", "desflurane")

# Simulated horizons, chosen for what each one exercises: 60 s is circuit
# and alveolar wash-in while the tissues are still empty, 600 s is the
# vessel-rich group approaching its own equilibrium, and 3600 s is far
# enough in for muscle and fat to carry a meaningful load. They are the
# horizons the pinned reference states below are computed at.
#
# 3600 s is also the only run this module drives past 900 s, and it is the
# one horizon whose measured residual is genuinely the shipped step's own:
# the trajectory gates all peak inside a transient the oracle cannot resolve
# at its 0.05 s step (see `ORACLE_STEP_S`), whereas held settings for an hour
# leave the oracle converged to 1.2e-15 and the residual is then rounding
# accumulated over 36 000 shipped steps. It grows by nine to sixty-seven fold
# from 60 s to 3600 s — 8.9x for sevoflurane, 19.4x for isoflurane, 67.0x for
# desflurane, over the endpoint table at `HELD_RUN_ROUNDING_BOUND` — and the
# spread is why the growth is quoted as a range rather than as one figure: it
# is set by how far the slow compartments have filled by the horizon, which
# differs by agent. The worst state migrates from the fast circuit to the slow
# muscle compartment, which no trajectory shorter than an hour ever reaches.
# `test_the_shipped_step_reaches_the_pinned_reference_horizons` is the gate
# that covers it, and endpoint sampling is right there for the same reason:
# at 3600 s the maximum is at the endpoint, not inside a transient.
HORIZONS_S = (60.0, 600.0, 3600.0)

# The historical operating point, kept because the pinned reference states
# below are its solution. 5% is the highest concentration all three shipped
# vaporizers can deliver (isoflurane's maximum), so one dial setting serves
# every agent.
DELIVERED_FRACTION = 0.05
FRESH_GAS_FLOW_L_MIN = 4.0
CIRCUIT_VOLUME_L = 6.0

# The model's own supported input ranges, restated here rather than imported
# for the same reason as SHIPPED_STEP_S below — this gate states the domain it
# claims to cover in its own file, so that a widened domain fails here rather
# than silently enlarging what these measurements are read as covering.
# `test_envelope_limits_match_the_supported_input_ranges` is what keeps the
# restatement true; without it, moving a limit would silently shrink or
# stretch the domain this gate covers, which is the defect PL-042 exists to
# fix. Before PL-0MLQ these were the interface's slider limits and the
# restatement was checked against `simulation_view`, because the interface was
# the only place the domain was declared.
#
# The floors matter as much as the maxima and are checked with them. The worst
# trajectory this gate drives reaches zero cardiac output, so flooring that
# control above zero would take the bound's own worst case out of the
# reachable domain without failing anything. `docs/MODEL.md` § "Supported
# input ranges" records that zero is supported on all four controls,
# deliberately (PL-629Z).
MAX_FRESH_GAS_FLOW_L_MIN = 10.0
MAX_ALVEOLAR_VENTILATION_L_MIN = 12.0
MAX_CARDIAC_OUTPUT_L_MIN = 10.0
MIN_FRESH_GAS_FLOW_L_MIN = 0.0
MIN_ALVEOLAR_VENTILATION_L_MIN = 0.0
MIN_CARDIAC_OUTPUT_L_MIN = 0.0
MIN_DELIVERED_CONCENTRATION_PERCENT = 0.0

# The resolution every concentration is displayed at, restated for the same
# reason as the slider limits and checked against the interface in the same
# test. `docs/MODEL.md` § "Displayed precision" is where the choice is argued.
CONCENTRATION_DISPLAY_DECIMALS = 2


@dataclass(frozen=True)
class OperatingPoint:
    """A point in the space of settings the interface can produce.

    Frozen so it can key the reference-solution cache; the four fields are
    exactly the sliders that enter the governing equations. Circuit volume is
    not among them: it is a data-file parameter with no slider, and it scales
    the circuit equation alone rather than changing the coupling between
    compartments, which is where a wrong transfer rate would show. PL-GYH2
    carries the question of whether it should be a control at all, and what
    range it would need if it became one.
    """

    delivered_fraction: float
    fresh_gas_flow_l_min: float
    alveolar_ventilation_l_min: float
    cardiac_output_l_min: float


@dataclass(frozen=True)
class Phase:
    """One leg of a trajectory: settings held for a fixed duration.

    A run of the application is a sequence of these — the settings hold
    until someone moves a slider — so a gate driven by a phase list covers
    what the application actually produces, where one held `OperatingPoint`
    covers only the runs in which nothing is ever changed.
    """

    duration_s: float
    point: OperatingPoint


def _default_operating_point() -> OperatingPoint:
    """The point the pinned reference states were computed at."""

    patient = load_reference_adult_parameters()

    return OperatingPoint(
        delivered_fraction=DELIVERED_FRACTION,
        fresh_gas_flow_l_min=FRESH_GAS_FLOW_L_MIN,
        alveolar_ventilation_l_min=patient.default_alveolar_ventilation_l_min,
        cardiac_output_l_min=patient.default_cardiac_output_l_min,
    )


def _max_dial(agent_id: str) -> float:
    """The agent's own vaporizer maximum, as a fraction."""

    return load_agent_parameters(agent_id).max_delivered_concentration_percent / 100.0


def _envelope_corner(agent_id: str) -> OperatingPoint:
    """The corner of the settings envelope, where the shipped step's own error is worst.

    Established by sweeping all four axes rather than assumed: fresh gas flow
    and alveolar ventilation both increase the disagreement monotonically to
    their slider maxima; cardiac output has an interior *minimum* near
    5 L/min and rises toward both ends, with the upper end the larger; and the
    equations are linear in the delivered fraction, so the agent's own
    vaporizer maximum is its worst dial. The measurements are recorded in
    `docs/MODEL.md` § "Independent-solution test".

    The sweep was run while the operator split shipped, and the corner it
    found is still the right one under the exact step, for a different
    reason: measured against a converged oracle (RK4 at 0.0015625 s), the
    shipped step's own worst residual anywhere in `ALL_GATE_TRAJECTORIES` is
    1.5626e-14 in the desflurane vessel-rich fraction at 567.5 s, here. What
    it is no longer is the worst number this module *reports* — that is the
    ventilator start, where most of what is measured is the oracle's own
    truncation rather than the shipped step's error (`ORACLE_STEP_S`).

    Monotonicity is measured, not proved. A change to the governing equations
    could move the maximum off this corner, which is why the sweep is worth
    re-running rather than trusting when the model changes.
    """

    return OperatingPoint(
        delivered_fraction=_max_dial(agent_id),
        fresh_gas_flow_l_min=MAX_FRESH_GAS_FLOW_L_MIN,
        alveolar_ventilation_l_min=MAX_ALVEOLAR_VENTILATION_L_MIN,
        cardiac_output_l_min=MAX_CARDIAC_OUTPUT_L_MIN,
    )


def _ventilator_start(agent_id: str) -> tuple[Phase, ...]:
    """Prime the circuit with the ventilator off, then start ventilating.

    A manoeuvre the interface offers and a user performs: the vaporizer is
    open and fresh gas is running while alveolar ventilation is still zero,
    so the circuit fills to the dial setting against lungs that cannot take
    any of it. Starting ventilation then presents the largest circuit-to-
    alveolar gradient the machine can produce, at the largest ventilation it
    can produce.

    Five minutes is far longer than the circuit needs: at 10 L/min into 6 L
    its time constant is 36 s, so the first phase ends saturated and the
    scenario does not depend on exactly how long it ran.
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
    """Fill circuit and lungs with no circulation, then restore it and dial off.

    This is the most violent trajectory the four sliders can produce, for a
    reason that is structural rather than clinical: holding cardiac output at
    zero lets circuit and alveoli saturate at the dial setting while every
    blood and tissue compartment stays empty, which is the furthest apart the
    six states can be driven. Turning perfusion on and the vaporizer off in
    the same move then makes every compartment's equilibrium the opposite of
    where it sits, so all six transients run at once.

    Under the operator split it was also the trajectory that measured worst,
    which is why it was added. It no longer is: the exact step's disagreement
    with the oracle peaks on `_ventilator_start` instead — 7.747e-13 against
    this scenario's 2.693e-13 for desflurane, 2.9 times — because what a
    trajectory that turns now measures is mostly how hard the *oracle* is
    working through the transient, not how hard the shipped step is. The
    scenario is kept because it is still the widest spread of initial states
    the interface can set up, and because it is the only gate trajectory that
    reaches a floor rather than a maximum on any control.

    Zero cardiac output is a supported input, decided and recorded rather than
    inherited: `docs/MODEL.md` § "Supported input ranges" gives the reasons,
    of which the operative one is that reducing cardiac output accelerates
    alveolar wash-in and zero is that lesson's clearest case. So this
    trajectory is inside the domain the gate must cover, not an edge case
    tolerated at its boundary.

    The gate does not rest on it alone even so: `_ventilator_start` above
    needs no zero-perfusion phase and measures worse, so a later decision to
    floor the slider above zero would leave a gate that still means something
    while this trajectory was replaced.

    Ten minutes of loading is enough to saturate: extending it to twenty
    changed the measured coefficient by 4e-5 relative when that was the
    quantity being measured.
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
                MIN_DELIVERED_CONCENTRATION_PERCENT / 100.0,
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
                load_agent_parameters(agent_id).mac_percent / 100.0,
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


# The trajectories the gate drives, found by sweeping the corners of both
# phases' settings and then each axis separately around the winner. What the
# sweep showed, and why these two are the ones kept:
#
#   - The worst is always the first transition after the loading phase
#     saturates. Repeating the cycle three or six times does not raise the
#     peak at all, and shortening the phases lowers it, so the disagreement is
#     bounded rather than accumulating over a run. Re-measured under the exact
#     step this still holds and holds more sharply: on the ventilator start
#     the running maximum at 60 s, 600 s, 1800 s and 3600 s is the same
#     number, reached at about 306 s and never approached again.
#   - Inserting a third phase between the two never beat the pair; the best
#     middle phases were the ones that simply held the loading corner longer.
#   - Every axis is monotone toward the corner used, except cardiac output in
#     the loading phase, which is worst at zero — the opposite end from the
#     constant-setting corner, where it is worst at the maximum.
#
# The sweep was run while the split shipped and its ordering of the two
# scenarios has since reversed (see `_unperfused_load_then_dial_off`), so what
# it establishes now is that these two bracket what a turning trajectory does,
# not which of them is the extreme. Monotonicity is measured, not proved, so a
# change to the governing equations could move the maximum off these
# trajectories and the sweep is worth re-running rather than trusting.
SETTING_CHANGE_SCENARIOS = (
    ("ventilator start", _ventilator_start),
    ("unperfused load then dial off", _unperfused_load_then_dial_off),
)

# Every trajectory this module drives, for the checks that must hold on all of
# them rather than only where the disagreement is worst.
ALL_GATE_TRAJECTORIES = (
    ("ordinary use", _ordinary_use),
    ("reference point, held", _held_default_settings),
    ("envelope corner, held", _envelope_corner_held),
    *SETTING_CHANGE_SCENARIOS,
)


# Long enough to contain the worst disagreement anywhere in the envelope: at
# the corner it occurs early in the wash-in transient — 5.4 s for isoflurane,
# 6.6 s for sevoflurane, 7.2 s for desflurane — and the running maximum is
# unchanged whether the run stops at 60 s, 600 s, 1800 s or 3600 s, to every
# digit. The trajectory gates therefore run to 600 s and take the maximum over
# the whole trajectory rather than sampling endpoints.
#
# Held *default* settings are the exception and are why `HORIZONS_S` still has
# a 3600 s entry: there nothing transient is happening, the residual is
# rounding accumulating with the step count, and it keeps growing for the
# whole hour. Taking a maximum over 600 s cannot see that; only a longer run
# can, which is what `test_the_shipped_step_reaches_the_pinned_reference_horizons`
# is for.
ENVELOPE_HORIZON_S = 600.0

# The step the interface runs at (`app.simulation_view.SIMULATION_STEP_S`),
# restated rather than imported so that this reference test stays
# independent of the application layer.
#
# `test_displayed_resolution_and_shipped_step_match_the_interface` checks the
# restatement, for the same reason it checks the slider limits, but not for
# the reason it used to. It used to say that every measured figure here was a
# first-order coefficient multiplied by this step, so that a moved step
# rescaled all of them. That was true of the operator split and is not true of
# the exact propagator, which solves the interval exactly however it is
# subdivided and has no coefficient to multiply (`PL-X9KD`).
#
# The step still has to be checked, for two reasons that survive:
#
#   - What this module measures is accumulated floating-point rounding, and
#     rounding accumulates with the *number* of steps rather than with their
#     size. A run of an hour is 36 000 roundings at this step and 144 000 at
#     0.025 s, and the measured residual over held default settings duly
#     grows: 6.96e-15, 2.72e-14, 4.997e-14 for sevoflurane at 0.1 s, 0.05 s
#     and 0.025 s. That is what `HELD_RUN_ROUNDING_BOUND` measures, and it is
#     the shipped step's own. It is *not* what the trajectory gates report:
#     on the transients that set their worst case, 86% to 99.8% of the figure
#     is the oracle's own truncation rather than the shipped step's, which
#     `ORACLE_STEP_S` decomposes.
#   - The step is when a setting change takes effect, so it is what the phase
#     boundaries of every trajectory here mean. Two of the five trajectories
#     turn, and a shipped step that moved while this one did not would move
#     those turns off the instants these measurements were taken at.
#
# What is *not* a reason any more: `core.uptake_system.MAXIMUM_SIMULATION_STEP_S`
# is not derived from anything measured here. `docs/MODEL.md` § "Supported
# simulation step" records its old derivation as void and the value as carried
# forward pending `PL-X9KD`. Until PL-VP7N the step was restated here without
# any check at all.
SHIPPED_STEP_S = 0.1

# The oracle's own step. Deliberately not 0.1 s, so that agreement can never
# be an artifact of the two solvers sharing a step size.
#
# **It is not converged during a fast transient, and that is now the larger
# half of every number this module reports.** The 2.6e-16 figure this comment
# used to quote — a 0.05 s RK4 run against a 0.005 s one, across all six
# states — was measured at the *default* settings, where it is true and
# remains true. It does not transfer to a trajectory driven at the envelope
# corner or through a setting change, and the gates that matter are driven at
# both. Decomposing the worst gate number three ways, at the instant and state
# it occurs (desflurane, ventilator start, alveolar, 307.4 s), against a
# converged oracle at 0.0015625 s:
#
#     what the gate reports  |shipped(0.1) - oracle(0.05)|   7.7470e-13
#     the oracle's own error  |oracle(0.05) - converged|     7.7562e-13
#     the shipped step's own  |shipped(0.1) - converged|     9.1593e-16
#
# so 99.88% of it is the oracle at that instant. Halving the oracle's step
# divides that term by 15.94 and then 15.38, against 2^4 = 16: the signature of
# RK4 truncation and not of rounding. Taken as maxima over the whole trajectory
# rather than at one instant the shipped step's own term is larger — 9.7977e-15,
# in vessel rich at 592.1 s — because the three maxima fall at different places.
# The same decomposition on the envelope corner and the unperfused-load
# trajectories gives the oracle 86% to 99.8%, lowest at the sevoflurane
# envelope corner.
#
# **This makes the gates conservative rather than wrong.** What they bound is
# the sum of both solutions' errors, of which the shipped step's own share is
# at most 1.5626e-14 anywhere in `ALL_GATE_TRAJECTORIES` and 5.2260e-14 over a
# 3600 s run. A returning method error still fails them, because any method
# error is orders above either figure. What they cannot do is measure the
# shipped step at better than the oracle's own resolution on a transient.
#
# **Refining it is not free, and it is not done here — but not because the
# pinned states forbid it.** That was the reason first written down and it is
# wrong: re-integrating the oracle at 0.0125 s and at 0.003125 s leaves all
# nine `PINNED_REFERENCE_STATES` entries passing under this module's own
# `rel=1e-9, abs=1e-15`, so refinement would not re-pin them. What it would
# cost is `_oracle_step_for`'s "half the step under test" rule and
# `ORACLE_STEP_S` moving together, or
# `test_lockstep_oracle_step_matches_the_pinned_one` fails; and RK4 time rising
# fourfold per halving on a file that already runs for the better part of a
# minute. Refining to 0.0125 s is therefore a CI-cost decision rather than a
# correctness one, and it is left open here rather than settled.
# `test_the_shipped_step_reaches_the_pinned_reference_horizons` is the gate
# that does not need this: held settings for an hour leave the oracle's own
# error at 1.2e-15 to 2.1e-15, so there the residual is the shipped step's own.
ORACLE_STEP_S = 0.05

# Retired here (`PL-X9KD`): `SPLITTING_ERROR_BOUND_PER_STEP_SECOND = 2.8e-3`,
# `EXACT_SOLUTION_FLOOR = 1e-12`, and the four tests they served. Recorded
# rather than simply deleted, because "the gate was loosened until it passed"
# and "the gate measured a quantity that no longer exists" look identical in a
# diff and are opposite things.
#
# The bound was a first-order splitting coefficient C in an error C·Δt, set at
# 1.22 times a measured worst of 2.29e-3 s^-1. The shipped step is now one
# matrix exponential of the whole coupled system, so there is no C: re-expressed
# as a coefficient, the worst residual reachable anywhere is 7.747e-12 s^-1, and
# the bound sat 3.61e8 times above it. Its three consumers passed with 8.6 to
# 9.7 orders of magnitude of slack, which is not a gate.
#
# `EXACT_SOLUTION_FLOOR` was the escape hatch `test_shipped_split_error_is_first_order_in_step`
# took when the error fell below what a split could produce. Measured, it fired
# on all nine parametrizations, so that test asserted nothing — and worse than
# nothing: with the early return removed, all nine would *fail*, because the
# measured step ratios run 0.147 to 18.6 and the assertion required every one
# of them in (1.9, 2.1). Its own margin to the floor was 1.29x on desflurane's
# ventilator start, so a platform accumulating slightly more rounding would
# have stopped taking the early return and started failing on a true property.
# It cost about 25 s of the file's 56 s to do that.
#
# What replaced each of them, and what needed a new gate rather than a
# replacement:
#
#   - `test_shipped_split_is_bounded_across_the_settings_envelope` and
#     `test_shipped_split_is_bounded_across_setting_changes` are reproduced
#     exactly by `test_exact_step_matches_the_independent_solution_everywhere`
#     — same trajectories, same driver, same measured residuals to every
#     printed digit, at the same instants and in the same states — under a
#     tolerance 6.45 times the worst rather than 3.61e8 times it. Pure
#     deletion; nothing transfers because nothing was lost.
#   - `test_shipped_split_error_is_first_order_in_step` varied the step over
#     trajectories that *turn*, which its nearest replacement
#     (`test_the_disagreement_does_not_shrink_with_the_step`) did not. That is
#     a real property and it is not decorative: on a turning trajectory the
#     coarsest step is the worst by 10 to 35 times, the opposite of what
#     happens at held settings. The step test now runs the setting-change
#     trajectories too, which is where that property went.
#   - `test_shipped_split_matches_independent_solution` was the only test in
#     the repository driving the shipped solver past 900 s. That is not
#     cleanup-able: at 3600 s the residual is two to sixteen times its 600 s
#     value, it sits at the endpoint rather than in a transient, and it lives
#     in muscle — a compartment that is never the worst state on any of the
#     five surviving trajectories. Retiring it as written would also have
#     orphaned the 3600 s entries of `PINNED_REFERENCE_STATES`, leaving them
#     constraining the oracle alone. It survives as
#     `test_the_shipped_step_reaches_the_pinned_reference_horizons` under
#     `HELD_RUN_ROUNDING_BOUND` below.
#
# What the shipped exact step is allowed to disagree with the oracle by, as an
# absolute difference in any of the six fractions, anywhere on any gate
# trajectory (`PL-GS5X`).
#
# **It is not the retired splitting bound rescaled, and it is a different kind
# of quantity.** That bound was a first-order coefficient C in an error C·Δt:
# a systematic method error, which shrinks as the step shrinks. The shipped
# step is now one matrix exponential
# of the whole coupled system, which is the *exact* solution of these
# equations over the interval, so there is no method error left to have an
# order — and the residual measured here is floating-point accumulation in two
# independently written solutions, which grows with the *number* of steps and
# therefore gets slightly worse as the step gets smaller. Bounding a
# coefficient would state the opposite of what is true, so this bound is
# absolute.
#
# **Derived, not inherited.** `PL-P0BB` refuses reuse of the ~2e-15 figure,
# which described the old mechanism's accounting residual. Measured 2026-09-06
# over every agent, every horizon in `HORIZONS_S`, and every trajectory in
# `ALL_GATE_TRAJECTORIES`, taking the maximum over the whole trajectory rather
# than at endpoints:
#
#     endpoint, default settings, 3600 s      5.2e-14  (isoflurane, muscle)
#     ordinary use                            3.8e-15
#     envelope corner, held                   1.9e-13  (desflurane, alveolar)
#     unperfused load then dial off           3.2e-13  (isoflurane, alveolar)
#     ventilator start                        7.7e-13  (desflurane, alveolar)
#
# The worst is 7.7e-13 and this bound allows 6.5 times it. Against the split
# it replaced, whose worst over the same domain was 2.29e-4 at this step, the
# exact step is eight orders of magnitude closer to the independent solution.
#
# **What that 6.5 is headroom over was misstated when this bound was set, and
# the correction is worth having even though it does not move the value
# (`PL-X9KD`).** The 7.7e-13 is not the shipped step's error. Decomposed
# against a converged oracle it is 86% to 99.8% the oracle's own RK4
# truncation at `ORACLE_STEP_S`, across the trajectories that set it — 99.8%
# on the ventilator start that carries the worst figure, 86% at its lowest on
# the sevoflurane envelope corner. Measured against a
# converged oracle instead, the shipped step is inside 1.5626e-14 anywhere in
# `ALL_GATE_TRAJECTORIES` and 5.2260e-14 over an hour, so this bound has 320x
# and 95.7x over what it is nominally protecting. It is set where it is because
# what the gate can *observe* is the sum of both solutions' errors, and 6.5x is
# the honest margin on the observable.
#
# **The residual is rounding and not truncation, which is what makes an
# absolute bound the right shape — but the evidence originally given for that
# covered one trajectory only.** Refining the oracle's own step eightfold —
# 0.05 s to 0.00625 s — leaves the residual unchanged to three figures at held
# default settings (1.385e-14, 1.373e-14, 1.393e-14, 1.346e-14 for sevoflurane
# at 3600 s; reproduced exactly). Held settings are the case where that is
# true. The same refinement on the ventilator start drops the residual 68-fold,
# from 7.7470e-13 to 1.1435e-14, and on the envelope corner 12-fold, because
# there the oracle is not converged and the refinement is removing *its*
# truncation. So the claim holds for the shipped step and is established by the
# held-settings run and by the three-way decomposition above, not by refinement
# on a trajectory that turns.
#
# **The margin is wider than the retired splitting bound's 1.22 and
# deliberately so.** That bound constrained a systematic coefficient, which is
# reproducible between machines. This one constrains accumulated rounding,
# which is not: a different libm `exp`, or a compiler contracting a multiply
# and an add into one FMA, moves the last bits of both solutions. Six and a
# half times is still eight orders below the error of any method that is not
# exact, so the gate still fails the moment method error returns — which is the
# only thing it is here to catch.
EXACT_STEP_ORACLE_TOLERANCE = 5e-12

# What the shipped step alone is allowed to accumulate over a run at held
# settings, as an absolute difference in any of the six fractions at the
# horizon (`PL-X9KD`). Used by
# `test_the_shipped_step_reaches_the_pinned_reference_horizons`.
#
# **Why this is a second constant rather than a reuse of the tolerance above.**
# The trajectory gates measure the shipped step and the oracle together, and on
# the transients that set their worst case the oracle is the larger term (see
# `ORACLE_STEP_S`). Held default settings for an hour are the one place in this
# module where that is not so: refining the oracle from 0.05 s to 0.00625 s
# moves the number by under 3%, and the three-way decomposition gives the
# oracle 2.1168e-15 against the shipped step's own 5.2260e-14. This is
# therefore the only gate here whose bound can be derived from what the shipped
# step itself does, and a bound derived from that should not be five times
# looser than the arithmetic it is bounding just because a different gate,
# measuring a different thing, needs the room.
#
# **The derivation.** Measured 2026-09-06 at the reference operating point,
# endpoint of each horizon in `HORIZONS_S`, worst over the six fractions:
#
#                     60 s                600 s               3600 s
#     sevoflurane     1.5543e-15 circuit  6.8279e-15 circuit  1.3850e-14 muscle
#     isoflurane      2.6749e-15 circuit  1.3420e-14 circuit  5.1919e-14 muscle
#     desflurane      7.2511e-16 circuit  2.9490e-15 circuit  4.8562e-14 muscle
#
# The worst is 5.1919e-14 and this bound allows 19.3 times it. The margin is
# set from what the shipped step's own rounding path can be moved by, rather
# than from that figure plus a guess: solving the identical 3600 s interval at
# 0.05 s and at 0.025 s instead of 0.1 s — the same exact propagator over the
# same interval, differently subdivided, so every difference is the shipped
# side's own accumulation — moves the answer by up to 3.1675e-13, taking the
# maximum over every pair of those three steps, all six fractions and all three
# agents (desflurane worst; sevoflurane 1.3725e-13, isoflurane 2.2699e-13).
# This bound clears that by 3.2 times, which is the room a different libm or a
# contracted multiply-add needs. It does not clear a method error: the coarsest
# supported step under any method with an order is orders above it.
#
# The subdivision spread is the larger of the two figures, and deliberately the
# one the margin is taken over: a platform that rounds differently moves the
# shipped solution by about as much as re-subdividing the interval does, and
# nothing about the pinned oracle constrains that.
#
# Note what the growth signature is, because it is what the gate detects. The
# residual grows with run length at a fixed step (nine- to sixty-sevenfold from
# 60 s to 3600 s, by agent) and grows again as the step *shrinks*, and the
# worst state migrates
# from circuit to muscle as the slow compartment fills. That is rounding
# accumulating once per step, not truncation. A residual that started shrinking
# with the step would be method error returning, and
# `test_the_disagreement_does_not_shrink_with_the_step` is what looks for it.
HELD_RUN_ROUNDING_BOUND = 1e-12

# How far apart two compartments may be while the shipped step still inverts
# which of them is displayed as higher. The ordinal reading the interface
# invites — the circuit leads the alveoli lead the tissues — is only misleading
# if an inversion happens between two readouts a reader would see as separated,
# so this bounds the gap at which one can occur rather than forbidding
# inversions outright.
#
# **Derived from the absolute bound rather than fitted, which the previous
# value was not.** It used to be 3.0 counts, set at 1.7 times a measured 1.73
# counts under the operator split, with an arithmetic sanity check that was
# itself wrong: it added "half a count of rounding each" on top of two
# displacements. Rounding cannot contribute. `_displayed_percent` is monotone
# non-decreasing — verified over 2 000 000 random ordered pairs and 18 009
# pairs straddling exact display-count boundaries at ±3e-17 to ±5e-16, with
# zero violations — so it can never produce an ordering opposite to the raw
# one. The correct figure for that check was 5.6 counts, not 6.6.
#
# With monotonicity, the bound is a consequence rather than a measurement.
# Write e = reference - shipped. An inversion of (left, right) needs
# shipped[left] > shipped[right] and reference[left] < reference[right], and by
# monotonicity both hold on the raw values too. The gap the test measures is
# then
#
#     reference[right] - reference[left]
#         = (shipped[right] - shipped[left]) + (e[right] - e[left])
#         < e[right] - e[left]  <=  |e[right]| + |e[left]|
#         <= 2 * EXACT_STEP_ORACLE_TOLERANCE
#
# because the first bracket is negative and every |e| is what the gate above
# bounds. Converting to counts of the last displayed digit gives the expression
# below: 1.0e-7 counts. Measured, the widest gap any inversion occupies is 0.0
# — there are no inversions at all, over 1 485 000 pair comparisons — and the
# largest pairwise differential |e[left] - e[right]| anywhere is 1.104e-12 in
# fraction, 1.104e-8 counts, 9.1 times under this. An error-injection sweep
# confirms the shape: displacing the states by ±ε produces a widest inverted
# gap that approaches 2ε from below at every scale and never exceeds it.
#
# **What this test is for, now that the bound follows from the one above.** It
# is no longer a second, independent bound on the solver: if the absolute gate
# passes, this one cannot fail. What it still checks is the step from a state
# to a displayed row — that `_displayed_percent` is monotone in practice on
# real trajectories rather than only on random pairs, and that the display path
# has not acquired a transformation that reorders. The gate keeps its
# gap-threshold shape rather than asserting zero inversions, because crossings
# really are sampled at gaps below the differential (the smallest nonzero true
# gap seen is 2.354e-15 in fraction, below the 1.104e-12 differential), so an
# inversion is arithmetically reachable there and a zero-inversion assertion
# would be a platform coin-flip.
MAX_INVERTED_GAP_IN_DISPLAY_COUNTS = (
    2.0 * EXACT_STEP_ORACLE_TOLERANCE * 100.0 * 10.0**CONCENTRATION_DISPLAY_DECIMALS
)

# Names this module is allowed to import from `anesthesia_sim`: the two
# parameter loaders the oracle needs, the system under test, the module
# declaring the input domain this gate measures over, and the view module
# whose displayed resolution and shipped step every figure here is quoted at.
#
# `supported_ranges` and `simulation_view` are on this list for two
# assertions — that the limits restated above are still the model's, and that
# the resolution and step they are quoted at are still the interface's — and
# the rule the list enforces is unaffected by either: what must never be
# imported is a solver, because comparing the implementation against itself
# proves nothing. Modules of constants are not that. The oracle itself
# (`_build_derivative`) still uses the parameter loaders alone.
ALLOWED_PACKAGE_IMPORTS = frozenset(
    {
        "load_agent_parameters",
        "load_reference_adult_parameters",
        "AgentUptakeSystem",
        "formatting",
        "simulation_view",
        "supported_ranges",
    }
)

# State order for every vector in this module:
# (F_C circuit, F_A alveolar, F_v mixed venous, F_vrg, F_mus, F_fat).
STATE_LABELS = ("circuit", "alveolar", "mixed venous", "vessel rich", "muscle", "fat")

# The independent solution itself, pinned so that a later edit to the oracle
# or to a parameter file cannot quietly move the reference the shipped core
# is measured against. A failure here is not a failure of the core: it says
# the oracle or its inputs changed, and the new values must be re-derived
# and reviewed before they are pinned again.
#
# Re-derived 2026-09-07 (`PL-8ZJQ`), from the oracle and not from the shipped
# solver, after `venous_pool_volume_l` moved from 1.0 L to Davis and Mapleson's
# 1.222 L. That is the case this pin exists for: a deliberate parameter change
# fails all nine here first, which is the review it is meant to force. The
# largest movement is 8.3e-4 relative, in the mixed-venous state, which is where
# a venous-pool change should show and nowhere else.
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
    the implementation under test, which is what makes agreement evidence.
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
    delivered_fraction = point.delivered_fraction

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

        # Tissues: perfusion-limited, driven by arterial (= alveolar).
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

    system.set_fresh_gas_flow(point.fresh_gas_flow_l_min)
    system.set_alveolar_ventilation(point.alveolar_ventilation_l_min)
    system.set_cardiac_output(point.cardiac_output_l_min)
    system.set_delivered_concentration(point.delivered_fraction)


def _shipped_system(agent_id: str, point: OperatingPoint) -> AgentUptakeSystem:
    """The implementation under test, configured at one operating point."""

    system = _empty_shipped_system(agent_id)
    _apply_operating_point(system, point)

    return system


def _shipped_states(system: AgentUptakeSystem) -> tuple[float, ...]:
    """Read the six displayed states, in STATE_LABELS order."""

    patient = system.patient

    return (
        system.circuit.circuit_concentration_fraction,
        system.alveoli.concentration_fraction,
        patient.mixed_venous_fraction,
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
        system.advance(step_s)

    return _shipped_states(system)


def _oracle_step_for(shipped_step_s: float) -> float:
    """Half the step under test.

    Halving keeps the two solvers off a shared step size — agreement then
    cannot be an artifact of them taking the same stride. At the shipped 0.1 s
    step this is `ORACLE_STEP_S`, so a trajectory driven here and a pinned
    reference state above are integrated identically, which is the coincidence
    `test_lockstep_oracle_step_matches_the_pinned_one` keeps true.

    This rule, not `EXACT_STEP_ORACLE_TOLERANCE`, is what would have to change
    to make the trajectory gates measure the shipped step rather than the sum
    of both solutions' errors. It is what pins the oracle to 0.05 s during a
    transient it needs 0.0125 s to resolve, and `ORACLE_STEP_S` records what
    that costs and why it is not changed here.
    """

    return shipped_step_s / 2.0


def _worst_error_over_phases(
    agent_id: str, phases: Sequence[Phase], shipped_step_s: float = SHIPPED_STEP_S
) -> tuple[float, float, str]:
    """Return the largest disagreement anywhere in the trajectory.

    Both solutions are driven through the same phase list, and both apply a
    phase's settings at the same instant: the shipped system by the setters
    the interface calls, the oracle by rebuilding its derivative. What is
    compared is therefore the two solvers alone, not two different piecewise
    schedules.

    Sampling endpoints is not enough here, and neither is one held setting.
    Except at held default settings, the worst disagreement is always inside a
    transient — the wash-in one, or the one a setting change itself starts.
    Stepping the two solutions in lockstep and taking the maximum costs nothing
    extra, since the RK4 integration is the expense and it happens either way.

    Until `PL-X9KD` this returned `worst_error / shipped_step_s`, and a second
    wrapper multiplied the step back in for the callers that wanted the
    difference. That division was the first-order coefficient C in an error
    C·Δt, which the exact step does not have; dividing its residual by the step
    produces a number varying with the step for no physical reason. The round
    trip was also not lossless — two of five sampled residuals came back a unit
    in the last place adrift — so with the last caller wanting C retired, the
    division goes with it.

    Returns (absolute error, simulated time of the worst, state label).
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
            system.advance(shipped_step_s)

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

    This is also what lets the bounds below keep narrow margins: any parameter
    revision fails here first and must be re-derived and reviewed, so no bound
    has to leave room for one.

    These states are the RK4 oracle's own solution, not the shipped solver's,
    and that is what makes this a regression gate rather than a self-comparison
    — re-pinning them from the shipped solver would destroy it. It is also why
    `ORACLE_STEP_S` cannot be refined without re-deriving all nine of them.
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

    This is the check mass balance cannot make: a wrong transfer rate leaves
    the accounting residual untouched but moves these six numbers.

    It is also the only gate here that drives the shipped solver for a full
    hour, and the only one whose measured residual is the shipped step's own at
    every horizon it drives. The trajectory gate's held-settings
    parametrizations are shipped-dominated too — the oracle contributes 17.7%
    of the "reference point, held" figure — but the three transients that set
    that gate's tolerance are not (`ORACLE_STEP_S` decomposes the difference).
    Both properties follow from holding settings: nothing transient
    is happening, so the oracle is converged and the disagreement is rounding
    accumulated once per step. It therefore keeps growing for as long as the
    run does — two to sixteen times its 600 s value by 3600 s — and none of the
    trajectory gates, which top out at 900 s and take a maximum over a
    transient, can see it. By the endpoint the worst state is muscle, which is
    never the worst state on any of the five gate trajectories.

    Sampling the endpoint rather than the whole run is right for the same
    reason: at 3600 s the maximum *is* the endpoint.

    Retiring this test's predecessor without replacing it would also have
    orphaned the 3600 s entries of `PINNED_REFERENCE_STATES`. The 60 s and
    600 s entries stay anchored to the shipped solver through the
    "reference point, held" trajectory, whose inline oracle is bit-identical
    to `_reference_state` at those horizons; nothing else reaches 3600 s.
    """

    point = _default_operating_point()
    error, state_label = _worst_state_error(
        _run_shipped(agent_id, duration_s, SHIPPED_STEP_S, point),
        _reference_state(agent_id, duration_s, point),
    )

    assert error <= HELD_RUN_ROUNDING_BOUND, (
        f"{agent_id} at {duration_s:.0f} s diverges from the independent "
        f"solution by {error:.3e} in the {state_label} fraction, above the "
        f"{HELD_RUN_ROUNDING_BOUND:.3e} allowed. At held settings the oracle "
        f"is converged at {ORACLE_STEP_S} s, so this residual is the shipped "
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

    This replaced two gates that bounded a first-order splitting coefficient
    over the same trajectories, at a bound eight orders of magnitude looser
    than what the exact step achieves. They still passed and still said
    something true, but a gate that loose cannot tell an exact propagator from
    a merely good approximation of one — so it could not detect the regression
    that matters here, which is any return of method error at all. `PL-X9KD`
    retired them once this had been measured to reproduce them exactly: same
    trajectories, same driver, same residuals to every printed digit, at the
    same instants and in the same states.

    Every agent and every gate trajectory, with the maximum taken over the
    whole run rather than at its endpoint, because outside held default
    settings the worst disagreement is always inside a transient. A full hour
    of held settings is the case this cannot see, and
    `test_the_shipped_step_reaches_the_pinned_reference_horizons` is what
    covers it.
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
    """The tolerance above holds at every supported step, not just the shipped one.

    This is what the retired `test_shipped_split_error_is_first_order_in_step`
    did for the split, inverted. There the claim was that halving the step
    halved the error, so bounding a coefficient at one step bounded it at all
    of them. Here the claim is that the step size does not enter: an exact
    propagator solves the same interval exactly however it is subdivided, so
    the same absolute bound must hold at 0.1 s, 0.05 s and 0.025 s alike. A
    method error of any order fails this by being visibly larger at the
    coarsest step and shrinking as the step shrinks.

    **The setting-change trajectories are here because the retired test ran
    them and this one did not (`PL-X9KD`).** That was the one property of the
    retired test that did not transfer, and it is not decorative: which step is
    worst depends on the trajectory, in opposite directions.

      - At held settings the *finest* step is the worst, because it takes four
        times as many steps and accumulates four times as much rounding:
        6.96e-15, 2.72e-14, 4.997e-14 for sevoflurane at 0.1, 0.05, 0.025 s.
      - On a trajectory that turns the *coarsest* is the worst, by 10 to 35
        times: 7.747e-13, 5.954e-14, 5.704e-14 for desflurane's ventilator
        start. That is not the shipped step degrading at 0.1 s. The oracle runs
        at half the step under test (`_oracle_step_for`), so at the coarsest
        pairing it is running at 0.05 s through a transient it needs 0.0125 s
        to resolve, and what falls away as the step shrinks is the oracle's own
        truncation.

    So the only claim this test makes is that no supported step exceeds the
    tolerance. It deliberately does not assert a direction: a version of it
    that did would have been true on one trajectory and false on the other two.
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

    `_oracle_step_for` halves whatever step is under test, which at the
    shipped step is `ORACLE_STEP_S` — the step every pinned reference state
    was computed at. Letting the two drift apart would move what the gates
    below measure while leaving the pinned states untouched, so the
    coincidence is checked rather than described.
    """

    assert _oracle_step_for(SHIPPED_STEP_S) == ORACLE_STEP_S


def test_envelope_limits_match_the_supported_input_ranges() -> None:
    """The restated limits are still the model's own declared domain.

    Without this, widening a supported range would silently leave the gate
    measuring a subset of the domain it is read as covering, and nothing
    would fail — which is exactly how the bound came to be narrower than the
    reachable settings in the first place.

    The floors are checked alongside the maxima because the worst trajectory
    the gate drives reaches zero cardiac output: flooring that control above
    zero would remove the bound's own worst case from the reachable domain,
    which is the same defect at the other end of the axis.

    Before PL-0MLQ the comparison was against `simulation_view`'s slider
    limits, because the interface was the only place a supported range was
    written down. `core/supported_ranges.py` declares them now and refuses a
    setting outside them, so this is a check against the model itself; that
    the interface offers exactly the same domain is
    `test_the_sliders_span_the_supported_input_ranges` in the view's own
    suite.
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


def test_displayed_resolution_and_shipped_step_match_the_interface() -> None:
    """The two interface facts every figure here is quoted at are unchanged.

    The displayed resolution, because
    `test_displayed_ordering_reverses_only_at_a_crossing` measures a property
    of the rounded values and adding a decimal would change what it proves
    without changing anything it reads. The shipped step, because what this
    module measures is rounding accumulated once per step and because the step
    is when a setting change takes effect — `SHIPPED_STEP_S` carries both, and
    records that neither is the coefficient-times-step reason this docstring
    used to give.

    The delivered-concentration floor is here rather than with the supported
    ranges above because it is the only control the interface states in
    percent where the core's own guard is a fraction.

    The resolution is read from `app/formatting.py`, which declares it, and
    not from `app/simulation_view.py`, which imports it for a slider's drag
    label. Asserting against the importer would let this pass on an
    accidental re-export after the declaration moved again (PL-WB0X).
    """

    from anesthesia_sim.app import formatting, simulation_view

    assert (
        MIN_DELIVERED_CONCENTRATION_PERCENT,
        CONCENTRATION_DISPLAY_DECIMALS,
        SHIPPED_STEP_S,
    ) == (
        simulation_view.MIN_DELIVERED_CONCENTRATION_PERCENT,
        formatting.CONCENTRATION_DISPLAY_DECIMALS,
        simulation_view.SIMULATION_STEP_S,
    ), (
        "the interface's displayed resolution or simulation step has changed; "
        "re-run the trajectory sweeps and re-derive the measured figures in "
        "docs/MODEL.md"
    )


def _displayed_percent(fraction: float) -> float:
    """The value the interface shows for a fraction, at its own resolution."""

    return round(fraction * 100.0, CONCENTRATION_DISPLAY_DECIMALS)


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

    The six readouts sit in one row to be read *ordinally* — the circuit leads
    the alveoli lead the tissues — and an ordinal reading is corrupted only if
    the error flips which of two compartments is displayed as higher. An
    inversion while two compartments are crossing is not a defect: their true
    gap is then below what the display resolves, and the ordering is genuinely
    ambiguous. An inversion at a gap a reader would call a gradient is, and
    that is what this forbids.

    **What this measures, now that its threshold is derived rather than
    fitted.** `MAX_INVERTED_GAP_IN_DISPLAY_COUNTS` is a consequence of
    `EXACT_STEP_ORACLE_TOLERANCE` plus the monotonicity of
    `_displayed_percent`, so a failure here that was not also a failure of
    `test_exact_step_matches_the_independent_solution_everywhere` would mean
    the monotonicity assumption had broken — a display path that reorders, or
    a rounding rule that does. That is the part of the chain the absolute gate
    cannot see, and it is on the safety-critical side of the model-to-readout
    boundary. The derivation is written out where the constant is defined.

    Measured, there are no inversions at all: zero over 1 485 000 pair
    comparisons. The test keeps its gap-threshold shape rather than asserting
    that, because crossings really are sampled at gaps below the arithmetic —
    the smallest nonzero true gap seen is 2.354e-15 in fraction, below the
    1.104e-12 worst pairwise differential — so an inversion is reachable there
    and a zero-inversion assertion would turn a different libm into a failure.

    `docs/MODEL.md` § "Displayed precision" cites this test as the reason the
    interface marks nothing about comparing two compartments.
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
            system.advance(SHIPPED_STEP_S)

            for _ in range(round(SHIPPED_STEP_S / oracle_step_s)):
                reference = _rk4_step(derivative, reference, oracle_step_s)

            step_index += 1
            shipped_displayed = tuple(_displayed_percent(v) for v in _shipped_states(system))
            reference_displayed = tuple(_displayed_percent(v) for v in reference)

            for left in range(len(STATE_LABELS)):
                for right in range(left + 1, len(STATE_LABELS)):
                    shipped_order = _display_ordering(shipped_displayed, left, right)
                    reference_order = _display_ordering(reference_displayed, left, right)

                    # A tie on one side and an order on the other is the
                    # display resolving a gap the other side rounds away, not
                    # a reader being told the wrong compartment is higher.
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
        f"so either that gate is also failing or the display path has stopped "
        f"being monotone; docs/MODEL.md's 'Displayed precision' cites this "
        f"test as the reason the interface marks nothing about comparing two "
        f"compartments."
    )


def test_oracle_imports_no_solver_from_core() -> None:
    """Keep this file a verification rather than a tautology.

    The oracle must re-derive the model from parameters alone. Importing any
    solver from `core/` — a compartment's exact update, the coupled step
    itself — would make this module compare the implementation against
    itself and pass no matter how wrong the dynamics were.
    """

    module = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported_names = {
        alias.name
        for node in ast.walk(module)
        if isinstance(node, ast.ImportFrom)
        if (node.module or "").startswith("anesthesia_sim")
        for alias in node.names
    }

    assert imported_names <= ALLOWED_PACKAGE_IMPORTS, (
        "this module imports "
        f"{sorted(imported_names - ALLOWED_PACKAGE_IMPORTS)} from the package "
        "under test; the independent solution may use the parameter loaders "
        "only"
    )
