"""Read and write the file that holds the reader's agent prices, units and axis top.

A preference belongs to the reader, not to a layout. So preferences are kept
in `preferences.json`, beside the Workspaces' `workspaces.json` in the same
directory but never inside it (`PL-MQHN`, `PL-93B3`). This module is the only
code that reads and writes the file. Nothing in it imports Qt.

**What is stored.** Three kinds of preference are stored, and nothing else:

- At most one `AgentPrice` for each shipped agent. `docs/INTERFACE.md` § "A cost
  at the reader's price" specifies its fields and what is refused. The reader
  enters a price per bottle, as a bottle price and a bottle volume in
  millilitres of liquid. The price per millilitre is never stored, so it
  cannot disagree with the two figures it comes from.
- The unit in which the agent cost View shows the delivered agent: millilitres
  of liquid, the default, or litres of vapour (`ROADMAP.md` § "v0.7.0 - the
  schematic", entry 8). The unit is stored as an `AgentAmountUnit` member.
  `app/formatting.py` keys its precision table by the same members, so a
  stored unit and a formatted value cannot name a unit in two different ways.
- The top of the MAC axis that every concentration chart and every compartment
  schematic is drawn to, a `ChartCeiling` (`docs/INTERFACE.md` § "The chart's
  fixed MAC axis", `PL-7LZ7`). The file stores the top's MAC multiple, such as
  3.0. Version 1 of the document had no top, so a version 1 file opens at the
  standard top, without a notice, and its next save writes version 2.

The project ships no price. A reader with no file has no prices, the default
unit and the standard top.

**Two choices that `docs/INTERFACE.md` § "Setting a price" left to this module**
(`PL-93B3`, 2026-11-01):

- A currency is refused unless it is three capital letters. It is not also
  checked against the list of codes that ISO 4217 assigns. That list changes
  several times a year. Checking it would need a dated copy of the list with
  its own provenance, and a copy that fell out of date would refuse a real
  currency. The three-letter code exists to remove an ambiguous "$", and any
  three letters remove it. A mistyped code, such as `UDS`, is printed beside
  every cost and every price, where the reader sees it.
- A bottle volume is refused unless it is a positive finite number. It is not
  also limited to the sizes in which the agents are sold, because no source
  gives such a limit. A volume typed in litres or as a count of bottles,
  instead of in millilitres, makes the price per millilitre 100 to 1000 times
  too high. The readout prints that price beside every cost (`docs/INTERFACE.md`
  § "A cost at the reader's price").

**What a launch finds, and what it does.** `PreferencesStore.load` returns a
`LoadedPreferences`, which says whether saving is allowed and carries any
notice for the reader. No problem with the file passes without a notice:

- *No file.* The session has no prices, the default unit and the standard
  top, and there is no notice. Saving is on.
- *A file that this build can read.* Each price, the unit and the top are
  checked one by one. A refused price is not used, and it is never replaced by
  a default. The reader is told which price was refused and why, and that
  agent then has no valid price. When the unit is refused, the default unit is
  used, with a notice. When the top is refused, the standard top is used, and
  every chart and schematic says so (`chart_ceiling_notice`). Each refused
  entry is kept exactly as it was written and is written back on the next
  save. That stops when the reader sets a new value in its place, or discards
  the refused prices and unit (`Preferences.without_refused_entries`). So a
  save never deletes something the reader wrote without the reader asking.
- *A file that a newer build wrote.* It is not read. Saving is off for the
  session, so the file is never overwritten. The notice names the file, its
  version and this build's version, and says what the reader can do. The
  Workspaces file follows the same rule (`PL-SSQW`).
- *A file that cannot be read, or cannot be checked entry by entry.* It is
  handled in the same way as a file from a newer build. This covers a file
  that is not UTF-8 JSON, and one with a duplicated key, a missing or unknown
  key, a container of the wrong kind, two prices for one agent, or a number
  too large for a float. An example of the last is 1e400, which could not be
  written back. Saving is off, so the file stays as it is for the reader to
  repair or remove. The notice says what is wrong with the file, in the
  words the agent cost View uses, and what the reader can do (`PL-W312`).

**How the file is written.** `save` uses `user_files`, which the Workspaces
store uses as well. It writes the whole document to `preferences.json.tmp`,
`fsync`s it and replaces the file with `os.replace`. So the file on disk is
always either the whole new document or the previous file, unchanged. A first
run writes nothing until the first save, which creates the directory.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping, Sequence, Set
from dataclasses import dataclass, field, replace
from datetime import date, datetime
from math import isfinite
from pathlib import Path
from types import MappingProxyType
from typing import Final

from anesthesia_sim.app.currency_code import is_currency_code
from anesthesia_sim.app.display_units import DisplayUnit
from anesthesia_sim.app.formatting import MAC_UNIT_SUFFIX, AgentAmountUnit, ChartCeiling
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES
from anesthesia_sim.core.validation import require_positive_finite
from anesthesia_sim.user_files import remove_quietly, sync_directory_quietly, write_synced

__all__ = [
    "AGENT_COST_VIEW_UNITS",
    "DEFAULT_AGENT_COST_VIEW_UNIT",
    "PREFERENCES_FILE_NAME",
    "PREFERENCES_SCHEMA_VERSION",
    "AgentPrice",
    "LoadedPreferences",
    "Preferences",
    "PreferencesFileError",
    "PreferencesStore",
    "RefusedEntry",
    "chart_ceiling_notice",
    "refusals_notice",
    "unsaved_preferences_notice",
]

PREFERENCES_FILE_NAME: Final = "preferences.json"
_PENDING_FILE_NAME: Final = f"{PREFERENCES_FILE_NAME}.tmp"

#: The version of the document that this build writes, and the newest it reads.
#: Version 2 added the axis top (`PL-7LZ7`).
PREFERENCES_SCHEMA_VERSION: Final = 2

#: The units that the agent cost View can show the delivered agent in, the
#: default first (`ROADMAP.md` § "v0.7.0 - the schematic", entry 8).
AGENT_COST_VIEW_UNITS: Final = (
    AgentAmountUnit.MILLILITRES_OF_LIQUID,
    AgentAmountUnit.LITRES_OF_VAPOUR,
)
DEFAULT_AGENT_COST_VIEW_UNIT: Final = AGENT_COST_VIEW_UNITS[0]

# The document's keys, so that reading and writing spell each one once.
_SCHEMA_VERSION_KEY: Final = "schema_version"
_UNIT_KEY: Final = "agent_cost_unit"
_PRICES_KEY: Final = "agent_prices"
_CHART_CEILING_KEY: Final = "chart_axis_top_mac"
#: The keys that a document of each version holds, every one of them required.
_DOCUMENT_KEYS: Final = MappingProxyType(
    {
        1: frozenset({_SCHEMA_VERSION_KEY, _UNIT_KEY, _PRICES_KEY}),
        2: frozenset({_SCHEMA_VERSION_KEY, _UNIT_KEY, _PRICES_KEY, _CHART_CEILING_KEY}),
    }
)
#: What the agent cost View and the charts call each setting of the file, for a
#: notice that names a missing one. The schema version is checked first, so it
#: is never named as missing.
_DOCUMENT_KEY_WORDS: Final = MappingProxyType(
    {
        _SCHEMA_VERSION_KEY: "version",
        _UNIT_KEY: "choice of how agent amounts are shown",
        _PRICES_KEY: "agent prices",
        _CHART_CEILING_KEY: "axis top",
    }
)
_AGENT_KEY: Final = "agent"
_BOTTLE_PRICE_KEY: Final = "bottle_price"
_BOTTLE_VOLUME_KEY: Final = "bottle_volume_ml"
_CURRENCY_KEY: Final = "currency"
_APPLIES_ON_KEY: Final = "applies_on"
#: What a user calls each part of a price, for a refusal that names a missing
#: one. The file's own keys are for a developer (`PL-VT87`).
_PRICE_KEY_WORDS: Final = MappingProxyType(
    {
        _AGENT_KEY: "agent",
        _APPLIES_ON_KEY: "date",
        _BOTTLE_PRICE_KEY: "bottle price",
        _BOTTLE_VOLUME_KEY: "bottle volume",
        _CURRENCY_KEY: "currency",
    }
)
_PRICE_KEYS: Final = frozenset(
    {_AGENT_KEY, _BOTTLE_PRICE_KEY, _BOTTLE_VOLUME_KEY, _CURRENCY_KEY, _APPLIES_ON_KEY}
)

# regex: a date must be an ISO 8601 calendar date in its extended form, such as 2008-03-05.
# `date.fromisoformat` also accepts the basic form, 20080305, which a reader could take
# for another number. So the pattern is checked before `date.fromisoformat` runs.
_DATE_PATTERN: Final = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


class PreferencesFileError(Exception):
    """The preferences file could not be saved, or saving is off for the session.

    The message names the file, what was being done, and the reason.
    """


def _require_above_zero(name: str, value: object) -> None:
    """Refuse a bottle price or volume that is not a number above zero, in a user's words.

    `require_positive_finite` makes the check, and this restates its refusal
    for the user who typed the value, who reads it in the price form and in the
    notice of refused preferences (`PL-VT87`). The original error is kept as
    the cause, for a developer.

    Raises:
        TypeError: `value` is not a number, or is a `bool`.
        SimulationConfigurationError: `value` is zero, negative, a NaN, an
            infinity or too large for a float.
    """

    message = f"{name} must be a number above zero, and it is {value!r}"

    try:
        require_positive_finite(name, value)  # type: ignore[arg-type]
    except TypeError as error:
        raise TypeError(message) from error
    except SimulationConfigurationError as error:
        raise SimulationConfigurationError(message) from error


@dataclass(frozen=True, slots=True)
class AgentPrice:
    """The reader's price for one agent, with the fields that `docs/INTERFACE.md` specifies.

    § "A cost at the reader's price" lists the fields and what is refused.

    Every check runs when the price is built, so a price that exists is
    valid. The same checks apply when a reader enters a price and when the
    file is read, because both build this class.

    Attributes:
        agent_id: The agent the price is for, a key of
            `core.parameters.AGENT_DATA_FILENAMES`.
        bottle_price: The price of one bottle, in `currency`.
        bottle_volume_ml: The volume of that bottle, in millilitres of liquid
            agent.
        currency: The ISO 4217 alphabetic code of the price's currency, such
            as `USD`.
        applies_on: The day on which the price applied, which is the day it
            was quoted rather than the day it was typed in.
    """

    agent_id: str
    bottle_price: float
    bottle_volume_ml: float
    currency: str
    applies_on: date

    def __post_init__(self) -> None:
        """Refuse a price that `docs/INTERFACE.md` § "Setting a price" says the store refuses.

        Raises:
            SimulationConfigurationError: If the simulator has no agent of
                that name, if the bottle price or the bottle volume is not a
                positive finite number, or if the currency is not three
                capital letters. The message names the field, in the words the
                View uses, and the value. A price of
                zero is refused because it is far more likely to be an empty
                field than an agent given away.
            TypeError: If the agent, the currency or the date is of the wrong
                type, or if the bottle price or volume is not a number. A
                `datetime` is refused as the date, because its time of day
                would claim more precision than the date of a quote has.
        """

        if not isinstance(self.agent_id, str):
            raise TypeError(f"the agent must be named in words, and it is {self.agent_id!r}")

        if self.agent_id not in AGENT_DATA_FILENAMES:
            raise SimulationConfigurationError(
                f"the simulator has no agent called {self.agent_id!r}; it has "
                f"{', '.join(sorted(AGENT_DATA_FILENAMES))}"
            )

        _require_above_zero("the bottle price", self.bottle_price)
        _require_above_zero(
            f"the bottle volume in {DisplayUnit.AGENT_LIQUID_MILLILITRES.recorded}",
            self.bottle_volume_ml,
        )

        if not isinstance(self.currency, str) or not is_currency_code(self.currency):
            message = (
                "the currency must be a three-letter code in capital letters, such as USD, "
                f"and it is {self.currency!r}"
            )
            if not isinstance(self.currency, str):
                raise TypeError(message)
            raise SimulationConfigurationError(message)

        if isinstance(self.applies_on, datetime) or not isinstance(self.applies_on, date):
            raise TypeError(f"the date must be a calendar date, and it is {self.applies_on!r}")

        object.__setattr__(self, "bottle_price", float(self.bottle_price))
        object.__setattr__(self, "bottle_volume_ml", float(self.bottle_volume_ml))

    @property
    def price_per_liquid_ml(self) -> float:
        """Return the price of one millilitre of liquid agent, in `currency`.

        This property is the only place that computes the price per
        millilitre. The store never holds the price per millilitre, so it
        cannot disagree with the bottle price and volume that it comes from
        (`docs/INTERFACE.md` § "A cost at the reader's price"). Both figures are
        positive and finite, but the quotient of two such floats can still be
        infinite or zero, such as 1e308 over 0.5. The cost readout shows no
        cost in that case (`app/agent_cost.py`).
        """

        return self.bottle_price / self.bottle_volume_ml


@dataclass(frozen=True, slots=True)
class RefusedEntry:
    """An entry of the preferences file that was refused when the file was read.

    It is kept exactly as it was written, so that the next save writes it
    back rather than deleting it.

    Attributes:
        raw: The entry as the file held it: one price object, or the value
            of the unit or of the top.
        reason: Why it was refused, as the notice states it.
        agent_id: The agent that a refused price names, or `None` for the
            unit, for the top, or for a price that does not give its agent as
            a string.
    """

    raw: object
    reason: str
    agent_id: str | None


@dataclass(frozen=True, slots=True)
class Preferences:
    """Hold the reader's settings: a price per agent, the agent cost View's unit, and the axis top.

    It is immutable. Each `with_` method returns a new record. Setting a
    value drops any refused entry that the value replaces, because the reader
    has now said what they want there.

    Attributes:
        agent_prices: Each agent's valid price, keyed by agent id.
        agent_cost_unit: The unit in which the agent cost View shows the
            delivered agent, one of `AGENT_COST_VIEW_UNITS`.
        refused_prices: The price entries refused when the file was read, in
            the file's order. None of them is used.
        refused_unit: The unit entry refused when the file was read, or
            `None`.
        chart_ceiling: The top of the MAC axis that every concentration
            chart and every compartment schematic is drawn to.
        refused_chart_ceiling: The top entry refused when the file was read,
            or `None`.
    """

    agent_prices: Mapping[str, AgentPrice] = field(default_factory=lambda: MappingProxyType({}))
    agent_cost_unit: AgentAmountUnit = DEFAULT_AGENT_COST_VIEW_UNIT
    refused_prices: tuple[RefusedEntry, ...] = ()
    refused_unit: RefusedEntry | None = None
    chart_ceiling: ChartCeiling = ChartCeiling.STANDARD
    refused_chart_ceiling: RefusedEntry | None = None

    def __post_init__(self) -> None:
        """Refuse a record whose prices, unit or top break the rules listed under Raises.

        Raises:
            SimulationConfigurationError: If a price is keyed by an agent
                other than its own, or if the unit is not one of
                `AGENT_COST_VIEW_UNITS`.
            TypeError: If a price is not an `AgentPrice`, or the top is not a
                `ChartCeiling`.
        """

        for agent_id, price in self.agent_prices.items():
            if not isinstance(price, AgentPrice):
                raise TypeError(f"a stored price is an AgentPrice, not {type(price).__name__}")

            if price.agent_id != agent_id:
                raise SimulationConfigurationError(
                    f"the price stored under {agent_id!r} is for {price.agent_id!r}"
                )

        _require_cost_view_unit(self.agent_cost_unit)

        if not isinstance(self.chart_ceiling, ChartCeiling):
            raise TypeError(
                f"the axis top is a ChartCeiling, not {type(self.chart_ceiling).__name__}"
            )

        object.__setattr__(self, "agent_prices", MappingProxyType(dict(self.agent_prices)))

    def price_for(self, agent_id: str) -> AgentPrice | None:
        """Return the reader's valid price for `agent_id`, or `None` when it has none."""

        return self.agent_prices.get(agent_id)

    def with_price(self, price: AgentPrice) -> Preferences:
        """Return these preferences with `price` set for its agent, replacing any earlier one.

        Raises:
            TypeError: If `price` is not an `AgentPrice`. Its fields were
                checked when it was built, so nothing else is checked here.
        """

        if not isinstance(price, AgentPrice):
            raise TypeError(f"a price is set from an AgentPrice, not {type(price).__name__}")

        return replace(
            self,
            agent_prices={**self.agent_prices, price.agent_id: price},
            refused_prices=tuple(
                entry for entry in self.refused_prices if entry.agent_id != price.agent_id
            ),
        )

    def without_price(self, agent_id: str) -> Preferences:
        """Return these preferences with no price for `agent_id`, refused or valid."""

        return replace(
            self,
            agent_prices={
                key: value for key, value in self.agent_prices.items() if key != agent_id
            },
            refused_prices=tuple(
                entry for entry in self.refused_prices if entry.agent_id != agent_id
            ),
        )

    @property
    def holds_refused_entries(self) -> bool:
        """Whether a refused price or a refused unit is still kept.

        These are the entries that `refusals_notice` names and the agent cost
        View offers to discard. A refused top is named on the charts and
        schematics instead (`chart_ceiling_notice`), so it is not counted here.
        """

        return bool(self.refused_prices) or self.refused_unit is not None

    def without_refused_entries(self) -> Preferences:
        """Return these preferences with every refused price and the refused unit discarded.

        The agent cost View offers this beside the notice that names the
        refused entries, and asks the reader to confirm it (`PL-7KXN`). It lets
        the reader clear a refused entry that no new value replaces, such as a
        price entry that names no agent. Without it, such an entry would be
        written back at every save and named in the notice at every launch.
        A refused top is kept. A top picked on any chart or schematic replaces
        it (`with_chart_ceiling`).
        """

        return replace(self, refused_prices=(), refused_unit=None)

    def with_agent_cost_unit(self, unit: AgentAmountUnit) -> Preferences:
        """Return these preferences with the agent cost View shown in `unit`.

        Raises:
            SimulationConfigurationError: If `unit` is not one of
                `AGENT_COST_VIEW_UNITS`.
        """

        return replace(self, agent_cost_unit=unit, refused_unit=None)

    def with_chart_ceiling(self, ceiling: ChartCeiling) -> Preferences:
        """Return these preferences with every chart and schematic drawn to `ceiling`.

        Raises:
            TypeError: If `ceiling` is not a `ChartCeiling`.
        """

        return replace(self, chart_ceiling=ceiling, refused_chart_ceiling=None)


@dataclass(frozen=True, slots=True)
class LoadedPreferences:
    """What `PreferencesStore.load` found, for the interface to use and show.

    Attributes:
        preferences: The preferences to use for the session.
        writable: `False` when saving is off for the session, because the file
            was written by a newer build or could not be checked. `save`
            refuses to write while it is `False`.
        notice: The sentence to show the reader, naming the file and what was
            done, or `None` when nothing needs saying.
    """

    preferences: Preferences
    writable: bool
    notice: str | None


#: What the notice for a file that cannot be used at all says about the
#: session, after the reason (`PreferencesStore._read_only`).
UNUSABLE_PREFERENCES_FILE_EFFECT: Final = (
    "None of your saved settings is in use, and the application does not save changes you "
    "make now, so the file stays as it is."
)
#: What a reader can do about a file that cannot be used at all. Preferences
#: are read only at launch, so each way out ends in a restart. Moving the file
#: away starts the application with no saved settings, so it is named apart
#: from correcting the file, as `NEWER_PREFERENCES_FILE_NEXT_STEP` names it.
UNUSABLE_PREFERENCES_FILE_NEXT_STEP: Final = (
    "To use your saved settings again, correct the file, then restart the application. To "
    "start again without them, move the file out of its folder, then restart the application."
)
#: What a reader can do about a file that a newer version of the application
#: saved. This version cannot read it, so correcting it is not a way out.
NEWER_PREFERENCES_FILE_NEXT_STEP: Final = (
    "To use your saved settings, open the newer version of the application. To start again "
    "without them, move the file out of its folder, then restart this version."
)


class PreferencesStore:
    """The reader's preferences file in one directory, read at launch and written on request."""

    def __init__(self, directory: Path) -> None:
        """Keep the directory that holds `preferences.json`. Nothing is read or written yet."""

        self._directory = Path(directory)
        self._loaded: LoadedPreferences | None = None

    @property
    def path(self) -> Path:
        """The preferences file's path, whether or not it exists."""

        return self._directory / PREFERENCES_FILE_NAME

    def load(self) -> LoadedPreferences:
        """Read the file, decide what the session uses, and return the result.

        It never raises because of the file's content or an operating-system
        error. It returns a `LoadedPreferences` for each outcome that the
        module docstring lists.
        """

        self._loaded = self._load()

        return self._loaded

    def save(self, preferences: Preferences) -> Path:
        """Write `preferences` atomically and return the file's path.

        Raises:
            TypeError: `preferences` is not a `Preferences`, or a refused
                entry holds a value that JSON cannot write, such as a set.
            ValueError: a refused entry holds a number that is not finite,
                such as NaN, or holds itself. No entry read from the file can
                hold such a value, so only a `RefusedEntry` built in code can.
            PreferencesFileError: nothing has been loaded, saving is off for
                the session, or the operating system refused a step. The
                message names the file and the reason. A failed save leaves
                the file as it was.
        """

        if not isinstance(preferences, Preferences):
            raise TypeError(
                f"preferences are saved from Preferences, not {type(preferences).__name__}"
            )

        if self._loaded is None:
            raise PreferencesFileError(
                f"nothing has been loaded from {self.path}, so whether saving there is safe is "
                "not known; load first"
            )

        if not self._loaded.writable:
            raise PreferencesFileError(f"saving is off for this session. {self._loaded.notice}")

        text = _to_json(preferences)
        pending = self._directory / _PENDING_FILE_NAME

        try:
            text.encode("utf-8")
        except UnicodeEncodeError:
            raise PreferencesFileError(
                f"the preferences could not be saved to {self.path}: they hold text that is "
                "not valid Unicode"
            ) from None

        try:
            self._directory.mkdir(parents=True, exist_ok=True)
            write_synced(pending, text)
            os.replace(pending, self.path)
        except OSError as error:
            remove_quietly(pending)
            raise PreferencesFileError(
                f"the preferences could not be saved to {self.path}: {error.strerror or error}"
            ) from None

        sync_directory_quietly(self._directory)

        return self.path

    def _load(self) -> LoadedPreferences:
        try:
            text = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return LoadedPreferences(Preferences(), writable=True, notice=None)
        except UnicodeDecodeError:
            return self._read_only(
                "the file's text is not in UTF-8, the encoding that the application saves"
            )
        except OSError as error:
            return self._read_only(f"the file could not be read ({error.strerror or error})")

        try:
            document = json.loads(
                text,
                object_pairs_hook=_refuse_repeated_keys,
                parse_constant=_refuse_constant,
                parse_float=_finite_float,
                parse_int=_whole_number,
            )
        except _InvalidDocument as invalid:
            return self._read_only(str(invalid))
        except json.JSONDecodeError as error:
            return self._read_only(_undecodable(text, error))
        except RecursionError:
            return self._read_only(
                "the file's entries are nested too deeply for the application to read them"
            )

        try:
            preferences = _from_document(document)
        except _NewerFile as newer:
            return self._read_only(
                f"a newer version of the application saved the file as version {newer.version}, "
                f"and this version reads files up to version {PREFERENCES_SCHEMA_VERSION}",
                NEWER_PREFERENCES_FILE_NEXT_STEP,
            )
        except _InvalidDocument as invalid:
            return self._read_only(str(invalid))

        return LoadedPreferences(
            preferences, writable=True, notice=refusals_notice(self.path, preferences)
        )

    def _read_only(
        self, reason: str, next_step: str = UNUSABLE_PREFERENCES_FILE_NEXT_STEP
    ) -> LoadedPreferences:
        """Return the defaults, with saving off, for a file that cannot be used at all.

        The notice says what went wrong, then what that means for the
        session, then what the reader can do, as `refusals_notice` does. The
        file's path comes last, as Microsoft's Windows error-message guidelines
        ask for a full path (`PL-W312`, which records the sources).
        """

        return LoadedPreferences(
            Preferences(),
            writable=False,
            notice=(
                f"The application could not use your preferences file, because {reason}. "
                f"{UNUSABLE_PREFERENCES_FILE_EFFECT} {next_step} The file is {self.path}."
            ),
        )


def refusals_notice(path: Path, preferences: Preferences) -> str | None:
    """Return the notice naming each refused entry that `preferences` still keeps, or None.

    A launch shows this notice for the entries refused when the file at `path`
    was read. After a save, the dashboard calls this again, because the reader
    may have replaced a refused entry by then, and that entry's reason no
    longer applies.

    The notice lists each refused preference on a line of its own, names it,
    and says what is wrong with it in the user's words, as the GOV.UK Design
    System's error summary lists each error. Microsoft's Windows error-message
    guidelines ask for a problem stated "in terms of user actions or goals" and
    for a full file path to stay out of the main instruction, so the path comes
    last. The notice says what the reader can do, as a refusal a user reads
    must (NUREG-0700 Rev. 3, guideline 2.7.3-1). `PL-VT87` records the sources. The agent cost View
    shows it, with the form that sets a price and the offer to discard the
    refused entries under it.
    """

    refused = [entry.reason for entry in preferences.refused_prices]

    if preferences.refused_unit is not None:
        refused.append(preferences.refused_unit.reason)

    if not refused:
        return None

    lines = "\n".join(f"• {reason}" for reason in refused)

    return (
        f"These saved settings could not be used:\n{lines}\n"
        f"{REFUSED_PREFERENCES_NEXT_STEP} They are saved in {path}."
    )


#: What a reader can do about a refused preference, which the notice that names
#: them ends with. The form and the offer to discard are both under the notice
#: in the agent cost View.
REFUSED_PREFERENCES_NEXT_STEP: Final = (
    "Set them again in this View, or discard the refused entries below."
)


def chart_ceiling_notice(preferences: Preferences) -> str | None:
    """Return the notice that every chart and schematic shows for a refused top, or None.

    The notice is shown under each View's axis top control, which is where the
    reader picks a top to replace the refused one.
    """

    refused = preferences.refused_chart_ceiling

    return None if refused is None else refused.reason


def unsaved_preferences_notice(error: PreferencesFileError) -> str:
    """Return what the reader is told when a change of preference could not be saved.

    The change still applies until the application closes. The wording is a
    placeholder.
    """

    return f"This change lasts only until the application closes, because {error}"


class _NewerFile(Exception):
    def __init__(self, version: int) -> None:
        super().__init__(version)
        self.version = version


class _InvalidDocument(Exception):
    pass


def _require_cost_view_unit(unit: object) -> None:
    if unit not in AGENT_COST_VIEW_UNITS:
        offered = ", ".join(member.value for member in AGENT_COST_VIEW_UNITS)
        raise SimulationConfigurationError(
            f"the agent cost View shows {offered}, and {unit!r} is not one of them"
        )


def _refuse_repeated_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    keys = [key for key, _ in pairs]
    repeated = sorted({key for key in keys if keys.count(key) > 1})

    if repeated:
        raise _InvalidDocument(f"the file writes the setting {repeated[0]!r} twice in one place")

    return dict(pairs)


def _refuse_constant(constant: str) -> float:
    raise _InvalidDocument(
        f"the file holds {constant}, which is not a number a preference can hold"
    )


def _finite_float(literal: str) -> float:
    # A literal too large for a float, such as 1e400, parses to an infinity
    # rather than raising. An infinity kept in a refused entry could not be
    # written back, because JSON has no way to write it, so every later save
    # would fail. Refusing it here treats the whole file as one this build
    # cannot check, which turns saving off and leaves the file as it is.
    value = float(literal)

    if not isfinite(value):
        raise _InvalidDocument(
            f"the file holds {literal}, which is too large to be a number a preference can hold"
        )

    return value


def _whole_number(literal: str) -> int:
    # Python refuses to convert a whole number longer than
    # `sys.get_int_max_str_digits()` digits, 4,300 by default, as a guard
    # against slow conversion. No preference is a number that long.
    try:
        return int(literal)
    except ValueError:
        raise _InvalidDocument(
            f"the file holds a whole number {len(literal.lstrip('-')):,} digits long, which is too "
            "long to be a number a preference can hold"
        ) from None


def _undecodable(text: str, error: json.JSONDecodeError) -> str:
    """Return why the file's text is not JSON, by where the first fault is, in the reader's words.

    The decoder's own message, such as "Expecting value", names a part of the
    JSON grammar, which the reader does not know. The line and column lead the
    reader to the fault in any text editor.
    """

    if not text.strip():
        return "the file is empty"

    return (
        f"the file's text at line {error.lineno}, column {error.colno} is not in the format "
        "that the application saves"
    )


#: The deepest nesting of lists and objects that a document may hold. A price
#: entry is one object of plain values, so its document nests three deep. A
#: refused entry is written back exactly as it was read. So a deeply nested
#: entry made a 30 KB file write 450 MB on its first save, and one in a 130 KB
#: file ran the process out of memory (`PL-B396`'s adversarial review).
_DEEPEST_NESTING: Final = 8


def _refuse_what_cannot_be_written_back(document: object) -> None:
    """Refuse a document that a save could not write back as it was read.

    A save writes every refused entry back unchanged. So a document is refused
    whole if it nests deeper than `_DEEPEST_NESTING`, or if any of its text is
    not valid Unicode. JSON lets a file hold a lone surrogate such as
    `"\\ud800"`, which cannot be written to a UTF-8 file. Refusing the whole
    document turns saving off, so the file stays as it is.
    """

    pending: list[tuple[object, int]] = [(document, 1)]

    while pending:
        value, depth = pending.pop()

        if isinstance(value, str):
            try:
                value.encode("utf-8")
            except UnicodeEncodeError:
                raise _InvalidDocument(
                    "the file holds text that is not valid Unicode, so the application could not "
                    "save it back unchanged"
                ) from None
            continue

        if not isinstance(value, dict | list):
            continue

        if depth > _DEEPEST_NESTING:
            raise _InvalidDocument(
                f"the file's entries are nested more than {_DEEPEST_NESTING} levels deep, and no "
                "preferences file that the application saves is"
            )

        children = [*value.keys(), *value.values()] if isinstance(value, dict) else value
        pending.extend((child, depth + 1) for child in children)


def _from_document(document: object) -> Preferences:
    if not isinstance(document, dict):
        raise _InvalidDocument(
            "the file does not hold a set of named settings, which is how the application "
            "saves them"
        )

    _refuse_what_cannot_be_written_back(document)

    if _SCHEMA_VERSION_KEY not in document:
        raise _InvalidDocument("the file gives no version")

    version = document[_SCHEMA_VERSION_KEY]

    shown = json.dumps(version, ensure_ascii=False)

    if isinstance(version, float) and version.is_integer() and version >= 1:
        raise _InvalidDocument(
            f"the file's version, {shown}, is written with a decimal point, and the application "
            f"reads a version only as a whole number written without one, such as {int(version)}"
        )

    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise _InvalidDocument(f"the file's version, {shown}, is not a whole number from 1 up")

    if version > PREFERENCES_SCHEMA_VERSION:
        raise _NewerFile(version)

    keys = set(document)
    expected = _DOCUMENT_KEYS[version]
    if keys != expected:
        raise _InvalidDocument(_wrong_settings(version, expected - keys, keys - expected))

    raw_prices = document[_PRICES_KEY]
    if not isinstance(raw_prices, list):
        raise _InvalidDocument(
            "the file's agent prices are not written as a list, which is how the application "
            "saves them"
        )

    prices: dict[str, AgentPrice] = {}
    refused: list[RefusedEntry] = []
    named: set[str] = set()

    for position, raw in enumerate(raw_prices):
        agent_id = raw.get(_AGENT_KEY) if isinstance(raw, dict) else None
        agent_id = agent_id if isinstance(agent_id, str) else None

        if agent_id is not None:
            if agent_id in named:
                raise _InvalidDocument(
                    f"the file holds two prices for {agent_id}, so the application cannot tell "
                    "which one applies"
                )
            named.add(agent_id)

        try:
            price = _price_from_entry(raw)
        except (SimulationConfigurationError, TypeError, ValueError) as error:
            # Name the price by its agent where the entry gives one, as the
            # reader set it in the View, and otherwise by its place in the file.
            name = (
                f"Your {agent_id} price"
                if agent_id is not None
                else f"Price {position + 1} in the file"
            )
            refused.append(RefusedEntry(raw, f"{name}: {error}.", agent_id))
        else:
            prices[price.agent_id] = price

    raw_unit = document[_UNIT_KEY]
    unit = DEFAULT_AGENT_COST_VIEW_UNIT
    refused_unit = None
    unit_member = next(
        (member for member in AGENT_COST_VIEW_UNITS if member.value == raw_unit), None
    )

    if unit_member is None:
        offered = " or ".join(member.value for member in AGENT_COST_VIEW_UNITS)
        refused_unit = RefusedEntry(
            raw_unit,
            f"How agent amounts are shown: {raw_unit!r} is not one of the choices, {offered}, "
            f"so the View shows {DEFAULT_AGENT_COST_VIEW_UNIT.value}.",
            None,
        )
    else:
        unit = unit_member

    ceiling, refused_ceiling = (
        (ChartCeiling.STANDARD, None)
        if version == 1
        else _chart_ceiling_from(document[_CHART_CEILING_KEY])
    )

    return Preferences(
        agent_prices=prices,
        agent_cost_unit=unit,
        refused_prices=tuple(refused),
        refused_unit=refused_unit,
        chart_ceiling=ceiling,
        refused_chart_ceiling=refused_ceiling,
    )


def _wrong_settings(version: int, missing: Set[str], unknown: Set[str]) -> str:
    """Return why a file's settings are not the ones its version holds, in the View's words.

    A missing setting is named as the View names it (`_DOCUMENT_KEY_WORDS`).
    A setting the file's version does not have is named as the file writes
    it, in quotes, because the View has no name for it. `_price_from_entry`
    words a price entry's wrong fields the same way.
    """

    problems = []

    if missing:
        words = sorted(_DOCUMENT_KEY_WORDS[key] for key in missing)
        problems.append(f"has {_listed([f'no {word}' for word in words])}")

    if unknown:
        problems.append(
            f"holds settings that a version {version} file does not have: "
            f"{', '.join(repr(key) for key in sorted(unknown))}"
        )

    return f"the file {', and '.join(problems)}"


def _listed(words: Sequence[str]) -> str:
    """Return `words` as a list in a sentence, such as "no agent prices and no axis top"."""

    return words[0] if len(words) == 1 else f"{', '.join(words[:-1])} and {words[-1]}"


def _chart_ceiling_from(raw: object) -> tuple[ChartCeiling, RefusedEntry | None]:
    """Return the top that a document's entry names, or the standard top and the refused entry.

    The entry must be a number equal to one of `ChartCeiling`'s MAC multiples.
    """

    # `type` rather than `isinstance`, so that True does not pass for 1.
    ceiling = next(
        (member for member in ChartCeiling if type(raw) in (int, float) and raw == member.value),
        None,
    )

    if ceiling is not None:
        return ceiling, None

    # The value is shown as the file holds it, so text reads in quotes and a
    # JSON null as null. Text such as "4.5" then reads as text, which is why
    # the sentence says that the top is a number.
    values = [f"{member.value:g}" for member in ChartCeiling]
    offered = f"{', '.join(values[:-1])} or {values[-1]}{MAC_UNIT_SUFFIX}"
    shown = json.dumps(raw, ensure_ascii=False)
    reason = (
        f"The saved axis top, {shown}, is not one of the numbers {offered}, so every "
        f"chart and schematic shows {ChartCeiling.STANDARD.label}. Choose a top to replace it."
    )

    return ChartCeiling.STANDARD, RefusedEntry(raw, reason, None)


def _price_from_entry(raw: object) -> AgentPrice:
    if not isinstance(raw, dict):
        raise TypeError(f"it is not a price, and it holds {raw!r}")

    keys = set(raw)
    if keys != _PRICE_KEYS:
        problems = []
        missing = [_PRICE_KEY_WORDS[key] for key in sorted(_PRICE_KEYS - keys)]
        unknown = [repr(key) for key in sorted(keys - _PRICE_KEYS)]
        if missing:
            listed = (
                missing[0] if len(missing) == 1 else f"{', '.join(missing[:-1])} or {missing[-1]}"
            )
            problems.append(f"it has no {listed}")
        if unknown:
            problems.append(f"it holds entries the simulator does not use: {', '.join(unknown)}")
        raise ValueError(", and ".join(problems))

    applies_on = raw[_APPLIES_ON_KEY]
    if not isinstance(applies_on, str) or _DATE_PATTERN.fullmatch(applies_on) is None:
        raise ValueError(
            "the date must be written as year-month-day, such as 2008-03-05, "
            f"and it is {applies_on!r}"
        )

    try:
        day = date.fromisoformat(applies_on)
    except ValueError:
        raise ValueError(f"the date {applies_on!r} is not a real calendar date") from None

    return AgentPrice(
        agent_id=raw[_AGENT_KEY],
        bottle_price=raw[_BOTTLE_PRICE_KEY],
        bottle_volume_ml=raw[_BOTTLE_VOLUME_KEY],
        currency=raw[_CURRENCY_KEY],
        applies_on=day,
    )


def _price_to_entry(price: AgentPrice) -> dict[str, object]:
    return {
        _AGENT_KEY: price.agent_id,
        _BOTTLE_PRICE_KEY: price.bottle_price,
        _BOTTLE_VOLUME_KEY: price.bottle_volume_ml,
        _CURRENCY_KEY: price.currency,
        _APPLIES_ON_KEY: price.applies_on.isoformat(),
    }


def _to_json(preferences: Preferences) -> str:
    entries: list[object] = [_price_to_entry(price) for price in preferences.agent_prices.values()]
    entries += [entry.raw for entry in preferences.refused_prices]
    unit = (
        preferences.agent_cost_unit.value
        if preferences.refused_unit is None
        else preferences.refused_unit.raw
    )
    ceiling = (
        preferences.chart_ceiling.value
        if preferences.refused_chart_ceiling is None
        else preferences.refused_chart_ceiling.raw
    )

    return (
        json.dumps(
            {
                _SCHEMA_VERSION_KEY: PREFERENCES_SCHEMA_VERSION,
                _UNIT_KEY: unit,
                _PRICES_KEY: entries,
                _CHART_CEILING_KEY: ceiling,
            },
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    )
