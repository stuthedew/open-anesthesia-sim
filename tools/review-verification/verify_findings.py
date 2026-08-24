"""Re-run each reproducible defect from the architecture review.

Every check reports REPRODUCED if the reviewed behaviour is still present,
or FIXED if the working tree no longer exhibits it. Re-run this after
changing anything the review touched: a check that flips to FIXED means the
review write-up is now stale for that finding, which the exit code reports.

Read-only. Nothing here mutates the repository, and the two monkeypatches
are restored before the process exits.

Run:  uv run python tools/review-verification/verify_findings.py
"""

from __future__ import annotations

import dataclasses
import importlib.resources
import inspect
import json
from typing import Any

from _report import FIXED, REPRODUCED, Report, main_guard
from pydantic import BaseModel, field_validator, model_validator

from anesthesia_sim.app import controller, simulation_view
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.core import (
    alveolar,
    blood,
    circuit,
    parameters,
    patient,
    respiratory_system,
    simulation,
    tissue,
)
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.exceptions import AnesthesiaSimulationError
from anesthesia_sim.core.parameters import (
    load_reference_adult_parameters,
    parse_agent_parameters,
    parse_reference_adult_parameters,
)
from anesthesia_sim.core.respiratory_system import RespiratorySystem

# Every module that could plausibly call into a compartment, for the
# dead-code scan in P1-6.
SHIPPED_MODULES = (
    respiratory_system,
    alveolar,
    blood,
    circuit,
    patient,
    simulation,
    tissue,
    controller,
    simulation_view,
)


def _agent_payload(agent_id: str) -> dict[str, Any]:
    """Read one packaged agent file as raw JSON, without going through core."""

    resource = importlib.resources.files("anesthesia_sim.data.agents").joinpath(f"{agent_id}.json")

    with resource.open("r", encoding="utf-8") as stream:
        payload: dict[str, Any] = json.load(stream)

    return payload


def check_loop_dies_silently(report: Report) -> None:
    """P1-1: a core guard raises an exception the app cannot catch or survive."""

    system = RespiratorySystem.for_agent("sevoflurane")
    system.set_delivered_concentration(0.08)

    raised: Exception | None = None

    try:
        for _ in range(60):
            system.advance(60.0)
    except Exception as error:  # noqa: BLE001 - capturing the type is the point
        raised = error

    timer_source = inspect.getsource(simulation_view.SimulationView._run_simulation_timer)
    unguarded = "try" not in timer_source

    if raised is None:
        report.record("P1-1", "large step raises from deep inside a compartment", FIXED)
        return

    outside_hierarchy = not isinstance(raised, AnesthesiaSimulationError)

    report.record(
        "P1-1",
        "core raises outside its own exception hierarchy",
        REPRODUCED if outside_hierarchy else FIXED,
        f"raised {type(raised).__name__}: {raised}\n"
        f"AnesthesiaSimulationError subclass: {not outside_hierarchy}",
    )
    report.record(
        "P1-1",
        "the simulation timer has no exception handling",
        REPRODUCED if unguarded else FIXED,
        "a raise here kills the asyncio task while the UI still reads 'Running'",
    )


def check_vaporizer_max_bypass(report: Report) -> None:
    """P1-2: the setter path does not bound the agent's vaporizer maximum.

    Fixed means the setter rejects the request outright. A clamp would
    also stop the impossible value being simulated, so the stored
    concentration is checked either way: what must never happen is a run
    continuing at a dial position the vaporizer does not have.
    """

    sim = SimulationController(agent_id="isoflurane")
    maximum = sim.snapshot().max_delivered_concentration_percent
    rejected: Exception | None = None

    try:
        sim.set_delivered_concentration(0.50)
    except AnesthesiaSimulationError as error:
        rejected = error

    resulting = sim.snapshot().delivered_concentration_fraction * 100.0
    detail = (
        f"agent maximum {maximum:.1f}%, "
        + (
            f"rejected ({type(rejected).__name__})"
            if rejected is not None
            else "accepted and simulated"
        )
        + f", running at {resulting:.1f}%"
    )

    report.record(
        "P1-2",
        "set_delivered_concentration ignores the vaporizer maximum",
        REPRODUCED if resulting > maximum else FIXED,
        detail,
    )


def check_data_file_defaults_are_dead(report: Report) -> None:
    """P1-3: the controller's literals win over the cited data-file defaults."""

    original = respiratory_system.load_reference_adult_parameters
    edited = dataclasses.replace(
        load_reference_adult_parameters(),
        default_cardiac_output_l_min=6.5,
        default_alveolar_ventilation_l_min=5.5,
    )

    respiratory_system.load_reference_adult_parameters = lambda: edited

    try:
        snapshot = SimulationController().snapshot()
    finally:
        respiratory_system.load_reference_adult_parameters = original

    ignored = snapshot.cardiac_output_l_min != 6.5 or snapshot.alveolar_ventilation_l_min != 5.5

    report.record(
        "P1-3",
        "cited data-file defaults never reach the running app",
        REPRODUCED if ignored else FIXED,
        "data file says CO 6.5, VA 5.5 -> "
        f"app runs CO {snapshot.cardiac_output_l_min}, VA {snapshot.alveolar_ventilation_l_min}",
    )


def check_schema_ignores_unknown_keys(report: Report) -> None:
    """P1-4: a misspelled key in a safety-critical data file loads clean."""

    payload = _agent_payload("sevoflurane")
    genuine = payload["blood_gas_partition_coefficient"]

    payload["blood_gas_partitition_coefficient"] = 9.9  # deliberate typo
    payload["tissue_gas_partition_coefficients"]["brain"] = 1.1

    try:
        parsed = parse_agent_parameters(payload)
        accepted = True
        loaded = parsed.blood_gas_partition_coefficient
    except ValueError:
        accepted = False
        loaded = genuine

    patient_payload: dict[str, Any] = {"totally_bogus_field": "ignored"}
    resource = importlib.resources.files("anesthesia_sim.data.patients").joinpath(
        "reference_adult.json"
    )

    with resource.open("r", encoding="utf-8") as stream:
        patient_payload |= json.load(stream)

    try:
        parse_reference_adult_parameters(patient_payload)
        patient_accepted = True
    except ValueError:
        patient_accepted = False

    report.record(
        "P1-4",
        "Pydantic schemas silently ignore unknown keys",
        REPRODUCED if accepted and patient_accepted else FIXED,
        f"typo'd agent key dropped, blood:gas still {loaded} (not 9.9)\n"
        "extra patient key accepted; no model sets extra='forbid'",
    )


def check_mac_cross_check_is_order_dependent(report: Report) -> None:
    """P1-5: the only cross-field agent check depends on declaration order.

    Probed against the shipped guard rather than a look-alike: the guard
    function is pulled off `_AgentPayload` and re-registered, the way the
    shipped model registers it, in a model that declares the two fields in
    each order. The original `field_validator` reading `info.data` fires
    only when the maximum is declared first; a `model_validator` sees a
    fully populated instance, so declaration order cannot reach it.
    """

    payload_model = parameters._AgentPayload  # noqa: SLF001 - the guard under test
    guard_name = "_mac_percent_must_not_exceed_vaporizer_max"
    guard = payload_model.__dict__[guard_name]
    registered_as_model_validator = (
        guard_name in payload_model.__pydantic_decorators__.model_validators
    )

    def build(first: str, second: str) -> type[BaseModel]:
        registered = (
            model_validator(mode="after")(guard)
            if registered_as_model_validator
            else field_validator("mac_percent")(classmethod(guard))
        )
        namespace: dict[str, Any] = {
            "__annotations__": {first: float, second: float},
            "guard": registered,
        }

        return type("OrderProbe", (BaseModel,), namespace)

    payload = {"max_delivered_concentration_percent": 5.0, "mac_percent": 40.0}
    accepted: dict[str, bool] = {}

    for first, second in (
        ("max_delivered_concentration_percent", "mac_percent"),
        ("mac_percent", "max_delivered_concentration_percent"),
    ):
        try:
            build(first, second).model_validate(payload)
            accepted[first] = True  # accepted: the guard did not fire
        except Exception:  # noqa: BLE001 - any validation failure means it fired
            accepted[first] = False

    report.record(
        "P1-5",
        "MAC cross-check silently no-ops if the fields are reordered",
        REPRODUCED if any(accepted.values()) else FIXED,
        "max declared first -> "
        + ("ACCEPTED" if accepted["max_delivered_concentration_percent"] else "rejected")
        + "\nmac declared first -> "
        + ("ACCEPTED: 40% MAC on a 5% vaporizer" if accepted["mac_percent"] else "rejected"),
    )


def check_dead_non_conservative_ventilation(report: Report) -> None:
    """P1-6: an unused public method models the same physics, non-conservatively."""

    # PL-022 deleted the method, so absence is checked first: calling it
    # unconditionally would raise here instead of reporting anything. The
    # original two-part probe still runs if the method ever comes back.
    if not hasattr(AlveolarCompartment, "advance_ventilation"):
        report.record(
            "P1-6",
            "advance_ventilation is uncalled and does not conserve agent",
            FIXED,
            "AlveolarCompartment.advance_ventilation no longer exists (PL-022).\n"
            "The only ventilation path is RespiratorySystem._exchange_circuit_and_alveoli,\n"
            "which moves agent between circuit and alveoli as an equal-and-opposite pair.",
        )
        return

    # Scan every shipped module's source for an actual call site. The
    # definition itself lives in alveolar.py, so that module is checked for
    # ".advance_ventilation(" rather than the bare name.
    callers = [
        module.__name__
        for module in SHIPPED_MODULES
        if ".advance_ventilation(" in inspect.getsource(module)
    ]

    alveoli = AlveolarCompartment(gas_volume_l=2.5, alveolar_ventilation_l_min=4.0)
    before = alveoli.agent_amount_l
    gained = alveoli.advance_ventilation(inspired_fraction=0.08, simulation_step_s=1.0)

    # The real path removes exactly this amount from the circuit. This method
    # returns it and leaves the source untouched: agent appears from nowhere.
    creates_agent = gained > 0.0 and alveoli.agent_amount_l > before

    report.record(
        "P1-6",
        "advance_ventilation is uncalled and does not conserve agent",
        REPRODUCED if not callers and creates_agent else FIXED,
        f"callers inside core/: {callers or 'none'}\n"
        f"alveolar amount +{gained:.6f} L with no matching circuit debit",
    )


def check_mass_balance_cannot_detect_dynamics_error(report: Report) -> None:
    """P2-1: mass balance passes even when the solution is badly inaccurate."""

    accurate = RespiratorySystem.for_agent("sevoflurane")
    accurate.set_delivered_concentration(0.08)

    coarse = RespiratorySystem.for_agent("sevoflurane")
    coarse.set_delivered_concentration(0.08)

    for _ in range(36000):
        accurate.advance(0.1)

    for _ in range(360):
        coarse.advance(10.0)

    divergence = abs(
        coarse.alveoli.concentration_fraction - accurate.alveoli.concentration_fraction
    )
    validation = coarse.agent_simulation_validation

    blind = validation.passes_validation and divergence > 1e-4

    report.record(
        "P2-1",
        "mass balance passes while the dynamics are visibly wrong",
        REPRODUCED if blind else FIXED,
        f"dt=10 s alveolar fraction differs from dt=0.1 s by {divergence:.2e} "
        f"({divergence * 100:.3f} percentage points)\n"
        f"yet mass-balance residual is {validation.absolute_error_l:.2e} L and passes",
    )


def check_venous_pool_dominates_early_display(report: Report) -> None:
    """P2-4: the least-justified compartment drives the first minutes of F_v."""

    def mixed_venous_at(volume_l: float, duration_s: float) -> float:
        system = RespiratorySystem.for_agent("sevoflurane")
        system.patient.venous_blood.volume_l = volume_l
        system.set_delivered_concentration(0.08)

        for _ in range(round(duration_s / 0.1)):
            system.advance(0.1)

        return system.patient.mixed_venous_fraction

    lines: list[str] = []
    largest_shift = 0.0

    for duration_s in (30.0, 60.0, 120.0):
        pooled = mixed_venous_at(1.0, duration_s)
        instant = mixed_venous_at(0.01, duration_s)
        shift = abs(pooled - instant) / instant
        largest_shift = max(largest_shift, shift)
        lines.append(
            f"t={duration_s:5.0f}s  pooled {pooled:.5f}  near-instant {instant:.5f}"
            f"  {-shift * 100:+6.1f}%"
        )

    report.record(
        "P2-4",
        "the 1.0 L venous pool dominates early mixed-venous values",
        REPRODUCED if largest_shift > 0.1 else FIXED,
        "\n".join(lines),
    )


def main() -> int:
    report = Report("Finding verification - does each reviewed defect still reproduce?")
    report.start()

    check_loop_dies_silently(report)
    check_vaporizer_max_bypass(report)
    check_data_file_defaults_are_dead(report)
    check_schema_ignores_unknown_keys(report)
    check_mac_cross_check_is_order_dependent(report)
    check_dead_non_conservative_ventilation(report)
    check_mass_balance_cannot_detect_dynamics_error(report)
    check_venous_pool_dominates_early_display(report)

    return report.finish()


if __name__ == "__main__":
    main_guard(main())
