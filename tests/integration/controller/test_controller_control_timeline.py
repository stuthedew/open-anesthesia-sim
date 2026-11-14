"""The simulation controller, driven against real runs.

These tests cover the record of each setting change.

`controller_support.py` holds what several of these files share.
"""

import pytest

from anesthesia_sim.app.control_record import CONTROL_INPUT_UNITS, ControlInput
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.core.concentration import Percent, fraction_from_percent, percent_from_fraction
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow
from tests.integration.controller.controller_support import _advance_for


def test_a_setting_change_is_recorded_with_the_time_it_took_effect() -> None:
    controller = SimulationController()
    controller.start()
    _advance_for(controller, 1.0)

    controller.set_fresh_gas_flow(FreshGasFlow(3.0))

    (change,) = controller.snapshot().control_timeline
    assert change.control is ControlInput.FRESH_GAS_FLOW
    assert change.elapsed_s == pytest.approx(1.0)
    assert change.previous_value == pytest.approx(4.0)
    assert change.new_value == pytest.approx(3.0)
    assert change.unit == "L/min"


def test_every_control_records_under_its_own_stable_identifier() -> None:
    """The stored identifiers are the timeline's contract with future runs.

    The test asserts them as literal strings, not against the enum. A rename
    would change the enum, and a recorded run stored under the old strings
    could then no longer be read. PL-9SH6 and PL-3TLK rename two of the
    setters underneath them in v0.4.1.
    """

    controller = SimulationController()

    controller.set_fresh_gas_flow(FreshGasFlow(3.0))
    controller.set_delivered_concentration_percent(Percent(3.0))
    controller.set_alveolar_ventilation(AlveolarVentilation(5.0))
    controller.set_cardiac_output(CardiacOutput(4.0))

    assert [change.control.value for change in controller.snapshot().control_timeline] == [
        "fresh_gas_flow",
        "delivered",
        "alveolar_ventilation",
        "cardiac_output",
    ]


def test_every_recorded_control_carries_its_declared_unit() -> None:
    controller = SimulationController()

    controller.set_fresh_gas_flow(FreshGasFlow(3.0))
    controller.set_delivered_concentration_percent(Percent(3.0))
    controller.set_alveolar_ventilation(AlveolarVentilation(5.0))
    controller.set_cardiac_output(CardiacOutput(4.0))

    for change in controller.snapshot().control_timeline:
        assert change.unit == CONTROL_INPUT_UNITS[change.control]


def test_the_delivered_dial_is_recorded_as_the_percent_the_core_holds() -> None:
    """Recording the model's fraction would break re-application.

    The timeline claims that re-applying it reproduces the run. Re-applying
    means calling the setter, which takes the percent the dial was set to
    (`PL-NJPB`). A record of 0.03 where the circuit stores 3.0 would hand a
    hundredfold error to whatever replays it.
    """

    controller = SimulationController()

    controller.set_delivered_concentration_percent(Percent(3.0))

    (change,) = controller.snapshot().control_timeline
    assert change.new_value == 3.0
    assert change.new_value == controller.snapshot().delivered_concentration_percent


def test_the_control_timeline_records_the_vaporizer_percent_as_dialled() -> None:
    """The recorded change and the run segment both give back the dial exactly.

    `PL-NJPB`. Both records used to store the fraction, which is the dial's
    percent divided by a hundred. At some dial positions, that fraction times
    a hundred does not equal the percent it came from: 0.9% read back as
    0.9000000000000001. The first assertion shows that 0.9 is such a
    position. Both recorded values are then compared with it by equality,
    not within a tolerance.
    """

    assert percent_from_fraction(fraction_from_percent(Percent(0.9))) != 0.9

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=1.0)

    controller.set_delivered_concentration_percent(Percent(0.9))

    (change,) = controller.snapshot().control_timeline
    assert change.control is ControlInput.DELIVERED
    assert change.new_value == 0.9
    assert controller.run_segments[-1].settings.delivered_concentration_percent == 0.9


def test_a_setting_equal_to_the_one_in_place_records_nothing() -> None:
    """A slider set again to the position it is already at is not a change."""

    controller = SimulationController()
    current = controller.snapshot().fresh_gas_flow_l_min

    controller.set_fresh_gas_flow(FreshGasFlow(current))

    assert controller.snapshot().control_timeline == ()


def test_a_refused_setting_records_nothing() -> None:
    """A refused setting never took effect, so it is not part of the run.

    The guarantee comes from the structure, not from chance. The recorder runs
    after the core's setter returns, so an error raised by the setter reaches
    the interface with the timeline untouched.
    """

    controller = SimulationController()

    with pytest.raises(SimulationConfigurationError):
        controller.set_delivered_concentration_percent(Percent(50.0))

    assert controller.snapshot().control_timeline == ()
    assert not controller.has_failed


def test_changes_within_one_step_collapse_to_what_the_model_integrated() -> None:
    """Only the value in place when a step runs is ever integrated.

    A dial dragged from 2% through 3% to 4% between two steps is one change
    from 2% to 4% as far as the run is concerned, and a timeline that
    listed the intermediate value would describe a run that never happened.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, 1.0)

    controller.set_delivered_concentration_percent(Percent(3.0))
    controller.set_delivered_concentration_percent(Percent(4.0))

    (change,) = controller.snapshot().control_timeline
    assert change.previous_value == pytest.approx(2.0)
    assert change.new_value == pytest.approx(4.0)
    assert change.elapsed_s == pytest.approx(1.0)


def test_a_change_undone_within_one_step_leaves_no_entry() -> None:
    """Returning to the step's own value means the model saw no change."""

    controller = SimulationController()

    controller.set_delivered_concentration_percent(Percent(3.0))
    controller.set_delivered_concentration_percent(Percent(2.0))

    assert controller.snapshot().control_timeline == ()


def test_the_same_control_changed_across_two_steps_records_both() -> None:
    """A setting is recorded for each step that the run was computed under."""

    controller = SimulationController()
    controller.start()

    controller.set_delivered_concentration_percent(Percent(3.0))
    _advance_for(controller, 1.0)
    controller.set_delivered_concentration_percent(Percent(4.0))

    first, second = controller.snapshot().control_timeline
    assert (first.previous_value, first.new_value) == pytest.approx((2.0, 3.0))
    assert (second.previous_value, second.new_value) == pytest.approx((3.0, 4.0))


def test_consecutive_changes_to_one_control_are_one_adjustment() -> None:
    """One drag of one slider counts as one adjustment, however many steps it spans."""

    controller = SimulationController()
    controller.start()

    controller.set_fresh_gas_flow(FreshGasFlow(3.0))
    _advance_for(controller, 1.0)
    controller.set_fresh_gas_flow(FreshGasFlow(2.0))

    timeline = controller.snapshot().control_timeline
    assert {change.adjustment for change in timeline} == {1}


def test_a_declared_boundary_separates_two_drags_of_one_control() -> None:
    """Timing cannot separate two drags, but the input boundary can.

    Two turns of the same dial arrive as a run of changes to one control,
    exactly as one turn does. Only the interface knows where the first
    gesture ended, and `begin_control_adjustment` is how it says so.
    """

    controller = SimulationController()
    controller.start()

    controller.set_fresh_gas_flow(FreshGasFlow(3.0))
    _advance_for(controller, 60.0)
    controller.begin_control_adjustment()
    controller.set_fresh_gas_flow(FreshGasFlow(2.0))

    first, second = controller.snapshot().control_timeline
    assert first.adjustment == 1
    assert second.adjustment == 2


def test_changing_a_different_control_starts_a_new_adjustment() -> None:
    controller = SimulationController()

    controller.set_fresh_gas_flow(FreshGasFlow(3.0))
    controller.set_cardiac_output(CardiacOutput(4.0))

    first, second = controller.snapshot().control_timeline
    assert first.adjustment == 1
    assert second.adjustment == 2


def test_reset_clears_the_control_timeline_with_the_run() -> None:
    controller = SimulationController()
    controller.start()
    _advance_for(controller, 1.0)
    controller.set_fresh_gas_flow(FreshGasFlow(3.0))

    controller.reset()

    assert controller.snapshot().control_timeline == ()


def test_reset_restarts_adjustment_numbering() -> None:
    """A run's adjustments are numbered from its own beginning.

    Carrying the count across a reset would make the first adjustment of a
    fresh run appear as the fourth of something the reader cannot see.
    """

    controller = SimulationController()
    controller.set_fresh_gas_flow(FreshGasFlow(3.0))
    controller.set_cardiac_output(CardiacOutput(4.0))

    controller.reset()
    controller.set_fresh_gas_flow(FreshGasFlow(2.0))

    (change,) = controller.snapshot().control_timeline
    assert change.adjustment == 1


def test_changing_agent_clears_the_control_timeline() -> None:
    """A new agent is a new run, and the old run's inputs are not its own."""

    controller = SimulationController()
    controller.set_fresh_gas_flow(FreshGasFlow(3.0))

    controller.set_agent("isoflurane")

    assert controller.snapshot().control_timeline == ()


def test_the_constructor_overrides_are_not_recorded_as_changes() -> None:
    """Initial conditions are what the run starts from, not inputs to it."""

    controller = SimulationController(
        fresh_gas_flow_l_min=FreshGasFlow(3.0), cardiac_output_l_min=CardiacOutput(4.0)
    )

    assert controller.snapshot().control_timeline == ()


def test_a_recorded_change_is_stamped_with_the_instant_it_took_effect() -> None:
    """The mark belongs at the instant the run changed, and it is drawn there.

    The chart draws its control mark as a line at `elapsed_s`. Since
    `PL-2FM6`, that instant is also a column of the drawn window. So the mark
    and the kink in the trace beneath it fall at the same instant by
    construction, not because two reads happen to agree.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, 2.0)

    controller.set_cardiac_output(CardiacOutput(4.0))

    (change,) = controller.snapshot().control_timeline
    elapsed_s = controller.snapshot().elapsed_s

    assert change.elapsed_s == pytest.approx(elapsed_s)
    _advance_for(controller, 2.0)
    window = controller.drawn_window(0.0, controller.snapshot().elapsed_s, 150)
    assert change.elapsed_s in window.times_s
