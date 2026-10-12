import copy
import json
from dataclasses import replace
from importlib.resources import files

import pytest

from anesthesia_sim.core import uptake_system
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.concentration import Fraction
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.parameters import (
    load_reference_adult_parameters,
    parse_reference_adult_parameters,
)
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    AlveolarVentilation,
)
from anesthesia_sim.core.uptake_system import AgentUptakeSystem


def test_rejects_agent_amount_above_alveolar_capacity() -> None:
    with pytest.raises(
        SimulationConfigurationError,
        match="^agent_amount_l exceeds the alveolar capacity for a concentration fraction of 1$",
    ):
        AlveolarCompartment(agent_amount_l=2.6)


def test_an_agent_amount_past_capacity_is_refused_at_the_write() -> None:
    """An assignment straight onto the amount meets the constructor's refusal, and writes nothing.

    `set_partial_pressure_fraction` takes a `Fraction`, so no setter could
    store an amount past the alveolar capacity; until `PL-544D` the field
    could, and the quotient read from it - a partial pressure above one
    atmosphere - was refused only when `SimulationController.snapshot()`
    built the `Fraction` two layers later. The compartment's `__setattr__`
    now holds the amount to `gas_volume_l` at the write, in the constructor's
    own words, and leaves the field holding what it held; `dataclasses.replace`
    and a copy write through the same `__setattr__`, as the flows' guard test
    shows for a flow (`PL-LBQY`). An amount at the capacity itself is written:
    a fraction of exactly one is the top of the range, not past it.
    """

    alveoli = AlveolarCompartment()
    alveoli.set_partial_pressure_fraction(Fraction(0.05))
    held = alveoli.agent_amount_l
    past_capacity = alveoli.gas_volume_l * 1.0000001
    refused = "^agent_amount_l exceeds the alveolar capacity for a concentration fraction of 1$"

    with pytest.raises(SimulationConfigurationError, match=refused):
        alveoli.agent_amount_l = past_capacity

    assert alveoli.agent_amount_l == held

    for not_an_amount in (-0.1, float("inf"), float("nan")):
        with pytest.raises(SimulationConfigurationError, match="agent_amount_l"):
            alveoli.agent_amount_l = not_an_amount

        assert alveoli.agent_amount_l == held

    with pytest.raises(SimulationConfigurationError, match=refused):
        replace(alveoli, agent_amount_l=past_capacity)

    smuggled = copy.copy(alveoli)
    object.__setattr__(smuggled, "agent_amount_l", past_capacity)

    with pytest.raises(SimulationConfigurationError, match=refused):
        copy.copy(smuggled)

    alveoli.agent_amount_l = alveoli.gas_volume_l

    assert alveoli.partial_pressure_fraction == 1.0


@pytest.mark.parametrize("invalid_value", [0.0, -1.0, float("inf"), float("nan")])
def test_rejects_invalid_alveolar_gas_volume(invalid_value: float) -> None:
    """A bad volume is refused under its own name, though the amount's write reads it first.

    The constructor writes `agent_amount_l` after `gas_volume_l` and before
    `__post_init__` has refused the volume, so the capacity check in
    `__setattr__` meets a capacity that is zero, negative, infinite or NaN
    and leaves it to `__post_init__`, which names the volume (`PL-544D`).
    """

    with pytest.raises(SimulationConfigurationError, match="gas_volume_l"):
        AlveolarCompartment(gas_volume_l=invalid_value)


@pytest.mark.parametrize("not_a_number", ["2.5", None])
def test_a_volume_that_is_not_a_number_is_refused_under_its_own_name(not_a_number: object) -> None:
    """The amount's write reads the volume first, and refuses a non-number by the volume's name.

    The capacity check `PL-544D` put in `__setattr__` reads `gas_volume_l`
    before `__post_init__` has required it, so without `require_a_number`
    there the comparison's own `TypeError` came back - "'<' not supported
    between instances of 'float' and 'str'" - naming neither the field nor
    its constraint, the shape `PL-3800` had removed (found at review). The
    message is `__post_init__`'s own, byte for byte.
    """

    with pytest.raises(TypeError, match=f"^gas_volume_l of {not_a_number!r} has type "):
        AlveolarCompartment(gas_volume_l=not_a_number)  # type: ignore[arg-type]


def test_a_rollback_restores_the_captured_amount_past_the_capacity_guard() -> None:
    """`restore_state` writes what the compartment held, whatever the capacity has become.

    A rollback that could raise would replace the step's own error and leave
    the compartments restored after this one holding the failed step
    (`AgentUptakeSystem.restore_state`), so it writes the slot past
    `__setattr__` (`PL-544D`, found at review). The volume is written past any
    guard it has or gets (`PL-19Y0`), since what is under test is the rollback
    and not how the capacity came to be below the amount; the state restored
    is the one the step began from, over capacity as it already was, for the
    snapshot's `Fraction` to refuse.
    """

    alveoli = AlveolarCompartment()
    alveoli.set_partial_pressure_fraction(Fraction(0.05))
    captured = alveoli.capture_state()
    alveoli.set_partial_pressure_fraction(Fraction(0.06))
    object.__setattr__(alveoli, "gas_volume_l", captured.agent_amount_l / 2)

    alveoli.restore_state(captured)

    assert alveoli.agent_amount_l == captured.agent_amount_l
    assert alveoli.partial_pressure_fraction == 2.0


def test_changing_ventilation_preserves_alveolar_agent() -> None:
    alveoli = AlveolarCompartment()
    alveoli.set_partial_pressure_fraction(Fraction(0.05))
    amount_before = alveoli.agent_amount_l

    alveoli.set_alveolar_ventilation(AlveolarVentilation(8.0))

    assert alveoli.alveolar_ventilation_l_min == 8.0
    assert alveoli.agent_amount_l == amount_before


def test_reset_clears_agent_and_preserves_settings() -> None:
    alveoli = AlveolarCompartment(
        gas_volume_l=3.0, alveolar_ventilation_l_min=AlveolarVentilation(5.0)
    )
    alveoli.set_partial_pressure_fraction(Fraction(0.05))

    alveoli.reset()

    assert alveoli.agent_amount_l == 0.0
    assert alveoli.partial_pressure_fraction == 0.0
    assert alveoli.gas_volume_l == 3.0
    assert alveoli.alveolar_ventilation_l_min == 5.0


def test_accepts_ventilation_at_both_ends_of_the_supported_range() -> None:
    """Zero is apnoea, a supported and deliberately teachable input; the
    maximum is the corner of the settings envelope the gates measure at."""

    for alveolar_ventilation_l_min in (0.0, MAXIMUM_ALVEOLAR_VENTILATION_L_MIN):
        alveoli = AlveolarCompartment(
            alveolar_ventilation_l_min=AlveolarVentilation(alveolar_ventilation_l_min)
        )

        assert alveoli.alveolar_ventilation_l_min == alveolar_ventilation_l_min

        alveoli.set_alveolar_ventilation(AlveolarVentilation(alveolar_ventilation_l_min))

        assert alveoli.alveolar_ventilation_l_min == alveolar_ventilation_l_min


def test_rejects_ventilation_above_the_supported_range() -> None:
    """Regression (PL-0MLQ): 200 L/min was accepted and simulated."""

    alveoli = AlveolarCompartment(alveolar_ventilation_l_min=AlveolarVentilation(4.0))

    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        alveoli.set_alveolar_ventilation(AlveolarVentilation(200.0))

    assert alveoli.alveolar_ventilation_l_min == 4.0


def test_rejects_construction_with_ventilation_above_the_supported_range() -> None:
    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        AlveolarCompartment(alveolar_ventilation_l_min=AlveolarVentilation(200.0))


def test_the_bare_alveolar_defaults_match_the_shipped_patient_file() -> None:
    """`PL-DJYF`: the literals in `core/alveolar.py` are a checked restatement.

    `data/patients/reference_adult.json` is the authority, and
    `AgentUptakeSystem.for_agent()` passes both values from it explicitly, so
    the field defaults are reached only by a bare unit-test construction. They
    are kept so that a test of alveolar physics need not load package data —
    but a reader meeting `gas_volume_l: float = 2.5` in `core/alveolar.py`
    will take it for the model's alveolar volume whatever the docstring says,
    so the two are not allowed to drift apart silently.

    This is `PL-4YY1`'s
    `test_the_bare_circuit_defaults_match_the_shipped_machine_file` applied to
    the compartment it left behind: the same restatement, in the same shape,
    one file over.
    """

    patient = load_reference_adult_parameters()
    alveoli = AlveolarCompartment()

    assert alveoli.gas_volume_l == patient.alveolar_gas_volume_l
    assert alveoli.alveolar_ventilation_l_min == patient.default_alveolar_ventilation_l_min


def test_for_agent_builds_the_alveoli_at_the_patient_file_s_values() -> None:
    """A run from the shipped patient file carries its values, and the 37.5 s they give.

    Asserting the ventilation time constant as well as the two inputs is the
    same reasoning `PL-4YY1` applied to the circuit's 90 s: 37.5 s is the
    alveolar washout the early rise is read against, and it is what a silent
    change to either value would move.

    It cannot show that the file was read, because the shipped values equal
    `AlveolarCompartment`'s field defaults;
    `test_for_agent_builds_the_alveoli_at_changed_patient_file_values` below
    does (`PL-H8QP`).
    """

    patient = load_reference_adult_parameters()
    alveoli = AgentUptakeSystem.for_agent("sevoflurane").alveoli

    assert alveoli.gas_volume_l == patient.alveolar_gas_volume_l
    assert alveoli.alveolar_ventilation_l_min == patient.default_alveolar_ventilation_l_min
    assert alveoli.gas_volume_l / alveoli.alveolar_ventilation_l_min * 60.0 == pytest.approx(37.5)


def test_for_agent_builds_the_alveoli_at_changed_patient_file_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The shipped path reads the file rather than falling through to a default.

    Because the defaults equal the shipped file's values, dropping the explicit
    keyword arguments in `for_agent()` would change no number in a run built
    from that file: the run would simply stop reading its own parameter file,
    and every provenance row pointing at `data/patients/reference_adult.json`
    would quietly become a claim about a file the model no longer consults. So
    this run is built from the shipped file with both values moved off the
    defaults, parsed as the loader parses it and handed to `for_agent()` by
    replacing the loader it calls, the way `tests/unit/test_circuit.py` hands it
    a machine profile (`PL-H8QP`). 3.0 L at 5.0 L/min is 36 s.
    """

    payload: dict[str, object] = json.loads(
        files("anesthesia_sim.data.patients")
        .joinpath("reference_adult.json")
        .read_text(encoding="utf-8")
    )
    payload["alveolar_gas_volume_l"] = 3.0
    payload["default_alveolar_ventilation_l_min"] = 5.0
    patient = parse_reference_adult_parameters(payload)
    monkeypatch.setattr(uptake_system, "load_reference_adult_parameters", lambda: patient)

    alveoli = AgentUptakeSystem.for_agent("sevoflurane").alveoli

    assert alveoli.gas_volume_l == 3.0
    assert alveoli.alveolar_ventilation_l_min == 5.0
    assert alveoli.gas_volume_l / alveoli.alveolar_ventilation_l_min * 60.0 == pytest.approx(36.0)
