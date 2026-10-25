"""Recover stored parameters from simulated measurements.

The other reference tests check that the shipped step solves the equations in
`docs/MODEL.md`. The oracle in `test_coupled_dynamics.py` integrates those same
equations independently, so it cannot detect an equation that the
specification itself states wrongly. This module is a third kind of check. Each
test runs the shipped model through a measurement procedure whose result is
fixed by a stored parameter, and requires the procedure to return that
parameter. Each procedure is written from a physical law, not from the
specification's equations. An error that the code and the specification share
therefore shows up here as a measurement that comes back wrong.

Lerou and Booij used this device to check their own system model. They
simulated the closed-circuit helium dilution measurement of alveolar volume,
and they report that the result supports the model's mathematical credibility
(Lerou JG, Booij LH. Model-based administration of inhalation anaesthesia. 1.
Developing a system model. Br J Anaesth 2001;86:12-28,
https://doi.org/10.1093/bja/86.1.12; PMID 11575385, retrieved from PubMed and
read at the abstract 2026-10-25). The first test below is their procedure. The
second recovers each tissue group's volume by the Fick principle.

Neither test needs a second gas. At zero cardiac output, blood carries none of
the agent away from the lungs, so the agent behaves as an insoluble tracer,
which is the role helium plays in the real measurement.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

import pytest

from anesthesia_sim.core.parameters import (
    load_agent_parameters,
    load_reference_adult_parameters,
    load_reference_circle_system_parameters,
)
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

AGENT_IDS = ("sevoflurane", "isoflurane", "desflurane")

# Declared here rather than imported from `core/units.py`, for the reason
# `test_coupled_dynamics.py` gives: a factor taken from the code under test
# would check that code against itself.
SECONDS_PER_MINUTE = 60.0

STEP_S = 0.1

# The dilution's three phases. The circuit fills for 300 s while ventilation is
# stopped, which is about three circuit time constants at the opening 4 L/min in
# the 6 L circuit. How full it gets does not matter, because the procedure reads
# the circuit's fraction at the moment it is closed. The closed circuit and the
# lungs then mix for 900 s. Their mixing time constant at 4 L/min of alveolar
# ventilation is V_C V_A / (V_dot_A (V_C + V_A)), about 26 s, so 900 s is about
# 34 time constants and leaves the two fractions apart only by rounding.
DILUTION_FILL_S = 300.0
DILUTION_MIXING_S = 900.0

# How far apart the circuit and alveolar fractions may be, relative to the
# circuit's, when the final reading is taken. This is the procedure's stop rule:
# a helium dilution is read once the spirometer's concentration stops falling.
# Measured 2026-10-25, the worst gap across the three agents is 5.5e-14.
DILUTION_EQUILIBRIUM_RELATIVE_GAP = 1e-12

# How far the recovered alveolar volume may sit from the stored one, relative to
# the stored one. Measured 2026-10-25, the worst residual across the three
# agents is 6.1e-13, so the bound allows about sixteen times that.
DILUTION_RELATIVE_TOLERANCE = 1e-11

# The washin's length. At 1800 s, muscle and fat hold enough agent that their
# fractions sit far above rounding, and the run still takes under a second per
# agent.
WASHIN_HORIZON_S = 1800.0

# How far a recovered tissue volume may sit from the stored one, relative to the
# stored one. The uptake is integrated by the trapezoidal rule over the 0.1 s
# samples, so the residual is the rule's error. Measured 2026-10-25, the worst
# residual is 7.9e-11, in isoflurane's vessel-rich group, so the bound allows
# about twelve times that.
WASHIN_RELATIVE_TOLERANCE = 1e-9


def _advance(system: AgentUptakeSystem, duration_s: float) -> None:
    step = SimulationStep(STEP_S)
    for _ in range(round(duration_s / STEP_S)):
        system.advance(step)


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_an_alveolar_volume_recovered_by_closed_circuit_dilution_matches_the_stored_value(
    agent_id: str,
) -> None:
    """Measure the alveolar volume as a closed-circuit helium dilution does.

    The breathing circuit plays the spirometer, a vessel of known volume $`V_C`$
    holding the tracer at a known fraction $`F_1`$. Once the circuit is closed
    and connected to the lungs, the tracer spreads into the alveolar gas until
    both sit at $`F_2`$. A closed system conserves the tracer, so
    $`V_CF_1 = (V_C + V_A)F_2`$, and therefore:

    $$
    V_A = V_C\\frac{F_1 - F_2}{F_2}
    $$

    The circuit is closed by setting the fresh gas flow to zero. Nothing then
    enters the circuit and nothing leaves it through the exhaust. This is not
    the closed-circuit anaesthesia technique that `docs/MODEL.md` § "Breathing
    circuit" says this model does not represent, because that technique needs
    fresh gas matched to the patient's uptake. Here there is no fresh gas and,
    at zero cardiac output, no uptake.

    The procedure checks the circuit and alveolar capacities and the
    ventilation exchange against conservation alone. Recovering the same
    volume for all three agents also checks that the agent's solubility does
    not enter once blood flow stops.
    """

    patient = load_reference_adult_parameters()
    circuit_volume_l = load_reference_circle_system_parameters().circuit_volume_l
    system = AgentUptakeSystem.for_agent(agent_id)

    # Fill the circuit while the lungs are cut off from it.
    system.set_alveolar_ventilation(AlveolarVentilation(0.0))
    _advance(system, DILUTION_FILL_S)
    assert system.alveoli.agent_amount_l == 0.0
    assert system.patient.total_agent_amount_l == 0.0
    initial_circuit_fraction = system.circuit.inspired_partial_pressure_fraction
    assert initial_circuit_fraction > 0.0

    # Close the circuit, stop the blood flow and ventilate the lungs from it.
    system.set_fresh_gas_flow(FreshGasFlow(0.0))
    system.set_cardiac_output(CardiacOutput(0.0))
    system.set_alveolar_ventilation(AlveolarVentilation(patient.default_alveolar_ventilation_l_min))
    _advance(system, DILUTION_MIXING_S)
    final_circuit_fraction = system.circuit.inspired_partial_pressure_fraction
    final_alveolar_fraction = system.alveoli.partial_pressure_fraction
    assert abs(final_circuit_fraction - final_alveolar_fraction) <= (
        DILUTION_EQUILIBRIUM_RELATIVE_GAP * final_circuit_fraction
    )
    assert system.patient.total_agent_amount_l == 0.0

    recovered_alveolar_volume_l = (
        circuit_volume_l
        * (initial_circuit_fraction - final_circuit_fraction)
        / final_circuit_fraction
    )

    assert recovered_alveolar_volume_l == pytest.approx(
        patient.alveolar_gas_volume_l, rel=DILUTION_RELATIVE_TOLERANCE
    )


@dataclass(frozen=True, slots=True)
class _StoredTissueGroup:
    """One tissue group's stored parameters, read from the data files."""

    volume_l: float
    perfusion_fraction: float
    tissue_gas_partition_coefficient: float


def _stored_tissue_groups(agent_id: str) -> dict[str, _StoredTissueGroup]:
    agent = load_agent_parameters(agent_id)
    patient = load_reference_adult_parameters()
    return {
        "vessel_rich": _StoredTissueGroup(
            volume_l=patient.vessel_rich_volume_l,
            perfusion_fraction=patient.vessel_rich_perfusion_fraction,
            tissue_gas_partition_coefficient=agent.vessel_rich_tissue_gas_partition_coefficient,
        ),
        "muscle": _StoredTissueGroup(
            volume_l=patient.muscle_volume_l,
            perfusion_fraction=patient.muscle_perfusion_fraction,
            tissue_gas_partition_coefficient=agent.muscle_tissue_gas_partition_coefficient,
        ),
        "fat": _StoredTissueGroup(
            volume_l=patient.fat_volume_l,
            perfusion_fraction=patient.fat_perfusion_fraction,
            tissue_gas_partition_coefficient=agent.fat_tissue_gas_partition_coefficient,
        ),
    }


@cache
def _volumes_recovered_from_washin(agent_id: str) -> dict[str, float]:
    """Recover each tissue group's volume from the opening wash-in, by the Fick principle.

    A tissue's uptake rate is its blood flow times the difference in agent
    content between the blood that enters it and the blood that leaves it. Blood
    holds $`\\lambda_{b:g}F`$ litres of agent vapour per litre at fraction
    $`F`$, so:

    $$
    \\dot U_i = Q_i\\lambda_{b:g}(F_a - F_{v,i})
    $$

    where $`F_{v,i}`$ is the fraction in the blood leaving the group. The run
    samples both fractions after every step, and the trapezoidal rule
    integrates the rate into the total uptake $`U_i`$. At the end of the run,
    the tissue holds $`\\lambda_{i:g}F_i`$ litres of agent vapour per litre at
    its own fraction $`F_i`$, which is what the tissue:gas partition
    coefficient means. Its volume is therefore:

    $$
    V_i = \\frac{U_i}{\\lambda_{i:g}F_i}
    $$

    The arterial fraction is read as the alveolar one. The model has no
    arterial compartment, because blood leaving the lungs is taken to
    equilibrate with alveolar gas (`docs/MODEL.md` § "Arterial blood").
    """

    agent = load_agent_parameters(agent_id)
    patient = load_reference_adult_parameters()
    stored = _stored_tissue_groups(agent_id)
    system = AgentUptakeSystem.for_agent(agent_id)
    tissues = dict(zip(stored, system.patient.tissues, strict=True))
    cardiac_output_l_s = patient.default_cardiac_output_l_min / SECONDS_PER_MINUTE

    def uptake_rates_l_s() -> dict[str, float]:
        arterial_fraction = system.alveoli.partial_pressure_fraction
        return {
            name: stored[name].perfusion_fraction
            * cardiac_output_l_s
            * agent.blood_gas_partition_coefficient
            * (arterial_fraction - tissue.venous_outflow_partial_pressure_fraction)
            for name, tissue in tissues.items()
        }

    step = SimulationStep(STEP_S)
    uptake_l = dict.fromkeys(stored, 0.0)
    previous_rates_l_s = uptake_rates_l_s()
    for _ in range(round(WASHIN_HORIZON_S / STEP_S)):
        system.advance(step)
        rates_l_s = uptake_rates_l_s()
        for name in uptake_l:
            uptake_l[name] += 0.5 * STEP_S * (previous_rates_l_s[name] + rates_l_s[name])
        previous_rates_l_s = rates_l_s

    return {
        name: uptake_l[name]
        / (stored[name].tissue_gas_partition_coefficient * tissue.partial_pressure_fraction)
        for name, tissue in tissues.items()
    }


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_a_tissue_volume_recovered_from_its_washin_matches_the_stored_value(agent_id: str) -> None:
    """Each tissue group's volume, measured by the Fick principle, is the stored one.

    The procedure is written from the Fick principle and the meaning of a
    partition coefficient, not from the tissue equation in `docs/MODEL.md`.
    It catches errors that still conserve agent, which the mass-balance check
    cannot see. Suppose the specification had written the tissue capacity as
    $`V_i\\lambda_{i:b}`$, leaving out the blood:gas factor, and formed the
    tissue's rate to match. Agent would still be conserved, and the code and
    the oracle would agree on the wrong trajectory. Every volume would come
    back here divided by $`\\lambda_{b:g}`$. On 2026-10-25 that error, muscle
    and fat with their flow fractions swapped, and every flow left in litres
    per minute were each put into the shipped code in turn. This test failed
    on each, and the agent accounting raised on none of them.
    """

    stored_volumes_l = {
        name: group.volume_l for name, group in _stored_tissue_groups(agent_id).items()
    }

    assert _volumes_recovered_from_washin(agent_id) == pytest.approx(
        stored_volumes_l, rel=WASHIN_RELATIVE_TOLERANCE
    )
