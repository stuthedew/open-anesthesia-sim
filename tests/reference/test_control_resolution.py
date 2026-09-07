"""Measure what a late control change costs, and hold the published table to it.

`MAXIMUM_SIMULATION_STEP_S` stopped being a numerical limit at `PL-X9KD`: the
exact step has no truncation error at any step size, so there is no accuracy
domain left to be outside of. What the constant declares instead is a
*control-resolution tolerance* — settings are held constant across a step, so
the step is the interval over which a control change is invisible to the model,
and a change is displaced later by up to one whole step.

That makes the tolerance a measurement rather than a definition, and
`docs/MODEL.md` § "Supported simulation step" publishes it as one: three
manoeuvres, worst displacement over all three agents, in percentage points of
one atmosphere. `core/uptake_system.py` repeats two of the figures in the
comment deriving the constant. Until this module they were held by prose in two
files and by nothing else, so a change to the governing equations, to a
partition coefficient, to the reference adult's volumes or to the supported
input envelope would have moved them silently: `make check` would pass, both
documents would keep asserting the old figures, and the tolerance a reader is
told the tool holds to would no longer be the one it holds to (`PL-ZVS7`).

**What is measured, precisely.** The same manoeuvre is driven twice from an
empty system, in lockstep, differing only in when the control change lands: on
time at the phase boundary, and `delay_s` later. The displacement is the
largest absolute difference between any of the six displayed compartments at
any step boundary, converted to percentage points. That is exactly the quantity
the tables name — the cost of a control action the model resolves one grid step
late — and nothing else enters it.

**This is a self-comparison, deliberately, and it is not the gate in
`test_coupled_dynamics.py`.** That module checks the shipped solution against
an independent integration and its whole premise is that the oracle shares no
code with the core. Here both runs are the shipped system: the quantity is a
difference between two schedules of the *same* solver, so an independent
solution would answer a different question. Nothing here verifies that the
equations are solved correctly; `test_coupled_dynamics.py` is what does that,
and this module measures a property of a solution it assumes correct.

**Constants are imported rather than restated, for the same reason.** With no
independence to protect, importing `core.supported_ranges` makes "at the
envelope corner" track the model's own declared domain: widening a supported
range moves the manoeuvre, moves the measurement, and fails here — which is
right, because the published tolerance would genuinely have changed. The
circuit volume is left at the model's own default for the same reason.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

import pytest

from anesthesia_sim.app.playback import SUPPORTED_PLAYBACK_RATES, PlaybackRate
from anesthesia_sim.core import supported_ranges
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.uptake_system import MAXIMUM_SIMULATION_STEP_S, AgentUptakeSystem

AGENT_IDS = ("sevoflurane", "isoflurane", "desflurane")

#: The six compartments the interface displays, in the order `STATE_LABELS`
#: gives them. The tolerance is stated over "every displayed compartment", so
#: the set this reads is what makes that phrase mean something.
STATE_LABELS = ("circuit", "alveolar", "mixed venous", "vessel rich", "muscle", "fat")

#: The step every figure below was measured at, and the step the interface
#: runs at. `test_the_tolerance_is_measured_at_the_supported_step` holds it to
#: `MAXIMUM_SIMULATION_STEP_S`: since `PL-NBCJ` that constant is an argued
#: decision with three recorded reasons rather than a default, and every figure
#: in both published tables is measured *at* it, so the two cannot be allowed
#: to part company.
SHIPPED_STEP_S = 0.1

#: The interface's run-loop tick, restated rather than imported from
#: `app/simulation_view.py`, which needs Flet. `test_simulation_view.py` holds
#: the shipped constant to this value, so a change there fails there; the same
#: restatement is made for the same reason in `tests/unit/test_playback.py`.
TICK_INTERVAL_S = 0.1

#: The fresh gas flow the case-opening manoeuvre runs at. "Reference flows" in
#: the published table is this together with the reference adult's own default
#: ventilation and cardiac output, which are read from the patient file below.
REFERENCE_FRESH_GAS_FLOW_L_MIN = 4.0

#: Simulated seconds each run is carried past its own control change.
#:
#: The worst displacement falls on the first step after the *late* run's change
#: lands — until then the on-time run has been diverging for the whole delay and
#: the late run has not started, and afterwards the two relax onto the same
#: trajectory — so what this has to be is comfortably clear of that instant
#: rather than long enough to contain a transient. Measured: at the largest
#: grid step this module drives (30 s), carrying every manoeuvre 120 s, 300 s
#: and 600 s past the change returns the same figure to six significant
#: digits. 120 s is four times the largest delay and is the value kept.
SETTLE_S = 120.0

#: How far a measurement may sit from the figure `docs/MODEL.md` prints and
#: still be the figure it prints.
#:
#: Both tables are published to two significant figures, so half a unit in the
#: last printed digit is up to 5% of the value — at 1.0x10^1 pp exactly that.
#: A measurement inside this band is a value the document already states; one
#: outside it is a value the document no longer states, which is the failure
#: this module exists to catch. Tightening it would pin digits `docs/MODEL.md`
#: does not publish, and a drift smaller than the publication's own precision
#: does not make a reader's understanding of the tolerance wrong.
PUBLICATION_RELATIVE_TOLERANCE = 0.05


@dataclass(frozen=True)
class OperatingPoint:
    """The four settings the interface can move, at one instant."""

    delivered_fraction: float
    fresh_gas_flow_l_min: float
    alveolar_ventilation_l_min: float
    cardiac_output_l_min: float


@dataclass(frozen=True)
class Manoeuvre:
    """One control action: settings held, then changed once.

    A single change is what the tolerance is defined over — it is the cost of
    *a* control action landing late — so each manoeuvre here has exactly one
    boundary, and `hold_s` is where it falls.
    """

    before: OperatingPoint
    after: OperatingPoint
    hold_s: float


def _case_opening(agent_id: str) -> Manoeuvre:
    """Dial off to 1 MAC at reference flows: the ordinary action, not an extreme.

    This is the row that decides whether the step is fine enough for what a
    reader actually does, so it is deliberately not an envelope corner: the
    reference adult's own ventilation and cardiac output, a 4 L/min fresh gas
    flow, and a dial moved from closed to one MAC of the agent in use.

    Nothing happens before the change — the dial is closed and the system
    starts empty, so no agent enters and all six compartments sit at zero for
    the whole hold. `test_the_case_opening_starts_from_an_empty_system` asserts
    that rather than leaving it to be assumed, which is what lets the hold be
    short enough to be cheap without changing the state the change acts on.
    """

    patient = load_reference_adult_parameters()
    closed = OperatingPoint(
        delivered_fraction=0.0,
        fresh_gas_flow_l_min=REFERENCE_FRESH_GAS_FLOW_L_MIN,
        alveolar_ventilation_l_min=patient.default_alveolar_ventilation_l_min,
        cardiac_output_l_min=patient.default_cardiac_output_l_min,
    )
    one_mac = load_agent_parameters(agent_id).mac_percent / 100.0

    return Manoeuvre(closed, _with_dial(closed, one_mac), hold_s=60.0)


def _unperfused_load_then_dial_off(agent_id: str) -> Manoeuvre:
    """Fill circuit and lungs with no circulation, then restore it and dial off.

    The widest spread of initial states the four sliders can set up: with
    cardiac output at zero the circuit and alveoli saturate at the dial setting
    while every blood and tissue compartment stays empty, and turning perfusion
    on and the vaporizer off in the same move makes every compartment's
    equilibrium the opposite of where it sits.

    The ten-minute hold is what saturates it, and is the same hold
    `test_coupled_dynamics.py` drives this manoeuvre with; shortening it would
    change the state the control change acts on and so the figure measured.
    """

    return Manoeuvre(
        before=OperatingPoint(
            delivered_fraction=_max_dial(agent_id),
            fresh_gas_flow_l_min=supported_ranges.MAXIMUM_FRESH_GAS_FLOW_L_MIN,
            alveolar_ventilation_l_min=supported_ranges.MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
            cardiac_output_l_min=supported_ranges.MINIMUM_CARDIAC_OUTPUT_L_MIN,
        ),
        after=OperatingPoint(
            delivered_fraction=0.0,
            fresh_gas_flow_l_min=supported_ranges.MAXIMUM_FRESH_GAS_FLOW_L_MIN,
            alveolar_ventilation_l_min=supported_ranges.MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
            cardiac_output_l_min=supported_ranges.MAXIMUM_CARDIAC_OUTPUT_L_MIN,
        ),
        hold_s=600.0,
    )


def _ventilator_start(agent_id: str) -> Manoeuvre:
    """Prime the circuit with the ventilator off, then start ventilating.

    The binding row of both tables. The vaporizer is open and fresh gas is
    running while alveolar ventilation is still zero, so the circuit fills to
    the dial setting against lungs that cannot take any of it; starting
    ventilation then presents the largest circuit-to-alveolar gradient the
    machine can produce, at the largest ventilation it can produce.

    Five minutes is far longer than the circuit needs — at 10 L/min into 6 L
    its time constant is 36 s — so the hold ends saturated and the figure does
    not depend on exactly how long it ran.
    """

    corner = OperatingPoint(
        delivered_fraction=_max_dial(agent_id),
        fresh_gas_flow_l_min=supported_ranges.MAXIMUM_FRESH_GAS_FLOW_L_MIN,
        alveolar_ventilation_l_min=supported_ranges.MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
        cardiac_output_l_min=supported_ranges.MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    )

    return Manoeuvre(
        before=_with_ventilation(corner, supported_ranges.MINIMUM_ALVEOLAR_VENTILATION_L_MIN),
        after=corner,
        hold_s=300.0,
    )


#: The three manoeuvres `docs/MODEL.md` § "Supported simulation step" tabulates,
#: with the displacement each is published as producing at the shipped step and
#: the agent published as binding it.
#:
#: The figures are written out rather than computed, which is the whole point:
#: these are the numbers a reader is told, so they are the numbers to fail
#: against. Two of the three manoeuvres are `SETTING_CHANGE_SCENARIOS` in
#: `test_coupled_dynamics.py` and are restated here rather than imported,
#: because what defines them for this measurement is the table's own prose -
#: that module drives them to answer a different question and is free to change
#: them for its own reasons.
PUBLISHED_TOLERANCE = {
    "case opening": (_case_opening, 6.7e-3, "desflurane"),
    "unperfused load then dial off": (_unperfused_load_then_dial_off, 5.0e-2, "desflurane"),
    "ventilator start": (_ventilator_start, 1.4e-1, "desflurane"),
}

#: The worst displacement per grid step at each playback rate the interface
#: offers, from the second table in the same section - the one `PL-NBWP` added
#: when it established that the interface waits one *step* for a control change
#: only at 1x, and `multiplier x 0.1` s above it.
#:
#: Keyed by multiplier rather than by delay so that a rung added to the ladder
#: without a measured displacement fails here, and a row published for a rung
#: nobody can select fails too. The 1x entry is the ventilator-start row of the
#: table above, which is the consistency between the two tables.
PUBLISHED_DISPLACEMENT_PER_GRID_STEP_PP = {1: 1.4e-1, 5: 7.0e-1, 20: 2.5, 60: 5.8, 300: 1.0e1}

#: What the case opening reaches at the coarsest grid the interface offers.
#: Published in the prose beneath the per-rate table, as the measure of how
#: much milder an ordinary action is than the binding one.
PUBLISHED_CASE_OPENING_AT_300X_PP = 1.5


def _max_dial(agent_id: str) -> float:
    """The agent's own vaporizer maximum, as a fraction."""

    return load_agent_parameters(agent_id).max_delivered_concentration_percent / 100.0


def _with_dial(point: OperatingPoint, delivered_fraction: float) -> OperatingPoint:
    """`point` with the vaporizer moved and nothing else."""

    return OperatingPoint(
        delivered_fraction=delivered_fraction,
        fresh_gas_flow_l_min=point.fresh_gas_flow_l_min,
        alveolar_ventilation_l_min=point.alveolar_ventilation_l_min,
        cardiac_output_l_min=point.cardiac_output_l_min,
    )


def _with_ventilation(point: OperatingPoint, alveolar_ventilation_l_min: float) -> OperatingPoint:
    """`point` with the ventilator moved and nothing else."""

    return OperatingPoint(
        delivered_fraction=point.delivered_fraction,
        fresh_gas_flow_l_min=point.fresh_gas_flow_l_min,
        alveolar_ventilation_l_min=alveolar_ventilation_l_min,
        cardiac_output_l_min=point.cardiac_output_l_min,
    )


def _system_at(agent_id: str, point: OperatingPoint) -> AgentUptakeSystem:
    """An empty system with every slider at `point`.

    The circuit volume is left at the model's own default rather than set here:
    the tolerance is a property of the rig that ships, so a change to it should
    move this measurement.
    """

    system = AgentUptakeSystem.for_agent(agent_id)
    _apply(system, point)

    return system


def _apply(system: AgentUptakeSystem, point: OperatingPoint) -> None:
    """Move every slider to `point`, leaving compartment contents untouched.

    This is what the interface does when a slider moves mid-run, and it is the
    only thing that happens at the manoeuvre's boundary: the settings change,
    the state does not.
    """

    system.set_fresh_gas_flow(point.fresh_gas_flow_l_min)
    system.set_alveolar_ventilation(point.alveolar_ventilation_l_min)
    system.set_cardiac_output(point.cardiac_output_l_min)
    system.set_delivered_concentration(point.delivered_fraction)


def _displayed_states(system: AgentUptakeSystem) -> tuple[float, ...]:
    """Read the six displayed compartments, in `STATE_LABELS` order."""

    patient = system.patient

    return (
        system.circuit.circuit_concentration_fraction,
        system.alveoli.concentration_fraction,
        patient.mixed_venous_fraction,
        patient.vessel_rich.partial_pressure_fraction,
        patient.muscle.partial_pressure_fraction,
        patient.fat.partial_pressure_fraction,
    )


@cache
def _worst_displacement_pp(manoeuvre_name: str, agent_id: str, delay_s: float) -> float:
    """The largest displacement `delay_s` of control delay causes, in percentage points.

    Two runs of the same manoeuvre from the same empty system, stepped in
    lockstep: one applies the new settings at the boundary, the other
    `delay_s` later. Both are carried `SETTLE_S` past their own change, and the
    maximum is taken over every displayed compartment at every step boundary
    rather than at an endpoint, because the worst is inside the interval the
    delay opens and not at either end of the run.

    Boundaries are counted in whole steps rather than compared as times: every
    hold and every grid step this module drives is an exact multiple of
    `SHIPPED_STEP_S`, and counting them keeps a float comparison out of the
    definition of when a control change lands.
    """

    build = PUBLISHED_TOLERANCE[manoeuvre_name][0]
    manoeuvre = build(agent_id)

    on_time = _system_at(agent_id, manoeuvre.before)
    late = _system_at(agent_id, manoeuvre.before)

    change_step = round(manoeuvre.hold_s / SHIPPED_STEP_S)
    late_change_step = change_step + round(delay_s / SHIPPED_STEP_S)
    total_steps = late_change_step + round(SETTLE_S / SHIPPED_STEP_S)

    worst = 0.0
    for step in range(total_steps):
        if step == change_step:
            _apply(on_time, manoeuvre.after)
        if step == late_change_step:
            _apply(late, manoeuvre.after)

        on_time.advance(SHIPPED_STEP_S)
        late.advance(SHIPPED_STEP_S)

        worst = max(
            worst,
            max(
                abs(a - b)
                for a, b in zip(_displayed_states(on_time), _displayed_states(late), strict=True)
            ),
        )

    return worst * 100.0


def _worst_over_agents(manoeuvre_name: str, delay_s: float) -> tuple[float, str]:
    """The worst displacement over all three agents, and which agent binds it."""

    measured = {
        agent_id: _worst_displacement_pp(manoeuvre_name, agent_id, delay_s)
        for agent_id in AGENT_IDS
    }
    binding = max(measured, key=lambda agent_id: measured[agent_id])

    return measured[binding], binding


def _grid_step_s(rate: PlaybackRate) -> float:
    """The simulated seconds between the instants a control change can land at.

    A tick advances its whole burst with nothing between the steps, so this is
    the steps that burst takes times the step size. Derived from the rate
    rather than restated, because `tests/unit/test_playback.py` already holds
    the derivation to the grid `docs/MODEL.md` publishes; what this module adds
    is what one such step costs.
    """

    steps = rate.steps_per_tick(tick_interval_s=TICK_INTERVAL_S, simulation_step_s=SHIPPED_STEP_S)

    return steps * SHIPPED_STEP_S


@pytest.mark.parametrize("manoeuvre_name", PUBLISHED_TOLERANCE)
def test_the_control_resolution_tolerance_table(manoeuvre_name: str) -> None:
    """The tolerance `MAXIMUM_SIMULATION_STEP_S` declares is the one it holds to.

    `docs/MODEL.md` § "Supported simulation step", the table under "The
    tolerance, in percentage points of one atmosphere", is what this asserts,
    and `core/uptake_system.py`'s comment deriving the constant repeats the
    case-opening and ventilator-start rows of it. Since `PL-X9KD` retired the
    accuracy derivation these three figures are the entire content of the
    constant, so moving the model has to move them here before it moves what a
    reader is told.

    The binding agent is asserted with the value because the table publishes it
    as a column: a parameter change that left the worst figure alone but moved
    which agent produced it would leave the table wrong in a way the number
    alone cannot see.
    """

    _, published_pp, published_binding_agent = PUBLISHED_TOLERANCE[manoeuvre_name]
    measured_pp, binding_agent = _worst_over_agents(manoeuvre_name, SHIPPED_STEP_S)

    assert measured_pp == pytest.approx(published_pp, rel=PUBLICATION_RELATIVE_TOLERANCE), (
        f"the {manoeuvre_name} manoeuvre now displaces a displayed compartment by "
        f"{measured_pp:.3g} pp per step, not the {published_pp:.3g} pp published in "
        'docs/MODEL.md "Supported simulation step"; re-measure the whole table, and '
        "update it and the MAXIMUM_SIMULATION_STEP_S comment in "
        "src/anesthesia_sim/core/uptake_system.py together"
    )
    assert binding_agent == published_binding_agent, (
        f"the {manoeuvre_name} manoeuvre is now worst for {binding_agent}, not the "
        f'{published_binding_agent} published in docs/MODEL.md "Supported simulation step"'
    )


@pytest.mark.parametrize("rate", SUPPORTED_PLAYBACK_RATES, ids=lambda rate: f"{rate.multiplier}x")
def test_the_displacement_per_grid_step_at_each_playback_rate(rate: PlaybackRate) -> None:
    """The per-rate table's cost column, held over the same three manoeuvres.

    `PL-NBWP` established that the interface waits one *step* for a control
    change only at 1x — above it a tick advances its whole burst uninterrupted,
    so the grid is `multiplier x 0.1` s — and disclosed the cost per rate rather
    than changing the behaviour. `tests/unit/test_playback.py` holds the grid
    column of that table to the rate ladder. This holds the column beside it:
    what one grid step of delay actually costs a displayed compartment.

    A rung added to the ladder fails here for want of a published figure, which
    is the intended failure: a rate offered without a measured displacement is
    a resolution claim nobody has made.
    """

    assert rate.multiplier in PUBLISHED_DISPLACEMENT_PER_GRID_STEP_PP, (
        f"{rate.multiplier}x is offered but what one of its grid steps costs is "
        'published nowhere; measure it and add the row to docs/MODEL.md "Supported '
        'simulation step" first'
    )

    published_pp = PUBLISHED_DISPLACEMENT_PER_GRID_STEP_PP[rate.multiplier]
    grid_step_s = _grid_step_s(rate)
    measured_pp, _ = max(
        (_worst_over_agents(manoeuvre_name, grid_step_s) for manoeuvre_name in PUBLISHED_TOLERANCE),
        key=lambda result: result[0],
    )

    assert measured_pp == pytest.approx(published_pp, rel=PUBLICATION_RELATIVE_TOLERANCE), (
        f"at {rate.multiplier}x the {grid_step_s:g} s control grid now costs "
        f"{measured_pp:.3g} pp, not the {published_pp:.3g} pp published in docs/MODEL.md "
        '"Supported simulation step"; re-measure the whole per-rate table'
    )


def test_every_published_displacement_belongs_to_an_offered_rate() -> None:
    """The other direction: a cost published for a rung nobody can select.

    Removing a rung and leaving its row would tell a reader what a resolution
    costs at a rate the interface does not offer.
    """

    assert set(PUBLISHED_DISPLACEMENT_PER_GRID_STEP_PP) == {
        rate.multiplier for rate in SUPPORTED_PLAYBACK_RATES
    }


def test_the_ventilator_start_binds_the_per_rate_table_at_every_rate() -> None:
    """The claim that one manoeuvre is the worst case throughout.

    `docs/MODEL.md` states that "the binding case is the ventilator start with
    desflurane throughout". It is a claim about every rate at once rather than
    about any one row, so no per-rate assertion above can hold it: the table
    would still pass with its own numbers if a different manoeuvre had become
    the one producing them.
    """

    for rate in SUPPORTED_PLAYBACK_RATES:
        grid_step_s = _grid_step_s(rate)
        worst_name = max(
            PUBLISHED_TOLERANCE, key=lambda name: _worst_over_agents(name, grid_step_s)[0]
        )
        _, binding_agent = _worst_over_agents(worst_name, grid_step_s)

        assert (worst_name, binding_agent) == ("ventilator start", "desflurane"), (
            f"at {rate.multiplier}x the worst displacement is now the {worst_name} "
            f"manoeuvre with {binding_agent}, not the ventilator start with desflurane "
            'that docs/MODEL.md "Supported simulation step" names as binding throughout'
        )


def test_the_case_opening_stays_milder_than_the_binding_manoeuvre_at_every_rate() -> None:
    """The published relation between an ordinary action and the worst one.

    `docs/MODEL.md` reads the per-rate table with the case opening beside it, so
    that a reader knows the tens of percentage points at 300x belong to an
    abrupt manoeuvre rather than to changing a dial. The gap narrows as the grid
    coarsens — the ventilator start's transient has largely run by the time a
    30 s grid step has passed, so its displacement saturates while the case
    opening's is still growing — and that narrowing is the part a reader could
    be misled by, which is why the ratio is asserted at both ends rather than
    only where it is widest.
    """

    ratios = {}
    for rate in SUPPORTED_PLAYBACK_RATES:
        grid_step_s = _grid_step_s(rate)
        case_opening_pp, _ = _worst_over_agents("case opening", grid_step_s)
        binding_pp, _ = _worst_over_agents("ventilator start", grid_step_s)
        ratios[rate.multiplier] = binding_pp / case_opening_pp

    assert min(ratios.values()) > 5.0, (
        f"the case opening is no longer an order milder than the ventilator start at "
        f"every rate (narrowest ratio {min(ratios.values()):.3g}x at "
        f"{min(ratios, key=lambda m: ratios[m])}x); docs/MODEL.md "
        '"Supported simulation step" reads the per-rate table on that relation'
    )
    assert ratios[1] == pytest.approx(21.0, rel=0.1)
    assert ratios[300] == pytest.approx(6.9, rel=0.1)

    case_opening_at_300x_pp, _ = _worst_over_agents(
        "case opening",
        _grid_step_s(max(SUPPORTED_PLAYBACK_RATES, key=lambda rate: rate.multiplier)),
    )

    assert case_opening_at_300x_pp == pytest.approx(
        PUBLISHED_CASE_OPENING_AT_300X_PP, rel=PUBLICATION_RELATIVE_TOLERANCE
    )


def test_the_tolerance_is_measured_at_the_supported_step() -> None:
    """The table and the constant are one decision, so they move together.

    Nothing else pins `MAXIMUM_SIMULATION_STEP_S` to its value:
    `test_the_shipped_step_is_within_the_maximum_simulation_step` asserts only
    that the shipped step does not exceed it, a relation both sides of which
    could move together. Since `PL-NBCJ` the value is an argued decision with
    three recorded reasons rather than a default, and every figure in both
    tables above is measured at it, so a silent change would leave two
    documents describing a tolerance the code no longer holds (`PL-ZVS7`).
    """

    assert MAXIMUM_SIMULATION_STEP_S == SHIPPED_STEP_S, (
        f"the largest supported step is now {MAXIMUM_SIMULATION_STEP_S} s, but the "
        f"control-resolution tolerance published in docs/MODEL.md 'Supported simulation "
        f"step' is measured at {SHIPPED_STEP_S} s; re-measure both tables at the new "
        "step, and update that section and the MAXIMUM_SIMULATION_STEP_S comment in "
        "src/anesthesia_sim/core/uptake_system.py together"
    )


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_the_case_opening_starts_from_an_empty_system(agent_id: str) -> None:
    """The case-opening hold is inert, which is what lets it be short.

    With the dial closed and the system empty no agent enters, so every
    compartment sits at zero for the whole hold and its length cannot reach the
    figure measured. Asserting it keeps `hold_s` an arbitrary choice rather than
    a hidden input to a safety-critical number.
    """

    manoeuvre = _case_opening(agent_id)
    system = _system_at(agent_id, manoeuvre.before)

    for _ in range(round(manoeuvre.hold_s / SHIPPED_STEP_S)):
        system.advance(SHIPPED_STEP_S)

    assert _displayed_states(system) == (0.0,) * len(STATE_LABELS)
