"""The dashboard, driven headless against real runs.

These tests cover the charts.

`simulation_view_support.py` describes the whole suite.
"""

import pytest
from pyqtgraph import PlotWidget
from PySide6.QtGui import QAccessible
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app.chart_time_base import (
    FIT_RUN_KEY,
    SELECTABLE_TIME_BASES,
    time_base_for_span,
)
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import WASH_IN_HEADING
from anesthesia_sim.app.formatting import (
    format_compartment_amount,
    format_elapsed,
    format_mac_awake_reference,
    format_mac_multiple,
    format_percent,
    format_time_base,
    format_wash_in_ratio,
)
from anesthesia_sim.app.qt_schematic import RunSchematic, SchematicCanvas
from anesthesia_sim.app.qt_widgets import DescribedGraphic
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.view_registry import CONCENTRATION_CHART, PARAMETER_CONTROLS
from anesthesia_sim.app.wash_in import read_wash_in_with_ventilation
from anesthesia_sim.core.concentration import MacPercent
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES, load_agent_parameters
from anesthesia_sim.core.supported_ranges import FreshGasFlow
from anesthesia_sim.layout.tree import AreaId
from tests.integration.announcement_support import TextChange, record_text_changes
from tests.integration.simulation_view.simulation_view_support import (
    _advance,
    _chosen_time_base,
    _concentration,
    _failing_assembly,
    _paused_run_with_history,
    _select_agent,
    _select_time_base,
    _settle,
    _shown_view,
    _wash_in,
)

# ------------------------------------------------ the charts, integrated


def test_the_concentration_chart_tells_a_screen_reader_what_it_plots_and_where_it_ends(
    application: QApplication,
) -> None:
    """The chart reports itself as an image, with a name and each trace's latest value (`PL-T9RB`).

    Before `PL-T9RB` the chart reached a screen reader as an unnamed client
    area, which VoiceOver passes over. The expected alveolar value is read
    from a second run built with the same settings, not from the run the chart
    draws. The text is written when a screen reader asks, so after a further
    frame it describes that frame, and once the frame is withheld it says so.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 600)
    fresh = SimulationController()
    fresh.start()
    _advance(fresh, 600)
    alveolar = fresh.snapshot().alveolar_partial_pressure_fraction
    mac_percent = MacPercent(float(load_agent_parameters("sevoflurane").mac_at_age_40_percent))
    view = _shown_view(application, controller)
    chart = _concentration(view).chart
    described = QAccessible.queryAccessibleInterface(chart)

    assert described.role() is QAccessible.Role.Graphic
    assert described.text(QAccessible.Text.Name) == (
        "Agent concentration and relative partial pressure over time, whole run so far, "
        "15 minutes shown"
    )
    assert "Modelled sevoflurane at 10m: Circuit (inspired) " in described.text(
        QAccessible.Text.Description
    )
    assert (
        f"; Alveolar (end-tidal-equivalent) {format_percent(alveolar)}, "
        f"{format_mac_multiple(alveolar, mac_percent)};"
        in described.text(QAccessible.Text.Description)
    )

    _advance(controller, 60)
    view.present(False)

    assert "Modelled sevoflurane at 11m: " in described.text(QAccessible.Text.Description)

    chart.withhold()

    assert described.text(QAccessible.Text.Name) == (
        "Agent concentration and relative partial pressure over time"
    )
    assert described.text(QAccessible.Text.Description) == (
        "Nothing is plotted, because no frame could be drawn for this chart."
    )


def test_the_concentration_chart_tells_a_screen_reader_when_its_text_changes(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A new frame reports a changed description, and a withheld one a changed name (`PL-T9RB`).

    A screen reader that keeps the texts it has read, as the AT-SPI client
    library on Linux does, would otherwise go on reading an earlier frame's
    values. A frame that changes neither text reports nothing, so a paused run
    sends no event on each tick. The name stays the same from 10 to 11
    minutes, because the whole run so far still fits in the 15 minutes shown.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 600)
    view = _shown_view(application, controller)
    chart = _concentration(view).chart
    recorded = record_text_changes(monkeypatch)

    _advance(controller, 60)
    view.present(False)

    assert _changes_of(chart, recorded) == [TextChange(chart, QAccessible.Event.DescriptionChanged)]

    recorded.clear()
    view.present(False)

    assert _changes_of(chart, recorded) == []

    chart.withhold()

    assert _changes_of(chart, recorded) == [
        TextChange(chart, QAccessible.Event.NameChanged),
        TextChange(chart, QAccessible.Event.DescriptionChanged),
    ]


def test_the_concentration_chart_reports_its_new_name_when_its_area_gains_or_loses_a_number(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`PL-XV64`: the chart's name adds its Area's name, loses it again, and reports each change.

    A screen reader that keeps the names it has read, as the AT-SPI client
    library on Linux does, would otherwise go on calling the chart by its old
    name once a second Area shows the chart, or once that Area is closed.
    Telling the chart the Area it is already in reports nothing.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 600)
    view = _shown_view(application, controller)
    chart = _concentration(view).chart
    described = QAccessible.queryAccessibleInterface(chart)
    alone = (
        "Agent concentration and relative partial pressure over time, whole run so far, "
        "15 minutes shown"
    )
    assert described.text(QAccessible.Text.Name) == alone
    recorded = record_text_changes(monkeypatch)

    chart.name_among_copies("Concentrations 2")

    assert described.text(QAccessible.Text.Name) == f"{alone}, Concentrations 2"
    assert _changes_of(chart, recorded) == [TextChange(chart, QAccessible.Event.NameChanged)]

    recorded.clear()
    chart.name_among_copies("Concentrations 2")

    assert _changes_of(chart, recorded) == []

    chart.name_among_copies(None)

    assert described.text(QAccessible.Text.Name) == alone
    assert _changes_of(chart, recorded) == [TextChange(chart, QAccessible.Event.NameChanged)]


def _changes_of(source: QWidget, recorded: list[TextChange]) -> list[TextChange]:
    """Return the reports of `source`'s changed texts, leaving out every other graphic's."""

    return [change for change in recorded if change.source is source]


def test_the_wash_in_plot_tells_a_screen_reader_what_it_plots_and_each_run_s_ratio(
    application: QApplication,
) -> None:
    """The plot reports itself as an image, with a name and the ratio it ends at (`PL-R1M6`).

    Before `PL-R1M6` the plot reached a screen reader as an unnamed client
    area. The expected ratio is read from a second run built with the same
    settings, through the wash-in rules, not from the run the plot draws. The
    name starts with the heading as Qt reads the heading's label to a screen
    reader, so the subscripts are dropped in the same way in both.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 600)
    fresh = SimulationController()
    fresh.start()
    _advance(fresh, 600)
    snapshot = fresh.snapshot()
    reading = read_wash_in_with_ventilation(
        snapshot.alveolar_partial_pressure_fraction,
        snapshot.inspired_partial_pressure_fraction,
        snapshot.reaching_alveolar_ventilation_l_min,
    )
    assert reading.plotted_ratio is not None
    view = _shown_view(application, controller)
    plot = _wash_in(view).chart
    heading = next(
        label for label in _wash_in(view).findChildren(QLabel) if label.text() == WASH_IN_HEADING
    )
    described = QAccessible.queryAccessibleInterface(plot)
    heading_name = QAccessible.queryAccessibleInterface(heading).text(QAccessible.Text.Name)

    assert described.role() is QAccessible.Role.Graphic
    assert heading_name == "Wash-in: FA/FI, alveolar as a fraction of the modelled circuit"
    assert described.text(QAccessible.Text.Name) == (
        f"{heading_name}, whole run so far, 15 minutes shown"
    )
    assert described.text(QAccessible.Text.Description).splitlines() == [
        "Line chart.",
        "Model outputs — not measurements.",
        "Modelled sevoflurane at 10m: Wash-in FA/FI (alveolar / modelled circuit), "
        f"{format_wash_in_ratio(reading.plotted_ratio)}.",
        "Equilibrium, FA = FI",
    ]

    plot.withhold()

    assert described.text(QAccessible.Text.Name) == heading_name
    assert described.text(QAccessible.Text.Description) == (
        "Nothing is plotted, because no frame could be drawn for this chart."
    )


def test_a_held_wash_in_plot_tells_a_screen_reader_the_ratio_at_its_right_edge(
    application: QApplication,
) -> None:
    """With the window held back, the description gives the ratio where the trace ends (`PL-R1M6`).

    At 50 minutes, a 15-minute window stepped back once shows 30m to 45m, as
    `test_simulation_view_held_window.py` works out for the concentration
    chart. The trace ends at the window's right edge, so the description gives
    the ratio at 45m, read from a second run advanced only to 45m, and not the
    reading at 50m that the row above the plot gives.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 3000)
    fresh = SimulationController()
    fresh.start()
    _advance(fresh, 2700)
    snapshot = fresh.snapshot()
    reading = read_wash_in_with_ventilation(
        snapshot.alveolar_partial_pressure_fraction,
        snapshot.inspired_partial_pressure_fraction,
        snapshot.reaching_alveolar_ventilation_l_min,
    )
    assert reading.plotted_ratio is not None
    view = _shown_view(application, controller)
    wash_in = _wash_in(view)
    wash_in.time_base_selector.setCurrentIndex(wash_in.time_base_selector.findData("900.0"))
    wash_in._window.earlier_button.click()
    described = QAccessible.queryAccessibleInterface(wash_in.chart)

    assert described.text(QAccessible.Text.Name).endswith("held: not following the run")
    assert described.text(QAccessible.Text.Description).splitlines()[2] == (
        "Modelled sevoflurane at 45m: Wash-in FA/FI (alveolar / modelled circuit), "
        f"{format_wash_in_ratio(reading.plotted_ratio)}."
    )


def test_each_schematic_tells_a_screen_reader_its_run_its_instant_and_its_values(
    application: QApplication,
) -> None:
    """Each run's schematic reports itself as an image with its run, instant and values (`PL-R1M6`).

    The expected alveolar tension and amount are read from a second run built
    with the same settings, not from the run the schematic draws. The name
    adds the run once runs are compared, as the line over the schematic does.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 600)
    fresh = SimulationController()
    fresh.start()
    _advance(fresh, 600)
    snapshot = fresh.snapshot()
    alveolar_amount = snapshot.compartment_agent_amounts.of(RecordedQuantity.ALVEOLAR)
    alveolar_line = (
        f"Alveolar: {format_percent(snapshot.alveolar_partial_pressure_fraction)}, "
        f"{format_compartment_amount(alveolar_amount)}, "
    )
    view = _shown_view(application, controller)
    (schematic,) = view.findChildren(RunSchematic)
    described = QAccessible.queryAccessibleInterface(schematic.canvas)

    assert described.role() is QAccessible.Role.Graphic
    assert described.text(QAccessible.Text.Name) == (
        "Compartment schematic, at 10m of simulated time"
    )
    assert any(
        line.startswith(alveolar_line)
        for line in described.text(QAccessible.Text.Description).splitlines()
    )

    schematic.show_name("Run 2")

    assert described.text(QAccessible.Text.Name) == (
        "Compartment schematic, Run 2, at 10m of simulated time"
    )


def test_the_wash_in_plot_and_each_schematic_tell_a_screen_reader_when_their_text_changes(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A later frame reports each changed text, and a frame that changes none reports nothing.

    A screen reader that keeps the texts it has read, as the AT-SPI client
    library on Linux does, would otherwise go on reading an earlier frame's
    values (`PL-R1M6`). The wash-in plot's name stays the same from 10 to 11
    minutes, because the whole run so far still fits in the 15 minutes shown.
    The schematic's name gives the instant, so it changes too.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 600)
    view = _shown_view(application, controller)
    plot = _wash_in(view).chart
    (canvas,) = view.findChildren(SchematicCanvas)
    recorded = record_text_changes(monkeypatch)

    _advance(controller, 60)
    view.present(False)

    assert _changes_of(plot, recorded) == [TextChange(plot, QAccessible.Event.DescriptionChanged)]
    assert _changes_of(canvas, recorded) == [
        TextChange(canvas, QAccessible.Event.NameChanged),
        TextChange(canvas, QAccessible.Event.DescriptionChanged),
    ]

    recorded.clear()
    view.present(False)

    assert _changes_of(plot, recorded) == []
    assert _changes_of(canvas, recorded) == []


def test_every_plot_and_schematic_reaches_a_screen_reader_as_a_described_image(
    application: QApplication,
) -> None:
    """Each plot, and each run's schematic, sits in a graphic with a name and a description.

    Qt describes a plain widget as an unnamed client area, which VoiceOver on
    macOS passes over, and nothing a widget paints reaches assistive
    technology. The dashboard here shows every registered kind of View, so a
    plot or a schematic added to any View is in this walk, and fails it until
    it gives a text alternative (`PL-R1M6`).
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 60)
    view = _shown_view(application, controller)
    pictures: list[QWidget] = [*view.findChildren(PlotWidget), *view.findChildren(SchematicCanvas)]

    assert len(pictures) >= 3

    for picture in pictures:
        graphic: QWidget | None = picture

        while graphic is not None and not isinstance(graphic, DescribedGraphic):
            graphic = graphic.parentWidget()

        assert graphic is not None, type(picture).__name__
        described = QAccessible.queryAccessibleInterface(graphic)
        assert described.role() is QAccessible.Role.Graphic, type(graphic).__name__
        assert described.text(QAccessible.Text.Name), type(graphic).__name__
        assert described.text(QAccessible.Text.Description), type(graphic).__name__


def test_the_chart_defaults_to_fitting_the_whole_run(application: QApplication) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 1200)
    view = _shown_view(application, controller)
    frame = _concentration(view).chart.frame

    assert _concentration(view).time_base_selector.currentData() == FIT_RUN_KEY
    assert _chosen_time_base(view) is None
    assert frame is not None
    assert frame.fitted is True
    assert frame.start_s == 0.0
    assert frame.stop_s >= 1200.0


def test_the_time_base_selector_offers_fit_run_and_the_settled_widths(
    application: QApplication,
) -> None:
    combo = _concentration(_shown_view(application, SimulationController())).time_base_selector

    assert [combo.itemData(index) for index in range(combo.count())] == [
        FIT_RUN_KEY,
        *(str(time_base.span_s) for time_base in SELECTABLE_TIME_BASES),
    ]
    assert [combo.itemText(index) for index in range(combo.count())] == [
        "Fit run",
        *(format_time_base(time_base.span_s) for time_base in SELECTABLE_TIME_BASES),
    ]


def test_selecting_a_time_base_makes_the_window_exactly_that_wide(
    application: QApplication,
) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 300)
    view = _shown_view(application, controller)

    for time_base in SELECTABLE_TIME_BASES:
        _select_time_base(view, str(time_base.span_s))
        frame = _concentration(view).chart.frame

        assert frame is not None
        assert frame.fitted is False
        assert frame.stop_s - frame.start_s == pytest.approx(time_base.span_s)
        assert _chosen_time_base(view) == time_base_for_span(time_base.span_s)


def test_a_run_shorter_than_the_selected_time_base_shows_whole(application: QApplication) -> None:
    """`PL-SSBP`: a chosen width wider than the run draws the run from zero."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 300)
    view = _shown_view(application, controller)

    _select_time_base(view, "900.0")
    frame = _concentration(view).chart.frame

    assert frame is not None
    assert frame.start_s == 0.0
    assert frame.stop_s == 900.0
    assert _concentration(view).chart.drawn_points(0, RecordedQuantity.ALVEOLAR)[0][0] == (
        pytest.approx(0.0)
    )


def test_both_plots_are_labelled_from_the_same_ticks(application: QApplication) -> None:
    """One frame, both charts: the ticks cannot disagree because there is one list."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 1800)
    view = _shown_view(application, controller)

    assert _wash_in(view).chart.frame is _concentration(view).chart.frame
    assert _wash_in(view).chart.axis_ticks("bottom") == _concentration(view).chart.axis_ticks(
        "bottom"
    )


def test_the_two_plots_share_one_frame_while_they_show_the_same_window(
    application: QApplication,
) -> None:
    """Each plot owns its window (`PL-L59K`), and plots at one window draw one frame (`PL-9LNF`)."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 300)
    view = _shown_view(application, controller)
    wash_in = _wash_in(view)

    for key in (FIT_RUN_KEY, "900.0", "43200.0"):
        _select_time_base(view, key)
        wash_in.time_base_selector.setCurrentIndex(wash_in.time_base_selector.findData(key))

        assert wash_in.chart.frame is _concentration(view).chart.frame

    _select_time_base(view, "900.0")
    frame = wash_in.chart.frame

    assert frame is not None
    assert frame is not _concentration(view).chart.frame
    assert frame.time_base == time_base_for_span(43200.0)
    assert format_time_base(43200.0) in wash_in.chart.time_axis_title


def test_the_time_axis_title_states_the_span_and_the_mode(application: QApplication) -> None:
    """The width is a mode (`PL-012`), so the time axis's title says which and how wide."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 7200)
    view = _shown_view(application, controller)
    frame = _concentration(view).chart.frame
    assert frame is not None

    title = _concentration(view).chart.time_axis_title

    assert "whole run so far" in title
    assert f"{format_time_base(frame.time_base.span_s)} shown" in title
    assert "simulated seconds" not in title

    _select_time_base(view, "7200.0")

    assert _concentration(view).chart.time_axis_title == "simulated time, 2 hours shown"


def test_choosing_a_time_base_changes_nothing_the_run_recorded(application: QApplication) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 20)
    view = _shown_view(application, controller)
    recorded = (controller.snapshot().elapsed_s, controller.run_segments)

    for key in (*(str(time_base.span_s) for time_base in SELECTABLE_TIME_BASES), FIT_RUN_KEY):
        _select_time_base(view, key)

        assert (controller.snapshot().elapsed_s, controller.run_segments) == recorded


def test_the_time_base_is_never_disabled(application: QApplication) -> None:
    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()
    view.present(False)

    assert view.runs[0]._agent_dropdown.isEnabled() is False
    assert _concentration(view).time_base_selector.isEnabled() is True


def test_a_window_pick_whose_frame_fails_leaves_the_control_on_the_window_drawn(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The control names the window on the plot, not one that never drew (`PL-G3K7`, `PL-L59K`)."""

    controller = _paused_run_with_history(1800)
    view = _shown_view(application, controller)
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    _select_time_base(view, "900.0")

    frame = _concentration(view).chart.frame
    assert frame is not None
    assert frame.fitted is True
    assert _concentration(view).time_base_selector.currentData() == FIT_RUN_KEY


def test_a_frame_is_assembled_and_checked_with_no_chart_shown(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Assembling a frame checks the runs, so a frame is assembled whatever the Areas hold.

    This is `PL-L59K`. With every chart replaced, no View asks for a window. A
    frame is still assembled at "Fit run". So a run state that the assembly
    rejects still halts every run, rather than going unnoticed until a chart
    is shown again.
    """

    view = _shown_view(application, _paused_run_with_history(60))

    for area in (AreaId(1), AreaId(3)):
        view.layout_container.choose_view(area, PARAMETER_CONTROLS)

    _settle(application)
    assert view.layout_container.frame_requests() == {}
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.present(False)

    assert all(run.controller.has_failed for run in view.runs)


def test_a_chart_s_window_returns_with_the_chart_after_its_area_shows_another_view(
    application: QApplication,
) -> None:
    """A chart's window is the View's own state, saved when the reader replaces it (`PL-L59K`).

    The time-base control sits in the chart View. So a reader closes the
    control only by choosing another View for the chart's Area. Meanwhile the
    F_A/F_I plot keeps its own window. A concentration chart brought back to
    that Area shows the window that the reader chose.
    """

    controller = _paused_run_with_history(1800)
    view = _shown_view(application, controller)
    _select_time_base(view, "1800.0")

    view.layout_container.choose_view(AreaId(1), PARAMETER_CONTROLS)
    _settle(application)
    view.present(False)

    frame = _wash_in(view).chart.frame
    assert frame is not None
    assert frame.fitted is True

    view.layout_container.choose_view(AreaId(1), CONCENTRATION_CHART)
    view.present(False)

    assert _chosen_time_base(view) == time_base_for_span(1800.0)
    assert _concentration(view).time_base_selector.currentData() == "1800.0"
    assert format_time_base(1800.0) in _concentration(view).chart.time_axis_title


def test_reset_leaves_the_selected_time_base_alone(application: QApplication) -> None:
    view = _shown_view(application, SimulationController())

    _select_time_base(view, "1800.0")
    view.runs[0]._reset_button.click()

    assert _chosen_time_base(view) == time_base_for_span(1800.0)
    assert _concentration(view).time_base_selector.currentData() == "1800.0"


# The words that follow each reference's value in its legend entry
# (`PL-K4CZ`). They are written out here rather than read from the templates,
# so a change to the entries' words fails this module.
_ONE_MAC_ENTRY_WORDS = ", reference adult (alveolar, wide dash)"
_BAND_ENTRY_WORDS = "; population, read against vessel-rich group trace"


def test_the_mac_axis_and_references_follow_the_agent(application: QApplication) -> None:
    """The divisor line, the 1 MAC line and the right axis are the running agent's."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    chart = _concentration(view).chart

    # Mapleson 1996 (PMID 8777094), Abstract: MAC at age 40 of 1.80% sevoflurane and
    # 6.6% desflurane. The reference adult is 40.
    assert _concentration(view).legend.one_mac_text == (
        "1 MAC sevoflurane (age 40) = 1.8%" + _ONE_MAC_ENTRY_WORDS
    )
    assert chart.one_mac_line() == 1.8
    assert chart.axis_ticks("right")[-1][1] == "3.0"
    assert chart.axis_ticks("right")[-1][0] == pytest.approx(5.4)

    _select_agent(view.runs[0], "desflurane")
    # Read from desflurane's own file, not from the switched run's snapshot,
    # which would agree with a band the switch failed to rebuild (`PL-JPS2`).
    mac_awake = load_agent_parameters("desflurane").mac_awake

    assert _concentration(view).legend.one_mac_text == (
        "1 MAC desflurane (age 40) = 6.6%" + _ONE_MAC_ENTRY_WORDS
    )
    assert _concentration(view).legend.band_mark.label == (
        format_mac_awake_reference(
            "Desflurane",
            fraction_of_mac=mac_awake.fraction_of_mac,
            standard_deviation_fraction_of_mac=mac_awake.standard_deviation_fraction_of_mac,
            mac_percent=MacPercent(6.6),
        )
        + _BAND_ENTRY_WORDS
    )
    assert chart.one_mac_line() == 6.6
    # 3 MAC of 6.6% is 19.8%, above desflurane's 18% dial maximum.
    assert chart.axis_ticks("right")[-1][1] == "3.0"
    assert chart.axis_ticks("right")[-1][0] == pytest.approx(19.8)


@pytest.mark.parametrize(
    ("previous_agent_id", "agent_id"),
    [
        (previous, chosen)
        for previous in AGENT_DATA_FILENAMES
        for chosen in AGENT_DATA_FILENAMES
        if previous != chosen
    ],
)
def test_the_mac_awake_band_after_a_switch_is_the_new_agents_own(
    application: QApplication, previous_agent_id: str, agent_id: str
) -> None:
    """After a switch, the band and its line of text use the chosen agent's own values.

    A switch keeps the controller. So a band the switch failed to rebuild
    would still hold the previous agent's fraction and spread, and the
    snapshot would agree with the chart. The expected values therefore come
    from the chosen agent's data file, and the test works out the band's
    edges itself (`PL-JPS2`). After a switch from sevoflurane, such a fault
    would draw desflurane's band at 1.74-2.34% instead of 1.78-2.54%.
    """

    view = _shown_view(application, SimulationController(agent_id=previous_agent_id))
    _select_agent(view.runs[0], agent_id)
    own = load_agent_parameters(agent_id)
    fraction = own.mac_awake.fraction_of_mac
    spread = own.mac_awake.standard_deviation_fraction_of_mac

    assert view.runs[0].controller.agent_id == agent_id
    assert _concentration(view).chart.mac_awake_band() == pytest.approx(
        (
            (fraction - spread) * own.mac_at_age_40_percent,
            (fraction + spread) * own.mac_at_age_40_percent,
        )
    )
    assert _concentration(view).legend.band_mark.label == (
        format_mac_awake_reference(
            own.display_name,
            fraction_of_mac=fraction,
            standard_deviation_fraction_of_mac=spread,
            mac_percent=own.mac_at_age_40_percent,
        )
        + _BAND_ENTRY_WORDS
    )


def test_a_recorded_change_is_marked_on_the_chart_at_its_own_time(
    application: QApplication,
) -> None:
    """`PL-DR1Z`: the mark is drawn at the change's instant on both plots."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 600)
    controller.begin_control_adjustment()
    controller.set_fresh_gas_flow(FreshGasFlow(2.0))
    _advance(controller, 600)
    view = _shown_view(application, controller)

    assert _concentration(view).chart.control_mark_times(0) == (pytest.approx(600.0),)
    assert _wash_in(view).chart.control_mark_times(0) == (pytest.approx(600.0),)
    assert view.runs[0]._control_timeline_text.text().startswith(format_elapsed(600.0))


def test_a_real_run_draws_the_ratio_of_its_own_recorded_compartments(
    application: QApplication,
) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 60)
    view = _shown_view(application, controller)
    snapshot = controller.snapshot()
    reading = read_wash_in_with_ventilation(
        snapshot.alveolar_partial_pressure_fraction,
        snapshot.inspired_partial_pressure_fraction,
        snapshot.reaching_alveolar_ventilation_l_min,
    )
    assert reading.plotted_ratio is not None

    stretches = _wash_in(view).chart.drawn_stretches(0)
    assert stretches
    last_time, last_ratio = stretches[-1][-1]

    assert last_time == pytest.approx(snapshot.elapsed_s)
    assert last_ratio == pytest.approx(reading.plotted_ratio)
    assert format_wash_in_ratio(last_ratio) in _wash_in(view).states.lines[0].text()
