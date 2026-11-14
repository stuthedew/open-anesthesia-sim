"""Draw one run's agent cost panel: the agent it has delivered, and its cost at the reader's price.

`app/agent_cost.py` computes every text this module shows (`PL-B396`,
`PL-1P15`). This module only lays the texts out and shows the ones for the
reader's unit and prices. The amount is printed large, with its unit on it,
and the caption under it says what the unit measures. The cost readout
follows. It shows the figures that were multiplied to give the cost, and where
the price came from. Every visual choice here, from the sizes to the order of
the lines, is a placeholder until the visual pass (`ROADMAP.md`,
planned-milestone item 33).
"""

from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from anesthesia_sim.app.agent_cost import DeliveredShown, cost_shown
from anesthesia_sim.app.compartment_schematic import instant_line
from anesthesia_sim.app.formatting import AgentAmountUnit
from anesthesia_sim.app.preferences import Preferences
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
    """One run's agent cost panel, showing its instant, the delivered amount and its cost.

    The agent cost View builds one for each displayed run, and writes it on
    every tick from that run's `RunPresentation` and the reader's preferences
    (`app/views.py`, `app/run_presentation.py`). The presentation holds the
    delivered agent, the run's name and the run's readouts together. So the
    panel shows the same step as the readouts, and it is withheld whenever
    they are (`PL-B396`, `PL-RF2S`). Every agent cost View is given the same
    preferences, so every panel shows the same unit, and prices the run at
    the reader's price for the run's own agent. Each write recomputes the
    cost from the delivered agent and the preferences that the panel holds
    at that moment. So no cost from an earlier instant, agent or price stays
    on screen.

    Args:
        shown: The delivered agent to show first.
        name: The run's name while runs are compared, or None.
    """

    def __init__(self, shown: DeliveredShown, name: str | None) -> None:
        super().__init__()
        self.name_text = styled_label("", color=INK, bold=True)
        self.label_text = styled_label("", color=INK, size_px=METRIC_NAME_SIZE)
        self.amount_text = styled_label("", color=INK, size_px=METRIC_VALUE_SIZE, bold=True)
        self.caption_text = styled_label("", color=MUTED, size_px=METRIC_QUALIFIER_SIZE, wrap=True)
        self.cost_label_text = styled_label("", color=INK, size_px=METRIC_NAME_SIZE, wrap=True)
        self.cost_text = styled_label(
            "", color=INK, size_px=METRIC_VALUE_SIZE, bold=True, wrap=True
        )
        self.working_text = styled_label("", color=INK, size_px=METRIC_QUALIFIER_SIZE, wrap=True)
        self.price_text = styled_label("", color=MUTED, size_px=METRIC_QUALIFIER_SIZE, wrap=True)
        self.rounded_text = styled_label("", color=MUTED, size_px=METRIC_QUALIFIER_SIZE, wrap=True)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(VIEW_ROW_SPACING)

        for line in (
            self.name_text,
            self.label_text,
            self.amount_text,
            self.caption_text,
            self.cost_label_text,
            self.cost_text,
            self.working_text,
            self.price_text,
            self.rounded_text,
        ):
            column.addWidget(line)

        self._name = name
        self._preferences = Preferences()
        self._shown = shown
        self.show_delivered(shown)

    @property
    def unit(self) -> AgentAmountUnit:
        """The unit the amount is shown in."""

        return self._preferences.agent_cost_unit

    def show_name(self, name: str | None) -> None:
        """Name the panel while runs are compared, or leave it unnamed when `name` is None."""

        self._name = name
        self.name_text.setText(instant_line(self._shown.instant, name))

    def show_preferences(self, preferences: Preferences) -> None:
        """Show the amount in the unit `preferences` hold, and the cost at the run's agent's price.

        Raises:
            ValueError: If the unit is not one the View offers.
        """

        self._write(self._shown, preferences)

    def show_delivered(self, shown: DeliveredShown) -> None:
        """Show `shown` in the panel's unit, with its cost at the prices the panel holds."""

        self._write(shown, self._preferences)

    def _write(self, shown: DeliveredShown, preferences: Preferences) -> None:
        """Write every line from `shown` and `preferences`, computing all before writing any."""

        unit = preferences.agent_cost_unit
        amount = shown.amount_in(unit)
        caption = shown.caption_in(unit)
        cost = cost_shown(shown, preferences)
        self._shown = shown
        self._preferences = preferences
        self.name_text.setText(instant_line(shown.instant, self._name))
        self.label_text.setText(shown.label)
        self.amount_text.setText(amount)
        self.caption_text.setText(caption)
        self.cost_label_text.setText(cost.label)
        self.cost_text.setText(cost.cost)

        for line, text in (
            (self.working_text, cost.working),
            (self.price_text, cost.price),
            (self.rounded_text, cost.rounded),
        ):
            line.setText(text)
            line.setHidden(not text)
