"""The simulation controller's preview, driven against real runs.

These tests cover the second at which a preview's F_A/F_I ratio crosses
equilibrium after the preview's first hour, where only the chart's columns are
predicted, and a preview at zero alveolar ventilation, which has no ratio to
cross.

`controller_support.py` holds what several of these files share.
"""

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


def test_an_apnoeic_preview_predicts_no_ratio_and_adds_no_crossing_second() -> None:
    """A preview at zero alveolar ventilation has no F_A/F_I ratio past the reach.

    The run above is previewed with the vaporizer turned off, on a 6-hour axis
    of 20 columns. After its first hour, the preview predicts only the
    columns, which are about 19 minutes apart here. Read by the inspired
    fraction floor and the equilibrium rule alone, the ratio is inside the
    wash-in domain at the end of the first hour and leaves it a few seconds
    later, and `PL-CJJ1` added that second as a column. A step at zero alveolar
    ventilation reached every predicted state, though, so none of them is a
    wash-in fraction (rule 3 of `app/wash_in.py`, `PL-49D5`). Nothing is drawn
    past the reach, and no second between two columns is predicted to find a
    crossing.

    The second that the two rules alone would have drawn comes from a twin run
    that applies the same settings and steps every second (rule 2 of
    `.claude/rules/test-oracles.md`).
    """

    reach_s = 30
    exact_s = reach_s + PREVIEW_EXACT_S
    previewed = _apnoeic_at_low_flow_after_a_brief_high_dose(8.0)
    window = previewed.preview_window(
        SettingPreview(ControlInput.DELIVERED, 0.0), 0.0, reach_s + 6 * 3600.0, 20
    )
    next_column_s = int(min(second for second in window.times_s if second > exact_s + 60))

    twin = _apnoeic_at_low_flow_after_a_brief_high_dose(0.0)
    twin.start()
    _advance_for(twin, duration_s=next_column_s - reach_s)

    def inside(second: int) -> bool:
        ratio = _ratio(twin._state.stored_states.state_at(CaseInstant(second)))

        return ratio is not None and is_wash_in(ratio)

    # The premise: by the first two rules alone, the ratio leaves the domain
    # between the end of the first hour and the next column.
    assert inside(exact_s)
    crossing_s = next(second for second in range(exact_s, next_column_s) if not inside(second))

    quotients = window.wash_in_quotients("sevoflurane")
    assert [
        second
        for second, quotient in zip(window.times_s, quotients, strict=True)
        if second > reach_s and quotient is not None
    ] == []
    assert crossing_s not in window.times_s
