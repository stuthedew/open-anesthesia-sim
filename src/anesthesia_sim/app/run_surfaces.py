"""The parts of one run that a reader may place in an Area, any number of times, in PySide6.

Four of a run's surfaces will sit in an Area rather than in the
unconditional region: the setting controls, the accounting panel, the line
naming the traces above the plot, and the line stating what the F_A/F_I plot
shows (`PL-9LNF`). An Area can be split, so two Areas can show the same
surface of the same run. Each class here is therefore built from nothing but
the values it draws. It holds no controller and no run state, and a second
instance of it draws the same values as the first
(`.claude/rules/ui-areas.md`, rules 1 to 3; `PL-TH35` Q8).

`RunView` keeps the run's state and a `LiveCopies` list of each kind. Its
`build_*` methods return a new instance each time, and its writers write
every live instance on the list. A control moved in one copy forwards its
value to the run, and the next write shows the value in force on every copy.

These classes decide nothing and format nothing: each value they are given
is already text, from `app/dashboard_frame.py`.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from typing import Final

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from anesthesia_sim.app.dashboard_frame import (
    ACCOUNTING_UNIT_CAPTION,
    Accounting,
    Emphasis,
    SettingReadout,
    StatusWord,
)
from anesthesia_sim.app.qt_widgets import ParameterSlider, style_label, styled_label
from anesthesia_sim.app.stylesheets import foreground_stylesheet, panel_stylesheet
from anesthesia_sim.app.theme import (
    ACCENT_TEXT,
    ACCOUNTING_STATUS_SIZE,
    INK,
    METRIC_QUALIFIER_SIZE,
    MUTED,
    PANEL_PADDING,
    WARNING,
)

__all__ = [
    "AccountingPanel",
    "LiveCopies",
    "OffScaleLine",
    "ParameterControls",
    "WashInStateLine",
    "emphasised",
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


class LiveCopies[W: QWidget]:
    """The copies of one kind of surface that Qt has not yet destroyed, oldest first.

    A copy is added when it is built and dropped when Qt destroys it, so a
    writer that loops over this list never writes a deleted widget. A copy
    that nobody places stays on the list until it is destroyed.
    """

    def __init__(self) -> None:
        self._copies: list[W] = []

    def add(self, copy: W) -> W:
        """Add a copy that was just built, and return it.

        Args:
            copy: The new copy.

        Returns:
            The same copy, so a builder can return the call.
        """

        self._copies.append(copy)
        copy.destroyed.connect(lambda: self._drop(copy))

        return copy

    def _drop(self, copy: W) -> None:
        self._copies = [kept for kept in self._copies if kept is not copy]

    def __iter__(self) -> Iterator[W]:
        return iter(tuple(self._copies))

    def __len__(self) -> int:
        return len(self._copies)

    def __getitem__(self, index: int) -> W:
        return self._copies[index]


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
            ValueError: If `settings` does not hold exactly four readouts.
        """

        super().__init__(parent)

        if len(settings) != 4:
            raise ValueError(f"ParameterControls needs four setting readouts, got {len(settings)}")

        (
            self._fresh_gas_flow_slider,
            self._delivered_concentration_slider,
            self._alveolar_ventilation_slider,
            self._cardiac_output_slider,
        ) = (ParameterSlider(setting) for setting in settings)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

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


class OffScaleLine(QLabel):
    """The line naming a run's traces that are above the top of the plot, hidden while none is."""

    def __init__(self, text: str | None, parent: QWidget | None = None) -> None:
        """Build the line.

        Args:
            text: The line to show, or None while no trace is off the plot.
            parent: The Qt parent.
        """

        super().__init__(parent)
        style_label(self, color=WARNING, size_px=METRIC_QUALIFIER_SIZE, italic=True, wrap=True)
        self.show_text(text)

    def show_text(self, text: str | None) -> None:
        """Write the line, or hide it while `text` is None."""

        self.setText(text or "")
        self.setHidden(text is None)


class WashInStateLine(QLabel):
    """The line stating what a run's F_A/F_I plot is showing."""

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        """Build the line.

        Args:
            text: The line to show.
            parent: The Qt parent.
        """

        super().__init__(text, parent)
        style_label(self, color=MUTED, size_px=METRIC_QUALIFIER_SIZE)

    def show_text(self, text: str) -> None:
        """Write the line."""

        self.setText(text)
