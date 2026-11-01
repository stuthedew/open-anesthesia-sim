"""Draw one run's agent cost panel: the agent it has delivered, in the unit the reader chose.

`app/agent_cost.py` computes every text this module shows (`PL-B396`). This
module only lays the texts out and shows the ones for the reader's unit. The
amount is printed large, with its unit on it, and the caption under it says
what the unit measures. Every visual choice here, from the sizes to the order
of the lines, is a placeholder until the visual pass (`ROADMAP.md`,
planned-milestone item 33).
"""

from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from anesthesia_sim.app.agent_cost import DeliveredShown
from anesthesia_sim.app.compartment_schematic import instant_line
from anesthesia_sim.app.formatting import AgentAmountUnit
from anesthesia_sim.app.preferences import DEFAULT_AGENT_COST_VIEW_UNIT
from anesthesia_sim.app.qt_widgets import styled_label
from anesthesia_sim.app.theme import (
    INK,
    METRIC_NAME_SIZE,
    METRIC_QUALIFIER_SIZE,
    METRIC_VALUE_SIZE,
    MUTED,
    VIEW_ROW_SPACING,
)

__all__ = ["RunAgentCost"]


class RunAgentCost(QWidget):
    """One copy of a run's agent cost panel: its instant, the delivered amount and its caption.

    The panel is one of the run's surfaces, the parts of a run that a reader
    may place in an Area. `RunView.build_agent_cost` builds each copy. The run
    writes every live copy at the same moments as its readouts, from the same
    snapshot. It withholds the copies whenever it withholds the readouts. It
    labels them with the run's name whenever it labels its own panels
    (`app/run_surfaces.py`, `PL-9LNF`). The View that holds the copy sets its
    unit from the reader's preference on every frame, so every copy shows the
    same unit.

    Args:
        shown: What the copies built earlier already show.
        name: The run's name while runs are compared, or None.
        parent: The run's view, so that the copy is deleted with its run.
    """

    def __init__(
        self, shown: DeliveredShown, name: str | None, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.name_text = styled_label("", color=INK, bold=True)
        self.label_text = styled_label("", color=INK, size_px=METRIC_NAME_SIZE)
        self.amount_text = styled_label("", color=INK, size_px=METRIC_VALUE_SIZE, bold=True)
        self.caption_text = styled_label("", color=MUTED, size_px=METRIC_QUALIFIER_SIZE, wrap=True)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(VIEW_ROW_SPACING)
        column.addWidget(self.name_text)
        column.addWidget(self.label_text)
        column.addWidget(self.amount_text)
        column.addWidget(self.caption_text)
        self._name = name
        self._unit = DEFAULT_AGENT_COST_VIEW_UNIT
        self._shown = shown
        self.show_delivered(shown)

    @property
    def unit(self) -> AgentAmountUnit:
        """The unit the amount is shown in."""

        return self._unit

    def show_name(self, name: str | None) -> None:
        """Name the panel while runs are compared, or leave it unnamed when `name` is None."""

        self._name = name
        self.name_text.setText(instant_line(self._shown.instant, name))

    def show_unit(self, unit: AgentAmountUnit) -> None:
        """Show the amount and its caption in `unit`.

        Raises:
            ValueError: If `unit` is not one the View offers.
        """

        self._write(self._shown, unit)

    def show_delivered(self, shown: DeliveredShown) -> None:
        """Show `shown` in the panel's unit."""

        self._write(shown, self._unit)

    def _write(self, shown: DeliveredShown, unit: AgentAmountUnit) -> None:
        """Write every line from `shown` in `unit`, checking the unit before any line changes."""

        amount = shown.amount_in(unit)
        caption = shown.caption_in(unit)
        self._shown = shown
        self._unit = unit
        self.name_text.setText(instant_line(shown.instant, self._name))
        self.label_text.setText(shown.label)
        self.amount_text.setText(amount)
        self.caption_text.setText(caption)
