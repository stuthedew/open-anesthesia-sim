"""The parts of one run that a reader may place in an Area, any number of times, in PySide6.

Two of a run's surfaces sit in an Area rather than in the unconditional
region, which is the part of the page that is always on screen. These two
surfaces are the setting controls and the accounting panel (`PL-9LNF`). The
lines that depend on a chart's time window, such as which traces are above
the axis, belong to each chart. `app/views.py` writes them from the chart's
frame (`PL-L59K`). An Area can be split, so two Areas can show the same
surface of the same run. Each class here is therefore built from nothing but
the values it draws. It holds no controller and no run state, and a second
instance of it draws the same values as the first
(`.claude/rules/ui-areas.md`, rules 1 to 3; `PL-TH35` Q8).

`RunView` keeps the run's state. It also keeps a list of the live copies of
each kind, which `keep_until_destroyed` maintains. Its `build_*` methods
return a new instance each time, and its writers write every live instance on
the list. When a reader moves a control in one copy, that copy forwards the
value to the run. The next write then shows the value in force on every copy.

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

__all__ = [
    "AccountingPanel",
    "ParameterControls",
    "emphasised",
    "keep_until_destroyed",
    "panel_frame",
]

#: The theme colour each status emphasis is drawn in. `dashboard_frame` names
#: the role so that it declares no colour; this is where the role meets the
#: palette, and the only place.
_EMPHASIS_COLOR: Final[Mapping[Emphasis, str]] = {
    Emphasis.MUTED: MUTED,
    Emphasis.ACCENT: ACCENT_TEXT,
    Emphasis.WARNING: WARNING,
}


def panel_frame(object_name: str) -> QFrame:
    """A PANEL-coloured, rounded frame scoped by name so its children keep their own colours."""

    frame = QFrame()
    frame.setObjectName(object_name)
    frame.setStyleSheet(panel_stylesheet(object_name))

    return frame


def emphasised(label: QLabel, word: StatusWord) -> None:
    """Write a status word and the colour of its emphasis."""

    label.setText(word.text)
    label.setStyleSheet(foreground_stylesheet(_EMPHASIS_COLOR[word.emphasis]))


def keep_until_destroyed[W: QWidget](copies: list[W], copy: W) -> W:
    """Add a copy that was just built to its list, and drop it when Qt destroys it.

    A writer that loops over `copies` therefore never writes a deleted
    widget. A copy that nobody places stays on the list until it is
    destroyed.

    Args:
        copies: The copies of one kind of surface that Qt has not destroyed,
            oldest first.
        copy: The new copy.

    Returns:
        The same copy, so a builder can return the call.
    """

    copies.append(copy)
    copy.destroyed.connect(lambda: _drop(copies, copy))

    return copy


def _drop[W: QWidget](copies: list[W], copy: W) -> None:
    copies[:] = [kept for kept in copies if kept is not copy]


class ParameterControls(QWidget):
    """The four setting controls in a row, in `dashboard_frame.PARAMETER_CONTROLS` order.

    Each `ParameterSlider` passes its signals up with the control it belongs
    to, so the run can tell which setting was moved without knowing which
    copy moved it.

    Attributes:
        adjustment_started: Emitted when the reader presses any slider's thumb.
        setting_requested: Emitted with the control and the value a slider
            was moved to. The run applies it or refuses it, and the next
            `show_settings` writes the value in force on every copy.
    """

    adjustment_started = Signal()
    setting_requested = Signal(object, float)

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
