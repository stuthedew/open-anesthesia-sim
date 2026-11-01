"""Read and write the file that holds the reader's agent prices and the agent cost View's unit.

A preference belongs to the reader, not to a layout. So preferences are kept
in `preferences.json`, beside the Workspaces' `workspaces.json` in the same
directory but never inside it (`PL-MQHN`, `PL-93B3`). This module is the only
code that reads and writes the file. Nothing in it imports Qt.

**What is stored.** Two kinds of preference are stored, and nothing else:

- At most one `AgentPrice` for each shipped agent. `docs/MODEL.md` § "A cost
  at the reader's price" specifies its fields and what is refused. The reader
  enters a price per bottle, as a bottle price and a bottle volume in
  millilitres of liquid. The price per millilitre is never stored, so it
  cannot disagree with the two figures it comes from.
- The unit in which the agent cost View shows the delivered agent: millilitres
  of liquid, the default, or litres of vapour (`ROADMAP.md` § "v0.7.0 - the
  schematic", entry 8). The unit is stored as an `AgentAmountUnit` member.
  `app/formatting.py` keys its precision table by the same members, so a
  stored unit and a formatted value cannot name a unit in two different ways.

The project ships no price. A reader with no file has no prices and the
default unit.

**Two choices that `docs/MODEL.md` left to this module** (`PL-93B3`, 2026-11-01):

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
  too high. The readout prints that price beside every cost (`docs/MODEL.md`
  § "A cost at the reader's price").

**What a launch finds, and what it does.** `PreferencesStore.load` returns a
`LoadedPreferences`, which says whether saving is allowed and carries any
notice for the reader. No problem with the file passes without a notice:

- *No file.* The session has no prices and the default unit, and there is no
  notice. Saving is on.
- *A file that this build can read.* Each price and the unit are checked one
  by one. A refused price is not used, and it is never replaced by a default.
  The reader is told which price was refused and why, and that agent then has
  no valid price. When the unit is refused, the default unit is used, with a
  notice. Each refused entry is kept exactly as it was written and is written
  back on the next save. That stops when the reader sets a new value in its
  place or discards it (`Preferences.without_refused_entries`). So a save
  never deletes something the reader wrote without the reader asking.
- *A file that a newer build wrote.* It is not read. Saving is off for the
  session, so the file is never overwritten. The notice names the file, its
  version and this build's version. The Workspaces file follows the same rule
  (`PL-SSQW`).
- *A file that cannot be read, or cannot be checked entry by entry.* It is
  handled in the same way as a file from a newer build. This covers a file
  that is not UTF-8 JSON, and one with a duplicated key, a missing or unknown
  key, a container of the wrong kind, two prices for one agent, or a number
  too large for a float. An example of the last is 1e400, which could not be
  written back. Saving is off, so the file stays as it is for the reader to
  repair or remove. The notice says what is wrong with the file.

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
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import date, datetime
from math import isfinite
from pathlib import Path
from types import MappingProxyType
from typing import Final

from anesthesia_sim.app.formatting import AgentAmountUnit
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
    "refusals_notice",
    "unsaved_preferences_notice",
]

PREFERENCES_FILE_NAME: Final = "preferences.json"
_PENDING_FILE_NAME: Final = f"{PREFERENCES_FILE_NAME}.tmp"

#: The version of the document that this build writes, and the newest it reads.
PREFERENCES_SCHEMA_VERSION: Final = 1

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
_DOCUMENT_KEYS: Final = frozenset({_SCHEMA_VERSION_KEY, _UNIT_KEY, _PRICES_KEY})
_AGENT_KEY: Final = "agent"
_BOTTLE_PRICE_KEY: Final = "bottle_price"
_BOTTLE_VOLUME_KEY: Final = "bottle_volume_ml"
_CURRENCY_KEY: Final = "currency"
_APPLIES_ON_KEY: Final = "applies_on"
_PRICE_KEYS: Final = frozenset(
    {_AGENT_KEY, _BOTTLE_PRICE_KEY, _BOTTLE_VOLUME_KEY, _CURRENCY_KEY, _APPLIES_ON_KEY}
)

# Three capital letters, the form of an ISO 4217 alphabetic code. `[A-Z]` in
# Python's `re` matches only the 26 ASCII capitals.
_CURRENCY_PATTERN: Final = re.compile(r"[A-Z]{3}")
# A date must be an ISO 8601 calendar date in its extended form, such as 2008-03-05.
# `date.fromisoformat` also accepts the basic form, 20080305, which a reader could take
# for another number. So the pattern is checked before `date.fromisoformat` runs.
_DATE_PATTERN: Final = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


class PreferencesFileError(Exception):
    """The preferences file could not be saved, or saving is off for the session.

    The message names the file, what was being done, and the reason.
    """


@dataclass(frozen=True, slots=True)
class AgentPrice:
    """The reader's price for one agent, with the fields that `docs/MODEL.md` specifies.

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
        """Refuse a price that `docs/MODEL.md` says the store refuses.

        Raises:
            SimulationConfigurationError: If the agent is not a shipped agent,
                if the bottle price or the bottle volume is not a positive
                finite number, or if the currency is not three capital
                letters. The message names the field and the value. A price of
                zero is refused because it is far more likely to be an empty
                field than an agent given away.
            TypeError: If the agent, the currency or the date is of the wrong
                type, or if the bottle price or volume is not a number. A
                `datetime` is refused as the date, because its time of day
                would claim more precision than the date of a quote has.
        """

        if not isinstance(self.agent_id, str):
            raise TypeError(f"an agent price's agent is a str, not {type(self.agent_id).__name__}")

        if self.agent_id not in AGENT_DATA_FILENAMES:
            raise SimulationConfigurationError(
                f"an agent price names {self.agent_id!r}, which is not a shipped agent; "
                f"expected one of {sorted(AGENT_DATA_FILENAMES)}"
            )

        require_positive_finite(f"the {self.agent_id} bottle price", self.bottle_price)
        require_positive_finite(
            f"the {self.agent_id} bottle volume in millilitres of liquid", self.bottle_volume_ml
        )

        if not isinstance(self.currency, str):
            raise TypeError(
                f"the {self.agent_id} price's currency is a str, not {type(self.currency).__name__}"
            )

        if _CURRENCY_PATTERN.fullmatch(self.currency) is None:
            raise SimulationConfigurationError(
                f"the {self.agent_id} price's currency must be an ISO 4217 code of three capital "
                f"letters, such as USD, and {self.currency!r} is not"
            )

        if isinstance(self.applies_on, datetime) or not isinstance(self.applies_on, date):
            raise TypeError(
                f"the {self.agent_id} price's date is a date, not {type(self.applies_on).__name__}"
            )

        object.__setattr__(self, "bottle_price", float(self.bottle_price))
        object.__setattr__(self, "bottle_volume_ml", float(self.bottle_volume_ml))


@dataclass(frozen=True, slots=True)
class RefusedEntry:
    """An entry of the preferences file that was refused when the file was read.

    It is kept exactly as it was written, so that the next save writes it
    back rather than deleting it.

    Attributes:
        raw: The entry as the file held it: one price object, or the unit's
            value.
        reason: Why it was refused, as the notice states it.
        agent_id: The agent that a refused price names, or `None` for the
            unit, or for a price that does not give its agent as a string.
    """

    raw: object
    reason: str
    agent_id: str | None


@dataclass(frozen=True, slots=True)
class Preferences:
    """Hold the reader's settings, which are a price per agent and the agent cost View's unit.

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
    """

    agent_prices: Mapping[str, AgentPrice] = field(default_factory=lambda: MappingProxyType({}))
    agent_cost_unit: AgentAmountUnit = DEFAULT_AGENT_COST_VIEW_UNIT
    refused_prices: tuple[RefusedEntry, ...] = ()
    refused_unit: RefusedEntry | None = None

    def __post_init__(self) -> None:
        """Refuse a record whose prices or unit break the rules listed under Raises.

        Raises:
            SimulationConfigurationError: If a price is keyed by an agent
                other than its own, or if the unit is not one of
                `AGENT_COST_VIEW_UNITS`.
            TypeError: If a price is not an `AgentPrice`.
        """

        for agent_id, price in self.agent_prices.items():
            if not isinstance(price, AgentPrice):
                raise TypeError(f"a stored price is an AgentPrice, not {type(price).__name__}")

            if price.agent_id != agent_id:
                raise SimulationConfigurationError(
                    f"the price stored under {agent_id!r} is for {price.agent_id!r}"
                )

        _require_cost_view_unit(self.agent_cost_unit)
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

    def without_refused_entries(self) -> Preferences:
        """Return these preferences with every refused entry discarded.

        The interface offers this so that the reader can clear a refused entry
        that no new value replaces, such as a price entry that names no agent.
        Without it, such an entry would be written back at every save and
        named in the notice at every launch.
        """

        return replace(self, refused_prices=(), refused_unit=None)

    def with_agent_cost_unit(self, unit: AgentAmountUnit) -> Preferences:
        """Return these preferences with the agent cost View shown in `unit`.

        Raises:
            SimulationConfigurationError: If `unit` is not one of
                `AGENT_COST_VIEW_UNITS`.
        """

        return replace(self, agent_cost_unit=unit, refused_unit=None)


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
            TypeError: `preferences` is not a `Preferences`.
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
            raise PreferencesFileError(f"saving is off for this session: {self._loaded.notice}")

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
        self._loaded = LoadedPreferences(preferences, writable=True, notice=None)

        return self.path

    def _load(self) -> LoadedPreferences:
        try:
            text = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return LoadedPreferences(Preferences(), writable=True, notice=None)
        except UnicodeDecodeError:
            return self._read_only("it is not UTF-8 text")
        except OSError as error:
            return self._read_only(f"it could not be read ({error.strerror or error})")

        try:
            document = json.loads(
                text,
                object_pairs_hook=_refuse_repeated_keys,
                parse_constant=_refuse_constant,
                parse_float=_finite_float,
            )
        except (ValueError, RecursionError) as error:
            return self._read_only(f"it is not a JSON document this build can read ({error})")

        try:
            preferences = _from_document(document)
        except _NewerFile as newer:
            return self._read_only(
                f"it was written at schema version {newer.version} by a newer build, and this "
                f"build reads version {PREFERENCES_SCHEMA_VERSION} and earlier"
            )
        except _InvalidDocument as invalid:
            return self._read_only(str(invalid))

        return LoadedPreferences(
            preferences, writable=True, notice=refusals_notice(self.path, preferences)
        )

    def _read_only(self, reason: str) -> LoadedPreferences:
        return LoadedPreferences(
            Preferences(),
            writable=False,
            notice=(
                f"the preferences file {self.path} was not used because {reason}. No price is "
                "set, and saving preferences is off for this session so that the file is left "
                "as it is"
            ),
        )


def refusals_notice(path: Path, preferences: Preferences) -> str | None:
    """Return the notice naming each refused entry that `preferences` still keeps, or None.

    A launch shows this notice for the entries refused when the file at `path`
    was read. After a save, the dashboard asks again, because the reader may
    have replaced a refused entry by then, and its reason no longer applies.
    """

    refused = [entry.reason for entry in preferences.refused_prices]

    if preferences.refused_unit is not None:
        refused.append(preferences.refused_unit.reason)

    if not refused:
        return None

    return f"some preferences in {path} were refused and are not used: " + "; ".join(refused)


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
        raise ValueError(f"the key {repeated[0]!r} is given twice in one object")

    return dict(pairs)


def _refuse_constant(constant: str) -> float:
    raise ValueError(f"{constant} is not a number a preference can hold")


def _finite_float(literal: str) -> float:
    # A literal too large for a float, such as 1e400, parses to an infinity
    # rather than raising. An infinity kept in a refused entry could not be
    # written back, because JSON has no way to write it, so every later save
    # would fail. Refusing it here treats the whole file as one this build
    # cannot check, which turns saving off and leaves the file as it is.
    value = float(literal)

    if not isfinite(value):
        raise ValueError(f"{literal} is too large to be a number a preference can hold")

    return value


#: The deepest nesting of lists and objects that a document may hold. A price
#: entry is one object of plain values, so its document nests three deep. A
#: refused entry is written back exactly as it was read, so a deeply nested
#: one made a 30 KB file write 450 MB on its first save, and a 130 KB one ran
#: the process out of memory (`PL-B396`'s adversarial review).
_DEEPEST_NESTING: Final = 8


def _refuse_what_cannot_be_written_back(document: object) -> None:
    """Refuse a document that a save could not write back as it was read.

    A save writes every refused entry back unchanged. So a document is refused
    whole if it nests deeper than `_DEEPEST_NESTING`, or if any of its text is
    not valid Unicode. JSON lets a file hold a lone surrogate such as
    `"\\ud800"`, which no UTF-8 file can be written with. Refusing the whole
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
                    "it holds text that is not valid Unicode, so it could not be written back"
                ) from None
            continue

        if not isinstance(value, dict | list):
            continue

        if depth > _DEEPEST_NESTING:
            raise _InvalidDocument(
                f"it nests lists and objects more than {_DEEPEST_NESTING} deep, which no "
                "preferences document does"
            )

        children = [*value.keys(), *value.values()] if isinstance(value, dict) else value
        pending.extend((child, depth + 1) for child in children)


def _from_document(document: object) -> Preferences:
    if not isinstance(document, dict):
        raise _InvalidDocument("its document is not a JSON object")

    _refuse_what_cannot_be_written_back(document)

    version = document.get(_SCHEMA_VERSION_KEY)

    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise _InvalidDocument(f"its {_SCHEMA_VERSION_KEY} is {version!r}, not a version from 1 up")

    if version > PREFERENCES_SCHEMA_VERSION:
        raise _NewerFile(version)

    keys = set(document)
    if keys != _DOCUMENT_KEYS:
        missing = sorted(_DOCUMENT_KEYS - keys)
        unknown = sorted(keys - _DOCUMENT_KEYS)
        raise _InvalidDocument(f"its keys are wrong: missing {missing}, not known {unknown}")

    raw_prices = document[_PRICES_KEY]
    if not isinstance(raw_prices, list):
        raise _InvalidDocument(f"its {_PRICES_KEY} is not a list")

    prices: dict[str, AgentPrice] = {}
    refused: list[RefusedEntry] = []
    named: set[str] = set()

    for position, raw in enumerate(raw_prices):
        agent_id = raw.get(_AGENT_KEY) if isinstance(raw, dict) else None
        agent_id = agent_id if isinstance(agent_id, str) else None

        if agent_id is not None:
            if agent_id in named:
                raise _InvalidDocument(
                    f"it holds two prices for {agent_id}, so it cannot say which applies"
                )
            named.add(agent_id)

        try:
            price = _price_from_entry(raw)
        except (SimulationConfigurationError, TypeError, ValueError) as error:
            refused.append(
                RefusedEntry(raw, f"the price at {_PRICES_KEY}[{position}]: {error}", agent_id)
            )
        else:
            prices[price.agent_id] = price

    raw_unit = document[_UNIT_KEY]
    unit = DEFAULT_AGENT_COST_VIEW_UNIT
    refused_unit = None
    unit_member = next(
        (member for member in AGENT_COST_VIEW_UNITS if member.value == raw_unit), None
    )

    if unit_member is None:
        offered = ", ".join(repr(member.value) for member in AGENT_COST_VIEW_UNITS)
        refused_unit = RefusedEntry(
            raw_unit,
            f"the agent cost unit {raw_unit!r} is not one of {offered}, so the View shows "
            f"{DEFAULT_AGENT_COST_VIEW_UNIT.value}",
            None,
        )
    else:
        unit = unit_member

    return Preferences(
        agent_prices=prices,
        agent_cost_unit=unit,
        refused_prices=tuple(refused),
        refused_unit=refused_unit,
    )


def _price_from_entry(raw: object) -> AgentPrice:
    if not isinstance(raw, dict):
        raise TypeError(f"an entry is a JSON object, not {type(raw).__name__}")

    keys = set(raw)
    if keys != _PRICE_KEYS:
        missing = sorted(_PRICE_KEYS - keys)
        unknown = sorted(keys - _PRICE_KEYS)
        raise ValueError(f"its keys are wrong: missing {missing}, not known {unknown}")

    applies_on = raw[_APPLIES_ON_KEY]
    if not isinstance(applies_on, str) or _DATE_PATTERN.fullmatch(applies_on) is None:
        raise ValueError(
            f"its date must be written as YYYY-MM-DD, such as 2008-03-05, and {applies_on!r} is not"
        )

    try:
        day = date.fromisoformat(applies_on)
    except ValueError:
        raise ValueError(f"its date {applies_on!r} is not a real calendar date") from None

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

    return (
        json.dumps(
            {
                _SCHEMA_VERSION_KEY: PREFERENCES_SCHEMA_VERSION,
                _UNIT_KEY: unit,
                _PRICES_KEY: entries,
            },
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    )
