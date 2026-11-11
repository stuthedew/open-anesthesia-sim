"""A generated run keeps what must hold after every action, however its settings are drawn.

Every other test steps the model from listed settings, and most step it once.
This test draws a run instead (`PL-GJ1W`). It draws a shipped agent, or volumes
and partition coefficients from anywhere in the numerical envelope. It draws
the flows and the dial across their supported ranges and at their edges. It
then changes one setting at a time and steps up to `MOST_STEPS_IN_AN_ACTION`
times after each change. After every action it checks what must hold for any
run:

1. Every fraction lies from 0 through 1, and between the lowest and highest of
   the opening state and the delivered concentrations.
2. The agent held, delivered and exhausted balance.
3. Each running total equals the exactly rounded sum of its step amounts.
4. The state agrees with the exact solution of the linear system over the
   action, evaluated at 50 digits.
5. The stepped state agrees with the canonical state of the run definition.
6. A sampled window ends exactly at the instant asked for, and its last column
   agrees with the canonical state there.
7. A run that only ever raised its dial, from one starting fraction and with
   its flows unchanged, is never described as elimination.

The test then repeats the same actions on a fresh system and requires the same
bits.

Each comparison allows a stated amount of rounding. `_rounding` gives the
amount for a number of propagators, and each use says how many it counts.
Hypothesis is steered toward the draw with the largest difference relative to
its allowance. The draw is derandomized, so every run of the suite tests the
same plans.

For developers. A run that halts on the agent balance is accepted only where
its step needs at least one squaring, which `docs/MODEL.md` § "The numerical
envelope" documents (`PL-D88N`). No other refusal from a step is accepted.
"""

import math
import sys
from decimal import Context, Decimal
from typing import NamedTuple

from hypothesis import example, given, settings, target
from hypothesis import strategies as st
from test_numerical_envelope import _decimal_exponential, _squarings
from test_numerical_envelope_sweep import (
    CEILING,
    CEILING_DIAL_PERCENT,
    COEFFICIENT_CORNERS,
    MACHINE_EPSILON,
    PROPAGATOR_MARGIN,
    VOLUMES,
    Corner,
    _system,
)

from anesthesia_sim.app.wash_in import WashInDomain, read_wash_in
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import (
    AgentSimulationValidationError,
    SimulationConfigurationError,
)
from anesthesia_sim.core.governing_equations import (
    ALVEOLAR_FRACTION,
    DELIVERED_AGENT_L,
    EXHAUSTED_AGENT_L,
    FIRST_TISSUE_FRACTION,
    INSPIRED_FRACTION,
    STATE_SIZE,
    UNIT_STATE,
    VENOUS_FRACTION,
    UptakeEquationSettings,
    build_system_matrix,
)
from anesthesia_sim.core.matrix_exponential import Matrix
from anesthesia_sim.core.numerical_envelope import MAXIMUM_VOLUME_L, MINIMUM_VOLUME_L
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES
from anesthesia_sim.core.run_definition import RunDefinition
from anesthesia_sim.core.simulation_step import (
    MAXIMUM_SIMULATION_STEP_S,
    MINIMUM_SIMULATION_STEP_S,
    SimulationStep,
)
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
)
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

EXAMPLES = 100
"""How many runs each run of the suite draws.

The weekly job that `PL-GJ1W` plans draws more, and runs the full 24 hours.
"""

MOST_ACTIONS = 4
"""The most actions in one run. Each action changes at most one setting and then steps."""

MOST_STEPS_IN_AN_ACTION = 2_000
"""The most steps one action takes.

A run then takes at most 8 000 steps, which is 800 s at the interface's 0.1 s
step. Growth that needs millions of steps is out of this test's reach.
"""

MOST_COLUMNS = 60
"""The most columns a sampled window has, as in `test_numerical_envelope_sweep.py`."""

ACCOUNTING_RELATIVE_TOLERANCE = 1e-9
"""The agent balance must close to one part in 10**9 of the agent the run has to account for.

This is a published limit and not a rounding limit. `docs/MODEL.md`
§ "Mass-balance identity" states it as the tolerance at which the model halts a
run. It is written here as a literal so that a change to the model's constant
fails this test.
"""

RUNNING_TOTAL_RELATIVE_ALLOWANCE = 2.0 * sys.float_info.epsilon
"""How far a compensated running total may lie from the exactly rounded sum of its terms.

This is a rounding limit. Kahan's compensated sum of terms x_j equals the sum
of x_j(1 + d_j) with each |d_j| at most 2**-52, plus a term of order
N * 2**-106 (Goldberg D. What every computer scientist should know about
floating-point arithmetic. ACM Comput Surv 1991;23(1):5-48, Theorem 8, p. 46).
Every term here is nonnegative, so the total lies within 2**-52 of the exact
sum, relative to that sum. The allowance is twice that, which leaves room for
the rounding of the exact sum itself. A plain running sum of 2 000 terms
exceeds it.
"""

SMALLEST_FULL_PRECISION_SCALE = sys.float_info.min / sys.float_info.epsilon
"""The smallest magnitude a difference is measured against, about 1e-292.

Below the smallest normal float, 2.2e-308, a value is stored with fewer than 53
bits, so its rounding is no longer a fixed share of its size. A run that opens
at a fraction of 2e-311 would otherwise be held to a share of 2e-311, which is
finer than the spacing of the floats there. Measuring against this scale
allows a difference of about 1e-307 for each step, which is still some 300
orders of magnitude below any displayed digit.
"""

SETTINGS = ("hold", "fresh gas flow", "alveolar ventilation", "cardiac output", "dial")
"""What one action may change. "hold" changes nothing and only steps."""


class Action(NamedTuple):
    """One setting moved to a position in its supported range, then a number of steps."""

    setting: str
    position: float
    steps: int


class Plan(NamedTuple):
    """One generated run: where it opens, its step and what is done to it.

    Each position is a share of the setting's supported range, from 0 at its
    lower edge to 1 at its upper edge. `agent_id` names a shipped agent, opened
    with no agent in any compartment. `corner` gives the volumes and
    coefficients of a run that is not a shipped agent's, opened with every
    compartment at `opening_fraction`.
    """

    agent_id: str | None
    corner: Corner | None
    opening_fraction: float
    flows: tuple[float, float, float]
    dial: float
    step_s: float
    actions: tuple[Action, ...]
    window_start: float
    columns: int


_POSITIONS = st.sampled_from((0.0, 1.0)) | st.floats(0.0, 1.0)

_VOLUMES_L = st.sampled_from(VOLUMES) | st.floats(-2.0, 4.0).map(
    lambda exponent: min(max(10.0**exponent, MINIMUM_VOLUME_L), MAXIMUM_VOLUME_L)
)

# Away from the corners, a blood:gas coefficient from 1e-2 to 1e3 and a
# tissue:blood coefficient from about 0.13 to 7.9 keep their product, the
# tissue:gas coefficient, inside the envelope of 1e-3 to 1e4.
_COEFFICIENTS = st.sampled_from(COEFFICIENT_CORNERS) | st.tuples(
    st.floats(-2.0, 3.0).map(lambda exponent: 10.0**exponent),
    st.floats(-0.9, 0.9).map(lambda exponent: 10.0**exponent),
)

_STEPS_S = st.sampled_from((MAXIMUM_SIMULATION_STEP_S, MINIMUM_SIMULATION_STEP_S)) | st.floats(
    MINIMUM_SIMULATION_STEP_S, MAXIMUM_SIMULATION_STEP_S
)

_ACTIONS = st.builds(
    Action,
    setting=st.sampled_from(SETTINGS),
    position=_POSITIONS,
    steps=st.integers(1, MOST_STEPS_IN_AN_ACTION),
)


@st.composite
def _plans(draw: st.DrawFn) -> Plan:
    agent_id = draw(st.none() | st.sampled_from(tuple(AGENT_DATA_FILENAMES)))
    corner = None
    opening_fraction = 0.0

    if agent_id is None:
        circuit_l, alveolar_l, venous_l, tissue_l = (draw(_VOLUMES_L) for _ in range(4))
        blood_gas, tissue_blood = draw(_COEFFICIENTS)
        corner = Corner(circuit_l, alveolar_l, venous_l, tissue_l, blood_gas, tissue_blood)
        opening_fraction = draw(_POSITIONS) * CEILING

    return Plan(
        agent_id=agent_id,
        corner=corner,
        opening_fraction=opening_fraction,
        flows=(draw(_POSITIONS), draw(_POSITIONS), draw(_POSITIONS)),
        dial=draw(_POSITIONS),
        step_s=draw(_STEPS_S),
        actions=tuple(draw(st.lists(_ACTIONS, min_size=1, max_size=MOST_ACTIONS))),
        window_start=draw(st.floats(0.0, 0.9)),
        columns=draw(st.integers(2, MOST_COLUMNS)),
    )


def _rounding(squarings: int, propagators: float) -> float:
    """Return the relative rounding allowed after `propagators` propagators of `squarings` each.

    `core/matrix_exponential.py` bounds one propagator's relative error at
    about 2**squarings times double precision's 2**-52. `PROPAGATOR_MARGIN` is
    the factor of three that the envelope sweep allows on that bound.

    The stepped path counts one propagator for every step, so its allowance
    grows in proportion to the number of steps. A rule of thumb that grows as
    the square root of the number of steps was tried first and is too small.
    A state held at equilibrium in a 10 000 L tissue drifted by 1.6e-12 over
    4 308 steps, which is 0.57 of this allowance and 38 times the square-root
    one (measured 2026-11-11). Such a slow compartment does not pull the state
    back, so each step's rounding adds to the last.
    """

    return PROPAGATOR_MARGIN * 2.0**squarings * MACHINE_EPSILON * propagators


def _largest_dial_percent(settings_now: UptakeEquationSettings) -> float:
    """Return the highest dial the run accepts: its vaporizer's maximum, or the input ceiling."""

    return min(float(settings_now.max_delivered_concentration_percent), CEILING_DIAL_PERCENT)


def _build(plan: Plan) -> AgentUptakeSystem:
    fresh_gas = plan.flows[0] * MAXIMUM_FRESH_GAS_FLOW_L_MIN
    ventilation = plan.flows[1] * MAXIMUM_ALVEOLAR_VENTILATION_L_MIN
    cardiac_output = plan.flows[2] * MAXIMUM_CARDIAC_OUTPUT_L_MIN

    if plan.corner is not None:
        return _system(
            plan.corner,
            (fresh_gas, ventilation, cardiac_output),
            plan.opening_fraction,
            plan.dial * CEILING_DIAL_PERCENT,
        )

    assert plan.agent_id is not None
    system = AgentUptakeSystem.for_agent(plan.agent_id)
    system.set_fresh_gas_flow(FreshGasFlow(fresh_gas))
    system.set_alveolar_ventilation(AlveolarVentilation(ventilation))
    system.set_cardiac_output(CardiacOutput(cardiac_output))
    system.set_delivered_concentration_percent(
        Percent(plan.dial * _largest_dial_percent(system.equation_settings()))
    )

    return system


def _apply(system: AgentUptakeSystem, action: Action) -> None:
    if action.setting == "fresh gas flow":
        system.set_fresh_gas_flow(FreshGasFlow(action.position * MAXIMUM_FRESH_GAS_FLOW_L_MIN))
    elif action.setting == "alveolar ventilation":
        system.set_alveolar_ventilation(
            AlveolarVentilation(action.position * MAXIMUM_ALVEOLAR_VENTILATION_L_MIN)
        )
    elif action.setting == "cardiac output":
        system.set_cardiac_output(CardiacOutput(action.position * MAXIMUM_CARDIAC_OUTPUT_L_MIN))
    elif action.setting == "dial":
        system.set_delivered_concentration_percent(
            Percent(action.position * _largest_dial_percent(system.equation_settings()))
        )


def _held_agent_l(settings_now: UptakeEquationSettings, state: tuple[float, ...]) -> float:
    """Return the agent held in the compartments, in litres of gas, from the settings and the state.

    Each gas compartment holds its volume times its fraction. The venous pool
    holds its volume times the blood:gas coefficient times its fraction. Each
    tissue holds its volume times its tissue:gas coefficient times its fraction
    (`docs/MODEL.md` § "Governing equations"). This is computed here and not
    read from the system under test.
    """

    blood_gas = settings_now.blood_gas_partition_coefficient

    return (
        settings_now.circuit_volume_l * state[INSPIRED_FRACTION]
        + settings_now.alveolar_volume_l * state[ALVEOLAR_FRACTION]
        + settings_now.venous_volume_l * blood_gas * state[VENOUS_FRACTION]
        + sum(
            tissue.volume_l
            * tissue.tissue_blood_partition_coefficient
            * blood_gas
            * state[FIRST_TISSUE_FRACTION + index]
            for index, tissue in enumerate(settings_now.tissues)
        )
    )


def _exact_state(
    matrix: Matrix, state: tuple[float, ...], step_s: float, steps: int
) -> list[Decimal]:
    """Return the state after `steps` steps of exactly `step_s`, from `state`, at 50 digits.

    Between two setting changes the model is a linear system with constant
    coefficients, so its exact solution is the matrix exponential applied to
    the state. The interval is the exact product of the binary step and the
    number of steps, so the reference covers the same time as the stepped run.
    """

    interval_s = Context(prec=60).multiply(Decimal(step_s), Decimal(steps))
    propagator = _decimal_exponential(matrix, str(interval_s))

    return [
        sum(propagator[row][column] * Decimal(state[column]) for column in range(STATE_SIZE))
        for row in range(STATE_SIZE)
    ]


class Residuals:
    """The largest difference each check has seen, as a multiple of its rounding allowance."""

    def __init__(self, *, enforce: bool) -> None:
        self.enforce = enforce
        self.worst: dict[str, float] = {}

    def record(self, check: str, difference: float, allowance: float, context: object) -> None:
        if difference == 0.0:
            ratio = 0.0
        elif allowance > 0.0:
            ratio = difference / allowance
        else:
            ratio = math.inf

        self.worst[check] = max(self.worst.get(check, 0.0), ratio)

        if self.enforce:
            assert ratio <= 1.0, (
                f"{check}: a difference of {difference!r} is {ratio:.3g} times its rounding "
                f"allowance of {allowance!r}; {context}"
            )


class _Run:
    """One generated run as it is executed: the stepped system, its definition and its history."""

    def __init__(self, plan: Plan) -> None:
        self.plan = plan
        self.system = _build(plan)
        self.settings = self.system.equation_settings()
        opening = self.system.state_vector()
        self.definition = RunDefinition(self.settings, opening, opened_at_s=CaseInstant(0.0))
        self.opening_held_l = _held_agent_l(self.settings, opening)
        self.dial_fraction = float(self.settings.delivered_concentration_percent) / 100.0
        fractions = opening[:DELIVERED_AGENT_L]
        self.lowest = min(*fractions, self.dial_fraction)
        self.highest = max(*fractions, self.dial_fraction)
        # With one starting fraction at or below the dial, constant flows and a
        # dial that only rises, every compartment rises toward the dial and the
        # alveolar fraction never passes the inspired one.
        self.only_washes_in = max(fractions) <= self.dial_fraction
        self.steps = 0
        self.delivered_l: list[float] = []
        self.exhausted_l: list[float] = []
        self.matrices = [build_system_matrix(self.settings)]
        self.segment_opened_s = 0.0
        self.closed_time_rounding = 0.0
        self.most_step_squarings = 0
        self.most_canonical_squarings = 0

    @property
    def elapsed_s(self) -> float:
        """The instant the run has reached, formed as the application forms it: steps times step."""

        return self.steps * self.plan.step_s

    def state(self) -> tuple[float, ...]:
        """Return the stepped state with the running totals in its two accumulated-amount entries.

        `AgentUptakeSystem.state_vector` leaves those two entries at zero,
        because the validator owns the running totals. The run definition's
        states carry the totals since the run opened, so this is the stepped
        state in the same form.
        """

        state = list(self.system.state_vector())
        accounting = self.system.agent_simulation_validation
        state[DELIVERED_AGENT_L] = accounting.delivered_agent_l
        state[EXHAUSTED_AGENT_L] = accounting.exhausted_agent_l

        return tuple(state)

    def _time_rounding_of_the_open_segment(self) -> float:
        """Return how far rounding of the clock can move a reading, as a share of its range.

        The run definition measures a segment as the difference of two rounded
        instants, which can differ from the stepped interval by one unit in the
        last place of the later instant. A reading moves fastest when a mode's
        time constant equals the interval, and then by less than that time
        error divided by the interval.
        """

        interval_s = self.elapsed_s - self.segment_opened_s

        return math.ulp(self.elapsed_s) / interval_s if interval_s > 0.0 else 0.0

    def change(self, action: Action) -> None:
        """Apply one action's setting, and record it in the run definition if it changed."""

        _apply(self.system, action)
        changed = self.system.equation_settings()

        if changed == self.settings:
            return

        dial_fraction = float(changed.delivered_concentration_percent) / 100.0

        # An unchanged dial means that a flow changed. After a flow change or a
        # lowered dial, the alveolar fraction may truly pass the inspired one.
        if dial_fraction <= self.dial_fraction:
            self.only_washes_in = False

        self.most_canonical_squarings = max(
            self.most_canonical_squarings,
            _squarings(self.matrices[-1], self.elapsed_s - self.segment_opened_s),
        )
        self.closed_time_rounding += self._time_rounding_of_the_open_segment()
        self.definition.record_change(changed)
        self.segment_opened_s = self.elapsed_s
        self.settings = changed
        self.dial_fraction = dial_fraction
        self.lowest = min(self.lowest, dial_fraction)
        self.highest = max(self.highest, dial_fraction)
        self.matrices.append(build_system_matrix(changed))

    def step(self, steps: int) -> bool:
        """Take `steps` steps. Return False where the run halts as `docs/MODEL.md` documents."""

        step = SimulationStep(self.plan.step_s)
        squarings = _squarings(self.matrices[-1], self.plan.step_s)
        self.most_step_squarings = max(self.most_step_squarings, squarings)

        for _ in range(steps):
            try:
                result = self.system.advance(step)
            except AgentSimulationValidationError:
                # `PL-D88N`: the fixed balance tolerance halts a stepped run
                # only where the step's propagator needs squarings.
                if squarings == 0:
                    raise

                return False

            self.delivered_l.append(result.fresh_gas_exchange.delivered_agent_l)
            self.exhausted_l.append(result.fresh_gas_exchange.exhausted_agent_l)
            self.steps += 1

        self.definition.advance_to(CaseInstant(self.elapsed_s))

        return True

    def _scales(self, owed_l: float) -> tuple[float, ...]:
        """Return what each state entry's difference is measured against.

        A fraction is measured against the highest fraction the run can hold,
        and an accumulated amount against the agent the run has to account for.
        """

        scales = [max(self.highest, SMALLEST_FULL_PRECISION_SCALE)] * STATE_SIZE
        scales[DELIVERED_AGENT_L] = max(owed_l, SMALLEST_FULL_PRECISION_SCALE)
        scales[EXHAUSTED_AGENT_L] = scales[DELIVERED_AGENT_L]
        scales[UNIT_STATE] = 1.0

        return tuple(scales)

    def check(self, before: tuple[float, ...], action: Action, residuals: Residuals) -> None:
        """Check everything that must hold once `action` has run from the state `before`."""

        state = self.state()
        context = f"after {self.steps} steps of {self.plan}, at {state}"
        stepped = _rounding(self.most_step_squarings, self.steps)

        assert all(math.isfinite(value) for value in state), context

        for fraction in state[:DELIVERED_AGENT_L]:
            assert 0.0 <= fraction <= 1.0, context
            residuals.record(
                "a fraction outside the opening state and the delivered concentrations",
                max(fraction - self.highest, self.lowest - fraction, 0.0),
                stepped * max(self.highest, SMALLEST_FULL_PRECISION_SCALE),
                context,
            )

        owed_l = self.opening_held_l + state[DELIVERED_AGENT_L]
        unaccounted_l = owed_l - state[EXHAUSTED_AGENT_L] - _held_agent_l(self.settings, state)
        residuals.record(
            "the agent balance",
            abs(unaccounted_l),
            ACCOUNTING_RELATIVE_TOLERANCE * max(owed_l, SMALLEST_FULL_PRECISION_SCALE),
            context,
        )

        for total_l, amounts_l in (
            (state[DELIVERED_AGENT_L], self.delivered_l),
            (state[EXHAUSTED_AGENT_L], self.exhausted_l),
        ):
            exact_l = math.fsum(amounts_l)
            residuals.record(
                "a running total against the exact sum of its step amounts",
                abs(total_l - exact_l),
                RUNNING_TOTAL_RELATIVE_ALLOWANCE * exact_l,
                context,
            )

        scales = self._scales(owed_l)
        exact = _exact_state(self.matrices[-1], before, self.plan.step_s, action.steps)
        over_the_action = _rounding(_squarings(self.matrices[-1], self.plan.step_s), action.steps)

        for value, reference, scale in zip(state, exact, scales, strict=True):
            residuals.record(
                "the stepped state against the 50-digit solution over the action",
                float(abs(Decimal(value) - reference)),
                over_the_action * scale,
                context,
            )

        canonical_squarings = max(
            self.most_canonical_squarings,
            _squarings(self.matrices[-1], self.elapsed_s - self.segment_opened_s),
        )
        time_rounding = self.closed_time_rounding + self._time_rounding_of_the_open_segment()
        canonical_allowance = (
            stepped + _rounding(canonical_squarings, len(self.matrices)) + time_rounding
        )

        try:
            canonical = self.definition.state_at(self.elapsed_s)
        except SimulationConfigurationError as refusal:
            # One propagator over a long stretch at a stiff corner needs more
            # squarings than the module allows, and says so.
            assert "squarings" in str(refusal), refusal
            canonical = None

        if canonical is not None:
            for value, other, scale in zip(state, canonical, scales, strict=True):
                residuals.record(
                    "the stepped state against the canonical state",
                    abs(value - other),
                    canonical_allowance * scale,
                    context,
                )

        self._check_the_window(canonical, canonical_allowance, scales, residuals, context)

        if self.only_washes_in:
            reading = read_wash_in(state[ALVEOLAR_FRACTION], state[INSPIRED_FRACTION])

            assert reading.domain is not WashInDomain.ELIMINATION, (
                f"a run that only washes in is described as elimination; {context}"
            )

    def _check_the_window(
        self,
        canonical: tuple[float, ...] | None,
        canonical_allowance: float,
        scales: tuple[float, ...],
        residuals: Residuals,
        context: str,
    ) -> None:
        """Sample a window that ends where the run stands, and check its last column."""

        start_s = self.plan.window_start * self.elapsed_s
        columns = self.plan.columns

        try:
            window = self.definition.evaluate(start_s, self.elapsed_s, columns)
        except SimulationConfigurationError as refusal:
            assert "squarings" in str(refusal), refusal
            return

        assert window.times_s[0] == start_s, context
        assert window.times_s[-1] == self.elapsed_s, (
            f"the last column is at {window.times_s[-1]!r} and not at the "
            f"{self.elapsed_s!r} asked for; {context}"
        )

        if canonical is None:
            return

        spacing_s = (self.elapsed_s - start_s) / (columns - 1)
        column_squarings = max(_squarings(matrix, spacing_s) for matrix in self.matrices)
        # The window chains one propagator per column, and one more at each
        # setting change inside it. Its last column is pinned to the instant
        # asked for, which can differ from the chained time by one rounding.
        allowance = (
            canonical_allowance
            + _rounding(column_squarings, columns + len(self.matrices))
            + math.ulp(self.elapsed_s) / spacing_s
        )

        for value, other, scale in zip(window.states[-1].values, canonical, scales, strict=True):
            residuals.record(
                "a window's last column against the canonical state",
                abs(value - other),
                allowance * scale,
                context,
            )


def _execute(plan: Plan, residuals: Residuals | None) -> tuple[str, ...]:
    """Run `plan`, checking after every action when `residuals` is given.

    Returns:
        The final state, each value written in hexadecimal so that two runs
        compare bit for bit.
    """

    run = _Run(plan)

    for action in plan.actions:
        run.change(action)
        before = run.state()

        if not run.step(action.steps):
            break

        if residuals is not None:
            run.check(before, action, residuals)

    return tuple(value.hex() for value in run.state())


SMALLEST_CORNER = Corner(
    circuit_l=MINIMUM_VOLUME_L,
    alveolar_l=MINIMUM_VOLUME_L,
    venous_l=MINIMUM_VOLUME_L,
    tissue_l=MINIMUM_VOLUME_L,
    blood_gas=1e-3,
    tissue_blood=1.0,
)
"""Every volume at the envelope's 0.01 L floor, with the lowest blood:gas coefficient."""

STIFFEST_CORNER = SMALLEST_CORNER._replace(blood_gas=1e4, tissue_blood=1e-3)
"""Every volume at 0.01 L with a blood:gas coefficient of 1e4, where a step needs squarings."""

ONE_STEP = (Action(setting="hold", position=0.0, steps=1),)


# The three plans below are conditions that the drawn plans reach only after
# 300 to 1 000 draws (measured 2026-11-11, `PL-GJ1W`). They are listed so that
# every run of the suite covers them.
@example(
    # `PL-N559`: with no flow at all, one step moves the alveolar fraction one
    # rounding above the inspired fraction.
    Plan(None, SMALLEST_CORNER, 0.5 * CEILING, (0.0, 0.0, 0.0), 1.0, 0.1, ONE_STEP, 0.0, 2)
)
@example(
    # `PL-9B1M`: every compartment at the input ceiling, at the corner where
    # one step with blood flow alone rounded a fraction upward.
    Plan(None, SMALLEST_CORNER, CEILING, (0.0, 0.0, 1.0), 0.0, 0.1, ONE_STEP, 0.0, 2)
)
@example(
    # `PL-D88N`: the same opening at the stiffest corner, which halts on the
    # agent balance within about 24 steps.
    Plan(
        None,
        STIFFEST_CORNER,
        CEILING,
        (0.0, 0.0, 1.0),
        0.0,
        0.1,
        (Action(setting="hold", position=0.0, steps=50),),
        0.0,
        2,
    )
)
@settings(derandomize=True, database=None, deadline=None, max_examples=EXAMPLES)
@given(_plans())
def test_a_generated_run_keeps_what_must_hold_after_every_action(plan: Plan) -> None:
    """Every check in the module docstring holds, and a replay of the plan gives the same bits.

    The expected values come from outside the stepped system: the opening state
    and the dials for the range of a fraction, the settings for the agent held,
    an exact sum for each running total, and a 50-digit matrix exponential for
    the state. An error larger than a comparison's stated rounding allowance
    fails it. An error inside that allowance passes, so this test does not show
    that a value is right in its last digits.
    """

    residuals = Residuals(enforce=True)
    final = _execute(plan, residuals)

    target(
        max(residuals.worst.values(), default=0.0),
        label="the largest difference, as a multiple of its rounding allowance",
    )

    assert _execute(plan, None) == final
