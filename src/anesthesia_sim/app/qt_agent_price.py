"""Let the reader set, change or remove their price for each agent, on the agent cost View.

`docs/MODEL.md` § "A cost at the reader's price" specifies what a price holds
and what is refused (`PL-1P15`). The reader enters the price of one bottle
and the bottle's volume in millilitres of liquid, its currency as an ISO 4217
code, and the date on which the price applied. The date starts at the day of
entry, for the reader to change, because a price goes stale from the day it
was quoted. `app/agent_cost.py` turns the texts into a price and refuses an
entry it cannot read. A refused entry changes nothing, and the form says why.

The form only asks for a change, through `ViewRequests.agent_price`. The
dashboard holds the prices and saves them, so every agent cost View prices
its runs at the same price. Every label and the layout are placeholders until
the visual pass (`ROADMAP.md`, planned-milestone item 33).
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import Final

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from anesthesia_sim.app.agent_cost import price_from_entry
from anesthesia_sim.app.display_units import DisplayUnit
from anesthesia_sim.app.formatting import format_entered_figure
from anesthesia_sim.app.preferences import AgentPrice, Preferences
from anesthesia_sim.app.qt_widgets import FocusedComboBox, styled_label
from anesthesia_sim.app.run_view import AVAILABLE_AGENTS
from anesthesia_sim.app.stylesheets import (
    filled_button_stylesheet,
    outlined_button_stylesheet,
    selector_stylesheet,
)
from anesthesia_sim.app.theme import (
    INK,
    METRIC_QUALIFIER_SIZE,
    MUTED,
    VIEW_HEADING_SPACING,
    VIEW_ROW_SPACING,
    WARNING,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError

__all__ = ["PRICE_ENTRY_HEADING", "PriceEntry"]

#: The form's heading, and the labels of its fields and buttons. Every one is
#: a placeholder. The bottle volume's label names its unit, so a volume typed
#: in litres or as a count of bottles is less likely (`docs/MODEL.md`
#: § "A cost at the reader's price").
PRICE_ENTRY_HEADING: Final = "Your price for an agent. The project supplies none."
AGENT_FIELD_LABEL: Final = "Agent"
BOTTLE_PRICE_FIELD_LABEL: Final = "Price of one bottle"
BOTTLE_VOLUME_FIELD_LABEL: Final = (
    f"Volume of that bottle, in {DisplayUnit.AGENT_LIQUID_MILLILITRES.label}"
)
CURRENCY_FIELD_LABEL: Final = "Currency, as its ISO 4217 code, such as USD"
APPLIES_ON_FIELD_LABEL: Final = "Date the price applied"
SET_PRICE_LABEL: Final = "Set price"
REMOVE_PRICE_LABEL: Final = "Remove price"

#: The date field shows a date as ISO 8601 writes it, as the readout does, so
#: 2008-03-05 never reads as May 3 (`docs/MODEL.md` § "A cost at the reader's
#: price").
_DATE_FORMAT: Final = "yyyy-MM-dd"

#: The most letters the currency field takes, the length of an ISO 4217 code.
_CURRENCY_LENGTH: Final = 3


class PriceEntry(QWidget):
    """The form in which the reader sets or removes their price for one agent.

    The agent selector starts on the first displayed run's agent. Choosing an
    agent fills the fields with its stored price, or empties them when it has
    none. The fields are filled again only when the stored price for the
    chosen agent changes, so a frame drawn while the reader types never
    overwrites what they typed.

    Args:
        request: Asks the dashboard to set the price for an agent, or to
            remove it when the price is None.
        today: Returns the day of entry, which the date field starts at.
    """

    def __init__(
        self,
        request: Callable[[str, AgentPrice | None], None],
        today: Callable[[], date] = date.today,
    ) -> None:
        super().__init__()
        self._request = request
        self._today = today
        self._preferences = Preferences()
        # What the fields were last filled from: the agent, its stored price,
        # and whether a refused entry for it is in the file. The last decides
        # whether Remove is offered, so a change to it refills too.
        self._filled_from: tuple[str, AgentPrice | None, bool] | None = None
        self._agent_chosen = False
        self.agent_selector = FocusedComboBox()
        self.agent_selector.setStyleSheet(selector_stylesheet())

        for agent_id, display_name in AVAILABLE_AGENTS:
            self.agent_selector.addItem(display_name, userData=agent_id)

        self.agent_selector.activated.connect(self._handle_agent_pick)
        self.bottle_price_edit = QLineEdit()
        self.bottle_volume_edit = QLineEdit()
        self.currency_edit = QLineEdit()
        self.currency_edit.setMaxLength(_CURRENCY_LENGTH)
        self.applies_on_edit = QDateEdit()
        self.applies_on_edit.setDisplayFormat(_DATE_FORMAT)
        self.applies_on_edit.setCalendarPopup(True)
        self.set_button = QPushButton(SET_PRICE_LABEL)
        self.set_button.setStyleSheet(filled_button_stylesheet())
        self.set_button.clicked.connect(self._handle_set)
        self.remove_button = QPushButton(REMOVE_PRICE_LABEL)
        self.remove_button.setStyleSheet(outlined_button_stylesheet())
        self.remove_button.clicked.connect(self._handle_remove)
        self.refusal = styled_label("", color=WARNING, size_px=METRIC_QUALIFIER_SIZE, wrap=True)
        self.refusal.setHidden(True)

        form = QFormLayout()
        form.setSpacing(VIEW_ROW_SPACING)

        for label, field in (
            (AGENT_FIELD_LABEL, self.agent_selector),
            (BOTTLE_PRICE_FIELD_LABEL, self.bottle_price_edit),
            (BOTTLE_VOLUME_FIELD_LABEL, self.bottle_volume_edit),
            (CURRENCY_FIELD_LABEL, self.currency_edit),
            (APPLIES_ON_FIELD_LABEL, self.applies_on_edit),
        ):
            form.addRow(styled_label(label, color=MUTED, wrap=True), field)

        buttons = QHBoxLayout()
        buttons.setSpacing(VIEW_HEADING_SPACING)
        buttons.addWidget(self.set_button)
        buttons.addWidget(self.remove_button)
        buttons.addStretch(1)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(VIEW_ROW_SPACING)
        column.addWidget(styled_label(PRICE_ENTRY_HEADING, color=INK, bold=True, wrap=True))
        column.addLayout(form)
        column.addLayout(buttons)
        column.addWidget(self.refusal)
        self._fill(self.agent_id)

    @property
    def agent_id(self) -> str:
        """The agent whose price the form shows.

        Raises:
            TypeError: If the selector holds something other than an agent
                id, which would mean the form was built wrongly.
        """

        agent_id = self.agent_selector.currentData()

        if not isinstance(agent_id, str):
            raise TypeError(f"the agent selector holds an agent id, not {agent_id!r}")

        return agent_id

    def show_prices(self, preferences: Preferences, first_run_agent_id: str | None) -> None:
        """Hold the prices in force, and fill the fields if the chosen agent's price changed.

        Args:
            preferences: The reader's preferences on this frame.
            first_run_agent_id: The first displayed run's agent, which the
                selector starts on, or None while its values are withheld.
        """

        self._preferences = preferences

        if not self._agent_chosen and first_run_agent_id is not None:
            self.agent_selector.setCurrentIndex(self.agent_selector.findData(first_run_agent_id))
            self._agent_chosen = True

        agent_id = self.agent_id

        if self._filled_from != _fill_key(preferences, agent_id):
            self._fill(agent_id)

    def _fill(self, agent_id: str) -> None:
        """Fill the fields with the stored price for `agent_id`, or empty them when it has none."""

        key = _fill_key(self._preferences, agent_id)
        _, price, refused = key
        self._filled_from = key

        if price is None:
            self.bottle_price_edit.clear()
            self.bottle_volume_edit.clear()
            self.currency_edit.clear()
            applies_on = self._today()
        else:
            self.bottle_price_edit.setText(format_entered_figure(price.bottle_price))
            self.bottle_volume_edit.setText(format_entered_figure(price.bottle_volume_ml))
            self.currency_edit.setText(price.currency)
            applies_on = price.applies_on

        self.applies_on_edit.setDate(QDate(applies_on.year, applies_on.month, applies_on.day))
        # Removing also discards a refused entry for the agent, which the
        # reader may want gone although no price is in force.
        self.remove_button.setEnabled(price is not None or refused)

    def _show_refusal(self, reason: str | None) -> None:
        self.refusal.setText(reason or "")
        self.refusal.setHidden(reason is None)

    def _handle_agent_pick(self, _index: int) -> None:
        """Show the chosen agent's stored price, and drop any refusal shown for another agent."""

        self._agent_chosen = True
        self._show_refusal(None)
        self._fill(self.agent_id)

    def _handle_set(self) -> None:
        """Ask for the price the fields hold, or say why it is refused and change nothing."""

        entered = self.applies_on_edit.date()

        try:
            price = price_from_entry(
                self.agent_id,
                self.bottle_price_edit.text(),
                self.bottle_volume_edit.text(),
                self.currency_edit.text(),
                date(entered.year(), entered.month(), entered.day()),
            )
        except SimulationConfigurationError as error:
            self._show_refusal(f"Your price was not set, so nothing changed: {error}.")
            return

        self._show_refusal(None)
        self._request(price.agent_id, price)

    def _handle_remove(self) -> None:
        """Ask for the chosen agent's price to be removed."""

        self._show_refusal(None)
        self._request(self.agent_id, None)


def _fill_key(preferences: Preferences, agent_id: str) -> tuple[str, AgentPrice | None, bool]:
    """Return what the form's fields and its Remove button show for `agent_id`."""

    refused = any(entry.agent_id == agent_id for entry in preferences.refused_prices)

    return agent_id, preferences.price_for(agent_id), refused
