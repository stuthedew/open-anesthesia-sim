"""These tests run the dashboard's leaf widgets without a display, using real controllers.

`app/qt_widgets.py` updates Qt widgets to match `dashboard_frame` values and makes no
decisions of its own. These tests check the few behaviors that belong to the widgets
themselves:

- that a readout's value cannot wrap onto a different line from its unit (`PL-3355`)
- that a slider's position is exactly the printed value (`PL-25KS`, D4)
- that a value written into a slider from a snapshot is never reported back as a change
- that the new-case dialog's default choice keeps the current case
- which cell of the marks editor each field sits in, the order in which Tab visits them, and
  how an entry and a refusal are written into it
- where the window opens (`PL-005`)
- that a selector draws its own arrow and none of the platform's button (`PL-9389`)

The widgets render on Qt's `offscreen` platform, which `tests/conftest.py` selects.
"""

from collections.abc import Iterator

import pytest
from PySide6.QtCore import QEvent, QPoint, QPointF, QRect, QSize, Qt
from PySide6.QtGui import QColor, QFontMetrics, QPalette
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QGridLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QStyle,
    QStyleOptionComboBox,
    QWidget,
)

from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import (
    COMPARTMENT_FIELD_LABEL,
    EMPTY_METRIC_QUALIFIER,
    EMPTY_METRIC_SECONDARY_VALUE,
    HEIGHT_FIELD_LABEL,
    INSTANT_FIELD_LABEL,
    MARK_NAME_FIELD_LABEL,
    READOUT_RESERVATIONS,
    READOUT_ROW_LADDER,
    TARGET_FORM_HEADING,
    TIME_FORM_HEADING,
    WIDEST_READOUT_SECONDARY,
    WIDEST_READOUT_VALUE,
    Readout,
    SettingReadout,
    new_case_question,
    readout_columns,
    readouts,
    setting_readouts,
    slider_position,
    slider_value,
)
from anesthesia_sim.app.formatting import format_flow, format_percent
from anesthesia_sim.app.playback import SUPPORTED_PLAYBACK_RATES
from anesthesia_sim.app.qt_widgets import (
    WINDOW_SCREEN_FRACTION,
    FlowLayout,
    MarkButton,
    MarkEditor,
    MarkEntry,
    MarkRefusal,
    MetricPanel,
    NewCaseDialog,
    NoticeLabel,
    ParameterSlider,
    ReadoutRow,
    SelectorComboBox,
    initial_window_geometry,
    styled_label,
)
from anesthesia_sim.app.stylesheets import (
    agent_selector_stylesheet,
    selector_stylesheet,
    transport_button_stylesheet,
)
from anesthesia_sim.app.theme import (
    ACCENT,
    AGENT_COLOR_SCHEMES,
    INK,
    MENU_ARROW_SIZE,
    MUTED,
    PANEL,
    PANEL_RADIUS,
    WARNING,
)
from anesthesia_sim.core.concentration import Percent, fraction_from_percent


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


def _clock_readout(value: str) -> Readout:
    return Readout("Simulated time", EMPTY_METRIC_QUALIFIER, value, WIDEST_READOUT_SECONDARY)


def _panel(readout: Readout) -> MetricPanel:
    return MetricPanel(
        readout, widest_value=WIDEST_READOUT_VALUE, widest_secondary=WIDEST_READOUT_SECONDARY
    )


def _row(application: QApplication, width: int) -> ReadoutRow:
    snapshot = SimulationController().snapshot()
    row = ReadoutRow(
        readouts(snapshot, SUPPORTED_PLAYBACK_RATES[0]), reservations=READOUT_RESERVATIONS
    )
    row.resize(width, 400)
    row.show()
    application.processEvents()

    return row


def _grid(row: ReadoutRow) -> QGridLayout:
    grid = row.layout()
    assert isinstance(grid, QGridLayout)

    return grid


def _cells(row: ReadoutRow) -> list[tuple[int, int]]:
    """Return the cell where each panel sits, in panel order.

    Every panel occupies exactly one cell.
    """

    grid = _grid(row)
    occupied: dict[QWidget, list[tuple[int, int]]] = {}

    for row_index in range(grid.rowCount()):
        for column in range(grid.columnCount()):
            item = grid.itemAtPosition(row_index, column)
            widget = None if item is None else item.widget()

            if widget is not None:
                occupied.setdefault(widget, []).append((row_index, column))

    cells = [occupied[panel] for panel in row.panels]
    assert all(len(found) == 1 for found in cells), "a readout given more than one cell"

    return [found[0] for found in cells]


def _width_for(row: ReadoutRow, columns: int) -> int:
    """Return the narrowest row width for `columns` panels at their reservations and spacing."""

    return row.width_for(columns)


def _resize(application: QApplication, row: ReadoutRow, width: int) -> None:
    row.resize(width, 400)
    application.processEvents()


def _one_line_height(like: QLabel) -> int:
    """Return the height of a one-line label in `like`'s font, from a label that cannot wrap."""

    reference = QLabel("0s")
    reference.setFont(like.font())

    return reference.sizeHint().height()


def _printed_value(setting: SettingReadout, value: float) -> float:
    """Return the number that the readout beside the slider prints for `value`, parsed back."""

    if setting.control is ControlInput.DELIVERED:
        return float(format_percent(fraction_from_percent(Percent(value))).rstrip("%"))

    return float(format_flow(value).split(" ")[0])


# ---------------------------------------------------------------- readouts


def test_no_metric_value_wraps_away_from_its_unit(application: QApplication) -> None:
    """A value label never breaks a line, however little width the layout offers (`PL-3355`)."""

    container = QWidget()
    panel = _panel(_clock_readout(WIDEST_READOUT_VALUE))
    panel.setParent(container)
    container.resize(1000, 200)
    container.show()
    application.processEvents()
    advance = QFontMetrics(panel.value_label.font()).horizontalAdvance(WIDEST_READOUT_VALUE)

    panel.setGeometry(0, 0, advance // 2, 200)
    application.processEvents()

    assert panel.value_label.wordWrap() is False
    assert panel.secondary_label.wordWrap() is False
    assert not panel.value_label.hasHeightForWidth()
    assert panel.value_label.sizeHint().height() == _one_line_height(panel.value_label)
    assert panel.value_label.heightForWidth(advance // 2) == _one_line_height(panel.value_label)
    assert panel.value_label.width() >= advance
    assert panel.minimum_value_width_px >= advance
    assert panel.minimumWidth() == panel.minimum_value_width_px


def test_every_readout_reserves_a_qualifier_line_and_an_equal_column(
    application: QApplication,
) -> None:
    """The row is scanned across, so no panel may differ in shape from its neighbours (`PL-8M05`).

    Every panel draws all four lines, at the sizes that rank them. Where a
    panel has no gloss or no second unit, it draws a spacer in that line.
    The widest rung of the ladder seats every readout side by side in equal
    columns, so an eighth panel cannot silently split the row.
    """

    row = _row(application, 2000)

    assert len(row.panels) == len(
        readouts(SimulationController().snapshot(), SUPPORTED_PLAYBACK_RATES[0])
    )

    for panel in row.panels:
        assert panel.name_label.text(), "a readout with no name"
        assert panel.qualifier_label.text(), "a readout that does not hold its gloss line open"
        assert panel.value_label.text(), "a readout with no value"
        assert panel.secondary_label.text(), (
            "a readout that does not hold its second-unit line open"
        )
        assert panel.qualifier_label.font().pixelSize() < panel.name_label.font().pixelSize()
        assert panel.secondary_label.font().pixelSize() < panel.value_label.font().pixelSize()

    assert row.columns() == READOUT_ROW_LADDER[0] == len(row.panels)
    assert [cell[0] for cell in _cells(row)] == [0] * len(row.panels)
    grid = _grid(row)
    assert {grid.columnStretch(column) for column in range(row.columns())} == {1}
    assert [grid.columnMinimumWidth(column) for column in range(row.columns())] == list(
        row.panel_minimum_widths_px
    )
    assert row.panel_minimum_widths_px[0] == max(row.panel_minimum_widths_px), (
        "the clock's column carries the widest reservation"
    )


def test_an_empty_gloss_line_is_as_tall_as_a_filled_one(application: QApplication) -> None:
    """A panel with no gloss or no second unit keeps both lines open, so the row keeps one baseline.

    The two spacer lines hold a no-break space. An empty string would give a
    shorter line in most fonts, which CI measured as 15 px against 16 px for
    the second-unit line (`PL-P55M`). So this test measures the labels
    instead of trusting the character. A panel built with both lines empty
    must be as tall, line by line, as a panel in the row with both filled
    (`PL-8M05`).
    """

    row = _row(application, 2000)
    filled = next(
        panel
        for panel in row.panels
        if panel.qualifier_label.text() and panel.secondary_label.text()
    )
    empty = _panel(
        Readout("Simulated time", EMPTY_METRIC_QUALIFIER, "0s", EMPTY_METRIC_SECONDARY_VALUE)
    )

    assert empty.qualifier_label.text() == EMPTY_METRIC_QUALIFIER
    assert empty.secondary_label.text() == EMPTY_METRIC_SECONDARY_VALUE
    assert empty.qualifier_label.sizeHint().height() == filled.qualifier_label.sizeHint().height()
    assert empty.secondary_label.sizeHint().height() == filled.secondary_label.sizeHint().height()
    assert empty.qualifier_label.sizeHint().height() > 0
    assert empty.secondary_label.sizeHint().height() > 0
    assert empty.sizeHint().height() == filled.sizeHint().height()


def test_the_clock_reserves_its_width_so_the_panel_cannot_move(application: QApplication) -> None:
    """The one value whose string changes length cannot shift its panel as it ticks."""

    panel = _panel(_clock_readout("0s"))
    reserved = (
        panel.minimumWidth(),
        panel.minimumSizeHint().width(),
        panel.value_label.minimumWidth(),
    )

    panel.set_readout(_clock_readout(WIDEST_READOUT_VALUE))

    assert panel.value_label.text() == WIDEST_READOUT_VALUE
    assert (
        panel.minimumWidth(),
        panel.minimumSizeHint().width(),
        panel.value_label.minimumWidth(),
    ) == reserved
    assert reserved[2] >= QFontMetrics(panel.value_label.font()).horizontalAdvance(
        WIDEST_READOUT_VALUE
    )


def test_the_readout_row_reflows_where_its_panels_stop_fitting(application: QApplication) -> None:
    """The row steps down the ladder at the width that its own reservation sets (`PL-8M05`).

    At the narrowest width that seats seven panels of the measured
    reservation, with the grid's spacing between them, the row is seven
    across. One pixel narrower, it is four across. At every step, no panel
    is laid outside the row. The test reads the widths from the row rather
    than writing them here, so it still passes on any font and at any
    display scale.
    """

    row = _row(application, 2000)
    seven, four, two = (_width_for(row, columns) for columns in (7, 4, 2))
    spacing = _grid(row).horizontalSpacing()

    assert spacing >= 0
    assert row.panel_minimum_width_px > 0
    assert (seven - 1 - four) > 0, "the four-across rung does not fit inside the seven-across width"

    for width, columns in (
        (seven, 7),
        (seven - 1, 4),
        (four, 4),
        (four - 1, 2),
        (two, 2),
        (two - 1, 1),
        (row.width_for(1), 1),
    ):
        _resize(application, row, width)

        assert row.width() == width
        assert row.columns() == columns
        assert columns == readout_columns(width, row.panel_minimum_widths_px, spacing)
        assert max(cell[1] for cell in _cells(row)) == columns - 1
        assert _cells(row) == [
            (index // columns, index % columns) for index in range(len(row.panels))
        ]

        for panel, reservation in zip(row.panels, row.panel_minimum_widths_px, strict=True):
            geometry = panel.geometry()

            assert geometry.width() >= reservation
            assert geometry.x() + geometry.width() <= row.width(), (
                f"a panel laid outside the row at {width} px, {columns} across"
            )


def test_a_narrowed_readout_row_reflows_rather_than_widening_its_scroll_area(
    application: QApplication,
) -> None:
    """The row's minimum width is one column's, so a container can narrow it and it steps down.

    If the row reported its seven-column minimum, a scroll area could never
    narrow it, because a scroll area widens its page to the widest minimum
    and scrolls. The readout row would then never reflow, and the page would
    overhang every window narrower than seven panels. Every panel keeps its
    own reservation, so no value wraps at the narrower count (`PL-3355`).
    """

    row = _row(application, 2000)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(row)
    scroll.resize(900, 400)
    scroll.show()
    application.processEvents()
    spacing = _grid(row).horizontalSpacing()

    assert row.minimumSizeHint().width() == row.panel_minimum_width_px
    assert row.minimumSize().width() == row.panel_minimum_width_px
    assert row.width() == scroll.viewport().width()
    assert scroll.horizontalScrollBar().maximum() == 0
    assert not scroll.horizontalScrollBar().isVisible()
    assert row.columns() == readout_columns(row.width(), row.panel_minimum_widths_px, spacing)
    assert 1 < row.columns() < len(row.panels)
    assert row.columns() == 4

    for panel in row.panels:
        geometry = panel.geometry()

        assert geometry.width() >= panel.minimum_value_width_px
        assert geometry.x() + geometry.width() <= row.width()

    scroll.close()


def test_a_flow_layout_wraps_at_its_width_and_lays_nothing_outside_it(
    application: QApplication,
) -> None:
    """The shape of Qt's Flow Layout example: left to right, then the next line."""

    host = QWidget()
    flow = FlowLayout(horizontal_spacing=16, vertical_spacing=6, parent=host)
    labels = [QLabel(f"entry {index} " * 3) for index in range(6)]

    for label in labels:
        flow.addWidget(label)

    widest = max(label.sizeHint().width() for label in labels)
    one_line = max(label.sizeHint().height() for label in labels)
    two_per_line = 2 * widest + 16 + 4

    assert flow.count() == len(labels)
    assert flow.minimumSize().width() == widest
    assert flow.minimumSize().height() == one_line
    assert flow.sizeHint() == flow.minimumSize()
    assert flow.hasHeightForWidth()
    assert flow.expandingDirections() == Qt.Orientation(0)
    assert flow.heightForWidth(10_000) == one_line
    assert flow.heightForWidth(two_per_line) == 3 * one_line + 2 * 6

    host.resize(two_per_line, flow.heightForWidth(two_per_line))
    host.show()
    application.processEvents()
    lines = sorted({label.geometry().y() for label in labels})

    assert len(lines) == 3
    assert [label.geometry().y() for label in labels] == [
        lines[0],
        lines[0],
        lines[1],
        lines[1],
        lines[2],
        lines[2],
    ]

    for label in labels:
        assert label.geometry().x() >= 0
        assert label.geometry().right() < two_per_line

    assert flow.takeAt(0) is not None
    assert flow.count() == len(labels) - 1
    assert flow.itemAt(len(labels)) is None
    assert flow.takeAt(len(labels)) is None
    host.close()


class _OneLineLabel(QLabel):
    """Words that wrap, and that ask for the width of one line."""

    def sizeHint(self) -> QSize:  # Qt spells this in camelCase.
        width = self.fontMetrics().horizontalAdvance(self.text()) + 1

        return QSize(width, self.heightForWidth(width))


def test_a_flow_layout_gives_an_item_wider_than_the_row_the_row_s_width(
    application: QApplication,
) -> None:
    """`PL-K4CZ`: words wider than the row wrap inside it, rather than running past its edge.

    The MAC-awake legend entry is such an item. It keeps to one line in a
    wide row and wraps in a narrow one.
    """

    host = QWidget()
    flow = FlowLayout(horizontal_spacing=16, vertical_spacing=6, parent=host)
    label = _OneLineLabel("a band of words that is wider than the row it sits in " * 2)
    label.setWordWrap(True)
    flow.addWidget(label)
    one_line = label.sizeHint()
    narrow = one_line.width() // 3

    assert flow.heightForWidth(one_line.width()) == one_line.height()
    assert flow.heightForWidth(narrow) == label.heightForWidth(narrow)
    assert flow.heightForWidth(narrow) > one_line.height()

    host.resize(narrow, flow.heightForWidth(narrow))
    host.show()
    application.processEvents()

    assert label.geometry().x() == 0
    assert label.geometry().width() == narrow
    assert label.geometry().height() == label.heightForWidth(narrow)
    host.close()


def test_a_readout_row_refuses_the_wrong_number_of_readouts(application: QApplication) -> None:
    row = _row(application, 1400)

    with pytest.raises(ValueError, match="7 panels and was given 1 readouts"):
        row.set_readouts([_clock_readout("0s")])


def test_a_readout_row_refuses_readings_of_other_quantities(application: QApplication) -> None:
    """A value shown under another quantity's name is the wrong value (`PL-F2YS`)."""

    row = _row(application, 1400)
    snapshot = SimulationController().snapshot()
    shorter = ReadoutRow(
        readouts(snapshot, SUPPORTED_PLAYBACK_RATES[0])[:6], reservations=READOUT_RESERVATIONS[:6]
    )
    reordered = ReadoutRow(
        readouts(snapshot, SUPPORTED_PLAYBACK_RATES[0])[::-1],
        reservations=READOUT_RESERVATIONS[::-1],
    )

    for other in (shorter, reordered):
        with pytest.raises(ValueError, match="cannot show the readings of a row"):
            row.add_readings(other)

    assert all(len(panel.findChildren(QLabel)) == 5 for panel in row.panels)


def test_a_readout_row_carries_a_second_row_s_readings_under_one_name_each(
    application: QApplication,
) -> None:
    """Each panel gains the other run's value, its second unit and its run's name.

    The other row is hidden. Deleting the returned readings leaves each panel
    with its own five labels again, as dropping a branch does.
    """

    row = _row(application, 1400)
    other = _row(application, 1400)

    readings = row.add_readings(other)
    row.set_run_name("Run 1")
    other.set_run_name("Run 2")
    application.processEvents()

    assert other.isHidden()
    assert len(readings) == len(row.panels) == 7

    for panel, compared, reading in zip(row.panels, other.panels, readings, strict=True):
        assert reading is compared.reading
        assert panel.isAncestorOf(compared.value_label)
        assert panel.isAncestorOf(compared.secondary_label)
        assert panel.run_name_label.text() == "Run 1"
        assert compared.run_name_label.text() == "Run 2"
        assert compared.run_name_label.isVisibleTo(panel)
        assert compared.run_name_label.y() < compared.value_label.y()

    for reading in readings:
        reading.setParent(None)
        reading.deleteLater()

    QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)

    assert all(len(panel.findChildren(QLabel)) == 5 for panel in row.panels)


def test_a_lone_run_s_panel_shows_no_run_name(application: QApplication) -> None:
    row = _row(application, 1400)
    row.set_run_name("Run 1")
    row.set_run_name(None)

    assert all(panel.run_name_label.isHidden() for panel in row.panels)


# ----------------------------------------------------------------- sliders


def _settings() -> tuple[SettingReadout, ...]:
    return setting_readouts(SimulationController().snapshot())


def test_the_value_applied_to_the_model_is_exactly_the_value_printed_beside_the_slider(
    application: QApplication,
) -> None:
    """A slider position and the readout beside it are one number (`PL-25KS`, D4)."""

    for setting in _settings():
        control = ParameterSlider(setting)
        emitted: list[float] = []
        control.value_changed.connect(emitted.append)
        minimum, maximum = control.slider.minimum(), control.slider.maximum()
        positions = sorted(
            {minimum, maximum, *range(minimum, maximum + 1, max(1, (maximum - minimum) // 40))}
        )

        for position in positions:
            emitted.clear()
            control.slider.setValue(position)

            if position == slider_position(setting.value, setting.decimals):
                continue

            assert emitted == [slider_value(position, setting.decimals)], setting.control
            assert control.value() == emitted[0]
            assert _printed_value(setting, control.value()) == control.value(), setting.control


def test_the_slider_steps_at_the_display_resolution(application: QApplication) -> None:
    for setting in _settings():
        control = ParameterSlider(setting)

        assert control.slider.minimum() == slider_position(setting.minimum, setting.decimals)
        assert control.slider.maximum() == slider_position(setting.maximum, setting.decimals)
        assert control.slider.singleStep() == 1
        assert control.slider.pageStep() == 1
        assert control.slider.value() == slider_position(setting.value, setting.decimals)
        assert control.value_label.text() == setting.value_text


def test_driving_a_slider_from_the_snapshot_emits_no_change(application: QApplication) -> None:
    """A value written from the snapshot must never be applied back to it as a change."""

    fresh_gas_flow, delivered, *_ = _settings()
    control = ParameterSlider(delivered)
    emitted: list[float] = []
    control.value_changed.connect(emitted.append)
    started: list[None] = []
    control.adjustment_started.connect(lambda: started.append(None))
    moved = SettingReadout(
        control=delivered.control,
        name="Delivered isoflurane",
        qualifier=delivered.qualifier,
        unit=delivered.unit,
        decimals=delivered.decimals,
        minimum=delivered.minimum,
        maximum=delivered.maximum * 2.0,
        value=delivered.value * 1.5,
        value_text="changed",
        secondary="changed again",
    )

    control.set_setting(moved)
    control.set_setting(fresh_gas_flow)

    assert emitted == []
    assert started == []
    assert control.slider.maximum() == slider_position(
        fresh_gas_flow.maximum, fresh_gas_flow.decimals
    )
    assert control.value() == fresh_gas_flow.value
    assert control.name_label.text() == fresh_gas_flow.name
    assert control.value_label.text() == fresh_gas_flow.value_text


def test_a_slider_press_declares_an_adjustment(application: QApplication) -> None:
    control = ParameterSlider(_settings()[0])
    started: list[None] = []
    control.adjustment_started.connect(lambda: started.append(None))

    control.slider.setSliderDown(True)
    control.slider.setSliderDown(False)

    assert started == [None]


def test_a_dragged_thumb_previews_until_release_and_then_applies_once(
    application: QApplication,
) -> None:
    """A pointer drag previews where the thumb stands and applies on release (`PL-5B1N`).

    The value is applied before the preview ends. So the frame drawn when the
    preview ends shows the run under the released setting, and never the old
    setting with the preview gone.
    """

    setting = _settings()[0]
    control = ParameterSlider(setting)
    events: list[tuple[str, float | None]] = []
    control.preview_moved.connect(lambda value: events.append(("preview", value)))
    control.preview_ended.connect(lambda: events.append(("ended", control.value())))
    control.value_changed.connect(lambda value: events.append(("applied", value)))
    start = slider_position(setting.value, setting.decimals)

    control.slider.setSliderDown(True)
    control.slider.setSliderPosition(start + 5)
    control.slider.setSliderPosition(start + 10)

    held = [
        ("preview", setting.value),
        ("preview", slider_value(start + 5, setting.decimals)),
        ("preview", slider_value(start + 10, setting.decimals)),
    ]
    assert events == held

    control.slider.setSliderDown(False)

    assert events == [
        *held,
        ("applied", slider_value(start + 10, setting.decimals)),
        ("ended", slider_value(start + 10, setting.decimals)),
    ]


def test_a_released_thumb_back_where_it_started_applies_nothing(application: QApplication) -> None:
    setting = _settings()[0]
    control = ParameterSlider(setting)
    applied: list[float] = []
    ended: list[None] = []
    control.value_changed.connect(applied.append)
    control.preview_ended.connect(lambda: ended.append(None))
    start = slider_position(setting.value, setting.decimals)

    control.slider.setSliderDown(True)
    control.slider.setSliderPosition(start + 5)
    control.slider.setSliderPosition(start)
    control.slider.setSliderDown(False)

    assert ended == [None]
    assert applied == []


def test_a_key_step_applies_at_once_and_previews_nothing(application: QApplication) -> None:
    setting = _settings()[0]
    control = ParameterSlider(setting)
    previewed: list[float] = []
    applied: list[float] = []
    control.preview_moved.connect(previewed.append)
    control.value_changed.connect(applied.append)
    start = slider_position(setting.value, setting.decimals)

    QTest.keyClick(control.slider, Qt.Key.Key_Right)

    assert applied == [slider_value(start + 1, setting.decimals)]
    assert previewed == []


def test_a_frame_written_during_a_drag_leaves_the_thumb_under_the_pointer(
    application: QApplication,
) -> None:
    """The run keeps its setting during a drag, so writing it must not pull the thumb back."""

    setting = _settings()[0]
    control = ParameterSlider(setting)
    start = slider_position(setting.value, setting.decimals)
    control.slider.setSliderDown(True)
    control.slider.setSliderPosition(start + 10)

    control.set_setting(setting)

    assert control.slider.sliderPosition() == start + 10
    assert control.value_label.text() == setting.value_text


def test_the_delivered_dial_shows_its_mac_line_and_the_flow_controls_do_not(
    application: QApplication,
) -> None:
    for setting in _settings():
        control = ParameterSlider(setting)
        control.show()
        application.processEvents()

        if setting.control is ControlInput.DELIVERED:
            assert setting.secondary
            assert not control.secondary_label.isHidden()
            assert control.secondary_label.text() == setting.secondary
        else:
            assert setting.secondary == ""
            assert control.secondary_label.isHidden()

        assert control.qualifier_label.text() == setting.qualifier
        assert control.qualifier_label.isHidden() == (setting.qualifier == "")
        assert control.qualifier_label.font().italic()
        assert control.name_label.font().bold()


def test_the_slider_active_track_is_the_accent(application: QApplication) -> None:
    """The filled track is drawn in `ACCENT`, the colour `PL-W8DQ` measures for it."""

    control = ParameterSlider(_settings()[0])
    control.resize(400, 120)
    control.show()
    application.processEvents()
    image = control.slider.grab().toImage()
    accent_columns = {
        x
        for x in range(image.width())
        for y in range(image.height())
        if image.pixelColor(x, y).name().upper() == ACCENT
    }

    assert accent_columns
    assert min(accent_columns) < image.width() // 4
    assert max(accent_columns) < image.width()


# ------------------------------------------------------ the transport buttons


def _under_a_dark_host(button: QPushButton) -> QPushButton:
    """Give one button the palette that a dark host appearance supplies.

    The palette is set on the widget rather than on the application, so that
    it cannot leak into the other tests that share the module-scoped
    `QApplication`. The values stand in for what macOS supplies in Dark
    appearance, where `PL-DHBX` was reported: a near-white `ButtonText` over
    a dark `Button`.
    """

    palette = QPalette(button.palette())
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#323232"))
    button.setPalette(palette)

    return button


def _channel_distance(one: str, other: str) -> int:
    """Return the largest per-channel difference between two colours, from 0 to 255."""

    first, second = QColor(one), QColor(other)

    return max(
        abs(first.red() - second.red()),
        abs(first.green() - second.green()),
        abs(first.blue() - second.blue()),
    )


def _transport_button(enabled: bool) -> QPushButton:
    """Return one transport button in the state under test."""

    button = QPushButton("Pause")
    button.setEnabled(enabled)

    return button


def _drawn(button: QPushButton, application: QApplication) -> list[str]:
    """Return every pixel of a rendered button as an upper-case hex colour name."""

    button.resize(90, 30)
    button.show()
    application.processEvents()
    image = button.grab().toImage()

    return [
        image.pixelColor(x, y).name().upper()
        for y in range(image.height())
        for x in range(image.width())
    ]


@pytest.mark.parametrize(
    ("enabled", "expected"), [(True, INK), (False, MUTED)], ids=["usable", "unavailable"]
)
def test_a_transport_button_draws_the_theme_rather_than_the_host_palette(
    application: QApplication, enabled: bool, expected: str
) -> None:
    """Start, Pause and Reset keep their own colours under a dark host appearance.

    This is the regression test for `PL-DHBX`, in both states, because the
    defect arrived twice. The buttons set no foreground at all, so they took
    Qt's palette `ButtonText`. That is the host appearance's value, not this
    interface's. So the buttons became illegible under macOS Dark, while every
    surface around them stayed in this light theme. The first fix declared
    `:enabled` only. The project owner's screenshots then showed that the
    *unavailable* button was still missing: Start while running, and Pause
    while paused. So this test pins both states.

    The bare button is rendered beside each one, so that the test cannot pass
    vacuously. If the platform plugin ignored the palette, both renderings
    would agree, and the second assertion would fail.
    """

    bare = _drawn(_under_a_dark_host(_transport_button(enabled)), application)
    declared = _transport_button(enabled)
    declared.setStyleSheet(transport_button_stylesheet())
    drawn = _drawn(_under_a_dark_host(declared), application)

    assert max(set(drawn), key=drawn.count) == PANEL.upper()
    assert max(set(bare), key=bare.count) != PANEL.upper()

    # The glyphs are antialiased, so no pixel need match the declared colour
    # exactly. The test therefore finds the declared colour nearest to the
    # label's darkest pixel. It must be the theme's, never the palette's white.
    darkest = min(drawn, key=lambda name: QColor(name).lightness())
    other = MUTED if expected == INK else INK

    assert _channel_distance(darkest, expected) < _channel_distance(darkest, "#FFFFFF")
    assert _channel_distance(darkest, expected) < _channel_distance(darkest, other)


# ------------------------------------------------------------ the selectors


def _arrow_space_colours(selector: SelectorComboBox, application: QApplication) -> list[str]:
    """Return the colour of each pixel in the space a selector's style sheet leaves for its arrow.

    The rows within `PANEL_RADIUS` of the top and bottom edges are left out,
    because the frame's rounded corners reach into the space there.
    """

    selector.addItem("0s")
    selector.setFixedWidth(160)
    selector.show()
    application.processEvents()
    option = QStyleOptionComboBox()
    selector.initStyleOption(option)
    space = selector.style().subControlRect(
        QStyle.ComplexControl.CC_ComboBox, option, QStyle.SubControl.SC_ComboBoxArrow, selector
    )
    image = selector.grab().toImage()

    assert space.width() >= MENU_ARROW_SIZE, space

    return [
        image.pixelColor(x, y).name().upper()
        for x in range(space.left(), space.right() + 1)
        for y in range(PANEL_RADIUS, selector.height() - PANEL_RADIUS)
    ]


@pytest.mark.parametrize("agent_id", [None, *AGENT_COLOR_SCHEMES])
def test_a_selector_draws_its_own_arrow_and_none_of_the_platform_s_button(
    application: QApplication, agent_id: str | None
) -> None:
    """The arrow space holds the selector's fill and its text colour, and nothing else (`PL-9389`).

    Before the fix, the platform style drew its drop-down button there, inside
    the style sheet's rounded frame. Its edge and shadow showed as a bracket,
    in greys that are neither the fill nor the text colour. The selector for a
    reading uses the interface's pair, and the agent selector uses each
    agent's ISO 5360 pair. The fill and text colours are taken from
    `app/theme.py`, not read back from the widget.
    """

    selector = SelectorComboBox()

    if agent_id is None:
        selector.setStyleSheet(selector_stylesheet())
        fill, text = PANEL, INK
    else:
        scheme = AGENT_COLOR_SCHEMES[agent_id]
        selector.setStyleSheet(agent_selector_stylesheet(scheme))
        fill, text = scheme.fill, scheme.foreground

    colours = _arrow_space_colours(selector, application)

    assert set(colours) == {fill.upper(), text.upper()}, sorted(set(colours))


# ------------------------------------------------------------ the notice


def test_the_notice_hides_when_there_is_nothing_to_say(application: QApplication) -> None:
    notice = NoticeLabel()

    assert notice.isHidden()
    assert notice.notice() is None
    assert notice.wordWrap()
    assert notice.font().bold()
    assert WARNING in notice.styleSheet()

    notice.set_notice("Setting refused")

    assert not notice.isHidden()
    assert notice.text() == notice.notice() == "Setting refused"

    notice.set_notice(None)

    assert notice.isHidden()
    assert notice.text() == ""
    assert notice.notice() is None


# ------------------------------------------------------------- the dialog


def _dialog() -> NewCaseDialog:
    snapshot = SimulationController().snapshot()

    return NewCaseDialog(new_case_question(snapshot, "Isoflurane", 0))


def test_the_new_case_dialogs_default_button_is_the_one_that_keeps_the_case(
    application: QApplication,
) -> None:
    """The safe button is the default, and Escape keeps the case.

    The destructive button comes first and is outlined. The safe button comes
    last and is filled.
    """

    dialog = _dialog()
    question = new_case_question(SimulationController().snapshot(), "Isoflurane", 0)
    finished: list[int] = []
    dialog.finished.connect(finished.append)

    assert dialog.isModal()
    assert dialog.discard_button.text() == question.discard_label
    assert dialog.keep_button.text() == question.keep_label
    assert dialog.title_label.text() == question.title
    assert tuple(label.text() for label in dialog.body_labels) == question.body
    assert INK in dialog.title_label.styleSheet() and dialog.title_label.font().bold()
    assert INK in dialog.body_labels[0].styleSheet()
    assert WARNING in dialog.body_labels[1].styleSheet() and dialog.body_labels[1].font().bold()
    assert MUTED in dialog.body_labels[2].styleSheet()
    assert dialog.keep_button.isDefault()
    assert not dialog.discard_button.isDefault()
    assert not dialog.discard_button.autoDefault()

    dialog.open()
    application.processEvents()
    QTest.keyClick(dialog, Qt.Key.Key_Escape)
    application.processEvents()

    assert finished == [int(QDialog.DialogCode.Rejected)]

    by_return = _dialog()
    by_return.open()
    application.processEvents()
    QTest.keyClick(by_return, Qt.Key.Key_Return)
    application.processEvents()

    assert by_return.result() == int(QDialog.DialogCode.Rejected)

    by_discard = _dialog()
    by_discard.open()
    application.processEvents()
    by_discard.discard_button.click()
    application.processEvents()

    assert by_discard.result() == int(QDialog.DialogCode.Accepted)


def test_the_discard_button_is_drawn_before_the_keep_button(application: QApplication) -> None:
    dialog = _dialog()
    dialog.show()
    application.processEvents()

    assert dialog.discard_button.geometry().right() < dialog.keep_button.geometry().left()
    assert dialog.discard_button.geometry().top() == dialog.keep_button.geometry().top()


# ----------------------------------------------------- the marks editor


def _form(editor: MarkEditor, index: int) -> QGridLayout:
    """Return the editor's form at this index in its column: 0 for times, 1 for targets."""

    column = editor.layout()
    item = None if column is None else column.itemAt(index)
    form = None if item is None else item.layout()
    assert isinstance(form, QGridLayout)

    return form


def _form_cells(editor: MarkEditor, form: QGridLayout) -> dict[str, tuple[int, ...]]:
    """Return the cell that each widget of one form spans, keyed by the widget's name.

    A cell is the widget's row and column and the number of rows and columns it
    spans. A widget is named by the editor attribute that holds it. No attribute
    holds a heading or the label that shows a field's name, so each of those is
    named by its text. A widget placed in the grid twice fails the test.
    """

    attributes = {id(value): name for name, value in vars(editor).items()}
    cells: dict[str, tuple[int, ...]] = {}

    for index in range(form.count()):
        item = form.itemAt(index)
        widget = None if item is None else item.widget()
        name = attributes.get(id(widget))

        if name is None:
            assert isinstance(widget, QLabel)
            name = widget.text()

        assert name not in cells, f"{name} is placed in the form twice"
        position = form.getItemPosition(index)
        assert isinstance(position, tuple)
        cells[name] = position

    return cells


def test_the_marks_editor_seats_each_field_in_its_cell(application: QApplication) -> None:
    """Each widget of both forms sits in the cell written here.

    Before `PL-4X5B`, the editor's code set each widget's row and column by
    number. The fields keep the cells transcribed from those numbers, so the
    test does not read them from the grid code that it checks. That code places
    a widget by where it is written in its form, and a widget written in two or
    three neighbouring columns spans them.

    `PL-CHX0` moved the editor from a window into the Bookmarks View, where an
    Area about 150 pixels tall scrolls it. Each Remove button stays directly
    under the list it acts on, as it was in the window. A Remove button above
    its list could be pressed while the list was scrolled out of view, and it
    would then remove a row the reader could not see. Each button's refusal
    is the row directly under it, so that it is on screen next to the button
    that was pressed.
    """

    editor = MarkEditor()

    assert _form_cells(editor, _form(editor, 0)) == {
        TIME_FORM_HEADING: (0, 0, 1, 3),
        INSTANT_FIELD_LABEL: (1, 0, 1, 1),
        "instant_spin": (1, 1, 1, 1),
        "instant_preview": (1, 2, 1, 1),
        MARK_NAME_FIELD_LABEL: (2, 0, 1, 1),
        "time_label_edit": (2, 1, 1, 2),
        "add_time_button": (3, 1, 1, 1),
        "add_time_notice": (4, 0, 1, 3),
        "time_list": (5, 0, 1, 3),
        "remove_time_button": (6, 1, 1, 1),
        "remove_time_notice": (7, 0, 1, 3),
    }
    assert _form_cells(editor, _form(editor, 1)) == {
        TARGET_FORM_HEADING: (0, 0, 1, 3),
        COMPARTMENT_FIELD_LABEL: (1, 0, 1, 1),
        "compartment_combo": (1, 1, 1, 2),
        HEIGHT_FIELD_LABEL: (2, 0, 1, 1),
        "height_spin": (2, 1, 1, 1),
        MARK_NAME_FIELD_LABEL: (3, 0, 1, 1),
        "target_label_edit": (3, 1, 1, 2),
        "add_target_button": (4, 1, 1, 1),
        "add_target_notice": (5, 0, 1, 3),
        "target_list": (6, 0, 1, 3),
        "remove_target_button": (7, 1, 1, 1),
        "remove_target_notice": (8, 0, 1, 3),
    }


def test_the_marks_editor_tabs_through_its_controls_from_top_to_bottom(
    application: QApplication,
) -> None:
    """The Tab key visits the editor's controls in the order a reader reads them.

    A keyboard user fills in the editor with Tab alone. WCAG 2.2 SC 2.4.3, Focus
    Order, asks for a focus order that "preserves meaning and operability". For the
    editor's two forms, that is the order in which they are read, from top to bottom.
    Qt's default Tab order is the order in which widgets were added to the editor.
    In this editor, the grid code adds them. So a grid that added its rows in any
    other order would fail here, even if every cell were correct.
    """

    editor = MarkEditor()
    attributes = {id(value): name for name, value in vars(editor).items()}
    visited: list[str] = []
    widget = editor.nextInFocusChain()

    # Qt's focus chain is a ring, so the walk ends back at the editor itself. The limit
    # on the loop makes a chain that never closes fail the test instead of hanging it.
    for _ in range(len(editor.findChildren(QWidget)) + 1):
        if widget is editor:
            break

        name = attributes.get(id(widget))

        if name is not None and widget.focusPolicy() & Qt.FocusPolicy.TabFocus:
            visited.append(name)

        widget = widget.nextInFocusChain()
    else:
        pytest.fail("the editor's focus chain never came back to the editor")

    assert visited == [
        "instant_spin",
        "time_label_edit",
        "add_time_button",
        "time_list",
        "remove_time_button",
        "compartment_combo",
        "height_spin",
        "target_label_edit",
        "add_target_button",
        "target_list",
        "remove_target_button",
    ]


def test_an_entry_written_into_the_editor_is_the_entry_it_returns_and_is_not_reported(
    application: QApplication,
) -> None:
    """`set_entry` fills every field and selection, and does not report the write as an edit.

    The dashboard copies what a reader entered in one copy of the editor into
    the others with `set_entry` (`PL-CHX0`). If that write emitted
    `entry_edited`, each copy would answer it by writing every other copy in
    turn. The entry is built here, not read from an editor, so the test does
    not check `entry` against itself.
    """

    editor = MarkEditor()
    rows = ("10m – first", "20m – second", "30m – third")
    editor.time_list.addItems(list(rows))
    editor.target_list.addItems(list(rows))
    edited: list[bool] = []
    editor.entry_edited.connect(lambda: edited.append(True))
    entry = MarkEntry(
        instant_s=1800,
        time_name="incision",
        compartment_row=3,
        height_mac=1.25,
        target_name="deep",
        time_row=2,
        target_row=1,
    )

    editor.set_entry(entry)

    assert editor.entry() == entry
    assert editor.instant_preview.text() == "30m"
    assert edited == []

    editor.time_label_edit.setText("closure")

    assert edited == [True]


def test_a_refusal_shows_under_the_button_that_was_pressed_and_clears_the_others(
    application: QApplication,
) -> None:
    """Each refusal shows under one button, and the next one replaces it.

    The four buttons share one refusal at a time, as the editor's single
    notice did before `PL-CHX0`. Each is shown under the button that was
    pressed, so that it is in view of that button.
    """

    editor = MarkEditor()
    notices = {
        MarkButton.ADD_TIME: editor.add_time_notice,
        MarkButton.REMOVE_TIME: editor.remove_time_notice,
        MarkButton.ADD_TARGET: editor.add_target_notice,
        MarkButton.REMOVE_TARGET: editor.remove_target_notice,
    }

    for pressed in MarkButton:
        editor.show_refusal(MarkRefusal(pressed, f"refused by {pressed.value}"))

        assert {button: notice.notice() for button, notice in notices.items()} == {
            button: f"refused by {pressed.value}" if button is pressed else None
            for button in MarkButton
        }

    editor.show_refusal(None)

    assert [notice.isHidden() for notice in notices.values()] == [True] * 4


def test_each_remove_button_is_drawn_below_the_list_it_removes_from(
    application: QApplication,
) -> None:
    """On screen, each Remove button is drawn under its whole list, and each Add button above it.

    The cells above say where the grid places each widget. This test checks the
    drawn geometry, so a list drawn over its button also fails (`PL-CHX0`).
    """

    editor = MarkEditor()
    editor.resize(400, 900)
    editor.show()
    application.processEvents()

    try:
        for add, listing, remove in (
            (editor.add_time_button, editor.time_list, editor.remove_time_button),
            (editor.add_target_button, editor.target_list, editor.remove_target_button),
        ):
            assert add.geometry().bottom() < listing.geometry().top()
            assert listing.geometry().bottom() < remove.geometry().top()
    finally:
        editor.close()


def _wheel_down(widget: QWidget) -> None:
    """Turn the mouse wheel one notch towards the reader over `widget`'s centre.

    The event enters through the window, as a real wheel's does. Qt offers an
    ignored wheel event to the widget's parents only when it came from the
    window system, so an event sent straight to the widget could not show
    whether the page scrolls.
    """

    window = widget.window().windowHandle()
    assert window is not None
    centre = widget.mapTo(widget.window(), widget.rect().center())
    QTest.wheelEvent(window, QPointF(centre), QPoint(0, -120))


def test_a_mouse_wheel_over_an_unfocused_field_scrolls_the_area_and_changes_no_mark(
    application: QApplication,
) -> None:
    """A wheel notch over the instant, the compartment or the height scrolls past it.

    The editor sits in an Area that scrolls. Qt's combo box and spin boxes
    change their value on a wheel event even without focus. A reader scrolling
    past them would then change the instant, the compartment or the height
    without seeing it, in every copy of the editor, and the next Add would mark
    a value the reader did not choose. So each of the three takes the wheel only
    once a click or the keyboard has given it focus, as the agent cost View's
    selectors do (`PL-B396`, `PL-8FSN`). The expected values are the ones
    written into the editor here, not read back from it.
    """

    editor = MarkEditor()
    editor.set_entry(
        MarkEntry(
            instant_s=600,
            time_name="",
            compartment_row=2,
            height_mac=1.0,
            target_name="",
            time_row=-1,
            target_row=-1,
        )
    )
    scroll = QScrollArea()
    scroll.setWidget(editor)
    scroll.setWidgetResizable(True)
    scroll.resize(400, 120)
    scroll.show()
    application.processEvents()
    bar = scroll.verticalScrollBar()
    entered = editor.entry()
    # Showing the window gives its first control focus. The name field takes
    # it here, so that none of the three fields under test has it.
    editor.time_label_edit.setFocus()
    application.processEvents()

    try:
        for field in (editor.instant_spin, editor.compartment_combo, editor.height_spin):
            scroll.ensureWidgetVisible(field)
            application.processEvents()
            before = bar.value()

            assert field.hasFocus() is False

            _wheel_down(field)
            application.processEvents()

            assert (
                editor.instant_spin.value(),
                editor.compartment_combo.currentIndex(),
                editor.height_spin.value(),
            ) == (600, 2, 1.0)
            assert bar.value() > before
            assert field.focusPolicy() == Qt.FocusPolicy.StrongFocus
    finally:
        scroll.close()

    assert editor.entry() == entered


# ------------------------------------------------------------- the window


def test_the_startup_window_is_sized_from_the_screen_and_centred() -> None:
    """The normal geometry: a fraction of the screen, centred, never below the minimum (`PL-005`).

    The window opens maximized over this geometry (`PL-Z4K6`). So these cases
    check what a reader gets back on un-maximizing the window. The launcher
    test in `tests/unit/test_bootstrap.py` checks the state the window opens in.
    """

    assert 0.0 < WINDOW_SCREEN_FRACTION <= 1.0

    assert initial_window_geometry(QRect(0, 0, 2000, 1000), QSize(100, 100), 0.8) == QRect(
        200, 100, 1600, 800
    )
    assert initial_window_geometry(QRect(50, 30, 1000, 600), QSize(100, 100), 0.5) == QRect(
        300, 180, 500, 300
    )
    assert initial_window_geometry(QRect(0, 0, 1000, 600), QSize(100, 100), 1.0) == QRect(
        0, 0, 1000, 600
    )
    # A minimum wider than the fraction wins, on that axis only. The window
    # stays centred on the available area even where it overhangs that area.
    assert initial_window_geometry(QRect(0, 0, 1000, 600), QSize(900, 100), 0.5) == QRect(
        50, 150, 900, 300
    )
    assert initial_window_geometry(QRect(0, 0, 1000, 600), QSize(900, 700), 0.5) == QRect(
        50, -50, 900, 700
    )

    for fraction in (0.0, -0.1, 1.5):
        with pytest.raises(ValueError, match="fraction of the screen"):
            initial_window_geometry(QRect(0, 0, 1000, 600), QSize(100, 100), fraction)


# ------------------------------------------------------------- the label


def test_a_styled_label_carries_its_colour_size_and_wrap(application: QApplication) -> None:
    label = styled_label("Fat", color=MUTED, size_px=14, bold=True, italic=True, wrap=True)

    assert label.text() == "Fat"
    assert label.styleSheet() == f"color: {MUTED};"
    assert label.font().pixelSize() == 14
    assert label.font().bold() and label.font().italic()
    assert label.wordWrap()
    assert not styled_label("Fat", color=INK).wordWrap()
