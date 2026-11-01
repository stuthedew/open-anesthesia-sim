"""Tests for the reader's preferences file, `app/preferences.py` (`PL-93B3`).

Every expected document below is written out by hand rather than produced by
the code under test. A "restart" is a second `PreferencesStore` built on the
same directory, which reads only what the first one wrote to disk.
"""

import json
from datetime import date, datetime
from pathlib import Path

import pytest

from anesthesia_sim.app.formatting import AgentAmountUnit
from anesthesia_sim.app.preferences import (
    PREFERENCES_FILE_NAME,
    AgentPrice,
    Preferences,
    PreferencesFileError,
    PreferencesStore,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError

# Gas Man's default isoflurane price is US$20.47 for a 100 mL bottle, "as of March 5,
# 2008" (Philip JH, *Workbook for Gas Man*, Appendix C, printed p. 171, and
# printed p. 105). `docs/MODEL.md` § "A cost at the reader's price" quotes it.
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


def test_a_price_and_a_unit_survive_a_restart(tmp_path: Path) -> None:
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
        ("agent", "halothane", "not a shipped agent"),
        ("bottle_price", 0, "bottle price"),
        ("bottle_price", -20.47, "bottle price"),
        ("bottle_price", "20.47", "bottle price"),
        ("bottle_price", True, "bottle price"),
        ("bottle_volume_ml", 0.0, "bottle volume"),
        ("currency", "usd", "three capital"),
        ("currency", "US", "three capital"),
        ("currency", "USDX", "three capital"),
        ("currency", "$", "three capital"),
        ("applies_on", "2008-02-30", "not a real calendar date"),
        ("applies_on", "03/05/2008", "YYYY-MM-DD"),
        ("applies_on", "20080305", "YYYY-MM-DD"),
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
    assert "agent_prices[1]" in loaded.notice
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
    assert "agent cost unit" in loaded.notice
    assert loaded.preferences.price_for("sevoflurane") is not None

    store.save(loaded.preferences)
    written = json.loads((tmp_path / PREFERENCES_FILE_NAME).read_text(encoding="utf-8"))

    assert written["agent_cost_unit"] == unit


def test_a_price_entry_that_is_not_an_object_is_refused_alone(tmp_path: Path) -> None:
    _write(tmp_path, _document(["isoflurane", SEVOFLURANE_PRICE_ENTRY]))

    loaded = PreferencesStore(tmp_path).load()

    assert loaded.writable
    assert loaded.preferences.price_for("sevoflurane") is not None
    assert loaded.notice is not None
    assert "agent_prices[0]" in loaded.notice


# ------------------------------------------------------------- the records


def test_a_price_entered_in_the_wrong_form_is_refused_where_it_is_built() -> None:
    with pytest.raises(SimulationConfigurationError, match="isoflurane bottle price"):
        AgentPrice("isoflurane", 0.0, 100.0, "USD", date(2008, 3, 5))

    with pytest.raises(SimulationConfigurationError, match="three capital letters"):
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
