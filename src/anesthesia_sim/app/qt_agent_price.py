"""Let the reader set, change or remove their price for each agent, on the agent cost View.

`docs/INTERFACE.md` § "A cost at the reader's price" specifies what a price holds
and what is refused (`PL-1P15`). The reader enters the price of one bottle
and the bottle's volume in millilitres of liquid, the price's currency as an
ISO 4217 code, and the date on which the price applied. The date starts at the
day of entry, and the reader can change it to the day the price was quoted,
because a price goes stale from that day. For an agent with a stored price the
date starts at that price's date. It moves to the day of entry when the reader
types another price, volume or currency, and the form says that it moved
(`PL-8FSN`). `app/agent_cost.py` turns the texts into a price and refuses an
entry it cannot read. A refused entry changes nothing, and the form says why.

The form only asks for a change, through `ViewRequests.agent_price`. The
dashboard holds the prices and saves them, so every agent cost View prices
its runs at the same price. Every label and the layout are placeholders until
the visual pass (`ROADMAP.md`, planned-milestone item 33).

`RefusedEntriesDiscard` is the View's offer to discard the entries of the
preferences file that were refused when the file was read (`PL-7KXN`).
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from functools import partial
from typing import Final

from PySide6.QtCore import QDate, QSignalBlocker
from PySide6.QtWidgets import QFormLayout, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget

from anesthesia_sim.app.agent_cost import (
    DISCARD_REFUSED_CONFIRM_LABEL,
    DISCARD_REFUSED_KEEP_LABEL,
    DISCARD_REFUSED_LABEL,
    DISCARD_REFUSED_WARNING,
    entry_date,
    price_from_entry,
)
from anesthesia_sim.app.display_units import DisplayUnit
from anesthesia_sim.app.formatting import format_entered_figure
from anesthesia_sim.app.preferences import AgentPrice, Preferences
from anesthesia_sim.app.qt_widgets import (
    FocusedComboBox,
    FocusedDateEdit,
    declare_interface_colours,
    styled_label,
)
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

__all__ = ["PRICE_ENTRY_HEADING", "PriceEntry", "RefusedEntriesDiscard"]

#: The form's heading, and the labels of its fields and buttons. Every one is
#: a placeholder. The bottle volume's label names its unit, so the reader is less
#: likely to type a volume in litres or as a count of bottles (`docs/INTERFACE.md`
#: § "A cost at the reader's price").
PRICE_ENTRY_HEADING: Final = "Your price per agent"
AGENT_FIELD_LABEL: Final = "Agent"
BOTTLE_PRICE_FIELD_LABEL: Final = "Bottle price"
BOTTLE_VOLUME_FIELD_LABEL: Final = f"Bottle volume ({DisplayUnit.AGENT_LIQUID_MILLILITRES.label})"
CURRENCY_FIELD_LABEL: Final = "Currency code, such as USD"
APPLIES_ON_FIELD_LABEL: Final = "Price date"
SET_PRICE_LABEL: Final = "Set price"
REMOVE_PRICE_LABEL: Final = "Remove price"
#: What the form says while it has moved the date of a stored price to the day
#: of entry, so that the reader sees the date change before they save it. The
#: wording is a placeholder.
DATE_MOVED_TEXT: Final = (
    "Price date set to today, because this is a new price. Change the date if the price was "
    "quoted on another day."
)

#: The date field shows a date as ISO 8601 writes it, as the readout does, so
#: 2008-03-05 is never mistaken for May 3 (`docs/INTERFACE.md` § "A cost at the
#: reader's price").
_DATE_FORMAT: Final = "yyyy-MM-dd"

#: The most letters the currency field takes, the length of an ISO 4217 code.
_CURRENCY_LENGTH: Final = 3


class PriceEntry(QWidget):
    """The form in which the reader sets or removes their price for one agent.

    The agent selector starts on the first displayed run's agent. Choosing an
    agent fills the fields with its stored price, or empties them when it has
    none. The fields are filled again only when the stored price for the
    chosen agent changes, so a frame drawn while the reader types never
    overwrites what they typed. Discarding a refused entry changes no stored
    price, so it leaves the fields as they are.

    The date of a stored price follows what the reader types. While the
    reader has not edited the date, typing another bottle price, bottle volume
    or currency moves the date to the day of entry, and typing the stored ones
    again moves it back (`agent_cost.entry_date`). The date field therefore
    always shows the date that Set price saves. A date that the reader edits
    is kept (`PL-8FSN`).

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
        # What the fields were last filled from. It is the agent, its stored
        # price, and whether a refused entry for the agent is in the file. The
        # last of the three decides only whether Remove is offered.
        self._filled_from: tuple[str, AgentPrice | None, bool] | None = None
        self._agent_chosen = False
        # Whether the reader has edited the date since the fields were filled.
        self._date_edited = False
        self.agent_selector = FocusedComboBox()
        self.agent_selector.setStyleSheet(selector_stylesheet())

        for agent_id, display_name in AVAILABLE_AGENTS:
            self.agent_selector.addItem(display_name, userData=agent_id)

        self.agent_selector.activated.connect(self._handle_agent_pick)
        self.bottle_price_edit = QLineEdit()
        self.bottle_volume_edit = QLineEdit()
        self.currency_edit = QLineEdit()
        self.currency_edit.setMaxLength(_CURRENCY_LENGTH)
        self.applies_on_edit = FocusedDateEdit()
        self.applies_on_edit.setDisplayFormat(_DATE_FORMAT)
        self.applies_on_edit.setCalendarPopup(True)
        self.applies_on_edit.dateChanged.connect(self._handle_date_edit)

        # An entry field paints its fill and its text from the palette, which
        # follows the host's appearance unless the field declares this
        # interface's colours (`PL-R51H`).
        for entry in (
            self.bottle_price_edit,
            self.bottle_volume_edit,
            self.currency_edit,
            self.applies_on_edit,
        ):
            declare_interface_colours(entry)

        # `textEdited` is emitted only for what the reader types, so filling
        # the fields from a stored price never moves the date.
        for typed in (self.bottle_price_edit, self.bottle_volume_edit, self.currency_edit):
            typed.textEdited.connect(self._handle_price_edit)

        self.date_moved = styled_label(
            DATE_MOVED_TEXT, color=MUTED, size_px=METRIC_QUALIFIER_SIZE, wrap=True
        )
        self.date_moved.setHidden(True)
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
        column.addWidget(self.date_moved)
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

        key = _fill_key(preferences, self.agent_id)

        if self._filled_from is not None and key[:2] == self._filled_from[:2]:
            # Only whether a refused entry is in the file can have changed. The
            # stored price is the one the fields were filled from, so what the
            # reader has typed since is left as it is.
            self._filled_from = key
            self._offer_remove()
        else:
            self._fill(key[0])

    def _fill(self, agent_id: str) -> None:
        """Fill the fields with the stored price for `agent_id`, or empty them when it has none."""

        key = _fill_key(self._preferences, agent_id)
        _, price, _ = key
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

        self._date_edited = False
        self._show_date(applies_on, moved=False)
        self._offer_remove()

    def _offer_remove(self) -> None:
        """Offer Remove while the chosen agent has a stored price or a refused entry.

        Removing also discards a refused entry for the agent, which the reader
        may want gone although no price is in force.
        """

        assert self._filled_from is not None, "the fields are filled before Remove is offered"
        _, price, refused = self._filled_from
        self.remove_button.setEnabled(price is not None or refused)

    def _show_date(self, applies_on: date, *, moved: bool) -> None:
        """Show `applies_on` in the date field, and say so when the form moved it there.

        The form's own change of the date is not the reader's edit, so the
        field's signal is blocked while the form sets it.
        """

        with QSignalBlocker(self.applies_on_edit):
            self.applies_on_edit.setDate(QDate(applies_on.year, applies_on.month, applies_on.day))

        self.date_moved.setHidden(not moved)

    def _handle_date_edit(self, _date: QDate) -> None:
        """Keep the date the reader chose, whatever they type in the other fields afterwards."""

        self._date_edited = True
        self.date_moved.setHidden(True)

    def _handle_price_edit(self, _text: str) -> None:
        """Date the replacement of a stored price at the day of entry, as `entry_date` decides."""

        if self._filled_from is None or self._date_edited:
            return

        _, stored, _ = self._filled_from

        if stored is None:
            return

        applies_on = entry_date(
            stored,
            self.bottle_price_edit.text(),
            self.bottle_volume_edit.text(),
            self.currency_edit.text(),
            self._today(),
        )
        self._show_date(applies_on, moved=applies_on != stored.applies_on)

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
            self._show_refusal(f"Price not set: {error}.")
            return

        self._show_refusal(None)
        self._request(price.agent_id, price)

    def _handle_remove(self) -> None:
        """Ask for the chosen agent's price to be removed."""

        self._show_refusal(None)
        self._request(self.agent_id, None)


class RefusedEntriesDiscard(QWidget):
    """The offer to discard the refused entries of the preferences file, and its question.

    A refused entry is written back at every save and named at every launch
    until the reader replaces it. An entry that names no agent can be replaced
    by nothing, so this offer is the reader's way to clear it. The discard
    cannot be undone, so the reader confirms it first. Pressing the offer
    replaces it, in its own place, with a warning and two buttons. Nothing opens
    over the View's values, and the run goes on. The button that keeps the
    entries stands where the offer stood and takes the keyboard focus, so a
    second click or a key press made without reading keeps them.

    Args:
        request: Asks the dashboard to discard every refused entry.
    """

    def __init__(self, request: Callable[[], None]) -> None:
        super().__init__()
        self._request = request
        self.offer_button = QPushButton(DISCARD_REFUSED_LABEL)
        self.offer_button.setStyleSheet(outlined_button_stylesheet())
        self.offer_button.clicked.connect(partial(self._ask, True))
        self.warning = styled_label(
            DISCARD_REFUSED_WARNING, color=WARNING, size_px=METRIC_QUALIFIER_SIZE, wrap=True
        )
        self.discard_button = QPushButton(DISCARD_REFUSED_CONFIRM_LABEL)
        self.discard_button.setStyleSheet(outlined_button_stylesheet())
        self.discard_button.clicked.connect(self._handle_discard)
        self.keep_button = QPushButton(DISCARD_REFUSED_KEEP_LABEL)
        self.keep_button.setStyleSheet(filled_button_stylesheet())
        self.keep_button.clicked.connect(partial(self._ask, False))
        buttons = QHBoxLayout()
        buttons.setSpacing(VIEW_HEADING_SPACING)
        # The button that keeps the entries stands where the offer stood, so a
        # second click made on the offer by mistake keeps them.
        buttons.addWidget(self.offer_button)
        buttons.addWidget(self.keep_button)
        buttons.addWidget(self.discard_button)
        buttons.addStretch(1)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(VIEW_ROW_SPACING)
        column.addWidget(self.warning)
        column.addLayout(buttons)
        self._ask(False)
        self.setHidden(True)

    def show_offer(self, offered: bool) -> None:
        """Show the offer while a refused entry is kept, and withdraw it once none is.

        An open question is left open while the offer still applies, so a frame
        drawn while the reader reads the warning does not close it.
        """

        if not offered:
            self._ask(False)

        self.setHidden(not offered)

    def _ask(self, asking: bool) -> None:
        """Show the question in place of the offer, or the offer in place of the question."""

        self.offer_button.setHidden(asking)

        for part in (self.warning, self.discard_button, self.keep_button):
            part.setHidden(not asking)

        if asking:
            self.keep_button.setFocus()

    def _handle_discard(self) -> None:
        """Close the question and ask for the refused entries to be discarded."""

        self._ask(False)
        self._request()


def _fill_key(preferences: Preferences, agent_id: str) -> tuple[str, AgentPrice | None, bool]:
    """Return what the form's fields and its Remove button show for `agent_id`."""

    refused = any(entry.agent_id == agent_id for entry in preferences.refused_prices)

    return agent_id, preferences.price_for(agent_id), refused
