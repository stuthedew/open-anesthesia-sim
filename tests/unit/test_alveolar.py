import json
from importlib.resources import files

import pytest

from anesthesia_sim.core import uptake_system
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.parameters import (
    load_reference_adult_parameters,
    parse_reference_adult_parameters,
)
from anesthesia_sim.core.supported_ranges import MAXIMUM_ALVEOLAR_VENTILATION_L_MIN
from anesthesia_sim.core.uptake_system import AgentUptakeSystem


def test_rejects_agent_amount_above_alveolar_capacity() -> None:
    with pytest.raises(
        SimulationConfigurationError,
        match="^agent_amount_l exceeds the alveolar capacity for a concentration fraction of 1$",
    ):
        AlveolarCompartment(agent_amount_l=2.6)


def test_changing_ventilation_preserves_alveolar_agent() -> None:
    alveoli = AlveolarCompartment()
    alveoli.set_partial_pressure_fraction(0.05)
    amount_before = alveoli.agent_amount_l

    alveoli.set_alveolar_ventilation(8.0)

    assert alveoli.alveolar_ventilation_l_min == 8.0
    assert alveoli.agent_amount_l == amount_before


def test_reset_clears_agent_and_preserves_settings() -> None:
    alveoli = AlveolarCompartment(gas_volume_l=3.0, alveolar_ventilation_l_min=5.0)
    alveoli.set_partial_pressure_fraction(0.05)

    alveoli.reset()

    assert alveoli.agent_amount_l == 0.0
    assert alveoli.partial_pressure_fraction == 0.0
    assert alveoli.gas_volume_l == 3.0
    assert alveoli.alveolar_ventilation_l_min == 5.0


def test_accepts_ventilation_at_both_ends_of_the_supported_range() -> None:
    """Zero is apnoea, a supported and deliberately teachable input; the
    maximum is the corner of the settings envelope the gates measure at."""

    for alveolar_ventilation_l_min in (0.0, MAXIMUM_ALVEOLAR_VENTILATION_L_MIN):
        alveoli = AlveolarCompartment(alveolar_ventilation_l_min=alveolar_ventilation_l_min)

        assert alveoli.alveolar_ventilation_l_min == alveolar_ventilation_l_min

        alveoli.set_alveolar_ventilation(alveolar_ventilation_l_min)

        assert alveoli.alveolar_ventilation_l_min == alveolar_ventilation_l_min


def test_rejects_ventilation_above_the_supported_range() -> None:
    """Regression (PL-0MLQ): 200 L/min was accepted and simulated."""

    alveoli = AlveolarCompartment(alveolar_ventilation_l_min=4.0)

    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        alveoli.set_alveolar_ventilation(200.0)

    assert alveoli.alveolar_ventilation_l_min == 4.0


def test_rejects_construction_with_ventilation_above_the_supported_range() -> None:
    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        AlveolarCompartment(alveolar_ventilation_l_min=200.0)


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
