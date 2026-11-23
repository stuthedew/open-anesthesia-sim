"""A refused setting reaches the learner named by its control, and the developer by its field.

The core refuses a setting outside a limit with a `SettingOutsideRange`, whose
message names the value by its field in the code, for a developer. The field,
the value, the limit and which limit refused it travel with the error as
fields. The interface builds the learner's banner from those fields, naming the
control by its label on screen (`setting_refusal_for_a_learner`, `PL-8QFW`).

Each expected limit below is typed by hand from its source rather than read
from the code under test: the supported input ranges from `docs/INTERFACE.md`
§ "Supported input ranges", and the range of a percent from its definition, 0
to 100. Each expected sentence is typed by hand too, with every value written
exactly, as Python's `repr` writes it.
"""

import copy
import pickle
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
    ("refuse", "quantity", "requested", "lowest", "highest", "limit"),
    [
        (
            lambda: FreshGasFlow(-1.0),
            "fresh_gas_flow_l_min",
            -1.0,
            0.0,
            10.0,
            SettingLimit.SUPPORTED_INPUT_RANGE,
        ),
        (
            lambda: AlveolarVentilation(13.0),
            "alveolar_ventilation_l_min",
            13.0,
            0.0,
            12.0,
            SettingLimit.SUPPORTED_INPUT_RANGE,
        ),
        (
            lambda: CardiacOutput(11.0),
            "cardiac_output_l_min",
            11.0,
            0.0,
            10.0,
            SettingLimit.SUPPORTED_INPUT_RANGE,
        ),
        (lambda: Percent(150.0), "percent", 150.0, 0.0, 100.0, SettingLimit.PERCENT),
        (
            _vaporizer_at_50_with_a_5_percent_maximum,
            "delivered_concentration_percent",
            50.0,
            0.0,
            5.0,
            SettingLimit.VAPORIZER_MAXIMUM,
        ),
        (
            _flow_of_9_on_a_machine_that_sets_half_to_8,
            "fresh_gas_flow_l_min",
            9.0,
            0.5,
            8.0,
            SettingLimit.MACHINE_RANGE,
        ),
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
    quantity: str,
    requested: float,
    lowest: float,
    highest: float,
    limit: SettingLimit,
) -> None:
    """Each of the four limits a dial can meet carries what the banner needs, not only words.

    A copy and a pickle keep every field. The constructor requires them, so
    Python's own way of rebuilding an exception from its message would fail.
    """

    refusal = _refusal(refuse)
    fields = (quantity, requested, lowest, highest, limit)

    for kept in (refusal, copy.copy(refusal), pickle.loads(pickle.dumps(refusal))):
        assert type(kept) is SettingOutsideRange
        assert str(kept) == str(refusal)
        assert (kept.quantity, kept.requested, kept.lowest, kept.highest, kept.limit) == fields


@pytest.mark.parametrize(
    ("control", "refuse", "learner"),
    [
        (
            ControlInput.DELIVERED,
            _vaporizer_at_50_with_a_5_percent_maximum,
            "the vaporizer setting cannot be 50.0%, because this agent's vaporizer delivers "
            "at most 5.0%",
        ),
        (
            ControlInput.DELIVERED,
            lambda: Percent(150.0, name="delivered_concentration_percent"),
            "the vaporizer setting cannot be 150.0%, because a concentration can only be from "
            "0.0% to 100.0%",
        ),
        (
            ControlInput.FRESH_GAS_FLOW,
            lambda: FreshGasFlow(10.04),
            "the fresh gas flow setting cannot be 10.04 L/min, because the model is claimed to "
            "represent a patient only from 0.0 L/min to 10.0 L/min",
        ),
        (
            ControlInput.DELIVERED,
            lambda: require_within_vaporizer_maximum(
                "delivered_concentration_percent", Percent(5.004), Percent(5.0)
            ),
            "the vaporizer setting cannot be 5.004%, because this agent's vaporizer delivers "
            "at most 5.0%",
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
        "flow-just-past-its-range",
        "dial-just-past-its-maximum",
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

    Each value is written exactly, so a value just past a limit never reads as
    the limit itself. The readout's format would write 10.04 L/min as 10.0 and
    5.004% as 5.00%, each equal to the limit it broke. The last case asks for an
    `int` too large for a `float`, which is written in full.
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


def test_a_range_refusal_of_another_control_s_field_is_shown_as_it_is() -> None:
    """A refusal of the vaporizer's field is never reworded as the cardiac output's.

    The settings record checks every field after one control moves, so moving
    cardiac output can meet a refusal of the vaporizer dial. Reworded for the
    cardiac output, it would read "the cardiac output setting cannot be 50.0
    L/min, because this agent's vaporizer delivers at most 5.0 L/min".
    """

    vaporizer = _refusal(_vaporizer_at_50_with_a_5_percent_maximum)

    assert setting_refusal_for_a_learner(ControlInput.CARDIAC_OUTPUT, vaporizer) is vaporizer
