"""Tests for the reader's preferences file, `app/preferences.py` (`PL-93B3`).

Every expected document below is written out by hand rather than produced by
the code under test. A "restart" is a second `PreferencesStore` built on the
same directory, which reads only what the first one wrote to disk.
"""

import json
from datetime import date, datetime
from pathlib import Path

import pytest
from test_user_files import make_the_platform_encoding_ascii

from anesthesia_sim.app.formatting import AgentAmountUnit
from anesthesia_sim.app.preferences import (
    PREFERENCES_FILE_NAME,
    AgentPrice,
    Preferences,
    PreferencesFileError,
    PreferencesStore,
    RefusedEntry,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError

# Gas Man's default isoflurane price is US$20.47 for a 100 mL bottle, "as of March 5,
# 2008" (Philip JH, *Workbook for Gas Man*, Appendix C, printed p. 171, and
# printed p. 105). `docs/INTERFACE.md` § "A cost at the reader's price" quotes it.
ISOFLURANE_PRICE = AgentPrice(
    agent_id="isoflurane",
    bottle_price=20.47,
    bottle_volume_ml=100.0,
    currency="USD",
    applies_on=date(2008, 3, 5),
)

# Gas Man's sevoflurane default: 240.34 for a 250 mL bottle (printed p. 172).
SEVOFLURANE_PRICE_ENTRY = {
    "agent": "sevoflurane",
    "bottle_price": 240.34,
    "bottle_volume_ml": 250.0,
    "currency": "USD",
    "applies_on": "2008-03-05",
}


def _write(directory: Path, document: object) -> Path:
    path = directory / PREFERENCES_FILE_NAME
    path.write_text(json.dumps(document), encoding="utf-8")

    return path


def _document(prices: list[object], unit: object = "millilitres of liquid") -> dict[str, object]:
    return {"schema_version": 1, "agent_cost_unit": unit, "agent_prices": prices}


# ----------------------------------------------------------------- persistence


def test_a_preference_survives_a_restart(tmp_path: Path) -> None:
    """The agent price and the agent cost View's unit both come back after a restart."""

    store = PreferencesStore(tmp_path)
    store.load()
    store.save(
        Preferences()
        .with_price(ISOFLURANE_PRICE)
        .with_agent_cost_unit(AgentAmountUnit.LITRES_OF_VAPOUR)
    )

    loaded = PreferencesStore(tmp_path).load()

    assert loaded.notice is None
    assert loaded.writable
    assert loaded.preferences.price_for("isoflurane") == ISOFLURANE_PRICE
    assert loaded.preferences.price_for("sevoflurane") is None
    assert loaded.preferences.agent_cost_unit is AgentAmountUnit.LITRES_OF_VAPOUR


def test_the_saved_document_is_the_one_the_schema_describes(tmp_path: Path) -> None:
    store = PreferencesStore(tmp_path)
    store.load()
    path = store.save(Preferences().with_price(ISOFLURANE_PRICE))

    assert json.loads(path.read_text(encoding="utf-8")) == {
        "schema_version": 1,
        "agent_cost_unit": "millilitres of liquid",
        "agent_prices": [
            {
                "agent": "isoflurane",
                "bottle_price": 20.47,
                "bottle_volume_ml": 100.0,
                "currency": "USD",
                "applies_on": "2008-03-05",
            }
        ],
    }
    assert sorted(entry.name for entry in tmp_path.iterdir()) == [PREFERENCES_FILE_NAME]


def test_a_first_run_has_no_price_and_the_liquid_unit_and_writes_nothing(tmp_path: Path) -> None:
    directory = tmp_path / "not yet created"
    loaded = PreferencesStore(directory).load()

    assert loaded.writable
    assert loaded.notice is None
    assert dict(loaded.preferences.agent_prices) == {}
    assert loaded.preferences.agent_cost_unit is AgentAmountUnit.MILLILITRES_OF_LIQUID
    assert not directory.exists()


def test_a_first_save_creates_the_directory(tmp_path: Path) -> None:
    directory = tmp_path / "a" / "b"
    store = PreferencesStore(directory)
    store.load()

    assert store.save(Preferences()) == directory / PREFERENCES_FILE_NAME
    assert (directory / PREFERENCES_FILE_NAME).is_file()


def test_saving_before_loading_is_refused(tmp_path: Path) -> None:
    with pytest.raises(PreferencesFileError, match="load first"):
        PreferencesStore(tmp_path).save(Preferences())


def test_a_save_the_system_refuses_names_the_file_and_leaves_no_temporary_file(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "prefs"
    store = PreferencesStore(directory)
    store.load()
    directory.mkdir()
    (directory / PREFERENCES_FILE_NAME).mkdir()

    with pytest.raises(PreferencesFileError, match="could not be saved to .*preferences.json"):
        store.save(Preferences())

    assert sorted(entry.name for entry in directory.iterdir()) == [PREFERENCES_FILE_NAME]


# ------------------------------------------------- files this build does not use


def test_a_file_from_a_newer_build_is_not_read_and_never_overwritten(tmp_path: Path) -> None:
    path = _write(tmp_path, {"schema_version": 2, "anything": "a newer build wrote"})
    before = path.read_bytes()
    store = PreferencesStore(tmp_path)

    loaded = store.load()

    assert not loaded.writable
    assert dict(loaded.preferences.agent_prices) == {}
    assert loaded.notice is not None
    assert "schema version 2" in loaded.notice
    assert "reads version 1" in loaded.notice
    assert str(path) in loaded.notice
    with pytest.raises(PreferencesFileError, match="saving is off"):
        store.save(Preferences().with_price(ISOFLURANE_PRICE))
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    ("text", "reason"),
    [
        ("{not json", "not a JSON document"),
        ("[]", "not a JSON object"),
        ('{"schema_version": 0}', "not a version from 1 up"),
        ('{"schema_version": true}', "not a version from 1 up"),
        ('{"schema_version": 1, "agent_cost_unit": "millilitres of liquid"}', "missing"),
        (
            '{"schema_version": 1, "agent_cost_unit": "millilitres of liquid", '
            '"agent_prices": [], "theme": "dark"}',
            "not known",
        ),
        (
            '{"schema_version": 1, "schema_version": 1, '
            '"agent_cost_unit": "millilitres of liquid", "agent_prices": []}',
            "given twice",
        ),
        (
            '{"schema_version": 1, "agent_cost_unit": "millilitres of liquid", "agent_prices": {}}',
            "not a list",
        ),
        (
            '{"schema_version": 1, "agent_cost_unit": "millilitres of liquid", '
            '"agent_prices": [{"agent": "isoflurane", "bottle_price": NaN, '
            '"bottle_volume_ml": 100, "currency": "USD", "applies_on": "2008-03-05"}]}',
            "NaN is not a number",
        ),
        (
            '{"schema_version": 1, "agent_cost_unit": "millilitres of liquid", '
            '"agent_prices": [{"agent": "isoflurane", "bottle_price": 20.47, '
            '"bottle_volume_ml": 1e400, "currency": "USD", "applies_on": "2008-03-05"}]}',
            "1e400 is too large",
        ),
        (
            '{"schema_version": 1, "agent_cost_unit": "millilitres of liquid", '
            '"agent_prices": ["\\ud800"]}',
            "not valid Unicode",
        ),
        (
            '{"schema_version": 1, "agent_cost_unit": "millilitres of liquid", '
            '"agent_prices": [' + "[" * 8 + "]" * 8 + "]}",
            "more than 8 deep",
        ),
    ],
    ids=[
        "not JSON",
        "not an object",
        "version 0",
        "version true",
        "a key missing",
        "an unknown key",
        "a repeated key",
        "prices not a list",
        "NaN",
        "a number too large for a float",
        "a lone surrogate, which no UTF-8 file can hold",
        "a refused entry nested past the limit",
    ],
)
def test_a_document_that_cannot_be_checked_entry_by_entry_turns_saving_off(
    tmp_path: Path, text: str, reason: str
) -> None:
    path = tmp_path / PREFERENCES_FILE_NAME
    path.write_text(text, encoding="utf-8")

    loaded = PreferencesStore(tmp_path).load()

    assert not loaded.writable
    assert dict(loaded.preferences.agent_prices) == {}
    assert loaded.notice is not None
    assert reason in loaded.notice
    assert path.read_text(encoding="utf-8") == text


def test_two_prices_for_one_agent_turn_saving_off(tmp_path: Path) -> None:
    _write(tmp_path, _document([SEVOFLURANE_PRICE_ENTRY, SEVOFLURANE_PRICE_ENTRY]))

    loaded = PreferencesStore(tmp_path).load()

    assert not loaded.writable
    assert loaded.notice is not None
    assert "two prices for sevoflurane" in loaded.notice


def test_a_file_that_is_not_utf8_turns_saving_off(tmp_path: Path) -> None:
    (tmp_path / PREFERENCES_FILE_NAME).write_bytes(b'{"schema_version": 1, "x": "\xff"}')

    loaded = PreferencesStore(tmp_path).load()

    assert not loaded.writable
    assert loaded.notice is not None
    assert "not UTF-8" in loaded.notice


def test_a_file_that_cannot_be_read_turns_saving_off(tmp_path: Path) -> None:
    (tmp_path / PREFERENCES_FILE_NAME).mkdir()

    loaded = PreferencesStore(tmp_path).load()

    assert not loaded.writable
    assert loaded.notice is not None
    assert "could not be read" in loaded.notice


# ---------------------------------------------- one entry refused, the rest used


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("agent", "halothane", "no agent called 'halothane'"),
        ("bottle_price", 0, "bottle price"),
        ("bottle_price", -20.47, "bottle price"),
        ("bottle_price", "20.47", "bottle price"),
        ("bottle_price", True, "bottle price"),
        ("bottle_volume_ml", 0.0, "bottle volume"),
        ("currency", "usd", "three-letter code in capital letters"),
        ("currency", "US", "three-letter code in capital letters"),
        ("currency", "USDX", "three-letter code in capital letters"),
        ("currency", "$", "three-letter code in capital letters"),
        ("applies_on", "2008-02-30", "not a real calendar date"),
        ("applies_on", "03/05/2008", "year-month-day"),
        ("applies_on", "20080305", "year-month-day"),
    ],
)
def test_a_refused_price_is_not_used_and_the_others_are(
    tmp_path: Path, field: str, value: object, reason: str
) -> None:
    refused = {**SEVOFLURANE_PRICE_ENTRY, "agent": "isoflurane", field: value}
    text = json.dumps(_document([SEVOFLURANE_PRICE_ENTRY, refused]))
    (tmp_path / PREFERENCES_FILE_NAME).write_text(text, encoding="utf-8")

    loaded = PreferencesStore(tmp_path).load()

    assert loaded.writable
    assert loaded.preferences.price_for("isoflurane") is None
    assert loaded.preferences.price_for("sevoflurane") == AgentPrice(
        agent_id="sevoflurane",
        bottle_price=240.34,
        bottle_volume_ml=250.0,
        currency="USD",
        applies_on=date(2008, 3, 5),
    )
    assert loaded.notice is not None
    # The refused price is named by the agent it gives, or by its place in the
    # file where it gives none as text.
    name = refused["agent"]
    named = f"Your {name} price: " if isinstance(name, str) else "Price 2 in the file: "
    assert named in loaded.notice
    assert reason in loaded.notice


def test_a_refused_price_is_written_back_unchanged_until_the_reader_replaces_it(
    tmp_path: Path,
) -> None:
    refused = {**SEVOFLURANE_PRICE_ENTRY, "agent": "isoflurane", "currency": "usd"}
    _write(tmp_path, _document([refused]))
    store = PreferencesStore(tmp_path)
    loaded = store.load()

    store.save(loaded.preferences.with_agent_cost_unit(AgentAmountUnit.LITRES_OF_VAPOUR))
    written = json.loads((tmp_path / PREFERENCES_FILE_NAME).read_text(encoding="utf-8"))

    assert written["agent_prices"] == [refused]

    store.save(store.load().preferences.with_price(ISOFLURANE_PRICE))
    reloaded = PreferencesStore(tmp_path).load()

    assert reloaded.notice is None
    assert reloaded.preferences.price_for("isoflurane") == ISOFLURANE_PRICE


@pytest.mark.parametrize("unit", ["millilitres of vapour", "mL", 3, None])
def test_a_refused_unit_falls_back_to_liquid_with_a_notice_and_is_kept(
    tmp_path: Path, unit: object
) -> None:
    _write(tmp_path, _document([SEVOFLURANE_PRICE_ENTRY], unit=unit))
    store = PreferencesStore(tmp_path)

    loaded = store.load()

    assert loaded.writable
    assert loaded.preferences.agent_cost_unit is AgentAmountUnit.MILLILITRES_OF_LIQUID
    assert loaded.notice is not None
    assert "How agent amounts are shown: " in loaded.notice
    assert loaded.preferences.price_for("sevoflurane") is not None

    store.save(loaded.preferences)
    written = json.loads((tmp_path / PREFERENCES_FILE_NAME).read_text(encoding="utf-8"))

    assert written["agent_cost_unit"] == unit


def test_the_notice_of_refused_preferences_says_what_the_reader_can_do(tmp_path: Path) -> None:
    """`PL-VT87`: the notice names each refused preference and why, then the way out.

    A refusal a user reads says what to do next (NUREG-0700 Rev. 3, guideline
    2.7.3-1). The expected sentences are written out here rather than read from
    the module, so a change to them fails this test.
    """
    refused_isoflurane = {**SEVOFLURANE_PRICE_ENTRY, "agent": "isoflurane", "currency": "usd"}
    refused_desflurane = {**SEVOFLURANE_PRICE_ENTRY, "agent": "desflurane", "bottle_price": 0}
    prices = [SEVOFLURANE_PRICE_ENTRY, refused_isoflurane, refused_desflurane]
    _write(tmp_path, _document(prices, unit="gallons"))

    notice = PreferencesStore(tmp_path).load().notice

    # Three refused entries, so a wrong separator between them shows. Each is
    # named first, then why it was refused.
    assert notice == (
        "These saved settings could not be used:\n"
        "• Your isoflurane price: the currency must be a three-letter code in capital letters, "
        "such as USD, and it is 'usd'.\n"
        "• Your desflurane price: the bottle price must be a number above zero, and it is 0.\n"
        "• How agent amounts are shown: 'gallons' is not one of the choices, millilitres of "
        "liquid or litres of vapour, so the View shows millilitres of liquid.\n"
        "Set them again in this View, or discard the refused entries below. "
        f"They are saved in {tmp_path / PREFERENCES_FILE_NAME}."
    )


def test_a_price_entry_that_is_not_an_object_is_refused_alone(tmp_path: Path) -> None:
    _write(tmp_path, _document(["isoflurane", SEVOFLURANE_PRICE_ENTRY]))

    loaded = PreferencesStore(tmp_path).load()

    assert loaded.writable
    assert loaded.preferences.price_for("sevoflurane") is not None
    assert loaded.notice is not None
    assert "Price 1 in the file: it is not a price" in loaded.notice


# ------------------------------------------------------------- the records


def test_a_price_entered_in_the_wrong_form_is_refused_where_it_is_built() -> None:
    with pytest.raises(
        SimulationConfigurationError, match="the bottle price must be a number above zero"
    ):
        AgentPrice("isoflurane", 0.0, 100.0, "USD", date(2008, 3, 5))

    with pytest.raises(SimulationConfigurationError, match="three-letter code in capital letters"):
        AgentPrice("isoflurane", 20.47, 100.0, "€", date(2008, 3, 5))

    with pytest.raises(TypeError, match="date"):
        AgentPrice("isoflurane", 20.47, 100.0, "USD", datetime(2008, 3, 5, 9, 0))


def test_a_unit_the_cost_view_does_not_offer_is_refused() -> None:
    with pytest.raises(SimulationConfigurationError, match="agent cost View shows"):
        Preferences().with_agent_cost_unit(AgentAmountUnit.MILLILITRES_OF_VAPOUR)


def test_a_price_keyed_under_another_agent_is_refused() -> None:
    with pytest.raises(SimulationConfigurationError, match="stored under 'sevoflurane'"):
        Preferences(agent_prices={"sevoflurane": ISOFLURANE_PRICE})


def test_setting_and_removing_a_price_leaves_the_other_agents_alone() -> None:
    sevoflurane = AgentPrice("sevoflurane", 240.34, 250.0, "USD", date(2008, 3, 5))
    preferences = Preferences().with_price(ISOFLURANE_PRICE).with_price(sevoflurane)
    newer = AgentPrice("isoflurane", 78.0, 100.0, "USD", date(2008, 3, 5))

    replaced = preferences.with_price(newer)
    removed = replaced.without_price("isoflurane")

    assert replaced.price_for("isoflurane") == newer
    assert replaced.price_for("sevoflurane") == sevoflurane
    assert removed.price_for("isoflurane") is None
    assert removed.price_for("sevoflurane") == sevoflurane
    assert preferences.price_for("isoflurane") == ISOFLURANE_PRICE


def test_a_refused_entry_that_names_no_agent_is_dropped_only_when_the_reader_discards_it(
    tmp_path: Path,
) -> None:
    nameless = {key: value for key, value in SEVOFLURANE_PRICE_ENTRY.items() if key != "agent"}
    _write(tmp_path, _document([nameless], unit="mL"))
    store = PreferencesStore(tmp_path)
    loaded = store.load()

    store.save(loaded.preferences.without_price("sevoflurane"))
    kept = json.loads((tmp_path / PREFERENCES_FILE_NAME).read_text(encoding="utf-8"))

    assert kept["agent_prices"] == [nameless]
    assert kept["agent_cost_unit"] == "mL"

    store.save(store.load().preferences.without_refused_entries())
    reloaded = PreferencesStore(tmp_path).load()

    assert reloaded.notice is None
    assert reloaded.preferences.agent_cost_unit is AgentAmountUnit.MILLILITRES_OF_LIQUID


def test_preferences_say_whether_they_keep_a_refused_entry(tmp_path: Path) -> None:
    """A refused price or a refused unit is a kept entry, and discarding leaves none (`PL-7KXN`)."""

    nameless = {key: value for key, value in SEVOFLURANE_PRICE_ENTRY.items() if key != "agent"}
    _write(tmp_path, _document([nameless]))
    refused_price = PreferencesStore(tmp_path).load().preferences
    _write(tmp_path, _document([], unit="mL"))
    refused_unit = PreferencesStore(tmp_path).load().preferences

    assert not Preferences().holds_refused_entries
    assert refused_price.refused_unit is None
    assert refused_price.holds_refused_entries
    assert refused_unit.refused_prices == ()
    assert refused_unit.holds_refused_entries
    assert not refused_price.without_refused_entries().holds_refused_entries
    assert not refused_unit.without_refused_entries().holds_refused_entries


def test_a_refused_entry_nested_to_the_limit_is_kept_and_written_back(tmp_path: Path) -> None:
    """Six lists inside the price list, eight levels in all, is the deepest the store keeps."""

    nested: object = []
    for _ in range(5):
        nested = [nested]
    _write(tmp_path, _document([nested]))
    store = PreferencesStore(tmp_path)
    loaded = store.load()

    assert loaded.writable
    assert loaded.preferences.refused_prices[0].raw == nested

    store.save(loaded.preferences.with_agent_cost_unit(AgentAmountUnit.LITRES_OF_VAPOUR))

    saved = json.loads((tmp_path / PREFERENCES_FILE_NAME).read_text(encoding="utf-8"))
    assert saved["agent_prices"] == [nested]


def test_a_save_holding_text_that_is_not_valid_unicode_is_refused_and_writes_nothing(
    tmp_path: Path,
) -> None:
    """Load refuses such a file, so this reaches the save's own guard through a built record."""

    store = PreferencesStore(tmp_path)
    store.load()
    preferences = Preferences(refused_prices=(RefusedEntry("\ud800", "a reason", None),))

    with pytest.raises(PreferencesFileError, match="not valid Unicode"):
        store.save(preferences)

    assert list(tmp_path.iterdir()) == []


# ------------------------------------------------- what each save leaves behind


def test_each_change_in_a_session_is_saved_without_loading_again(tmp_path: Path) -> None:
    """A store loaded once accepts a second save, and the file then holds the second change.

    The dashboard loads the store once, at launch, and saves at every change
    of preference. If a save left the store unready for the next one, every
    change after the first would last only until the application closed.
    """

    store = PreferencesStore(tmp_path)
    store.load()
    store.save(Preferences().with_price(ISOFLURANE_PRICE))
    store.save(
        Preferences()
        .with_price(ISOFLURANE_PRICE)
        .with_agent_cost_unit(AgentAmountUnit.LITRES_OF_VAPOUR)
    )

    reloaded = PreferencesStore(tmp_path).load()

    assert reloaded.notice is None
    assert reloaded.preferences.price_for("isoflurane") == ISOFLURANE_PRICE
    assert reloaded.preferences.agent_cost_unit is AgentAmountUnit.LITRES_OF_VAPOUR


def test_choosing_a_unit_replaces_a_refused_unit_in_the_file(tmp_path: Path) -> None:
    """A unit the reader chooses is what the file holds next, not the refused unit it replaces.

    A refused unit is written back unchanged until the reader sets a unit in
    its place. Once they have, the refused one has no further use. If it
    were kept, the next launch would refuse it again, and the agent cost View
    would show millilitres of liquid rather than the unit the reader chose.
    """

    _write(tmp_path, _document([], unit="mL"))
    store = PreferencesStore(tmp_path)
    loaded = store.load()

    store.save(loaded.preferences.with_agent_cost_unit(AgentAmountUnit.LITRES_OF_VAPOUR))
    reloaded = PreferencesStore(tmp_path).load()

    assert reloaded.notice is None
    assert reloaded.preferences.agent_cost_unit is AgentAmountUnit.LITRES_OF_VAPOUR


def test_removing_a_price_also_discards_that_agents_refused_entry(tmp_path: Path) -> None:
    """Removing an agent's price drops its refused entry too, and keeps every other refused entry.

    The reader removes a price to have none for that agent, refused or valid.
    A refused entry left behind would be written back at every save and named
    in the notice at every launch. The file holds three refused entries, so
    that the test can tell a removal of the one entry from a removal of the
    first or of all of them.
    """

    isoflurane = {**SEVOFLURANE_PRICE_ENTRY, "agent": "isoflurane", "currency": "usd"}
    sevoflurane = {**SEVOFLURANE_PRICE_ENTRY, "currency": "usd"}
    nameless = {key: value for key, value in SEVOFLURANE_PRICE_ENTRY.items() if key != "agent"}
    _write(tmp_path, _document([isoflurane, sevoflurane, nameless]))
    store = PreferencesStore(tmp_path)
    loaded = store.load()

    store.save(loaded.preferences.without_price("isoflurane"))
    written = json.loads((tmp_path / PREFERENCES_FILE_NAME).read_text(encoding="utf-8"))

    assert written["agent_prices"] == [sevoflurane, nameless]


def test_the_saved_file_is_written_for_a_person_to_read(tmp_path: Path) -> None:
    """The file holds one value to a line, indented by two spaces, with each character as itself.

    A file that this build cannot check is left as it is for the reader to
    repair by hand, so the store writes the file in the form a person reads.
    The refused unit "µL" stands for text the reader typed, which the file
    keeps as written rather than as an escape. The expected text is written
    out by hand.
    """

    _write(tmp_path, _document([], unit="µL"))
    store = PreferencesStore(tmp_path)
    loaded = store.load()

    path = store.save(loaded.preferences.with_price(ISOFLURANE_PRICE))

    assert path.read_text(encoding="utf-8") == (
        "{\n"
        '  "schema_version": 1,\n'
        '  "agent_cost_unit": "µL",\n'
        '  "agent_prices": [\n'
        "    {\n"
        '      "agent": "isoflurane",\n'
        '      "bottle_price": 20.47,\n'
        '      "bottle_volume_ml": 100.0,\n'
        '      "currency": "USD",\n'
        '      "applies_on": "2008-03-05"\n'
        "    }\n"
        "  ]\n"
        "}\n"
    )


# ------------------------------------------------- what a load refuses, and where


def _nested_lists(count: int) -> object:
    nested: object = []

    for _ in range(count - 1):
        nested = [nested]

    return nested


@pytest.mark.parametrize(
    ("document", "reason"),
    [
        (_document([{**SEVOFLURANE_PRICE_ENTRY, "agent": "\ud800"}]), "not valid Unicode"),
        (_document([SEVOFLURANE_PRICE_ENTRY], unit="\ud800"), "not valid Unicode"),
        (_document([_nested_lists(7), SEVOFLURANE_PRICE_ENTRY]), "more than 8 deep"),
    ],
    ids=[
        "a lone surrogate in a price's agent field",
        "a lone surrogate as the unit, beside a valid price",
        "seven nested lists, one past the deepest kept, before a valid price",
    ],
)
def test_what_could_not_be_written_back_turns_saving_off_wherever_it_sits(
    tmp_path: Path, document: object, reason: str
) -> None:
    """A lone surrogate or a list nested too deep anywhere in the file turns saving off.

    A save writes each refused entry back unchanged. Such an entry could not
    be written to a UTF-8 file, or would grow without bound, so the whole
    file is refused when it is read, wherever in the file the entry sits. In
    each case here a valid price sits beside it, and the check must not stop
    at the price's plain text and numbers. `writable` is a bool, and here it
    is False.
    """

    path = _write(tmp_path, document)
    text = path.read_text(encoding="utf-8")

    loaded = PreferencesStore(tmp_path).load()

    assert loaded.writable is False
    assert dict(loaded.preferences.agent_prices) == {}
    assert loaded.notice is not None
    assert reason in loaded.notice
    assert path.read_text(encoding="utf-8") == text


def test_a_price_whose_agent_is_not_text_is_refused_alone_and_names_no_agent(
    tmp_path: Path,
) -> None:
    """An entry that gives its agent as a number or a list is refused, and the load goes on.

    Such an entry names no agent, so it does not count as a second price for
    one, and the refused entry records no agent. A load never raises because
    of what the file holds. The file holds two entries with the same number
    and one with a list, beside a valid sevoflurane price.
    """

    numbered = {**SEVOFLURANE_PRICE_ENTRY, "agent": 3}
    listed = {**SEVOFLURANE_PRICE_ENTRY, "agent": ["isoflurane"]}
    _write(tmp_path, _document([numbered, numbered, listed, SEVOFLURANE_PRICE_ENTRY]))

    loaded = PreferencesStore(tmp_path).load()

    assert loaded.writable
    assert loaded.preferences.price_for("sevoflurane") == AgentPrice(
        agent_id="sevoflurane",
        bottle_price=240.34,
        bottle_volume_ml=250.0,
        currency="USD",
        applies_on=date(2008, 3, 5),
    )
    assert [entry.agent_id for entry in loaded.preferences.refused_prices] == [None, None, None]
    assert loaded.notice is not None
    assert all(f"Price {number} in the file: " in loaded.notice for number in (1, 2, 3))


def test_a_file_holding_text_beyond_ascii_is_read_whatever_the_platform_encoding_is(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A file holding "€" is read as UTF-8 where the platform's own encoding is ASCII.

    The store writes its file as UTF-8 and writes each character as itself,
    so a refused entry with a currency typed as "€" sits in the file as
    UTF-8. Read in the platform's own encoding, such a file would be refused
    at the next launch and saving would be turned off. The load runs with
    `make_the_platform_encoding_ascii` standing for a platform whose locale is
    ASCII.
    """

    refused = {**SEVOFLURANE_PRICE_ENTRY, "agent": "isoflurane", "currency": "€"}
    document = json.dumps(_document([refused]), ensure_ascii=False)
    (tmp_path / PREFERENCES_FILE_NAME).write_text(document, encoding="utf-8")
    make_the_platform_encoding_ascii(monkeypatch)

    loaded = PreferencesStore(tmp_path).load()

    assert loaded.writable
    assert [entry.raw for entry in loaded.preferences.refused_prices] == [refused]
