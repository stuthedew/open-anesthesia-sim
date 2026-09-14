"""What `AgentUptakeSystem.resume_at()` guarantees: a live system standing where a run stood.

`RunDefinition` answers any instant of a run in closed form, but what comes
back is a state vector rather than a running system. `resume_at()` is the seam
between the two, and `PL-J2TD` is what it exists for: a branch has to become
something a learner can *manage*, which means advancing it, and advancing needs
compartments rather than a curve.

**Three separate claims are held here, and each fails differently.**

- *The compartments come to hold the state that was asked for.* A branch that
  opened a fraction away from its parent would diverge from the first step, and
  `ROADMAP.md` item 12 requires the pre-branch history to be the same history
  rather than a reproduction of it.
- *The mass-balance accounting continues the case rather than restarting.* The
  two cumulative totals a keyframe carries are the case's - what the patient
  has actually received - so a branch restarting them at zero would report a
  litre count that is correct about the branch and wrong about the patient,
  which `CLAUDE.md`'s safety-critical standard counts as a presentation failure
  rather than a lesser kind. The anchor is carried for the same reason and the
  measurement under `test_the_accounting_anchor_is_carried_rather_than_derived`
  is why it is not derived.
- *A state the equations could not be read against is refused, and refused
  before anything is written.* `docs/MODEL.md` § "The canonical evaluation rule"
  says a drawn value may be drawn and nothing else; a partially seeded system
  would be the "partial state" `AgentUptakeSystem.advance()` already exists to
  make unrepresentable, arriving by a second route.

The clock a branch runs on is not this file's - it is the controller's, and
`tests/integration/test_controller.py` holds it. Everything here is true
whichever clock a branch keeps.
"""

import math
from dataclasses import replace

import pytest

from anesthesia_sim.core.agent_simulation_validation import AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L
from anesthesia_sim.core.concentration import Fraction
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
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

SIMULATION_STEP_S = 0.1
"""The step every run in this file takes, and the one the app layer ships."""

FRACTION_STATES: tuple[int, ...] = (
    INSPIRED_FRACTION,
    ALVEOLAR_FRACTION,
    VENOUS_FRACTION,
    *range(FIRST_TISSUE_FRACTION, FIRST_TISSUE_FRACTION + 3),
)
"""The six modelled fractions, as against the two accumulators and the constant.

`state_vector()` reports each step's own delivered and exhausted agent while a
keyframe carries the case's cumulative totals, so the two differ there by
design and the comparison that means anything is over these six.
"""

STEPPED_AGREEMENT = 5e-15
"""How far a resumed, stepped system may sit from the closed form, in fractions of 1 atm.

Measured on the run below rather than assumed: the worst departure over every
compartment at the instants probed is under 1e-15 of one atmosphere, against
the 1e-4 that `docs/MODEL.md` § "Displayed precision" resolves. Stated as an
absolute tolerance in fractions of one atmosphere for the reason
`docs/MODEL.md` § "Closed-form agreement test" gives: a relative one would
tighten without limit on the near-zero tissue fractions of an induction and
would say nothing about a displayed digit.
"""


def _run(
    steps: int = 6_000, dial_step: int = 2_000, flow_step: int = 4_000
) -> tuple[AgentUptakeSystem, RunDefinition]:
    """Step a sevoflurane run across two setting changes, building its definition alongside.

    The changes are applied the way `app/controller.py` applies them - the
    setter first, so the core has accepted the value, then the definition,
    which reads the settings back off the compartments - so the definition
    describes the run the system actually took.

    The two instants are arguments because the conservation residual a fork
    inherits depends on them; `test_the_accounting_anchor_is_carried_rather_than_derived`
    is the one test that needs a particular pair.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)

    for step in range(1, steps + 1):
        system.advance(SIMULATION_STEP_S)
        definition.advance_to(step * SIMULATION_STEP_S)

        if step == dial_step:
            system.set_delivered_partial_pressure_fraction(Fraction(0.008))
            definition.record_change(system.equation_settings())

        if step == flow_step:
            system.set_fresh_gas_flow(1.0)
            definition.record_change(system.equation_settings())

    return system, definition


def _fresh_system() -> AgentUptakeSystem:
    """A system built the way a branch's is: the parent's agent, nothing stepped."""

    return AgentUptakeSystem.for_agent("sevoflurane")


def _like(parent: AgentUptakeSystem) -> AgentUptakeSystem:
    """A fresh system carrying `parent`'s live settings, ready to be resumed at its state.

    A branch inherits its parent's agent and patient (`PL-TFX5`), so the
    volumes and coefficients come from the same data files the parent's did
    and only the four live controls are written here.

    **They are read off the compartments in the units the compartments hold,
    never recovered from a `RunSegment`.** A segment carries the litres per
    *second* the equations are written in, and `equation_settings()` divides
    by sixty to produce them - a conversion that does not round-trip:
    multiplying back by sixty reproduces a different settings object for 7 of
    the 101 cardiac outputs on a 0.1 L/min grid across the supported 0 to
    10 L/min range, first at 1.9 L/min, where the three per-tissue blood flows
    land one unit in the last place away because each is derived from cardiac
    output in litres per minute *before* the conversion. A branch built that
    way would assemble a system matrix one ulp from its parent's and solve
    slightly different equations from its first step, inside the tolerance
    that holds the two records together and so reported by nothing.
    """

    system = _fresh_system()
    system.set_fresh_gas_flow(parent.circuit.fresh_gas_flow_l_min)
    system.set_delivered_partial_pressure_fraction(
        parent.circuit.delivered_partial_pressure_fraction
    )
    system.set_alveolar_ventilation(parent.alveoli.alveolar_ventilation_l_min)
    system.set_cardiac_output(parent.patient.cardiac_output_l_min)

    assert system.equation_settings() == parent.equation_settings()

    return system


# --- The state arrives -------------------------------------------------------


def test_a_resumed_system_holds_the_state_it_was_given() -> None:
    """Element for element across the six fractions, not to within a tolerance.

    This is the property the branch's whole claim rests on. A fork that opened
    a rounding away from its parent would be a reproduction of the case rather
    than a continuation of it, and the difference is invisible in the first
    frame and compounding thereafter.
    """

    system_parent, definition = _run()
    opening = definition.segments[-1].opening
    system = _like(system_parent)

    system.resume_at(opening.state, initial_agent_l=0.0)

    resumed = system.state_vector()

    for entry in FRACTION_STATES:
        assert resumed[entry] == opening.state[entry], f"state[{entry}] did not arrive intact"

    assert resumed[UNIT_STATE] == 1.0


def test_a_resumed_system_steps_the_way_the_run_it_resumes_did() -> None:
    """The point of resuming at all: it advances by the path a live run takes.

    The system is stood at a keyframe and then stepped by the ordinary
    `advance()` - no second way to move a run forward is introduced - and what
    it reaches is compared against what the definition says the same settings
    reach over the same span. That is `docs/MODEL.md` § "Closed-form agreement
    test" applied to a system that did not step its way to its starting point.
    """

    system_parent, definition = _run()
    segment = definition.segments[-1]
    opening = segment.opening
    system = _like(system_parent)

    system.resume_at(opening.state, initial_agent_l=0.0)

    ahead = RunDefinition(segment.settings, opening.state, opened_at_s=0.0)

    for step in range(1, 601):
        system.advance(SIMULATION_STEP_S)
        ahead.advance_to(step * SIMULATION_STEP_S)

    stepped = system.state_vector()
    closed_form = ahead.state_at(600 * SIMULATION_STEP_S)

    for entry in FRACTION_STATES:
        assert abs(stepped[entry] - closed_form[entry]) < STEPPED_AGREEMENT, (
            f"state[{entry}] departed from the closed form"
        )


def test_two_systems_resumed_at_one_state_step_identically() -> None:
    """Determinism across the seam, which is what a comparison of two branches needs.

    `docs/MODEL.md` § "Deterministic replay test" requires element-for-element
    agreement rather than agreement within a tolerance, and a fork is where two
    runs most plausibly acquire a difference neither learner caused.
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

    A keyframe's two accumulators are cumulative from the start of the run it
    belongs to, so carrying them is what makes a branch's mass-balance readout
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
    """The identity holds across the seam, and the residual stays inside the check.

    `docs/MODEL.md`'s mass-balance identity is checked after every step at a
    tolerance tight enough to halt a run. Resuming writes the compartments and
    the two totals from separate entries of one canonical state, so nothing
    guarantees the identity closes by construction - which is the point. What
    is left over is the canonical path's own conservation residual, reported
    rather than absorbed.
    """

    system_parent, definition = _run()
    opening = definition.segments[-1].opening
    system = _like(system_parent)

    system.resume_at(opening.state, initial_agent_l=0.0)

    accounting = system.agent_simulation_validation

    assert accounting.passes_validation
    assert accounting.absolute_error_l < AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L


def test_the_accounting_anchor_is_carried_rather_than_derived() -> None:
    """Why `initial_agent_l` is an argument and not a calculation.

    The tempting alternative is to derive the anchor as the value that closes
    `docs/MODEL.md`'s mass-balance identity exactly - stored + exhausted -
    delivered. That quantity is the canonical path's own conservation residual
    with its sign reversed, and a residual has no reason to fall on the
    positive side; an anchor is an *amount* of agent, which
    `AgentSimulationValidator` rightly refuses below zero. So the derivation
    would refuse to open an ordinary branch, at rounding, for a reason with
    nothing wrong with it.

    **Measured rather than argued.** Across 72 keyframes - three agents, four
    dial instants, three flow instants, one keyframe per change - 16 of them,
    22%, put the derived anchor below zero, the worst at -1.1e-13 L. The run
    below is one of the 16 and is the smallest reproduction of it. Carried
    instead, the same residual stays inside the accounting check, which is
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
    """A non-zero anchor is the parent's, and it is not quietly replaced by the store."""

    system_parent, definition = _run()
    opening = definition.segments[-1].opening
    system = _like(system_parent)

    system.resume_at(opening.state, initial_agent_l=0.25)

    assert system.agent_simulation_validation.initial_agent_l == 0.25


# --- What is refused, and what a refusal leaves behind ------------------------


def test_a_drawn_value_cannot_resume_a_system() -> None:
    """`docs/MODEL.md` § "The canonical evaluation rule", enforced at this sink too.

    A drawn column and a fork's opening state are the same nine numbers in the
    same order, so nothing about their contents separates them; what does is
    that one of them is structurally not a state vector.
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
    """An infinity reaching a compartment would be a run that cannot be stopped."""

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

    with pytest.raises(SimulationConfigurationError, match="delivered_agent_l"):
        _fresh_system().resume_at(tuple(state), initial_agent_l=0.0)


def test_a_negative_anchor_cannot_resume_a_system() -> None:
    """The same rule for the anchor, which is also an amount of agent."""

    _, definition = _run()
    opening = definition.segments[-1].opening

    with pytest.raises(SimulationConfigurationError, match="initial_agent_l"):
        _fresh_system().resume_at(opening.state, initial_agent_l=-1e-9)


def test_a_refused_resume_leaves_every_compartment_as_it_was() -> None:
    """The guard that fires late must not leave the partial state it exists to prevent.

    `_write_state_vector` writes one compartment at a time, so a fraction the
    model cannot represent is refused after earlier compartments have already
    taken their new values. That is the same shape `AgentUptakeSystem.advance()`
    already handles, and it is handled the same way: the system is captured
    before the write and restored on any exit that is not a completed resume.
    """

    system_parent, definition = _run()
    opening = definition.segments[-1].opening
    system = _like(system_parent)

    system.resume_at(opening.state, initial_agent_l=0.0)

    before = system.capture_state()

    impossible = list(opening.state)
    impossible[FIRST_TISSUE_FRACTION + 2] = 1.5

    with pytest.raises(SimulationConfigurationError):
        system.resume_at(tuple(impossible), initial_agent_l=0.0)

    assert system.capture_state() == before


def test_a_refused_resume_leaves_the_accounting_period_as_it_was() -> None:
    """The totals are written after the compartments, so the rollback has to reach them too."""

    system_parent, definition = _run()
    opening = definition.segments[-1].opening
    system = _like(system_parent)

    system.resume_at(opening.state, initial_agent_l=0.125)

    impossible = list(opening.state)
    impossible[ALVEOLAR_FRACTION] = 2.0

    with pytest.raises(SimulationConfigurationError):
        system.resume_at(tuple(impossible), initial_agent_l=0.9)

    accounting = system.agent_simulation_validation

    assert accounting.initial_agent_l == 0.125
    assert accounting.delivered_agent_l == opening.state[DELIVERED_AGENT_L]


# --- The cached propagator ---------------------------------------------------


def test_resuming_does_not_strand_the_cached_propagator() -> None:
    """A propagator is a function of the settings, and this writes none of them.

    The cache is keyed on `_propagator_cache_key()`, which reads the volumes,
    flows and coefficients the system matrix is assembled from. Resuming writes
    compartment *fractions*, so the cached matrix is still the right one - and
    the check that says so is that a system resumed after stepping reaches the
    same place as one resumed before stepping ever built a cache.
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
    """The two shapes a caller has are the same shape, which is what makes this safe.

    `Keyframe.state` and `RunDefinition.state_at` return the identical object
    for an instant a run holds a keyframe at, so a branch built from either
    opens at the same place. This pins that, because a future keyframe that
    stored something else would make the two routes disagree silently.
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
    """The trap at the seam, pinned here because nothing downstream would catch it.

    `SimulationController._build_state` opens a run's definition from
    `uptake_system.state_vector()`, which is right for a run starting from a
    system that has not been told anything. Copying that line at a fork is
    wrong, and silently so: a compartment stores an *amount* and derives its
    fraction back from its own capacity, so writing a fraction in and reading
    it out is not the identity.

    **Measured on the shipped compartments**, over a 1e-6 grid across the
    first two percent of an atmosphere - the range a sevoflurane case actually
    occupies - the alveolar compartment returns a different float for 11.7% of
    fractions, mixed venous blood for 11.6% and fat for 3.4%. The circuit is
    exact over the same grid, which is what makes this the kind of defect that
    survives a spot check.

    A branch whose definition opened from the seeded system would fail
    `ROADMAP.md` item 12's element-wise reproduction on exactly those entries,
    at a magnitude no display resolves and no tolerance test would report. The
    keyframe the parent already holds costs nothing and cannot drift, and the
    second half below is why it is always available: a definition answers an
    instant it holds a keyframe for with that keyframe itself.
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
    """The pairing `RunSegment` exists to enforce, read at the seam that consumes it.

    A branch is settings *and* the state they start from. Pairing one segment's
    settings with another's opening would compute a stretch under settings it
    was never under, so the seam takes the segment rather than the two halves.
    """

    _, definition = _run()

    for segment in definition.segments:
        assert isinstance(segment, RunSegment)
        assert segment.opening.state[UNIT_STATE] == 1.0

    swapped = replace(definition.segments[0], opening=definition.segments[-1].opening)

    assert swapped.settings == definition.segments[0].settings
    assert swapped.opening is definition.segments[-1].opening
