"""A refused setting reaches the learner named by its control, and the developer by its field.

The core refuses a setting outside a limit with a `SettingOutsideRange`, whose
message names the value by its field in the code, for a developer. The value,
the limit and which limit refused it travel with the error as fields. The
interface builds the learner's banner from those fields, naming the control by
its label on screen (`setting_refusal_for_a_learner`, `PL-8QFW`).

Each expected limit below is typed by hand from its source rather than read
from the code under test: the supported input ranges from `docs/INTERFACE.md`
§ "Supported input ranges", and the range of a percent from its definition, 0
to 100. Each expected sentence is typed by hand too, with every value written
as the control's readout writes it: a flow to one decimal in L/min and a
percent to two decimals (`docs/INTERFACE.md` § "Displayed precision").
"""

from collections.abc import Callable

import pytest

from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.dashboard_frame import setting_refusal_for_a_learner
from anesthesia_sim.core.circuit import DeliverableFreshGasFlowRange, _require_deliverable_flow
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import (
    SettingLimit,
    SettingOutsideRange,
    SimulationConfigurationError,
)
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow
from anesthesia_sim.core.validation import require_within_vaporizer_maximum


def _refusal(refuse: Callable[[], object]) -> SettingOutsideRange:
    """Return the `SettingOutsideRange` that calling `refuse` raises."""

    with pytest.raises(SettingOutsideRange) as raised:
        refuse()

    return raised.value


def _vaporizer_at_50_with_a_5_percent_maximum() -> None:
    require_within_vaporizer_maximum("delivered_concentration_percent", Percent(50.0), Percent(5.0))


def _flow_of_9_on_a_machine_that_sets_half_to_8() -> None:
    _require_deliverable_flow(FreshGasFlow(9.0), DeliverableFreshGasFlowRange(0.5, 8.0))


@pytest.mark.parametrize(
    ("refuse", "requested", "lowest", "highest", "limit"),
    [
        (lambda: FreshGasFlow(-1.0), -1.0, 0.0, 10.0, SettingLimit.SUPPORTED_INPUT_RANGE),
        (lambda: AlveolarVentilation(13.0), 13.0, 0.0, 12.0, SettingLimit.SUPPORTED_INPUT_RANGE),
        (lambda: CardiacOutput(11.0), 11.0, 0.0, 10.0, SettingLimit.SUPPORTED_INPUT_RANGE),
        (lambda: Percent(150.0), 150.0, 0.0, 100.0, SettingLimit.PERCENT),
        (_vaporizer_at_50_with_a_5_percent_maximum, 50.0, 0.0, 5.0, SettingLimit.VAPORIZER_MAXIMUM),
        (_flow_of_9_on_a_machine_that_sets_half_to_8, 9.0, 0.5, 8.0, SettingLimit.MACHINE_RANGE),
    ],
    ids=[
        "fresh-gas-flow",
        "alveolar-ventilation",
        "cardiac-output",
        "percent",
        "vaporizer-maximum",
        "machine-range",
    ],
)
def test_each_limit_refuses_with_the_value_and_the_limit_as_fields(
    refuse: Callable[[], object],
    requested: float,
    lowest: float,
    highest: float,
    limit: SettingLimit,
) -> None:
    """Each of the four limits a dial can meet carries what the banner needs, not only words."""

    refusal = _refusal(refuse)

    assert (refusal.requested, refusal.lowest, refusal.highest, refusal.limit) == (
        requested,
        lowest,
        highest,
        limit,
    )


@pytest.mark.parametrize(
    ("control", "refuse", "learner"),
    [
        (
            ControlInput.DELIVERED,
            _vaporizer_at_50_with_a_5_percent_maximum,
            "the vaporizer setting cannot be 50.00%, because this agent's vaporizer delivers "
            "at most 5.00%",
        ),
        (
            ControlInput.DELIVERED,
            lambda: Percent(150.0, name="delivered_concentration_percent"),
            "the vaporizer setting cannot be 150.0%, because a concentration can only be from "
            "0.00% to 100.00%",
        ),
        (
            ControlInput.FRESH_GAS_FLOW,
            lambda: FreshGasFlow(12.0),
            "the fresh gas flow setting cannot be 12.0 L/min, because the model is claimed to "
            "represent a patient only from 0.0 L/min to 10.0 L/min",
        ),
        (
            ControlInput.FRESH_GAS_FLOW,
            _flow_of_9_on_a_machine_that_sets_half_to_8,
            "the fresh gas flow setting cannot be 9.0 L/min, because this anesthesia machine "
            "sets a flow only from 0.5 L/min to 8.0 L/min",
        ),
        (
            ControlInput.ALVEOLAR_VENTILATION,
            lambda: AlveolarVentilation(13.0),
            "the alveolar ventilation setting cannot be 13.0 L/min, because the model is "
            "claimed to represent a patient only from 0.0 L/min to 12.0 L/min",
        ),
        (
            ControlInput.CARDIAC_OUTPUT,
            lambda: CardiacOutput(10**400),
            f"the cardiac output setting cannot be {10**400} L/min, because the model is "
            "claimed to represent a patient only from 0.0 L/min to 10.0 L/min",
        ),
    ],
    ids=[
        "vaporizer-maximum",
        "percent",
        "supported-fresh-gas-flow",
        "machine-range",
        "alveolar-ventilation",
        "int-past-the-float-range",
    ],
)
def test_the_learner_reads_the_control_s_label_and_the_developer_the_core_s_message(
    control: ControlInput, refuse: Callable[[], object], learner: str
) -> None:
    """The banner's text names the control, the value and the limit, and keeps the core's words.

    The last case asks for an `int` too large for a `float`, which the flow's
    readout format cannot write, so the value is written as the core writes it.
    """

    developer = _refusal(refuse)

    refusal = setting_refusal_for_a_learner(control, developer)

    assert str(refusal) == learner
    assert refusal.__notes__ == [str(developer)]
    assert refusal.__cause__ is developer


def test_a_refusal_the_controller_already_words_is_shown_as_it_is() -> None:
    """Only a refusal outside a limit is reworded; the controller words its own for the learner."""

    stopped = SimulationConfigurationError(
        "the cardiac output setting cannot be changed on a stopped run, because no step will "
        "run under a new one"
    )

    assert setting_refusal_for_a_learner(ControlInput.CARDIAC_OUTPUT, stopped) is stopped
