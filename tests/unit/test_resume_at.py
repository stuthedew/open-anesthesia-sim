"""Tests that `AgentUptakeSystem.resume_at()` puts a live system at a state a run reached.

`RunDefinition` returns the state at any instant of a run in closed form, but
what it returns is a state vector rather than a running system.
`resume_at()` turns the one into the other. It exists for `PL-J2TD`. A learner
has to be able to *manage* a branch, which means advancing it, and advancing
needs compartments rather than a curve.

**These tests check three separate claims, and each one fails in a different
way.**

- *The compartments end up holding the state that was asked for.* A branch
  that opened even slightly away from its parent's state would diverge from
  the first step. `ROADMAP.md` item 12 requires the history before the branch
  to be the same history, not a reproduction of it.
- *The mass-balance accounting continues the case rather than restarting it.*
  The two cumulative totals that a keyframe carries belong to the case: they
  are what the patient has actually received. A branch that restarted them at
  zero would report a litre count that is correct about the branch and wrong
  about the patient. `CLAUDE.md`'s safety-critical standard counts that as a
  presentation failure, not as a lesser kind of error. The accounting anchor
  is carried for the same reason. The measurement in
  `test_the_accounting_anchor_is_carried_rather_than_derived` shows why the
  anchor is not derived instead.
- *A state that the equations cannot be evaluated against is refused, before
  anything is written.* `docs/MODEL.md` § "The canonical evaluation rule" says
  that a drawn value may be drawn and used for nothing else. A partially
  seeded system would be the "partial state" that `AgentUptakeSystem.advance()`
  already exists to make unrepresentable, arriving by a second route.

This file does not test the clock a branch runs on. That clock belongs to the
controller, and `tests/integration/test_controller.py` tests it. Everything
here is true whichever clock a branch keeps.
"""

import math
from collections.abc import Callable
from dataclasses import replace

import pytest

from anesthesia_sim.core.agent_simulation_validation import (
    AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L,
    AgentSimulationValidator,
)
from anesthesia_sim.core.concentration import Fraction, Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import (
    ALVEOLAR_FRACTION,
    DELIVERED_AGENT_L,
    EXHAUSTED_AGENT_L,
    FIRST_TISSUE_FRACTION,
    INSPIRED_FRACTION,
    STATE_SIZE,
    UNIT_STATE,
    VENOUS_FRACTION,
)
from anesthesia_sim.core.run_definition import DisplayState, Keyframe, RunDefinition, RunSegment
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.supported_ranges import CaseInstant, FreshGasFlow
from anesthesia_sim.core.tissue import TissueGroup
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

SIMULATION_STEP_S = SimulationStep(0.1)
"""The step every run in this file takes, and the one the app layer ships."""

FRACTION_STATES: tuple[int, ...] = (
    INSPIRED_FRACTION,
    ALVEOLAR_FRACTION,
    VENOUS_FRACTION,
    *range(FIRST_TISSUE_FRACTION, FIRST_TISSUE_FRACTION + 3),
)
"""The six modelled fractions, leaving out the two accumulators and the constant.

`state_vector()` reports the agent delivered and exhausted in each step alone,
while a keyframe carries the case's cumulative totals. So the two differ in
those entries by design, and only a comparison over these six fractions means
anything.
"""

STEPPED_AGREEMENT = 5e-15
"""How far a resumed, stepped system may sit from the closed form, in fractions of 1 atm.

The value was measured on the run below, not assumed. The worst departure
over every compartment at the instants probed is less than 1e-15 of one
atmosphere. The display resolves 1e-4, as `docs/MODEL.md` § "Displayed
precision" states. The tolerance is absolute, in fractions of one atmosphere,
for the reason that `docs/MODEL.md` § "Closed-form agreement test" gives. A
relative tolerance would tighten without limit on the near-zero tissue
fractions of an induction, and it would say nothing about a displayed digit.
"""


def _run(
    steps: int = 6_000, dial_step: int = 2_000, flow_step: int = 4_000
) -> tuple[AgentUptakeSystem, RunDefinition]:
    """Step a sevoflurane run across two setting changes, building its definition alongside.

    The changes are applied the way `app/controller.py` applies them. The
    setter runs first, so the core has accepted the value. Then the definition
    records the change, reading the settings back off the compartments. So the
    definition describes the run the system actually took.

    The two instants are arguments because the conservation residual that a
    fork inherits depends on them.
    `test_the_accounting_anchor_is_carried_rather_than_derived` is the one test
    that needs a particular pair.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )

    for step in range(1, steps + 1):
        system.advance(SIMULATION_STEP_S)
        definition.advance_to(CaseInstant(step * SIMULATION_STEP_S))

        if step == dial_step:
            system.set_delivered_concentration_percent(Percent(0.8))
            definition.record_change(system.equation_settings())

        if step == flow_step:
            system.set_fresh_gas_flow(FreshGasFlow(1.0))
            definition.record_change(system.equation_settings())

    return system, definition


def _fresh_system() -> AgentUptakeSystem:
    """Return a system built the way a branch's is: the parent's agent, and nothing stepped."""

    return AgentUptakeSystem.for_agent("sevoflurane")


def _like(parent: AgentUptakeSystem) -> AgentUptakeSystem:
    """Return a fresh system with `parent`'s live settings, ready to be resumed at its state.

    A branch inherits its parent's agent and patient (`PL-TFX5`). So the
    volumes and coefficients come from the same data files as the parent's,
    and only the four live controls are written here.

    **The controls are read off the compartments, in the litres per minute
    that the compartments store.** A `RunSegment` has stored the same values
    since `PL-SM5V`, so it is now an equally sound source. Before that, a
    segment stored litres per second. Multiplying back by sixty rebuilt a
    different settings object for 7 of the 101 cardiac outputs on a 0.1 L/min
    grid. A branch built that way solved a matrix that differed from its
    parent's by one unit in the last place. The difference was inside every
    tolerance, so nothing reported it. The assertion below catches a helper
    that drifts from its parent in that way.
    """

    system = _fresh_system()
    system.set_fresh_gas_flow(parent.circuit.fresh_gas_flow_l_min)
    system.set_delivered_concentration_percent(parent.circuit.delivered_concentration_percent)
    system.set_alveolar_ventilation(parent.alveoli.alveolar_ventilation_l_min)
    system.set_cardiac_output(parent.patient.cardiac_output_l_min)

    assert system.equation_settings() == parent.equation_settings()

    return system


# --- The state arrives -------------------------------------------------------


def test_a_resumed_system_holds_the_state_it_was_given() -> None:
    """Each fraction arrives within the single rounding that its compartment makes.

    A compartment stores an amount and derives its fraction back from its
    capacity. So writing a fraction and reading it back does not always return
    the same value. `PL-J2TD` measured a different float for 11.7% of alveolar
    fractions. For 3.5% to 14% of fractions in the alveolar, venous and tissue
    compartments, no stored amount reads back as the given value at all
    (`PL-2MD9`). That is why a branch's definition opens from the parent's
    `Keyframe` and never from this system's `state_vector()`. A branch's
    exactness comes from that definition, and
    `tests/integration/test_controller.py` checks a branch against its parent
    element for element on the canonical path.

    What this system can promise is that `resume_at` writes the state it was
    given, and that nothing else changes it. Each value goes through one
    multiplication into its compartment and one division out, which is
    provably within one unit in the last place of the given value. This test
    asserted exact equality until `PL-2MD9` moved the canonical path by a unit
    in the last place. After that change, the six fractions this test compares
    no longer happened to round-trip.
    """

    system_parent, definition = _run()
    opening = definition.segments[-1].opening
    system = _like(system_parent)

    system.resume_at(opening.state, initial_agent_l=0.0)

    resumed = system.state_vector()

    for entry in FRACTION_STATES:
        assert abs(resumed[entry] - opening.state[entry]) <= math.ulp(opening.state[entry]), (
            f"state[{entry}] did not arrive within the rounding its compartment makes"
        )

    assert resumed[UNIT_STATE] == 1.0


def test_a_resumed_system_steps_the_way_the_run_it_resumes_did() -> None:
    """A resumed system advances along the path a live run takes, which is the point of resuming.

    The system is placed at a keyframe and then stepped by the ordinary
    `advance()`. The test adds no second way to move a run forward. The state
    the system reaches is compared with the state that the definition gives
    for the same settings over the same span. That is `docs/MODEL.md`
    § "Closed-form agreement test", applied to a system that did not step its
    way to its starting point.
    """

    system_parent, definition = _run()
    segment = definition.segments[-1]
    opening = segment.opening
    system = _like(system_parent)

    system.resume_at(opening.state, initial_agent_l=0.0)

    ahead = RunDefinition(segment.settings, opening.state, opened_at_s=CaseInstant(0.0))

    for step in range(1, 601):
        system.advance(SIMULATION_STEP_S)
        ahead.advance_to(CaseInstant(step * SIMULATION_STEP_S))

    stepped = system.state_vector()
    closed_form = ahead.state_at(600 * SIMULATION_STEP_S)

    for entry in FRACTION_STATES:
        assert abs(stepped[entry] - closed_form[entry]) < STEPPED_AGREEMENT, (
            f"state[{entry}] departed from the closed form"
        )


def test_two_systems_resumed_at_one_state_step_identically() -> None:
    """Two systems resumed at one state step identically, as a comparison of branches needs.

    `docs/MODEL.md` § "Deterministic replay test" requires element-for-element
    agreement rather than agreement within a tolerance. A fork is the most
    likely place for two runs to acquire a difference that neither learner
    caused.
    """

    system_parent, definition = _run()
    segment = definition.segments[-1]
    left = _like(system_parent)
    right = _like(system_parent)

    for system in (left, right):
        system.resume_at(segment.opening.state, initial_agent_l=0.0)

        for _ in range(300):
            system.advance(SIMULATION_STEP_S)

    assert left.state_vector() == right.state_vector()


# --- The accounting continues the case ---------------------------------------


def test_a_resumed_system_continues_the_case_s_cumulative_totals() -> None:
    """The litres reported are the patient's, not the branch's.

    A keyframe's two accumulators count from the start of the case, not from
    the start of the run that holds the keyframe. That is why a branch has
    anything to carry. Carrying them makes a branch's mass-balance readout
    describe the case the patient is actually in.
    """

    system_parent, definition = _run()
    opening = definition.segments[-1].opening
    system = _like(system_parent)

    system.resume_at(opening.state, initial_agent_l=0.0)

    accounting = system.agent_simulation_validation

    assert accounting.delivered_agent_l == opening.state[DELIVERED_AGENT_L]
    assert accounting.exhausted_agent_l == opening.state[EXHAUSTED_AGENT_L]
    assert accounting.delivered_agent_l > 0.0, "the run under test delivered nothing to carry"


def test_a_resumed_system_still_balances() -> None:
    """The mass-balance identity still holds after resuming, and the residual stays in bounds.

    `docs/MODEL.md`'s mass-balance identity is checked after every step at a
    tolerance tight enough to halt a run. Resuming writes the compartments and
    the two totals from separate entries of one canonical state. So nothing
    guarantees by construction that the identity closes, and that is the point
    of this test. What is left over is the canonical path's own conservation
    residual, which is reported rather than absorbed.
    """

    system_parent, definition = _run()
    opening = definition.segments[-1].opening
    system = _like(system_parent)

    system.resume_at(opening.state, initial_agent_l=0.0)

    accounting = system.agent_simulation_validation

    assert accounting.passes_validation
    assert accounting.absolute_error_l < AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L


def test_the_accounting_anchor_is_carried_rather_than_derived() -> None:
    """Show why `initial_agent_l` is an argument and not a calculation.

    The tempting alternative is to derive the anchor as the value that closes
    `docs/MODEL.md`'s mass-balance identity exactly: stored + exhausted -
    delivered. That quantity is the canonical path's own conservation residual
    with its sign reversed. A residual has no reason to fall on the positive
    side. But an anchor is an *amount* of agent, which
    `AgentSimulationValidator` rightly refuses when it is less than zero. So
    the derivation would refuse to open an ordinary branch over a rounding
    error, when nothing is wrong with the branch.

    **This was measured, not only argued.** The survey covered 72 keyframes:
    three agents, four dial instants and three flow instants, with one
    keyframe per change. In 16 of them, 22%, the derived anchor was less than
    zero, the worst at -1.1e-13 L. The run below is one of the 16, and it is
    the smallest reproduction of the problem. When the anchor is carried
    instead, the same residual stays within the accounting check, which is
    where a conservation error belongs.
    """

    system_parent, definition = _run(steps=9_000, dial_step=3_000, flow_step=6_000)
    segment = definition.segments[-1]
    opening = segment.opening

    assert opening.instant_s == 600.0

    system = _like(system_parent)
    system.resume_at(opening.state, initial_agent_l=0.0)

    derived_anchor_l = (
        system.total_stored_agent_l
        + opening.state[EXHAUSTED_AGENT_L]
        - opening.state[DELIVERED_AGENT_L]
    )

    assert derived_anchor_l < 0.0, "the derivation this avoids has become safe; re-read the design"
    assert abs(derived_anchor_l) < AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L

    with pytest.raises(SimulationConfigurationError, match="initial_agent_l"):
        _like(system_parent).resume_at(opening.state, initial_agent_l=derived_anchor_l)

    assert system.agent_simulation_validation.passes_validation, (
        "carrying the anchor leaves the residual inside the check it belongs in"
    )


def test_a_carried_anchor_reaches_the_branch_s_own_accounting_period() -> None:
    """A non-zero anchor comes from the parent and is not quietly replaced by the stored agent."""

    system_parent, definition = _run()
    opening = definition.segments[-1].opening
    system = _like(system_parent)

    system.resume_at(opening.state, initial_agent_l=0.25)

    assert system.agent_simulation_validation.initial_agent_l == 0.25


# --- What is refused, and what a refusal leaves behind ------------------------


def test_a_drawn_value_cannot_resume_a_system() -> None:
    """`resume_at` also enforces `docs/MODEL.md` § "The canonical evaluation rule".

    A drawn column and a fork's opening state are the same nine numbers in the
    same order, so their contents cannot tell them apart. What separates them
    is that a drawn column is structurally not a state vector.
    """

    _, definition = _run()
    drawn = definition.evaluate(0.0, 600.0, 600).states[0]

    assert isinstance(drawn, DisplayState)

    with pytest.raises(SimulationConfigurationError, match="not a state vector"):
        _fresh_system().resume_at(drawn, initial_agent_l=0.0)  # type: ignore[arg-type]


def test_a_state_of_the_wrong_length_cannot_resume_a_system() -> None:
    """A vector from a model with a different compartment count is not this model's."""

    with pytest.raises(SimulationConfigurationError, match="entries but the equations carry"):
        _fresh_system().resume_at((0.0, 1.0), initial_agent_l=0.0)


def test_a_non_finite_state_cannot_resume_a_system() -> None:
    """An infinity written into a compartment would make a run that cannot be stopped."""

    state = [0.0] * STATE_SIZE
    state[UNIT_STATE] = 1.0
    state[ALVEOLAR_FRACTION] = math.inf

    with pytest.raises(SimulationConfigurationError, match="not finite"):
        _fresh_system().resume_at(tuple(state), initial_agent_l=0.0)


def test_a_state_whose_constant_is_not_one_cannot_resume_a_system() -> None:
    """The constant scales every forcing term, and nothing on screen would show it moving."""

    state = [0.0] * STATE_SIZE
    state[UNIT_STATE] = 0.5

    with pytest.raises(SimulationConfigurationError, match="constant one"):
        _fresh_system().resume_at(tuple(state), initial_agent_l=0.0)


def test_a_negative_cumulative_total_cannot_resume_a_system() -> None:
    """Agent delivered is an amount, and a run that delivered less than nothing never happened."""

    state = [0.0] * STATE_SIZE
    state[UNIT_STATE] = 1.0
    state[DELIVERED_AGENT_L] = -1.0

    with pytest.raises(
        SimulationConfigurationError,
        match=r"^state\[6\] \(delivered agent in L\) must be nonnegative",
    ):
        _fresh_system().resume_at(tuple(state), initial_agent_l=0.0)


def test_a_negative_anchor_cannot_resume_a_system() -> None:
    """The same rule applies to the anchor, which is also an amount of agent."""

    _, definition = _run()
    opening = definition.segments[-1].opening

    with pytest.raises(SimulationConfigurationError, match="initial_agent_l"):
        _fresh_system().resume_at(opening.state, initial_agent_l=-1e-9)


def _refusing(message: str) -> Callable[..., None]:
    """Return a stand-in method that refuses whatever it is given."""

    def refuse(*_: object, **__: object) -> None:
        raise SimulationConfigurationError(message)

    return refuse


def test_a_refused_resume_leaves_every_compartment_as_it_was(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A late refusal must not leave the partial state that the rollback exists to prevent.

    `_write_state_vector` writes one compartment at a time, and it writes the fat group
    last. `resume_at` captures the system before the write and restores it on any exit that
    is not a completed resume, as `AgentUptakeSystem.advance()` does. Since `PL-0WFJ`,
    `require_canonical_state` refuses an out-of-range fraction before anything is written.
    So no real state now reaches a refusal partway through the write. The test therefore
    injects a refusal at the fat group's write, after every other compartment has taken its
    new value.
    """

    system_parent, definition = _run()
    opening = definition.segments[-1].opening
    system = _like(system_parent)

    system.resume_at(opening.state, initial_agent_l=0.0)
    system.advance(SIMULATION_STEP_S)

    before = system.capture_state()
    original = TissueGroup.set_partial_pressure_fraction

    def refuse_the_fat_group(group: TissueGroup, fraction: Fraction) -> None:
        if group.name == "fat":
            raise SimulationConfigurationError("the fat group refused its fraction")

        original(group, fraction)

    monkeypatch.setattr(TissueGroup, "set_partial_pressure_fraction", refuse_the_fat_group)

    with pytest.raises(SimulationConfigurationError, match="the fat group refused"):
        system.resume_at(opening.state, initial_agent_l=0.0)

    assert system.capture_state() == before


def test_a_refused_resume_leaves_the_accounting_period_as_it_was(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The totals are written after the compartments, so the rollback has to restore them too.

    The refusal is injected at the last write, after the accounting period has been reset
    to the new anchor, for the reason the test above gives.
    """

    system_parent, definition = _run()
    opening = definition.segments[-1].opening
    system = _like(system_parent)

    system.resume_at(opening.state, initial_agent_l=0.125)

    monkeypatch.setattr(
        AgentSimulationValidator,
        "record_external_agent_transfer",
        _refusing("the transfer was refused"),
    )

    with pytest.raises(SimulationConfigurationError, match="the transfer was refused"):
        system.resume_at(opening.state, initial_agent_l=0.9)

    accounting = system.agent_simulation_validation

    assert accounting.initial_agent_l == 0.125
    assert accounting.delivered_agent_l == opening.state[DELIVERED_AGENT_L]


# --- The cached propagator ---------------------------------------------------


def test_resuming_does_not_strand_the_cached_propagator() -> None:
    """A propagator is a function of the settings, and resuming writes none of them.

    The cache is keyed on `_propagator_cache_key()`, which reads the volumes,
    flows and coefficients that the system matrix is assembled from. Resuming
    writes compartment *fractions*, so the cached matrix is still the right
    one. The test checks this: a system resumed after stepping reaches the same
    state as one resumed before any step built a cache.
    """

    system_parent, definition = _run()
    segment = definition.segments[-1]

    warmed = _like(system_parent)
    warmed.advance(SIMULATION_STEP_S)
    warmed.resume_at(segment.opening.state, initial_agent_l=0.0)

    cold = _like(system_parent)
    cold.resume_at(segment.opening.state, initial_agent_l=0.0)

    for _ in range(200):
        warmed.advance(SIMULATION_STEP_S)
        cold.advance(SIMULATION_STEP_S)

    assert warmed.state_vector() == cold.state_vector()


def test_a_keyframe_resumes_a_system_without_being_unwrapped_first() -> None:
    """The two forms a caller may hold are the same object, which is what makes this safe.

    `Keyframe.state` and `RunDefinition.state_at` return the identical object
    for an instant at which a run holds a keyframe. So a branch built from
    either opens at the same place. This test pins that, because a future
    keyframe that stored something else would make the two routes disagree
    silently.
    """

    system_parent, definition = _run()
    segment = definition.segments[-1]
    opening = segment.opening

    assert isinstance(opening, Keyframe)
    assert definition.state_at(opening.instant_s) == opening.state

    from_keyframe = _like(system_parent)
    from_keyframe.resume_at(opening.state, initial_agent_l=0.0)

    from_state_at = _like(system_parent)
    from_state_at.resume_at(definition.state_at(opening.instant_s), initial_agent_l=0.0)

    assert from_keyframe.state_vector() == from_state_at.state_vector()


def test_a_definition_opens_from_the_keyframe_and_never_from_the_seeded_system() -> None:
    """A trap when resuming, pinned here because nothing downstream would catch it.

    `SimulationController._build_state` opens a run's definition from
    `uptake_system.state_vector()`. That is right for a run that starts from a
    system no state has been written into. Copying that line at a fork is
    wrong, and silently so. A compartment stores an *amount* and derives its
    fraction back from its own capacity. So writing a fraction in and reading
    it out does not always return the same value.

    **This was measured on the shipped compartments**, over a 1e-6 grid across
    the first two percent of an atmosphere, which is the range a sevoflurane
    case actually occupies. The alveolar compartment returns a different float
    for 11.7% of fractions, mixed venous blood for 11.6% and fat for 3.4%. The
    circuit is exact over the same grid, so this defect can survive a spot
    check.

    A branch whose definition opened from the seeded system would fail
    `ROADMAP.md` item 12's element-wise reproduction on exactly those entries.
    It would fail at a magnitude that no display resolves and no tolerance test
    would report. The keyframe that the parent already holds costs nothing and
    cannot drift. The second half of this test shows why that keyframe is
    always available. For an instant at which a definition holds a keyframe,
    the definition returns that keyframe's state itself.
    """

    system = _fresh_system()
    compartments = (
        (
            "alveolar gas",
            system.alveoli.set_partial_pressure_fraction,
            lambda: system.alveoli.partial_pressure_fraction,
        ),
        (
            "mixed venous blood",
            system.patient.venous_blood.set_partial_pressure_fraction,
            lambda: system.patient.venous_blood.partial_pressure_fraction,
        ),
    )

    for name, write, read_back in compartments:
        drifted = 0

        for count in range(1, 20_001):
            fraction = count / 1_000_000.0
            write(Fraction(fraction))
            drifted += read_back() != fraction

        assert drifted > 0, (
            f"{name} now round-trips a fraction exactly over the whole grid; if every "
            "compartment does, the seam may open a definition from either and this "
            "test no longer says anything"
        )

    _, definition = _run()

    for segment in definition.segments:
        assert definition.state_at(segment.opening.instant_s) == segment.opening.state


def test_a_segment_and_its_opening_travel_together() -> None:
    """Check the pairing that `RunSegment` exists to enforce, where a branch consumes it.

    A branch is settings *and* the state they start from. Pairing one segment's
    settings with another's opening would compute a stretch of the run under
    settings it never had. So a branch takes the whole segment rather than its
    two halves.
    """

    _, definition = _run()

    for segment in definition.segments:
        assert isinstance(segment, RunSegment)
        assert segment.opening.state[UNIT_STATE] == 1.0

    swapped = replace(definition.segments[0], opening=definition.segments[-1].opening)

    assert swapped.settings == definition.segments[0].settings
    assert swapped.opening is definition.segments[-1].opening
