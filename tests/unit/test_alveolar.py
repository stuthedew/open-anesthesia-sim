import copy
import json
import pickle
import re
from dataclasses import astuple, replace
from importlib.resources import files
from math import inf, nan

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
        match=(
            r"^alveolar agent_amount_l of 2.6 L is more than the 2.5 L the alveolar compartment "
            r'holds at a partial pressure of one atmosphere \(docs/MODEL.md, "Gas compartments"\)$'
        ),
    ):
        AlveolarCompartment(
            gas_volume_l=2.5,
            alveolar_ventilation_l_min=AlveolarVentilation(4.0),
            agent_amount_l=2.6,
        )


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

    alveoli = AlveolarCompartment(
        gas_volume_l=2.5, alveolar_ventilation_l_min=AlveolarVentilation(4.0)
    )
    alveoli.set_partial_pressure_fraction(Fraction(0.05))
    held = alveoli.agent_amount_l
    past_capacity = alveoli.gas_volume_l * 1.0000001
    refused = (
        rf"^alveolar agent_amount_l of {re.escape(repr(past_capacity))} L is more than the "
        r"2.5 L the alveolar compartment holds at a partial pressure of one atmosphere "
        r'\(docs/MODEL.md, "Gas compartments"\)$'
    )

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


@pytest.mark.parametrize(
    ("field", "value", "error", "message"),
    [
        pytest.param(
            "gas_volume_l",
            0.0,
            SimulationConfigurationError,
            "^gas_volume_l must be positive and finite$",
            id="zero-volume",
        ),
        pytest.param(
            "gas_volume_l",
            -1.0,
            SimulationConfigurationError,
            "^gas_volume_l must be positive and finite$",
            id="negative-volume",
        ),
        pytest.param(
            "gas_volume_l",
            inf,
            SimulationConfigurationError,
            "^gas_volume_l must be positive and finite$",
            id="infinite-volume",
        ),
        pytest.param(
            "gas_volume_l",
            nan,
            SimulationConfigurationError,
            "^gas_volume_l must be positive and finite$",
            id="nan-volume",
        ),
        pytest.param(
            "gas_volume_l", True, TypeError, "^gas_volume_l of True has type bool", id="bool-volume"
        ),
        pytest.param(
            "gas_volume_l",
            0.5,
            SimulationConfigurationError,
            r"^gas_volume_l of 0.5 is too small for the 0.625 L of agent the alveolar "
            r"compartment holds: it would leave room for 0.5 L at a partial pressure of one "
            r'atmosphere \(docs/MODEL.md, "Gas compartments"\)$',
            id="volume-under-the-agent-held",
        ),
        pytest.param(
            "alveolar_ventilation_l_min",
            4.0,
            TypeError,
            "^alveolar_ventilation_l_min of 4.0 was not built as AlveolarVentilation",
            id="bare-ventilation",
        ),
        pytest.param(
            "gas_volume",
            1.0,
            AttributeError,
            "^'AlveolarCompartment' object has no attribute 'gas_volume'",
            id="misspelt-field",
        ),
    ],
)
def test_a_direct_write_is_held_to_the_constructors_checks(
    field: str, value: object, error: type[Exception], message: str
) -> None:
    """An assignment past the constructor and the setters is refused as they refuse it.

    Until `PL-19Y0` only the ventilation's type and the agent amount were
    checked at the write, so `gas_volume_l = 0.0` was accepted on a built
    compartment and the next fraction divided by it. The volume is now checked
    at its own write, for its own sign and against the agent held: 0.5 L under
    the 0.625 L held would put the alveolar partial pressure at 1.25
    atmospheres. A name that is no field passes the guard to the slots, which
    refuse it, so a misspelt write cannot leave the field it meant unchanged
    while appearing to succeed. Nothing is written when a value is refused.
    """

    alveoli = AlveolarCompartment(
        gas_volume_l=2.5, alveolar_ventilation_l_min=AlveolarVentilation(4.0)
    )
    alveoli.set_partial_pressure_fraction(Fraction(0.25))
    held = astuple(alveoli)

    with pytest.raises(error, match=message):
        setattr(alveoli, field, value)

    assert astuple(alveoli) == held


def test_a_volume_at_the_agent_held_is_written_and_a_copy_is_held_to_it_too() -> None:
    """The capacity bound is closed, and `replace`, a copy and a pickle meet the same checks.

    A volume equal to the agent held is a partial pressure of exactly one
    atmosphere, the top of the range rather than past it, as
    `set_circuit_volume` admits for the circuit. `dataclasses.replace` builds
    a new compartment, whose constructor writes the volume before the amount,
    so the amount's write is the one that refuses there; a copy and a pickle
    restore the fields one at a time through `__setattr__`, in the same order,
    so a volume planted past the guard is refused when either is made
    (`PL-19Y0`).
    """

    alveoli = AlveolarCompartment(
        gas_volume_l=2.5, alveolar_ventilation_l_min=AlveolarVentilation(4.0)
    )
    alveoli.set_partial_pressure_fraction(Fraction(0.25))
    refused = (
        r"^alveolar agent_amount_l of 0.625 L is more than the 0.5 L the alveolar compartment "
        r'holds at a partial pressure of one atmosphere \(docs/MODEL.md, "Gas compartments"\)$'
    )

    with pytest.raises(SimulationConfigurationError, match=refused):
        replace(alveoli, gas_volume_l=0.5)

    smuggled = copy.copy(alveoli)
    object.__setattr__(smuggled, "gas_volume_l", 0.5)

    with pytest.raises(SimulationConfigurationError, match=refused):
        copy.copy(smuggled)

    with pytest.raises(SimulationConfigurationError, match=refused):
        pickle.loads(pickle.dumps(smuggled))

    alveoli.gas_volume_l = alveoli.agent_amount_l

    assert alveoli.partial_pressure_fraction == 1.0


@pytest.mark.parametrize("invalid_value", [0.0, -1.0, float("inf"), float("nan")])
def test_rejects_invalid_alveolar_gas_volume(invalid_value: float) -> None:
    """A bad volume is refused under its own name, at its own write.

    The constructor writes `gas_volume_l` before `agent_amount_l`, and each
    write checks its own field (`PL-19Y0`), so the volume is refused before
    the amount's capacity check reads it. Until then `__post_init__` refused
    it after that read, which kept a leniency for a capacity that was not
    positive, and that leniency admitted every amount once a bad volume had
    been written past the constructor (`PL-544D`, found at review).
    """

    with pytest.raises(SimulationConfigurationError, match="gas_volume_l"):
        AlveolarCompartment(
            alveolar_ventilation_l_min=AlveolarVentilation(4.0), gas_volume_l=invalid_value
        )


@pytest.mark.parametrize("not_a_number", ["2.5", None])
def test_a_volume_that_is_not_a_number_is_refused_under_its_own_name(not_a_number: object) -> None:
    """The volume's own write refuses a non-number by the volume's name, before anything reads it.

    The capacity check `PL-544D` put in the amount's write read `gas_volume_l`
    before `__post_init__` had required it, so a `require_a_number` there
    stood in for the volume's own check: without it the comparison's own
    `TypeError` came back - "'<' not supported between instances of 'float'
    and 'str'" - naming neither the field nor its constraint, the shape
    `PL-3800` had removed (found at review). Since `PL-19Y0` the volume's own
    write requires it first, and the stand-in is gone.
    """

    with pytest.raises(TypeError, match=f"^gas_volume_l of {not_a_number!r} has type "):
        AlveolarCompartment(
            alveolar_ventilation_l_min=AlveolarVentilation(4.0), gas_volume_l=not_a_number
        )  # type: ignore[arg-type]


def test_a_rollback_restores_the_captured_amount_past_the_capacity_guard() -> None:
    """`restore_state` writes what the compartment held, whatever the capacity has become.

    A rollback that could raise would replace the step's own error and leave
    the compartments restored after this one holding the failed step
    (`AgentUptakeSystem.restore_state`), so it writes the slot past
    `__setattr__` (`PL-544D`, found at review). The volume is written past its
    own guard, which since `PL-19Y0` refuses it, because what is under test is
    the rollback and not how the capacity came to be below the amount; the
    state restored is the one the step began from, over capacity as it already
    was, for the snapshot's `Fraction` to refuse.
    """

    alveoli = AlveolarCompartment(
        gas_volume_l=2.5, alveolar_ventilation_l_min=AlveolarVentilation(4.0)
    )
    alveoli.set_partial_pressure_fraction(Fraction(0.05))
    captured = alveoli.capture_state()
    alveoli.set_partial_pressure_fraction(Fraction(0.06))
    object.__setattr__(alveoli, "gas_volume_l", captured.agent_amount_l / 2)

    alveoli.restore_state(captured)

    assert alveoli.agent_amount_l == captured.agent_amount_l
    assert alveoli.partial_pressure_fraction == 2.0


def test_changing_ventilation_preserves_alveolar_agent() -> None:
    alveoli = AlveolarCompartment(
        gas_volume_l=2.5, alveolar_ventilation_l_min=AlveolarVentilation(4.0)
    )
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
            gas_volume_l=2.5,
            alveolar_ventilation_l_min=AlveolarVentilation(alveolar_ventilation_l_min),
        )

        assert alveoli.alveolar_ventilation_l_min == alveolar_ventilation_l_min

        alveoli.set_alveolar_ventilation(AlveolarVentilation(alveolar_ventilation_l_min))

        assert alveoli.alveolar_ventilation_l_min == alveolar_ventilation_l_min


def test_rejects_ventilation_above_the_supported_range() -> None:
    """Regression (PL-0MLQ): 200 L/min was accepted and simulated."""

    alveoli = AlveolarCompartment(
        gas_volume_l=2.5, alveolar_ventilation_l_min=AlveolarVentilation(4.0)
    )

    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        alveoli.set_alveolar_ventilation(AlveolarVentilation(200.0))

    assert alveoli.alveolar_ventilation_l_min == 4.0


def test_rejects_construction_with_ventilation_above_the_supported_range() -> None:
    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        AlveolarCompartment(gas_volume_l=2.5, alveolar_ventilation_l_min=AlveolarVentilation(200.0))


@pytest.mark.parametrize("missing", ["gas_volume_l", "alveolar_ventilation_l_min"])
def test_an_alveolar_compartment_cannot_be_built_without_its_volume_or_ventilation(
    missing: str,
) -> None:
    """`PL-M85T`: neither value has a default, so every caller states the one it means.

    Each defaulted to a second copy of `data/patients/reference_adult.json`,
    2.5 L and 4.0 L/min, which only a test held equal to the file
    (`PL-DJYF`). `AgentUptakeSystem.for_agent()` passes both from the file.
    """

    given: dict[str, object] = {
        "gas_volume_l": 2.5,
        "alveolar_ventilation_l_min": AlveolarVentilation(4.0),
    }
    del given[missing]

    with pytest.raises(TypeError, match=f"missing 1 required positional argument: '{missing}'"):
        AlveolarCompartment(**given)  # type: ignore[arg-type]


def test_for_agent_builds_the_alveoli_at_the_patient_file_s_values() -> None:
    """A run from the shipped patient file carries its values, and the 37.5 s they give.

    Asserting the ventilation time constant as well as the two inputs is the
    same reasoning `PL-4YY1` applied to the circuit's 90 s: 37.5 s is the
    alveolar washout the early rise is read against, and it is what a silent
    change to either value would move.

    It cannot show that the file was read, because the shipped values are the
    ones a test would type;
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

    Until `PL-M85T` the defaults equalled the shipped file's values, so
    dropping the keyword arguments in `for_agent()` would have changed no
    number in a run built from that file: the run would simply have stopped
    reading its own parameter file, and every provenance row pointing at
    `data/patients/reference_adult.json` would quietly become a claim about a
    file the model no longer consults. So this run is built from the shipped
    file with both values moved off the shipped ones, parsed as the loader
    parses it and handed to `for_agent()` by
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
