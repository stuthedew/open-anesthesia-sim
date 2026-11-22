"""The MAC that a run divides by: one agent's 1 MAC for one patient, and the age it is for.

MAC falls with age. Mapleson's meta-analysis gives every inhaled agent's MAC
at age 40 and one equation for how it changes with age (Br J Anaesth
1996;76:179-185). Each agent file stores the MAC at age 40
(`AgentParameters.mac_at_age_40_percent`). That stored value is a property
of the agent. The MAC that a run divides by is a property of the agent *and*
the patient, so it is built here, in one function, from both.

The reference adult has no age input yet, and is the 40-year-old adult whose
MAC the agent file states. So today `mac_for_patient` returns the agent's MAC
at age 40, and says so in `PatientMac.age_years`. When patient age becomes an
input (`PL-8F9D`), Mapleson's age equation goes in `mac_for_patient`, and no
reader of a `PatientMac` changes.

Every MAC multiple the interface shows divides by `PatientMac.percent`, the
dial opens at it, and the `1 MAC` reference beside the chart prints it with
its age. No governing equation reads it. `docs/PARAMETERS.md` § \"Delivery-limit and
MAC parameters" gives its provenance.
"""

from __future__ import annotations

from dataclasses import dataclass

from anesthesia_sim.core.checked_number import shown
from anesthesia_sim.core.checked_record import restore_through_checks
from anesthesia_sim.core.concentration import MacPercent, require_mac_percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.parameters import (
    MAC_STORED_AT_AGE_YEARS,
    AgentParameters,
    ReferenceAdultParameters,
)

__all__ = ["PatientMac", "mac_for_patient"]


@dataclass(frozen=True, slots=True)
class PatientMac:
    """One agent's 1 MAC for one patient, as a percent of one atmosphere, and the patient's age.

    The two travel together, so that a MAC is never shown without the age it
    belongs to. `mac_for_patient` builds one.

    Raises:
        TypeError: `percent` was not built as a `MacPercent`
            (`core/concentration.py`), or `age_years` is not an `int`. A
            `bool` is refused, although Python counts it as an `int`.
        SimulationConfigurationError: `age_years` is not above zero.
    """

    percent: MacPercent
    age_years: int

    def __post_init__(self) -> None:
        require_mac_percent("percent", self.percent)

        if isinstance(self.age_years, bool) or not isinstance(self.age_years, int):
            raise TypeError(
                f"age_years of {shown(self.age_years)} must be a whole number of years, "
                f"and it has type {type(self.age_years).__name__}"
            )

        if self.age_years <= 0:
            raise SimulationConfigurationError(
                f"age_years of {self.age_years} is not an age: a MAC belongs to a patient "
                "older than zero years"
            )

    def __setstate__(self, state: object) -> None:
        """Restore an unpickled or copied record through the constructor's checks (`PL-8W1Q`)."""

        restore_through_checks(self, state)


def mac_for_patient(agent: AgentParameters, patient: ReferenceAdultParameters) -> PatientMac:
    """Return the agent's 1 MAC for this patient, with the age it belongs to.

    The reference adult is the 40-year-old adult that the agent file's MAC
    describes. So this returns `agent.mac_at_age_40_percent` at age 40. The
    module docstring says what changes here when age becomes an input.

    Raises:
        TypeError: `agent` is not an `AgentParameters`, or `patient` is not a
            `ReferenceAdultParameters`. Python does not enforce the
            annotations at run time, and the MAC at age 40 is right only for
            the patient that the reference adult's file describes.
    """

    if not isinstance(agent, AgentParameters):
        raise TypeError(f"agent must be an AgentParameters, and it has type {type(agent).__name__}")

    if not isinstance(patient, ReferenceAdultParameters):
        raise TypeError(
            "patient must be a ReferenceAdultParameters, the 40-year-old adult whose MAC "
            f"the agent files state, and it has type {type(patient).__name__}"
        )

    return PatientMac(percent=agent.mac_at_age_40_percent, age_years=MAC_STORED_AT_AGE_YEARS)
