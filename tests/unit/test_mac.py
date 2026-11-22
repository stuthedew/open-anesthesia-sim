"""The MAC that a run divides by, built from the agent and the patient (`core/mac.py`).

The expected MACs are Mapleson 1996's MACs at age 40, transcribed from the
abstract (Br J Anaesth 1996;76:179-185, PMID 8777094): 1.80% sevoflurane,
1.17% isoflurane and 6.6% desflurane. They are not read from the agent files,
so a file that held a wrong MAC would fail here.
"""

from __future__ import annotations

import copy
import pickle

import pytest

from anesthesia_sim.core.concentration import MacPercent, Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.mac import PatientMac, mac_for_patient
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters

#: Mapleson 1996, abstract: the MAC at age 40 of each shipped agent, in percent.
MAPLESON_MAC_AT_AGE_40_PERCENT = {"sevoflurane": 1.80, "isoflurane": 1.17, "desflurane": 6.6}

#: The age that Mapleson's figures above are stated for.
MAPLESON_REFERENCE_AGE_YEARS = 40


@pytest.mark.parametrize(("agent_id", "expected_percent"), MAPLESON_MAC_AT_AGE_40_PERCENT.items())
def test_the_reference_adult_s_mac_is_mapleson_s_mac_at_age_40(
    agent_id: str, expected_percent: float
) -> None:
    """The reference adult records no age, so the simulator uses Mapleson's MAC at age 40 for it."""

    patient_mac = mac_for_patient(
        load_agent_parameters(agent_id), load_reference_adult_parameters()
    )

    assert float(patient_mac.percent) == expected_percent
    assert patient_mac.age_years == MAPLESON_REFERENCE_AGE_YEARS


def test_the_run_s_mac_is_a_checked_mac_percent() -> None:
    """Every divisor downstream takes a `MacPercent`, so the function returns one."""

    patient_mac = mac_for_patient(
        load_agent_parameters("isoflurane"), load_reference_adult_parameters()
    )

    assert isinstance(patient_mac.percent, MacPercent)


def test_a_wrong_agent_or_patient_is_refused() -> None:
    """Python does not enforce the annotations, so the function checks both arguments."""

    agent = load_agent_parameters("sevoflurane")
    patient = load_reference_adult_parameters()

    with pytest.raises(TypeError, match="agent must be an AgentParameters"):
        mac_for_patient(patient, patient)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="patient must be a ReferenceAdultParameters"):
        mac_for_patient(agent, agent)  # type: ignore[arg-type]


def test_a_mac_that_is_not_a_mac_percent_is_refused() -> None:
    """A plain percent could be zero, so the record takes only a `MacPercent`."""

    with pytest.raises(TypeError):
        PatientMac(percent=Percent(1.8), age_years=40)  # type: ignore[arg-type]


@pytest.mark.parametrize("age_years", [True, 40.0, "40"])
def test_an_age_that_is_not_a_whole_number_of_years_is_refused(age_years: object) -> None:
    """A bool counts as an int in Python, and is refused all the same."""

    with pytest.raises(TypeError, match="whole number of years"):
        PatientMac(percent=MacPercent(1.8), age_years=age_years)  # type: ignore[arg-type]


@pytest.mark.parametrize("age_years", [0, -40])
def test_an_age_of_zero_or_less_is_refused(age_years: int) -> None:
    with pytest.raises(SimulationConfigurationError, match=f"age_years of {age_years}"):
        PatientMac(percent=MacPercent(1.8), age_years=age_years)


def test_a_copied_or_pickled_mac_is_the_same_mac() -> None:
    """A copy and every pickle protocol rebuild the record through its checks, unchanged."""

    patient_mac = PatientMac(percent=MacPercent(1.17), age_years=40)

    rebuilt = [copy.copy(patient_mac), copy.deepcopy(patient_mac)] + [
        pickle.loads(pickle.dumps(patient_mac, protocol))
        for protocol in range(pickle.HIGHEST_PROTOCOL + 1)
    ]

    assert all(each == patient_mac for each in rebuilt)


def test_a_restored_mac_with_an_age_of_zero_is_refused() -> None:
    """A saved record edited to an impossible age fails when it is loaded (`PL-8W1Q`)."""

    restored = object.__new__(PatientMac)

    with pytest.raises(SimulationConfigurationError, match="age_years of 0"):
        restored.__setstate__([MacPercent(1.8), 0])
