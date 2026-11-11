"""The widgets that draw one run's setting controls and its accounting panel, in PySide6.

Four kinds of widget show one run's values in an Area, which a reader can
split, move and close. Two of them are here: `ParameterControls`, the four
setting controls, and `AccountingPanel`, the mass-balance panel. The third,
the compartment schematic, is `RunSchematic` in `app/qt_schematic.py`, beside
the canvas it draws on (`PL-RNYV`). The fourth, the agent cost panel, is
`RunAgentCost` in `app/qt_agent_cost.py` (`PL-B396`).

Each of the four is built from nothing but the values it draws. It holds no
controller and no run state, so two instances given the same values draw the
same thing (`.claude/rules/ui-areas.md`, rules 1 to 3; `PL-TH35` Q8). The
Views in `app/views.py` build one for each displayed run, and write it on
every tick from that run's `RunPresentation` (`app/run_presentation.py`,
`PL-RF2S`). An Area can be split, so two Views can each hold a widget for the
same run. Both are written from the same presentation, so they agree. When a
reader moves a control, the View that holds it asks the dashboard for the
change, and the next tick shows the setting in force in every View.

The lines that depend on a chart's time window, such as which traces are
above the axis, belong to each chart. `app/views.py` writes them from the
chart's frame (`PL-L59K`).

These classes decide nothing and format nothing. Each value they are given is
already text, from `app/dashboard_frame.py`.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Final

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from anesthesia_sim.app.dashboard_frame import (
    ACCOUNTING_UNIT_CAPTION,
    PARAMETER_CONTROLS,
    Accounting,
    Emphasis,
    SettingReadout,
    StatusWord,
)
from anesthesia_sim.app.qt_widgets import ParameterSlider, styled_label
from anesthesia_sim.app.stylesheets import foreground_stylesheet, panel_stylesheet
from anesthesia_sim.app.theme import (
    ACCENT_TEXT,
    ACCOUNTING_STATUS_SIZE,
    INK,
    METRIC_QUALIFIER_SIZE,
    MUTED,
    PANEL_PADDING,
    PARAMETER_SLIDER_SPACING,
    WARNING,
)

__all__ = ["AccountingPanel", "ParameterControls", "emphasised", "panel_frame"]

#: The theme colour each status emphasis is drawn in. `dashboard_frame` names
#: only the role, so that it declares no colour. This table is the one place
#: where each role is given a colour from the palette.
_EMPHASIS_COLOR: Final[Mapping[Emphasis, str]] = {
    Emphasis.MUTED: MUTED,
    Emphasis.ACCENT: ACCENT_TEXT,
    Emphasis.WARNING: WARNING,
}


def panel_frame(object_name: str) -> QFrame:
    """Build a rounded frame in the PANEL colour.

    Its stylesheet is scoped to the frame's object name, so its children keep
    their own colours.
    """

    frame = QFrame()
    frame.setObjectName(object_name)
    frame.setStyleSheet(panel_stylesheet(object_name))

    return frame


def emphasised(label: QLabel, word: StatusWord) -> None:
    """Write a status word and the colour of its emphasis."""

    label.setText(word.text)
    label.setStyleSheet(foreground_stylesheet(_EMPHASIS_COLOR[word.emphasis]))


class ParameterControls(QWidget):
    """The four setting controls in a row, in `dashboard_frame.PARAMETER_CONTROLS` order.

    Each `ParameterSlider` passes its signals up with the control it belongs
    to, so the View that holds the row can ask for a change to that setting.

    Attributes:
        adjustment_started: Emitted when the reader presses any slider's thumb.
        setting_requested: Emitted with the control and the value a slider
            was moved to. The run applies it or refuses it, and the next
            `show_settings` writes the value in force.
        preview_requested: Emitted with the control and the value where a
            held thumb stands, so the charts can preview it (`PL-5B1N`).
        preview_ended: Emitted when a held thumb is released.
    """

    adjustment_started = Signal()
    setting_requested = Signal(object, float)
    preview_requested = Signal(object, float)
    preview_ended = Signal()

    def __init__(self, settings: Sequence[SettingReadout], parent: QWidget | None = None) -> None:
        """Build the four controls from the settings in force.

        Args:
            settings: `dashboard_frame.setting_readouts` for the run, one per
                control in `PARAMETER_CONTROLS` order.
            parent: The Qt parent.

        Raises:
            ValueError: If `settings` does not hold one readout per control in
                `PARAMETER_CONTROLS`.
        """

        super().__init__(parent)

        if len(settings) != len(PARAMETER_CONTROLS):
            raise ValueError(
                f"ParameterControls needs {len(PARAMETER_CONTROLS)} setting readouts, "
                f"one per control in PARAMETER_CONTROLS, got {len(settings)}"
            )

        (
            self._fresh_gas_flow_slider,
            self._delivered_concentration_slider,
            self._alveolar_ventilation_slider,
            self._cardiac_output_slider,
        ) = (ParameterSlider(setting) for setting in settings)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(PARAMETER_SLIDER_SPACING)

        for slider, setting in zip(self.sliders, settings, strict=True):
            layout.addWidget(slider, 1)
            slider.adjustment_started.connect(self.adjustment_started)
            slider.value_changed.connect(
                lambda value, control=setting.control: self.setting_requested.emit(control, value)
            )
            slider.preview_moved.connect(
                lambda value, control=setting.control: self.preview_requested.emit(control, value)
            )
            slider.preview_ended.connect(self.preview_ended)

    @property
    def sliders(self) -> tuple[ParameterSlider, ...]:
        """The four controls in `PARAMETER_CONTROLS` order."""

        return (
            self._fresh_gas_flow_slider,
            self._delivered_concentration_slider,
            self._alveolar_ventilation_slider,
            self._cardiac_output_slider,
        )

    def show_settings(self, settings: Sequence[SettingReadout]) -> None:
        """Write the settings in force into the four controls.

        `ParameterSlider.set_setting` blocks the slider's own signals, so the
        write does not come back as a request.

        Args:
            settings: `dashboard_frame.setting_readouts` for the run.
        """

        for slider, setting in zip(self.sliders, settings, strict=True):
            slider.set_setting(setting)


class AccountingPanel(QFrame):
    """One run's mass-balance panel: its heading, the status, what it means, and the amounts."""

    def __init__(self, shown: Accounting, heading: str, parent: QWidget | None = None) -> None:
        """Build the panel showing one accounting.

        Args:
            shown: The accounting to draw.
            heading: The panel's heading, which names the run while more
                than one is drawn (`dashboard_frame.compared_panel_heading`).
            parent: The Qt parent.
        """

        super().__init__(parent)
        self.setObjectName("accountingPanel")
        self.setStyleSheet(panel_stylesheet("accountingPanel"))
        self._accounting_heading_text = styled_label(heading, color=INK, bold=True)
        self._agent_accounting_status_text = styled_label(
            "", color=ACCENT_TEXT, size_px=ACCOUNTING_STATUS_SIZE, bold=True
        )
        self._agent_accounting_detail_text = styled_label("", color=MUTED, wrap=True)
        self._agent_amounts_text = styled_label("", color=MUTED)

        column = QVBoxLayout(self)
        column.setContentsMargins(PANEL_PADDING, PANEL_PADDING, PANEL_PADDING, PANEL_PADDING)
        column.addWidget(self._accounting_heading_text)
        column.addWidget(self._agent_accounting_status_text)
        column.addWidget(self._agent_accounting_detail_text)
        column.addWidget(
            styled_label(
                ACCOUNTING_UNIT_CAPTION, color=MUTED, size_px=METRIC_QUALIFIER_SIZE, italic=True
            )
        )
        column.addWidget(self._agent_amounts_text)
        self.show_accounting(shown)

    def show_accounting(self, shown: Accounting) -> None:
        """Write the status, its detail and the amounts."""

        emphasised(self._agent_accounting_status_text, shown.status)
        self._agent_accounting_detail_text.setText(shown.detail)
        self._agent_amounts_text.setText(shown.amounts)

    def show_heading(self, heading: str) -> None:
        """Write the panel's heading."""

        self._accounting_heading_text.setText(heading)
