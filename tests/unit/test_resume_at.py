"""Tests that `AgentUptakeSystem.resume_at()` puts a live system at a state a run reached.

A run stores the state of every second it has reached
(`core/stored_states.py`), but a stored state is a state vector rather than a
running system. `resume_at()` turns the one into the other. It exists for
`PL-J2TD`. A user
has to be able to *manage* a branch, which means advancing it, and advancing
needs compartments rather than a curve.

**These tests check three separate claims, and each one fails in a different
way.**

- *The compartments end up holding the state that was asked for.* A branch
  that opened even slightly away from its parent's state would diverge from
  the first step. `ROADMAP.md` item 12 requires the history before the branch
  to be the same history, not a reproduction of it.
- *The mass-balance accounting continues the case rather than restarting it.*
  The two cumulative totals that a stored state carries belong to the case: they
  are what the patient has actually received. A branch that restarted them at
  zero would report a litre count that is correct about the branch and wrong
  about the patient. `CLAUDE.md`'s safety-critical standard counts that as a
  presentation failure, not as a lesser kind of error. The accounting anchor
  is carried for the same reason. The measurement in
  `test_the_accounting_anchor_is_carried_rather_than_derived` shows why the
  anchor is not derived instead.
- *A state that the equations cannot be applied to is refused, before
  anything is written.* A partially seeded system would be the "partial
  state" that `AgentUptakeSystem.advance()` already exists to make
  unrepresentable, arriving by a second route.

This file does not test the clock a branch runs on. That clock belongs to the
controller, and `tests/integration/controller/` tests it. Everything
here is true whichever clock a branch keeps.
"""

import math
from collections.abc import Callable

import pytest

from anesthesia_sim.core.agent_simulation_validation import (
    AgentSimulationValidator,
    AgentSimulationValidatorState,
    TotalsCompensation,
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
    build_system_matrix,
)
from anesthesia_sim.core.matrix_exponential import matrix_exponential, propagate
from anesthesia_sim.core.rounding import AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.stored_states import Keyframe
from anesthesia_sim.core.supported_ranges import CaseInstant, FreshGasFlow
from anesthesia_sim.core.tissue import TissueGroup
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

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
atmosphere. The display resolves 1e-4, as `docs/INTERFACE.md` § "Displayed
precision" states. The tolerance is absolute, in fractions of one atmosphere,
because that is what the compartments contain and what a readout converts. A
relative tolerance would tighten without limit on the near-zero tissue
fractions of an induction, and it would say nothing about a displayed digit.
"""


def _run(
    duration_s: int = 600, dial_at_s: int = 200, flow_at_s: int = 400, fork_at_s: int | None = None
) -> tuple[AgentUptakeSystem, Keyframe]:
    """Step a sevoflurane run across two setting changes, and return the state stored at a fork.

    The run lasts ten minutes by default. The dial moves to 0.8% at 200 s and
    the fresh gas flow to 1 L/min at 400 s. The keyframe returned is a second
    of the run and the state that the run stored for it, which is what a
    branch taken there resumes at (`SimulationController._open_at`). The second
    is `fork_at_s`, or the second of the flow change when it is not given.

    The instants are arguments because the conservation residual that a fork
    inherits depends on them.
    `test_the_accounting_anchor_is_carried_rather_than_derived` is the one test
    that needs a particular set.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    run = SimulationState(uptake_system=system)

    for step in range(1, duration_s // SIMULATION_STEP_S + 1):
        run.advance()

        if step * SIMULATION_STEP_S == dial_at_s:
            system.set_delivered_concentration_percent(Percent(0.8))

        if step * SIMULATION_STEP_S == flow_at_s:
            system.set_fresh_gas_flow(FreshGasFlow(1.0))

    fork_s = CaseInstant(flow_at_s if fork_at_s is None else fork_at_s)

    return system, Keyframe(fork_s, run.stored_states.state_at(fork_s))


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
    `tests/integration/controller/test_controller_branching.py` checks a branch against its parent
    element for element on the canonical path.

    What this system can promise is that `resume_at` writes the state it was
    given, and that nothing else changes it. Each value goes through one
    multiplication into its compartment and one division out, which is
    provably within one unit in the last place of the given value. This test
    asserted exact equality until `PL-2MD9` moved the canonical path by a unit
    in the last place. After that change, the six fractions this test compares
    no longer happened to round-trip.
    """

    system_parent, opening = _run()
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

    The system is placed at a stored state and then stepped by the ordinary
    `advance()`. The test adds no second way to move a run forward. The state
    the system reaches after 60 steps is compared with one exact propagation
    of the same state over 60 s, under the same settings, for a system that
    did not step its way to its starting point.
    """

    system_parent, opening = _run()
    system = _like(system_parent)

    system.resume_at(opening.state, initial_agent_l=0.0)

    for _ in range(60 // SIMULATION_STEP_S):
        system.advance()

    stepped = system.state_vector()
    closed_form = propagate(
        matrix_exponential(build_system_matrix(system_parent.equation_settings()), 60.0),
        opening.state,
    )

    for entry in FRACTION_STATES:
        assert abs(stepped[entry] - closed_form[entry]) < STEPPED_AGREEMENT, (
            f"state[{entry}] departed from the closed form"
        )


def test_two_systems_resumed_at_one_state_step_identically() -> None:
    """Two systems resumed at one state step identically, as a comparison of branches needs.

    `docs/VERIFICATION.md` § "Deterministic replay test" requires element-for-element
    agreement rather than agreement within a tolerance. A fork is the most
    likely place for two runs to acquire a difference that neither user
    caused.
    """

    system_parent, opening = _run()
    left = _like(system_parent)
    right = _like(system_parent)

    for system in (left, right):
        system.resume_at(opening.state, initial_agent_l=0.0)

        for _ in range(30 // SIMULATION_STEP_S):
            system.advance()

    assert left.state_vector() == right.state_vector()


# --- The accounting continues the case ---------------------------------------


def test_a_resumed_system_continues_the_case_s_cumulative_totals() -> None:
    """The litres reported are the patient's, not the branch's.

    A keyframe's two accumulators count from the start of the case, not from
    the start of the run that holds the keyframe. That is why a branch has
    anything to carry. Carrying them makes a branch's mass-balance readout
    describe the case the patient is actually in.
    """

    system_parent, opening = _run()
    system = _like(system_parent)

    system.resume_at(opening.state, initial_agent_l=0.0)

    accounting = system.agent_simulation_validation

    assert accounting.delivered_agent_l == opening.state[DELIVERED_AGENT_L]
    assert accounting.exhausted_agent_l == opening.state[EXHAUSTED_AGENT_L]
    assert accounting.delivered_agent_l > 0.0, "the run under test delivered nothing to carry"


def test_a_resumed_system_still_balances() -> None:
    """The mass-balance identity still holds after resuming, and the residual stays in bounds.

    `docs/VERIFICATION.md`'s mass-balance identity is checked after every step at a
    tolerance tight enough to halt a run. Resuming writes the compartments and
    the two totals from separate entries of one canonical state. So nothing
    guarantees by construction that the identity closes, and that is the point
    of this test. What is left over is the canonical path's own conservation
    residual, which is reported rather than absorbed.
    """

    system_parent, opening = _run()
    system = _like(system_parent)

    system.resume_at(opening.state, initial_agent_l=0.0)

    accounting = system.agent_simulation_validation

    assert accounting.passes_validation
    assert accounting.absolute_error_l < AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L


def test_the_accounting_anchor_is_carried_rather_than_derived() -> None:
    """Show why `initial_agent_l` is an argument and not a calculation.

    The tempting alternative is to derive the anchor as the value that closes
    `docs/VERIFICATION.md`'s mass-balance identity exactly: stored + exhausted -
    delivered. That quantity is the canonical path's own conservation residual
    with its sign reversed. A residual has no reason to fall on the positive
    side. But an anchor is an *amount* of agent, which
    `AgentSimulationValidator` rightly refuses when it is less than zero. So
    the derivation would refuse to open an ordinary branch over a rounding
    error, when nothing is wrong with the branch.

    **This was measured, not only argued.** A 30-minute sevoflurane run, with
    the dial at 0.8% from 300 s and the fresh gas flow at 1 L/min from 600 s,
    stores 1 800 seconds after its opening. For 907 of them the derived anchor
    was less than zero, the worst at -5.8e-14 L at 1 800 s (measured
    2026-11-21 from the run's stored states). The fork below is at 1 200 s,
    where the derived anchor is -1.8e-14 L. When the anchor is carried
    instead, the same residual stays within the accounting check, which is
    where a conservation error belongs.
    """

    system_parent, opening = _run(duration_s=1200, dial_at_s=300, flow_at_s=600, fork_at_s=1200)

    assert opening.instant_s == 1200

    system = _like(system_parent)
    system.resume_at(opening.state, initial_agent_l=0.0)

    derived_anchor_l = (
        system.total_stored_agent_l
        + opening.state[EXHAUSTED_AGENT_L]
        - opening.state[DELIVERED_AGENT_L]
    )

    assert derived_anchor_l < 0.0, "the derivation this avoids has become safe; re-read the design"
    assert abs(derived_anchor_l) < AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L

    with pytest.raises(SimulationConfigurationError, match=r"^initial_agent_l must be nonnegative"):
        _like(system_parent).resume_at(opening.state, initial_agent_l=derived_anchor_l)

    assert system.agent_simulation_validation.passes_validation, (
        "carrying the anchor leaves the residual inside the check it belongs in"
    )


def test_a_carried_anchor_reaches_the_branch_s_own_accounting_period() -> None:
    """A non-zero anchor comes from the parent and is not quietly replaced by the stored agent."""

    system_parent, opening = _run()
    system = _like(system_parent)

    system.resume_at(opening.state, initial_agent_l=0.25)

    assert system.agent_simulation_validation.initial_agent_l == 0.25


# --- What is refused, and what a refusal leaves behind ------------------------


def test_nine_numbers_that_are_not_a_tuple_cannot_resume_a_system() -> None:
    """A value with a state's nine numbers in a state's order is refused when it is not a tuple.

    A state vector is a tuple. A record that wraps the same numbers, or a
    list of them, is refused by its structure, so a caller cannot resume a
    system at a value that only resembles a state.
    """

    _, opening = _run()

    with pytest.raises(SimulationConfigurationError, match="not a state vector"):
        _fresh_system().resume_at(list(opening.state), initial_agent_l=0.0)  # type: ignore[arg-type]


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

    _, opening = _run()

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

    system_parent, opening = _run()
    system = _like(system_parent)

    system.resume_at(opening.state, initial_agent_l=0.0)
    system.advance()

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

    The refusal is injected after the accounting period has been written with the new
    anchor, for the reason the test above gives. Only the first write is refused, because
    the rollback restores the period through the same method.
    """

    system_parent, opening = _run()
    system = _like(system_parent)

    held = TotalsCompensation(delivered_l=3e-18, exhausted_l=-2e-18)
    system.resume_at(opening.state, initial_agent_l=0.125, compensation=held)

    restore = AgentSimulationValidator.restore_state
    writes: list[float] = []

    def refuse_the_first_write(
        validator: AgentSimulationValidator, state: AgentSimulationValidatorState
    ) -> None:
        restore(validator, state)
        writes.append(state.initial_agent_l)

        if len(writes) == 1:
            raise SimulationConfigurationError("the accounting period was refused")

    monkeypatch.setattr(AgentSimulationValidator, "restore_state", refuse_the_first_write)

    with pytest.raises(SimulationConfigurationError, match="the accounting period was refused"):
        system.resume_at(opening.state, initial_agent_l=0.9)

    # The refused write did put the new anchor in place, and the rollback put the old one back.
    assert writes == [0.9, 0.125]

    accounting = system.agent_simulation_validation

    assert accounting.initial_agent_l == 0.125
    assert accounting.delivered_agent_l == opening.state[DELIVERED_AGENT_L]
    assert system.accounting_compensation() == held


def test_resuming_with_compensation_terms_puts_them_in_the_accounting() -> None:
    """The totals and their terms are the ones passed in, and the default terms are zero."""

    system_parent, opening = _run()
    system = _like(system_parent)
    terms = TotalsCompensation(delivered_l=6.9e-18, exhausted_l=-1.1e-18)

    system.resume_at(opening.state, initial_agent_l=0.0, compensation=terms)

    assert system.accounting_compensation() == terms
    assert system.agent_simulation_validator.delivered_compensation_l == 6.9e-18
    assert system.agent_simulation_validator.exhausted_compensation_l == -1.1e-18
    assert system.agent_simulation_validation.delivered_agent_l == opening.state[DELIVERED_AGENT_L]
    assert system.agent_simulation_validation.exhausted_agent_l == opening.state[EXHAUSTED_AGENT_L]

    system.resume_at(opening.state, initial_agent_l=0.0)

    assert system.accounting_compensation() == TotalsCompensation(delivered_l=0.0, exhausted_l=0.0)
    assert system.agent_simulation_validation.delivered_agent_l == opening.state[DELIVERED_AGENT_L]


@pytest.mark.parametrize("terms", [(1e-17, 2e-17), 0.0, None])
def test_resuming_with_terms_not_built_as_a_totals_compensation_changes_nothing(
    terms: object,
) -> None:
    system_parent, opening = _run()
    system = _like(system_parent)
    before = system.capture_state()

    with pytest.raises(TypeError, match="not TotalsCompensation"):
        system.resume_at(opening.state, initial_agent_l=0.0, compensation=terms)  # type: ignore[arg-type]

    assert system.capture_state() == before


@pytest.mark.parametrize(
    ("delivered_l", "exhausted_l", "names"),
    [
        (float("nan"), 0.0, "delivered_l must be finite"),
        (0.0, -float("inf"), "exhausted_l must be finite"),
    ],
)
def test_a_compensation_term_that_is_not_finite_cannot_be_built(
    delivered_l: float, exhausted_l: float, names: str
) -> None:
    with pytest.raises(SimulationConfigurationError, match=names):
        TotalsCompensation(delivered_l=delivered_l, exhausted_l=exhausted_l)


@pytest.mark.parametrize("term", ["0.0", None, True])
def test_a_compensation_term_that_is_not_a_number_cannot_be_built(term: object) -> None:
    with pytest.raises(TypeError):
        TotalsCompensation(delivered_l=0.0, exhausted_l=term)  # type: ignore[arg-type]


# --- The cached propagator ---------------------------------------------------


def test_resuming_does_not_strand_the_cached_propagator() -> None:
    """A propagator is a function of the settings, and resuming writes none of them.

    The cache is keyed on `_propagator_cache_key()`, which reads the volumes,
    flows and coefficients that the system matrix is assembled from. Resuming
    writes compartment *fractions*, so the cached matrix is still the right
    one. The test checks this: a system resumed after stepping reaches the same
    state as one resumed before any step built a cache.
    """

    system_parent, opening = _run()

    warmed = _like(system_parent)
    warmed.advance()
    warmed.resume_at(opening.state, initial_agent_l=0.0)

    cold = _like(system_parent)
    cold.resume_at(opening.state, initial_agent_l=0.0)

    for _ in range(20 // SIMULATION_STEP_S):
        warmed.advance()
        cold.advance()

    assert warmed.state_vector() == cold.state_vector()


def test_a_compartment_does_not_always_read_back_the_fraction_written_to_it() -> None:
    """A trap when resuming, pinned here because nothing downstream would catch it.

    A compartment stores an *amount* and derives its fraction back from its
    own capacity. So writing a fraction in and reading it out does not always
    return the same value.

    **This was measured on the shipped compartments**, over a 1e-6 grid across
    the first two percent of an atmosphere, which is the range a sevoflurane
    case actually occupies. The alveolar compartment returns a different float
    for 11.7% of fractions, mixed venous blood for 11.6% and fat for 3.4%. The
    circuit is exact over the same grid, so this defect can survive a spot
    check.

    That is why a branch's record ends with the state that its parent stored
    for the fork, and never with a state read back from the seeded system
    (`SimulationController._open_at`). A record that ended with the state
    read back would show a value for the fork that differs from the parent's
    in its last place.
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
