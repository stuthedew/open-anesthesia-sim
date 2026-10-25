"""Measure what a late control change costs, and check the published table against it.

Since `PL-X9KD`, `MAXIMUM_SIMULATION_STEP_S` is no longer a numerical limit. The
exact step has no truncation error at any step size, so there is no accuracy
domain left to stay inside. The constant now declares a *control-resolution
tolerance*. Settings are held constant across a step, so a control change is
invisible to the model until the step ends. A change therefore takes effect up
to one whole step late.

That makes the tolerance a measurement rather than a definition, and
`docs/MODEL.md` § "Supported simulation step" publishes it as one. The table
gives three manoeuvres, each with its worst displacement over all three agents,
in percentage points of one atmosphere. `core/uptake_system.py` repeats two of
the figures in the comment that derives the constant. Before this module, only
the prose in those two files stated the figures, and nothing checked them. A
change to the governing equations, to a partition coefficient, to the reference
adult's volumes or to the supported input envelope would have moved them
silently. `make check` would pass, both documents would keep stating the old
figures, and the tool would no longer meet the tolerance that a reader is told
it meets (`PL-ZVS7`).

**What is measured, precisely.** The same manoeuvre is driven twice from an
empty system, in lockstep. The two runs differ only in when the control change
lands: one on time at the phase boundary, and one `delay_s` later. The
displacement is the largest absolute difference between the two runs in any of
the six displayed compartments at any step boundary, converted to percentage
points. That is exactly the quantity the tables name: the cost of a control
action that the model resolves one grid step late. Nothing else enters it.

**This is a self-comparison, deliberately, and it is not the gate in
`test_coupled_dynamics.py`.** That module checks the shipped solution against
an independent integration, and its whole premise is that the oracle shares no
code with the core. Here both runs use the shipped system. The quantity is a
difference between two schedules of the *same* solver, so an independent
solution would answer a different question. Nothing here verifies that the
equations are solved correctly. `test_coupled_dynamics.py` does that, and this
module measures a property of a solution that it assumes is correct.

**Constants are imported rather than restated, for the same reason.** There is
no independence to protect, so importing `core.supported_ranges` makes "at the
envelope corner" follow the model's own declared domain. Widening a supported
range moves the manoeuvre and the measurement, and the test fails here. That is
right, because the published tolerance would genuinely have changed. The
circuit volume is left at the model's own default for the same reason.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

import pytest

from anesthesia_sim.app.playback import SUPPORTED_PLAYBACK_RATES, PlaybackRate
from anesthesia_sim.core import supported_ranges
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.simulation_step import MAXIMUM_SIMULATION_STEP_S, SimulationStep
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

AGENT_IDS = ("sevoflurane", "isoflurane", "desflurane")

#: `STATE_LABELS` lists the six compartments that the interface displays, in
#: display order. The tolerance is stated over "every displayed compartment", so
#: this set is what gives that phrase its meaning.
STATE_LABELS = ("circuit", "alveolar", "mixed venous", "vessel rich", "muscle", "fat")

#: The step at which every figure below was measured, and the step the interface
#: runs at. `test_the_tolerance_is_measured_at_the_supported_step` checks that it
#: equals `MAXIMUM_SIMULATION_STEP_S`. Since `PL-NBCJ`, that constant is an
#: argued decision with three recorded reasons rather than a default. Every
#: figure in both published tables is measured *at* it, so the two must not be
#: allowed to differ.
SHIPPED_STEP_S = SimulationStep(0.1)

#: The interface's run-loop tick. It is restated here rather than imported from
#: `app/simulation_view.py`, because that module needs Flet.
#: `test_simulation_view.py` checks that the shipped constant equals this value,
#: so a change there fails there. `tests/unit/test_playback.py` restates the
#: value for the same reason.
TICK_INTERVAL_S = 0.1

#: The fresh gas flow at which the case-opening manoeuvre runs. "Reference flows"
#: in the published table means this flow together with the reference adult's
#: own default ventilation and cardiac output, which are read from the patient
#: file below.
REFERENCE_FRESH_GAS_FLOW_L_MIN = 4.0

#: Simulated seconds that each run is carried past its own control change.
#:
#: The worst displacement falls on the first step after the *late* run's change
#: lands. Until then, the on-time run has been diverging for the whole delay and
#: the late run has not started. Afterwards, the two runs relax onto the same
#: trajectory. So this value only has to reach comfortably past that instant. It
#: does not have to be long enough to contain a transient. This was measured at
#: the largest grid step that this module drives, 30 s. Carrying every manoeuvre
#: 120 s, 300 s or 600 s past the change gives the same figure to six
#: significant digits. 120 s is four times the largest delay, and it is the
#: value kept.
SETTLE_S = 120.0

#: How far a measurement may sit from the figure that `docs/MODEL.md` prints and
#: still count as that figure.
#:
#: Both tables are published to two significant figures, so half a unit in the
#: last printed digit is up to 5% of the value. At 1.0x10^1 pp it is exactly
#: that much. A measurement inside this band is a value the document already
#: states. A measurement outside it is a value the document no longer states,
#: which is the failure this module exists to catch. Tightening the band would
#: pin digits that `docs/MODEL.md` does not publish. A drift smaller than the
#: publication's own precision does not make a reader's understanding of the
#: tolerance wrong.
PUBLICATION_RELATIVE_TOLERANCE = 0.05


@dataclass(frozen=True)
class OperatingPoint:
    """The four settings the interface can move, at one instant, in the units they are set in."""

    delivered_percent: float
    fresh_gas_flow_l_min: float
    alveolar_ventilation_l_min: float
    cardiac_output_l_min: float


@dataclass(frozen=True)
class Manoeuvre:
    """One control action: settings held, then changed once.

    The tolerance is defined over a single change, because it is the cost of
    *a* control action landing late. So each manoeuvre here has exactly one
    boundary, and `hold_s` is the time at which the boundary falls.
    """

    before: OperatingPoint
    after: OperatingPoint
    hold_s: float


def _case_opening(agent_id: str) -> Manoeuvre:
    """Turn the dial from off to 1 MAC at reference flows: the ordinary action, not an extreme.

    This row decides whether the step is fine enough for what a reader actually
    does, so it is deliberately not an envelope corner. It uses the reference
    adult's own ventilation and cardiac output, a 4 L/min fresh gas flow, and a
    dial moved from closed to one MAC of the agent in use.

    Nothing happens before the change. The dial is closed and the system starts
    empty, so no agent enters, and all six compartments stay at zero for the
    whole hold. `test_the_case_opening_starts_from_an_empty_system` asserts this
    rather than leaving it assumed. That assertion is what lets the hold be short
    enough to be cheap without changing the state on which the change acts.
    """

    patient = load_reference_adult_parameters()
    closed = OperatingPoint(
        delivered_percent=0.0,
        fresh_gas_flow_l_min=REFERENCE_FRESH_GAS_FLOW_L_MIN,
        alveolar_ventilation_l_min=patient.default_alveolar_ventilation_l_min,
        cardiac_output_l_min=patient.default_cardiac_output_l_min,
    )
    one_mac = load_agent_parameters(agent_id).mac_percent

    return Manoeuvre(closed, _with_dial(closed, one_mac), hold_s=60.0)


def _unperfused_load_then_dial_off(agent_id: str) -> Manoeuvre:
    """Fill the circuit and lungs with no circulation, then restore circulation and dial off.

    This manoeuvre sets up the widest spread of initial states that the four
    sliders can produce. With cardiac output at zero, the circuit and alveoli
    saturate at the dial setting while every blood and tissue compartment stays
    empty. Turning perfusion on and the vaporizer off in the same move then makes
    every compartment's equilibrium the opposite of where the compartment sits.

    The ten-minute hold is what saturates the circuit and alveoli. It is the same
    hold that `test_coupled_dynamics.py` uses for this manoeuvre. Shortening it
    would change the state on which the control change acts, and so would change
    the figure measured.
    """

    return Manoeuvre(
        before=OperatingPoint(
            delivered_percent=_max_dial(agent_id),
            fresh_gas_flow_l_min=supported_ranges.MAXIMUM_FRESH_GAS_FLOW_L_MIN,
            alveolar_ventilation_l_min=supported_ranges.MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
            cardiac_output_l_min=supported_ranges.MINIMUM_CARDIAC_OUTPUT_L_MIN,
        ),
        after=OperatingPoint(
            delivered_percent=0.0,
            fresh_gas_flow_l_min=supported_ranges.MAXIMUM_FRESH_GAS_FLOW_L_MIN,
            alveolar_ventilation_l_min=supported_ranges.MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
            cardiac_output_l_min=supported_ranges.MAXIMUM_CARDIAC_OUTPUT_L_MIN,
        ),
        hold_s=600.0,
    )


def _ventilator_start(agent_id: str) -> Manoeuvre:
    """Prime the circuit with the ventilator off, then start ventilating.

    This is the binding row of both tables, the row that sets the worst figure.
    The vaporizer is open and fresh gas is running while alveolar ventilation is
    still zero. So the circuit fills to the dial setting against lungs that
    cannot take up any of it. Starting ventilation then presents the largest
    circuit-to-alveolar gradient that the machine can produce, at the largest
    ventilation it can produce.

    Five minutes is far longer than the circuit needs. At 10 L/min into 6 L, the
    circuit's time constant is 36 s. So the hold ends with the circuit saturated,
    and the figure does not depend on exactly how long the hold ran.
    """

    corner = OperatingPoint(
        delivered_percent=_max_dial(agent_id),
        fresh_gas_flow_l_min=supported_ranges.MAXIMUM_FRESH_GAS_FLOW_L_MIN,
        alveolar_ventilation_l_min=supported_ranges.MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
        cardiac_output_l_min=supported_ranges.MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    )

    return Manoeuvre(
        before=_with_ventilation(corner, supported_ranges.MINIMUM_ALVEOLAR_VENTILATION_L_MIN),
        after=corner,
        hold_s=300.0,
    )


#: The three manoeuvres that `docs/MODEL.md` § "Supported simulation step"
#: tabulates. Each comes with the displacement it is published as producing at
#: the shipped step, and with the agent published as binding it, meaning the
#: agent that produces the worst figure.
#:
#: The figures are written out rather than computed, which is the whole point.
#: These are the numbers a reader is told, so they are the numbers to fail
#: against. Two of the three manoeuvres also appear in `SETTING_CHANGE_SCENARIOS`
#: in `test_coupled_dynamics.py`. They are restated here rather than imported,
#: because the table's own prose is what defines them for this measurement. That
#: module drives them to answer a different question, and it is free to change
#: them for its own reasons.
PUBLISHED_TOLERANCE = {
    "case opening": (_case_opening, 6.7e-3, "desflurane"),
    "unperfused load then dial off": (_unperfused_load_then_dial_off, 5.0e-2, "desflurane"),
    "ventilator start": (_ventilator_start, 1.4e-1, "desflurane"),
}

#: The worst displacement per grid step at each playback rate that the interface
#: offers. The figures come from the second table in the same section. `PL-NBWP`
#: added that table when it established that the interface waits one *step* for
#: a control change only at 1x. Above 1x, the interface waits `multiplier x 0.1` s.
#:
#: The table is keyed by multiplier rather than by delay. So a playback rate
#: added without a measured displacement fails here, and so does a row published
#: for a rate that nobody can select. The 1x entry is the ventilator-start row of
#: the table above, and that shared entry keeps the two tables consistent.
PUBLISHED_DISPLACEMENT_PER_GRID_STEP_PP = {1: 1.4e-1, 5: 7.0e-1, 20: 2.5, 60: 5.8, 300: 1.0e1}

#: The second-worst manoeuvre's displacement at each rate. `docs/MODEL.md`
#: publishes it as the column beside the bound, so that a reader can see how
#: much room the bound has. At 300x the two round to the same published figure
#: (`PL-WT07`), so the numbers alone cannot show the gap.
#: `PUBLISHED_BINDING_MARGIN` below gives the gap as a ratio instead.
PUBLISHED_SECOND_WORST_PER_GRID_STEP_PP = {1: 5.0e-2, 5: 2.5e-1, 20: 9.8e-1, 60: 2.8, 300: 1.0e1}

#: The published ratio of the worst manoeuvre's displacement to the second
#: worst's. `docs/MODEL.md` states the bound's headroom as this ratio. The ratio
#: is checked more tightly than `PUBLICATION_RELATIVE_TOLERANCE` on purpose. The
#: 300x entry is 1.03, and a 5% band there would admit the reversal that this
#: column exists to make visible.
PUBLISHED_BINDING_MARGIN = {1: 2.84, 5: 2.78, 20: 2.56, 60: 2.11, 300: 1.03}

#: How far the published margin may drift before the table must be restated. The
#: margin is a ratio of two measurements of the same kind, so it moves less
#: than either of them does. A tolerance of 1% keeps the 300x entry meaningful.
MARGIN_RELATIVE_TOLERANCE = 0.01

#: The displacement that the case opening reaches at the coarsest grid the
#: interface offers. It is published in the prose beneath the per-rate table, as
#: the measure of how much milder an ordinary action is than the binding one.
PUBLISHED_CASE_OPENING_AT_300X_PP = 1.5


def _max_dial(agent_id: str) -> float:
    """Return the agent's own vaporizer maximum in percent, the unit its dial is set in."""

    return load_agent_parameters(agent_id).max_delivered_concentration_percent


def _with_dial(point: OperatingPoint, delivered_percent: float) -> OperatingPoint:
    """Return a copy of `point` with only the vaporizer setting changed."""

    return OperatingPoint(
        delivered_percent=delivered_percent,
        fresh_gas_flow_l_min=point.fresh_gas_flow_l_min,
        alveolar_ventilation_l_min=point.alveolar_ventilation_l_min,
        cardiac_output_l_min=point.cardiac_output_l_min,
    )


def _with_ventilation(point: OperatingPoint, alveolar_ventilation_l_min: float) -> OperatingPoint:
    """Return a copy of `point` with only the ventilator setting changed."""

    return OperatingPoint(
        delivered_percent=point.delivered_percent,
        fresh_gas_flow_l_min=point.fresh_gas_flow_l_min,
        alveolar_ventilation_l_min=alveolar_ventilation_l_min,
        cardiac_output_l_min=point.cardiac_output_l_min,
    )


def _system_at(agent_id: str, point: OperatingPoint) -> AgentUptakeSystem:
    """Build an empty system with every slider set to `point`.

    The circuit volume is left at the model's own default rather than set here.
    The tolerance is a property of the system that ships, so a change to that
    system, including its default circuit volume, should move this measurement.
    """

    system = AgentUptakeSystem.for_agent(agent_id)
    _apply(system, point)

    return system


def _apply(system: AgentUptakeSystem, point: OperatingPoint) -> None:
    """Move every slider to `point`, leaving compartment contents untouched.

    This is what the interface does when a slider moves mid-run. It is also the
    only thing that happens at the manoeuvre's boundary: the settings change, and
    the state does not.
    """

    system.set_fresh_gas_flow(FreshGasFlow(point.fresh_gas_flow_l_min))
    system.set_alveolar_ventilation(AlveolarVentilation(point.alveolar_ventilation_l_min))
    system.set_cardiac_output(CardiacOutput(point.cardiac_output_l_min))
    system.set_delivered_concentration_percent(Percent(point.delivered_percent))


def _displayed_states(system: AgentUptakeSystem) -> tuple[float, ...]:
    """Read the six displayed compartments, in `STATE_LABELS` order."""

    patient = system.patient

    return (
        system.circuit.inspired_partial_pressure_fraction,
        system.alveoli.partial_pressure_fraction,
        patient.mixed_venous_partial_pressure_fraction,
        patient.vessel_rich.partial_pressure_fraction,
        patient.muscle.partial_pressure_fraction,
        patient.fat.partial_pressure_fraction,
    )


@cache
def _worst_displacement_pp(manoeuvre_name: str, agent_id: str, delay_s: float) -> float:
    """Return the largest displacement, in percentage points, that a delay of `delay_s` causes.

    The function runs the same manoeuvre twice from the same empty system and
    steps both runs in lockstep. One run applies the new settings at the
    boundary, and the other applies them `delay_s` later. Both runs are carried
    `SETTLE_S` past their own change. The maximum is taken over every displayed
    compartment at every step boundary, not at an endpoint, because the worst
    falls inside the interval that the delay opens and not at either end of the
    run.

    Boundaries are counted in whole steps rather than compared as times. Every
    hold and every grid step that this module drives is an exact multiple of
    `SHIPPED_STEP_S`. Counting steps keeps a float comparison out of the
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
    """Return the worst displacement over all three agents, and the agent that produces it."""

    measured = {
        agent_id: _worst_displacement_pp(manoeuvre_name, agent_id, delay_s)
        for agent_id in AGENT_IDS
    }
    binding = max(measured, key=lambda agent_id: measured[agent_id])

    return measured[binding], binding


def _ranked_over_manoeuvres(grid_step_s: float) -> list[tuple[str, float, str]]:
    """Return the three manoeuvres at one grid step, worst first, with their agents.

    The per-rate table publishes the top two of this ranking and the margin
    between them, so the ordering is part of the measurement, not a convenience.
    `PL-WT07` found `docs/MODEL.md` quoting a margin against the third-placed
    manoeuvre while the second sat 3% away at 300x.
    """

    measured = [
        (manoeuvre_name, *_worst_over_agents(manoeuvre_name, grid_step_s))
        for manoeuvre_name in PUBLISHED_TOLERANCE
    ]

    return sorted(measured, key=lambda result: result[1], reverse=True)


def _grid_step_s(rate: PlaybackRate) -> float:
    """Return the simulated seconds between the instants at which a control change can land.

    A tick advances its whole burst of steps with nothing in between. So the
    grid step is the number of steps in that burst times the step size. It is
    derived from the rate rather than restated, because
    `tests/unit/test_playback.py` already checks the derivation against the grid
    that `docs/MODEL.md` publishes. What this module adds is the cost of one such
    grid step.
    """

    steps = rate.steps_per_tick(tick_interval_s=TICK_INTERVAL_S, simulation_step_s=SHIPPED_STEP_S)

    return steps * SHIPPED_STEP_S


@pytest.mark.parametrize("manoeuvre_name", PUBLISHED_TOLERANCE)
def test_the_control_resolution_tolerance_table(manoeuvre_name: str) -> None:
    """The model meets the tolerance that `MAXIMUM_SIMULATION_STEP_S` declares.

    This test asserts the table in `docs/MODEL.md` § "Supported simulation step"
    that sits under "The tolerance, in percentage points of one atmosphere". The
    comment in `core/uptake_system.py` that derives the constant repeats the
    case-opening and ventilator-start rows of that table. Since `PL-X9KD` retired
    the accuracy derivation, these three figures are the entire content of the
    constant. So a change to the model has to move them here before it changes
    what a reader is told.

    The binding agent is asserted along with the value, because the table
    publishes it as a column. A parameter change could leave the worst figure
    alone but change which agent produced it. That would make the table wrong in
    a way that the number alone cannot show.
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
    """Check the per-rate table's cost column over the same three manoeuvres.

    `PL-NBWP` established that the interface waits one *step* for a control
    change only at 1x. Above 1x, a tick advances its whole burst without
    interruption, so the grid is `multiplier x 0.1` s. That item disclosed the
    cost per rate rather than changing the behaviour.
    `tests/unit/test_playback.py` checks the grid column of that table against
    the ladder of playback rates. This test checks the column beside it: what one
    grid step of delay actually costs a displayed compartment.

    A rate added to the ladder fails here for want of a published figure, and
    that is the intended failure. A rate offered without a measured displacement
    is a resolution claim that nobody has made.
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
    """Check the reverse direction: no cost is published for a rate nobody can select.

    Removing a rate and leaving its row would tell a reader what the control
    resolution costs at a rate that the interface does not offer.
    """

    assert set(PUBLISHED_DISPLACEMENT_PER_GRID_STEP_PP) == {
        rate.multiplier for rate in SUPPORTED_PLAYBACK_RATES
    }


def test_the_ventilator_start_binds_the_per_rate_table_at_every_rate() -> None:
    """Check the claim that one manoeuvre is the worst case at every rate.

    `docs/MODEL.md` states that "at every rate the worst is the ventilator
    start with desflurane and the second worst is the unperfused load then dial
    off". That is a claim about every rate at once rather than about any one row,
    so no per-rate assertion above can check it. The table would still pass with
    its own numbers if a different manoeuvre had become the one producing them.

    `PL-WT07` is why the section now calls that a measured fact rather than a
    property of the manoeuvre. The margin is 1.03x at 300x, which is inside
    `PUBLICATION_RELATIVE_TOLERANCE`. So the published figure would survive a
    reversal, and this is the only assertion in the module that would not.
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


@pytest.mark.parametrize("rate", SUPPORTED_PLAYBACK_RATES, ids=lambda rate: f"{rate.multiplier}x")
def test_the_second_worst_manoeuvre_and_the_margin_above_it(rate: PlaybackRate) -> None:
    """Check the two columns that `PL-WT07` added, and the manoeuvre they belong to.

    `docs/MODEL.md` publishes the runner-up beside the bound so that a reader
    can see how much room the bound has. Before `PL-WT07`, the section quoted
    the bound's headroom against the *case opening*. Those figures were correct,
    but the case opening is the third-placed manoeuvre. The actual runner-up sat
    1.03x away at 300x, so the section over-stated the margin by about seven
    times, in the reassuring direction.

    There are three assertions, because the columns fail in three different
    ways. The identity of the runner-up is asserted first. At 300x the top two
    round to the same published figure, so a swap between them moves no number
    in the table, and nothing else here would detect it. The value is asserted
    next, against the same publication tolerance as every other figure. The
    margin is asserted last and more tightly, because a 5% band around 1.03 spans
    1.0 and would admit the reversal that the column exists to make visible.
    """

    grid_step_s = _grid_step_s(rate)
    ranked = _ranked_over_manoeuvres(grid_step_s)
    (worst_name, worst_pp, _), (second_name, second_pp, second_agent) = ranked[0], ranked[1]

    assert (second_name, second_agent) == ("unperfused load then dial off", "desflurane"), (
        f"at {rate.multiplier}x the second-worst displacement is now the {second_name} "
        f"manoeuvre with {second_agent}, not the unperfused load then dial off with "
        'desflurane that docs/MODEL.md "Supported simulation step" publishes as the '
        "second-worst column"
    )

    published_second_pp = PUBLISHED_SECOND_WORST_PER_GRID_STEP_PP[rate.multiplier]

    assert second_pp == pytest.approx(published_second_pp, rel=PUBLICATION_RELATIVE_TOLERANCE), (
        f"at {rate.multiplier}x the second-worst manoeuvre now costs {second_pp:.3g} pp, "
        f"not the {published_second_pp:.3g} pp published in docs/MODEL.md "
        '"Supported simulation step"; re-measure the whole per-rate table'
    )

    published_margin = PUBLISHED_BINDING_MARGIN[rate.multiplier]

    assert worst_pp / second_pp == pytest.approx(published_margin, rel=MARGIN_RELATIVE_TOLERANCE), (
        f"at {rate.multiplier}x the bound leads the {second_name} manoeuvre by "
        f"{worst_pp / second_pp:.3g}x, not the {published_margin:.3g}x published in "
        'docs/MODEL.md "Supported simulation step"; the margin column is what tells a '
        "reader how much room the bound has, and it is computed before rounding, so "
        "dividing the published columns will not reproduce it"
    )

    assert worst_name == "ventilator start"


def test_the_case_opening_stays_milder_than_the_binding_manoeuvre_at_every_rate() -> None:
    """Check the published relation between an ordinary action and the worst one.

    `docs/MODEL.md` presents the per-rate table with the case opening beside it.
    That way a reader knows that the tens of percentage points at 300x belong to
    an abrupt manoeuvre rather than to changing a dial. The gap narrows as the
    grid coarsens. The ventilator start's transient has largely run its course by
    the time a 30 s grid step has passed, so its displacement saturates while the
    case opening's displacement is still growing. That narrowing is the part that
    could mislead a reader, which is why the ratio is asserted at both ends rather
    than only where it is widest.
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

    Nothing else pins `MAXIMUM_SIMULATION_STEP_S` to its value.
    `test_the_shipped_step_is_within_the_maximum_simulation_step` asserts only
    that the shipped step does not exceed it, and both sides of that relation
    could move together. Since `PL-NBCJ`, the value is an argued decision with
    three recorded reasons rather than a default, and every figure in both
    tables above is measured at it. A silent change would leave two documents
    describing a tolerance that the code no longer meets (`PL-ZVS7`).
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

    With the dial closed and the system empty, no agent enters. Every
    compartment stays at zero for the whole hold, so the hold's length cannot
    affect the figure measured. Asserting this keeps `hold_s` an arbitrary choice
    rather than a hidden input to a safety-critical number.
    """

    manoeuvre = _case_opening(agent_id)
    system = _system_at(agent_id, manoeuvre.before)

    for _ in range(round(manoeuvre.hold_s / SHIPPED_STEP_S)):
        system.advance(SHIPPED_STEP_S)

    assert _displayed_states(system) == (0.0,) * len(STATE_LABELS)
