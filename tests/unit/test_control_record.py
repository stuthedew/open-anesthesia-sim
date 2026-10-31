"""Tests of which settings field holds each control's value (`control_value`)."""

from collections.abc import Callable

import pytest

from anesthesia_sim.app.control_record import ControlInput, ControlSettings, control_value
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

# Four settings, each a different number, so a control read from another
# control's field returns the wrong value instead of an equal one. Each is a
# step the interface's sliders offer, inside its supported range, and none is
# a shipped default.
_FRESH_GAS_FLOW_L_MIN = 2.5
_DELIVERED_PERCENT = 3.25
_ALVEOLAR_VENTILATION_L_MIN = 6.5
_CARDIAC_OUTPUT_L_MIN = 4.5

_EXPECTED = {
    ControlInput.FRESH_GAS_FLOW: _FRESH_GAS_FLOW_L_MIN,
    ControlInput.DELIVERED: _DELIVERED_PERCENT,
    ControlInput.ALVEOLAR_VENTILATION: _ALVEOLAR_VENTILATION_L_MIN,
    ControlInput.CARDIAC_OUTPUT: _CARDIAC_OUTPUT_L_MIN,
}


def test_the_four_settings_are_distinct() -> None:
    """A test below would pass a swapped field if two of these were equal."""

    assert len(set(_EXPECTED.values())) == len(_EXPECTED)
    assert set(_EXPECTED) == set(ControlInput)


def _equation_settings() -> ControlSettings:
    """The settings a run's stretch is computed under, with the four values set."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    system.set_fresh_gas_flow(FreshGasFlow(_FRESH_GAS_FLOW_L_MIN))
    system.set_delivered_concentration_percent(Percent(_DELIVERED_PERCENT))
    system.set_alveolar_ventilation(AlveolarVentilation(_ALVEOLAR_VENTILATION_L_MIN))
    system.set_cardiac_output(CardiacOutput(_CARDIAC_OUTPUT_L_MIN))

    return system.equation_settings()


def _run_settings() -> ControlSettings:
    """The settings the setting controls show, with the four values set."""

    controller = SimulationController()
    controller.set_fresh_gas_flow(FreshGasFlow(_FRESH_GAS_FLOW_L_MIN))
    controller.set_delivered_concentration_percent(Percent(_DELIVERED_PERCENT))
    controller.set_alveolar_ventilation(AlveolarVentilation(_ALVEOLAR_VENTILATION_L_MIN))
    controller.set_cardiac_output(CardiacOutput(_CARDIAC_OUTPUT_L_MIN))

    return controller.settings()


@pytest.mark.parametrize("build", [_equation_settings, _run_settings], ids=["equation", "run"])
@pytest.mark.parametrize("control", list(ControlInput), ids=str)
def test_each_control_reads_the_value_it_was_set_to(
    build: Callable[[], ControlSettings], control: ControlInput
) -> None:
    """Each control's value is the number it was set to, in the unit it was set in.

    Both records that the controller and the readouts read are checked, so
    the one map cannot be right for one record and wrong for the other. The
    delivered concentration is the percent dialled, not a fraction
    (`PL-NJPB`).
    """

    assert control_value(build(), control) == _EXPECTED[control]
