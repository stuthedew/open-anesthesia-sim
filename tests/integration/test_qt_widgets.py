"""The dashboard's leaf widgets, driven headless against real controllers.

`app/qt_widgets.py` moves Qt widgets to match `dashboard_frame` values and
decides nothing; these tests hold the few things the widgets *do* own -
that a readout value cannot wrap away from its unit (`PL-3355`), that a
slider position is exactly the printed value (`PL-25KS`, D4), that a
snapshot written into a slider never comes back out as a change, that the
new-case dialog's default keeps the case, that the splitter handles are
inert, and where the window opens (`PL-005`). They render under the
`offscreen` platform `tests/conftest.py` selects.
"""

from collections.abc import Iterator

import pytest
from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QFontMetrics
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialog, QGridLayout, QLabel, QScrollArea, QWidget

from anesthesia_sim.app.controller import ControlInput, SimulationController
from anesthesia_sim.app.dashboard_frame import (
    EMPTY_METRIC_QUALIFIER,
    READOUT_ROW_LADDER,
    WIDEST_READOUT_SECONDARY,
    WIDEST_READOUT_VALUE,
    Readout,
    SettingReadout,
    delivered_fraction,
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
    MetricPanel,
    NewCaseDialog,
    NoticeLabel,
    ParameterSlider,
    ReadoutRow,
    inert_splitter,
    initial_window_geometry,
    styled_label,
)
from anesthesia_sim.app.theme import ACCENT, INK, MUTED, WARNING


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
        readouts(snapshot, SUPPORTED_PLAYBACK_RATES[0]),
        widest_value=WIDEST_READOUT_VALUE,
        widest_secondary=WIDEST_READOUT_SECONDARY,
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
    """The narrowest row that seats `columns` panels at the row's own reservation and spacing."""

    return columns * row.panel_minimum_width_px + (columns - 1) * _grid(row).horizontalSpacing()


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
        return float(format_percent(delivered_fraction(value)).rstrip("%"))

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
    assert {grid.columnMinimumWidth(column) for column in range(row.columns())} == {
        row.panel_minimum_width_px
    }


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
        (row.panel_minimum_width_px, 1),
    ):
        _resize(application, row, width)

        assert row.width() == width
        assert row.columns() == columns
        assert columns == readout_columns(width, row.panel_minimum_width_px, spacing)
        assert max(cell[1] for cell in _cells(row)) == columns - 1
        assert _cells(row) == [
            (index // columns, index % columns) for index in range(len(row.panels))
        ]

        for panel in row.panels:
            geometry = panel.geometry()

            assert geometry.width() >= row.panel_minimum_width_px
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
    assert row.columns() == readout_columns(row.width(), row.panel_minimum_width_px, spacing)
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


# ----------------------------------------------------------- the splitter


def test_the_splitter_handles_are_inert(application: QApplication) -> None:
    sections = [QWidget() for _ in range(3)]

    for section in sections:
        section.setMinimumSize(50, 50)

    splitter = inert_splitter(Qt.Orientation.Horizontal, sections)
    splitter.resize(600, 200)
    splitter.show()
    application.processEvents()
    sizes = splitter.sizes()

    assert not splitter.childrenCollapsible()
    assert splitter.count() == 3

    for index in range(1, splitter.count()):
        handle = splitter.handle(index)

        assert not handle.isEnabled()
        assert handle.cursor().shape() == Qt.CursorShape.ArrowCursor

    handle = splitter.handle(1)
    start = handle.rect().center()
    QTest.mousePress(handle, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, start)
    QTest.mouseMove(handle, start + type(start)(120, 0))
    QTest.mouseRelease(
        handle,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
        start + type(start)(120, 0),
    )
    application.processEvents()

    assert splitter.sizes() == sizes


# ------------------------------------------------------------- the window


def test_the_startup_window_is_sized_from_the_screen_and_centred() -> None:
    """A fraction of the available screen, centred there, never below the minimum (`PL-005`)."""

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
