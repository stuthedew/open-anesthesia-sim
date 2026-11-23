"""The simulation controller's preview, driven against real runs.

These tests cover the second at which a preview's F_A/F_I ratio crosses
equilibrium after the preview's first hour, where only the chart's columns are
predicted.

`controller_support.py` holds what several of these files share.
"""

import pytest

from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.controller import PREVIEW_EXACT_S, SettingPreview, SimulationController
from anesthesia_sim.app.run_series import COMPARTMENT_STATE_INDEX, RecordedQuantity
from anesthesia_sim.app.wash_in import is_wash_in, wash_in_ratio
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CaseInstant, FreshGasFlow
from tests.integration.controller.controller_support import _advance_for


def _apnoeic_at_low_flow_after_a_brief_high_dose(delivered_percent: float) -> SimulationController:
    """Return a run given 8% sevoflurane at 10 L/min for 30 s, then apnoea at 0.5 L/min.

    The run is paused at 30 s with the fresh gas flow turned down and the
    alveolar ventilation at zero. The vaporizer is then set to
    `delivered_percent`.
    """

    run = SimulationController()
    run.set_fresh_gas_flow(FreshGasFlow(10.0))
    run.set_delivered_concentration_percent(Percent(8.0))
    run.start()
    _advance_for(run, duration_s=30)
    run.pause()
    run.set_fresh_gas_flow(FreshGasFlow(0.5))
    run.set_alveolar_ventilation(AlveolarVentilation(0.0))
    run.set_delivered_concentration_percent(Percent(delivered_percent))

    return run


def _ratio(state: tuple[float, ...]) -> float | None:
    """Return F_A/F_I in `state`, or None where the inspired fraction is too small to divide by."""

    return wash_in_ratio(
        state[COMPARTMENT_STATE_INDEX[RecordedQuantity.ALVEOLAR]],
        state[COMPARTMENT_STATE_INDEX[RecordedQuantity.CIRCUIT]],
    )


def test_a_preview_draws_where_its_ratio_leaves_wash_in_before_a_column_with_no_ratio() -> None:
    """The crossing second is drawn even when the next column has no F_A/F_I ratio at all.

    The run above is previewed with the vaporizer turned off, on a 6-hour axis
    of 20 columns. After its first hour, the preview predicts only the
    columns, which are about 19 minutes apart here. The ratio is inside the
    wash-in domain at the end of the first hour and leaves it a few seconds
    later. The inspired fraction then falls below the smallest value the
    ratio is divided by before the next column, so that column has no ratio.
    The second at which the ratio left the domain must still be drawn.
    Without it, the wash-in trace would stop below the equilibrium line with
    no sign that it reached the line (`PL-CJJ1`).

    The expected second comes from a twin run that applies the same settings
    and steps every second (rule 2 of `.claude/rules/test-oracles.md`).
    """

    reach_s = 30
    exact_s = reach_s + PREVIEW_EXACT_S
    previewed = _apnoeic_at_low_flow_after_a_brief_high_dose(8.0)
    window = previewed.preview_window(
        SettingPreview(ControlInput.DELIVERED, 0.0), 0.0, reach_s + 6 * 3600.0, 20
    )
    next_column = min(second for second in window.times_s if second > exact_s + 60)
    next_column_s = int(next_column)

    twin = _apnoeic_at_low_flow_after_a_brief_high_dose(0.0)
    twin.start()
    _advance_for(twin, duration_s=next_column_s - reach_s)

    def twin_state(second: int) -> tuple[float, ...]:
        return twin._state.stored_states.state_at(CaseInstant(second))

    def inside(second: int) -> bool:
        ratio = _ratio(twin_state(second))

        return ratio is not None and is_wash_in(ratio)

    crossing_s = next(second for second in range(exact_s, next_column_s) if not inside(second))

    # The premises: inside the domain at the end of the first hour, leaving it
    # with a ratio to draw, and no ratio at the next column, which is a
    # whole second.
    assert next_column_s == next_column
    assert inside(exact_s)
    assert _ratio(twin_state(crossing_s)) is not None
    assert _ratio(twin_state(next_column_s)) is None

    assert crossing_s in window.times_s
    assert window.states[window.times_s.index(crossing_s)] == pytest.approx(twin_state(crossing_s))
