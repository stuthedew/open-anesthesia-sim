"""These tests run the dashboard's leaf widgets without a display, using real controllers.

`app/qt_widgets.py` updates Qt widgets to match `dashboard_frame` values and makes no
decisions of its own. These tests check the few behaviors that belong to the widgets
themselves:

- that a readout's value cannot wrap onto a different line from its unit (`PL-3355`)
- that a slider's position is exactly the printed value (`PL-25KS`, D4)
- that a value written into a slider from a snapshot is never reported back as a change
- that the new-case dialog's default choice keeps the current case
- which cell of the bookmark editor each field sits in, and the order in which Tab visits them
- where the window opens (`PL-005`)

The widgets render on Qt's `offscreen` platform, which `tests/conftest.py` selects.
"""

from collections.abc import Iterator

import pytest
from PySide6.QtCore import QEvent, QRect, QSize, Qt
from PySide6.QtGui import QColor, QFontMetrics, QPalette
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QGridLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QWidget,
)

from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import (
    COMPARTMENT_FIELD_LABEL,
    EMPTY_METRIC_QUALIFIER,
    HEIGHT_FIELD_LABEL,
    INSTANT_FIELD_LABEL,
    MAC_TARGET_HEADING,
    MARK_NAME_FIELD_LABEL,
    READOUT_RESERVATIONS,
    READOUT_ROW_LADDER,
    TIME_BOOKMARK_HEADING,
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
    BookmarkDialog,
    FlowLayout,
    MetricPanel,
    NewCaseDialog,
    NoticeLabel,
    ParameterSlider,
    ReadoutRow,
    initial_window_geometry,
    styled_label,
)
from anesthesia_sim.app.stylesheets import transport_button_stylesheet
from anesthesia_sim.app.theme import ACCENT, INK, MUTED, PANEL, WARNING
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
    """Where each panel sits, in panel order; every panel occupies exactly one cell."""

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
    """The narrowest row that seats `columns` panels at their own reservations and spacing."""

    return row.width_for(columns)


def _resize(application: QApplication, row: ReadoutRow, width: int) -> None:
    row.resize(width, 400)
    application.processEvents()


def _one_line_height(like: QLabel) -> int:
    """The height of a one-line label in `like`'s font, from a label that cannot wrap."""

    reference = QLabel("0s")
    reference.setFont(like.font())

    return reference.sizeHint().height()


def _printed_value(setting: SettingReadout, value: float) -> float:
    """The number the readout beside the slider prints for `value`, read back."""

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
    """The row is read across, so no panel may be shaped unlike its neighbours (`PL-8M05`).

    Every panel draws all four lines - a spacer where it has no gloss or
    no second unit - at the sizes that rank them, and the widest rung of
    the ladder seats every readout side by side in equal columns, so an
    eighth panel cannot silently split the row.
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
    """The row steps down the ladder at the width its own reservation sets (`PL-8M05`).

    At the narrowest width that seats seven panels of the measured
    reservation with the grid's spacing between them, the row is seven
    across; one pixel narrower it is four; and at every step no panel is
    laid outside the row. The widths are read from the row rather than
    written here, so the test holds on any font and at any display scale.
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
    """The row's minimum is one column's, so a container can narrow it and it steps down.

    A row reporting its seven-column minimum could never be narrowed by a
    scroll area, which widens its page to the widest minimum and scrolls;
    the readout row would then never reflow and the page would overhang
    every window narrower than seven panels. Every panel keeps its own
    reservation, so no value wraps at the narrower count (`PL-3355`).
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

    The other row is hidden, and deleting the readings it returns leaves each
    panel with its own five labels again, as dropping a branch does.
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
    """Give one button the palette a dark host appearance supplies.

    Set on the widget rather than the application so it cannot leak into the
    other tests sharing the module-scoped `QApplication`. The values stand in
    for what macOS supplies in Dark appearance, where `PL-DHBX` was reported:
    a near-white `ButtonText` over a dark `Button`.
    """

    palette = QPalette(button.palette())
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#323232"))
    button.setPalette(palette)

    return button


def _channel_distance(one: str, other: str) -> int:
    """The largest per-channel difference between two colours, 0-255."""

    first, second = QColor(one), QColor(other)

    return max(
        abs(first.red() - second.red()),
        abs(first.green() - second.green()),
        abs(first.blue() - second.blue()),
    )


def _transport_button(enabled: bool) -> QPushButton:
    """One transport button in the state under test."""

    button = QPushButton("Pause")
    button.setEnabled(enabled)

    return button


def _drawn(button: QPushButton, application: QApplication) -> list[str]:
    """Every pixel of a rendered button, as upper-case hex names."""

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

    The regression test for `PL-DHBX`, in both states, because the defect
    arrived twice. The buttons set no foreground at all, so they took Qt's
    palette `ButtonText` - the host appearance's value, not this interface's -
    and went illegible under macOS Dark while every surface around them stayed
    this light theme's. The first fix declared `:enabled` only, and the project
    owner's screenshots then showed the *unavailable* button still absent: Start
    while running, Pause while paused. So both states are pinned here.

    The bare button is rendered beside each so the test cannot pass vacuously:
    if the platform plugin ignored the palette, both halves would agree and the
    second assertion would fail.
    """

    bare = _drawn(_under_a_dark_host(_transport_button(enabled)), application)
    declared = _transport_button(enabled)
    declared.setStyleSheet(transport_button_stylesheet())
    drawn = _drawn(_under_a_dark_host(declared), application)

    assert max(set(drawn), key=drawn.count) == PANEL.upper()
    assert max(set(bare), key=bare.count) != PANEL.upper()

    # No pixel need land exactly on the declared colour - the glyphs are
    # antialiased - so the label is identified by which declared colour its
    # darkest pixel is nearest: the theme's, never the palette's white.
    darkest = min(drawn, key=lambda name: QColor(name).lightness())
    other = MUTED if expected == INK else INK

    assert _channel_distance(darkest, expected) < _channel_distance(darkest, "#FFFFFF")
    assert _channel_distance(darkest, expected) < _channel_distance(darkest, other)


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
    """Destructive first and outlined; safe last, filled and the default; Escape keeps."""

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


# ----------------------------------------------------- the bookmark editor


def _form(dialog: BookmarkDialog, index: int) -> QGridLayout:
    """The editor's form at this place in its column: 0 for times, 1 for targets."""

    column = dialog.layout()
    item = None if column is None else column.itemAt(index)
    form = None if item is None else item.layout()
    assert isinstance(form, QGridLayout)

    return form


def _form_cells(dialog: BookmarkDialog, form: QGridLayout) -> dict[str, tuple[int, ...]]:
    """Return the cell that each widget of one form spans, keyed by the widget's name.

    A cell is the widget's row and column and the number of rows and columns it
    spans. A widget is named by the dialog attribute that holds it. No attribute
    holds a heading or the label that shows a field's name, so each of those is
    named by its text. A widget placed in the grid twice fails the test.
    """

    attributes = {id(value): name for name, value in vars(dialog).items()}
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


def test_the_bookmark_editor_seats_each_field_in_the_cell_it_always_had(
    application: QApplication,
) -> None:
    """Each widget of both forms keeps the cell that the editor gave it by number.

    Before `PL-4X5B`, the editor's code set each widget's row and column by
    number. The expected cells are transcribed from those numbers, so the test
    does not read them from the grid code that it checks. That code now places a
    widget by where it is written in its form, and a widget written in two or
    three neighbouring columns spans them.
    """

    dialog = BookmarkDialog()

    assert _form_cells(dialog, _form(dialog, 0)) == {
        TIME_BOOKMARK_HEADING: (0, 0, 1, 3),
        INSTANT_FIELD_LABEL: (1, 0, 1, 1),
        "instant_spin": (1, 1, 1, 1),
        "instant_preview": (1, 2, 1, 1),
        MARK_NAME_FIELD_LABEL: (2, 0, 1, 1),
        "time_label_edit": (2, 1, 1, 2),
        "add_time_button": (3, 1, 1, 1),
        "time_list": (4, 0, 1, 3),
        "remove_time_button": (5, 1, 1, 1),
    }
    assert _form_cells(dialog, _form(dialog, 1)) == {
        MAC_TARGET_HEADING: (0, 0, 1, 3),
        COMPARTMENT_FIELD_LABEL: (1, 0, 1, 1),
        "compartment_combo": (1, 1, 1, 2),
        HEIGHT_FIELD_LABEL: (2, 0, 1, 1),
        "height_spin": (2, 1, 1, 1),
        MARK_NAME_FIELD_LABEL: (3, 0, 1, 1),
        "target_label_edit": (3, 1, 1, 2),
        "add_target_button": (4, 1, 1, 1),
        "target_list": (5, 0, 1, 3),
        "remove_target_button": (6, 1, 1, 1),
    }


def test_the_bookmark_editor_tabs_through_its_controls_from_top_to_bottom(
    application: QApplication,
) -> None:
    """The Tab key visits the editor's controls in the order a reader reads them.

    A keyboard user fills in the editor with Tab alone. WCAG 2.2 SC 2.4.3, Focus
    Order, asks for a focus order that "preserves meaning and operability". For the
    editor's two forms, that is the order in which they are read, from top to bottom.
    Qt's default Tab order is the order in which widgets were added to the dialog.
    In this dialog, the grid code adds them. So a grid that added its rows in any
    other order would fail here, even if every cell were correct.
    """

    dialog = BookmarkDialog()
    attributes = {id(value): name for name, value in vars(dialog).items()}
    dialog.show()
    application.processEvents()
    first = application.focusWidget()
    visited: list[str] = []
    widget = first

    # Qt's focus chain is a ring, so the walk ends back at the first widget. The limit
    # on the loop makes a chain that never closes fail the test instead of hanging it.
    for _ in range(len(dialog.findChildren(QWidget)) + 1):
        assert widget is not None
        name = attributes.get(id(widget))

        if name is not None and widget.focusPolicy() & Qt.FocusPolicy.TabFocus:
            visited.append(name)

        widget = widget.nextInFocusChain()

        if widget is first:
            break
    else:
        pytest.fail("the editor's focus chain never came back to its first control")

    dialog.close()

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
        "close_button",
    ]


# ------------------------------------------------------------- the window


def test_the_startup_window_is_sized_from_the_screen_and_centred() -> None:
    """The normal geometry: a fraction of the screen, centred, never below the minimum (`PL-005`).

    The window opens maximized over it (`PL-Z4K6`), so these are the cases for
    what a reader gets back on un-maximizing; the launcher test in
    `tests/unit/test_bootstrap.py` holds the state the window opens in.
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
    # A minimum wider than the fraction wins on that axis alone, and the
    # window stays centred on the available area even where it overhangs.
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
