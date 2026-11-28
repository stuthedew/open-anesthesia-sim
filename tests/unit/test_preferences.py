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

from anesthesia_sim.app.formatting import AgentAmountUnit, ChartCeiling
from anesthesia_sim.app.preferences import (
    PREFERENCES_FILE_NAME,
    PREFERENCES_SCHEMA_VERSION,
    AgentPrice,
    Preferences,
    PreferencesFileError,
    PreferencesStore,
    RefusedEntry,
    chart_ceiling_notice,
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
        "schema_version": 2,
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
        "chart_axis_top_mac": 3.0,
    }
    assert sorted(entry.name for entry in tmp_path.iterdir()) == [PREFERENCES_FILE_NAME]


@pytest.mark.parametrize(
    ("ceiling", "written"),
    [(ChartCeiling.LOW, 1.5), (ChartCeiling.STANDARD, 3.0), (ChartCeiling.HIGH, 4.5)],
    ids=["1.5 xMAC", "3 xMAC", "4.5 xMAC"],
)
def test_the_axis_top_is_saved_as_its_mac_multiple_and_survives_a_restart(
    tmp_path: Path, ceiling: ChartCeiling, written: float
) -> None:
    """Every chart and schematic shares one top, which the file keeps across a restart (`PL-7LZ7`).

    The expected multiples are the three tops that `docs/INTERFACE.md` § "The
    chart's fixed MAC axis" lists.
    """

    store = PreferencesStore(tmp_path)
    store.load()
    path = store.save(Preferences().with_chart_ceiling(ceiling))

    assert json.loads(path.read_text(encoding="utf-8"))["chart_axis_top_mac"] == written

    loaded = PreferencesStore(tmp_path).load()

    assert loaded.notice is None
    assert loaded.writable
    assert loaded.preferences.chart_ceiling is ceiling
    assert chart_ceiling_notice(loaded.preferences) is None


def test_a_version_1_file_opens_at_the_standard_top_and_its_next_save_writes_version_2(
    tmp_path: Path,
) -> None:
    """A file written before the top was a preference has none, and is not refused for it.

    v0.6.22 to v0.6.24 wrote version 1. The file's prices and unit are kept,
    and the next save adds the top.
    """

    _write(tmp_path, _document([SEVOFLURANE_PRICE_ENTRY], unit="litres of vapour"))
    store = PreferencesStore(tmp_path)
    loaded = store.load()

    assert loaded.notice is None
    assert loaded.writable
    assert loaded.preferences.chart_ceiling is ChartCeiling.STANDARD
    assert loaded.preferences.refused_chart_ceiling is None

    path = store.save(loaded.preferences)

    assert json.loads(path.read_text(encoding="utf-8")) == {
        "schema_version": 2,
        "agent_cost_unit": "litres of vapour",
        "agent_prices": [SEVOFLURANE_PRICE_ENTRY],
        "chart_axis_top_mac": 3.0,
    }


@pytest.mark.parametrize("written", [1.5, 3, 3.0, 4.5], ids=["1.5", "3 as int", "3.0", "4.5"])
def test_a_saved_top_is_read_whether_written_as_an_int_or_a_float(
    tmp_path: Path, written: float
) -> None:
    _write(tmp_path, {**_document([]), "schema_version": 2, "chart_axis_top_mac": written})

    loaded = PreferencesStore(tmp_path).load()

    assert loaded.preferences.chart_ceiling.value == written
    assert loaded.preferences.refused_chart_ceiling is None


@pytest.mark.parametrize(
    ("raw", "shown"),
    [
        (7, "7"),
        (2.0, "2.0"),
        (0, "0"),
        ("4.5", '"4.5"'),
        (True, "true"),
        (None, "null"),
        ([4.5], "[4.5]"),
    ],
    ids=["7", "2.0", "0", "the text 4.5", "true", "null", "a list"],
)
def test_a_saved_top_off_the_choices_is_refused_named_on_the_charts_and_kept(
    tmp_path: Path, raw: object, shown: str
) -> None:
    """A refused top falls back to 3 xMAC, and the charts say so until the reader picks one.

    The notice is written out by hand. The agent cost View's notice and its
    offer to discard do not name the top, because the top is not set there.
    `True` is refused although it equals 1 in Python, and the text "4.5" is
    refused although it reads as a top. The value is shown as the file holds
    it, so the text "4.5" is in quotes and the sentence says the top is a
    number.
    """

    _write(tmp_path, {**_document([]), "schema_version": 2, "chart_axis_top_mac": raw})
    store = PreferencesStore(tmp_path)
    loaded = store.load()
    preferences = loaded.preferences

    assert loaded.writable
    assert loaded.notice is None
    assert preferences.chart_ceiling is ChartCeiling.STANDARD
    assert chart_ceiling_notice(preferences) == (
        f"The saved axis top, {shown}, is not one of the numbers 1.5, 3 or 4.5 ×MAC, so every "
        "chart and schematic shows 3 ×MAC. Choose a top to replace it."
    )
    assert not preferences.holds_refused_entries
    assert preferences.without_refused_entries().refused_chart_ceiling is not None

    path = store.save(preferences.with_price(ISOFLURANE_PRICE))

    assert json.loads(path.read_text(encoding="utf-8"))["chart_axis_top_mac"] == raw

    picked = PreferencesStore(tmp_path).load().preferences.with_chart_ceiling(ChartCeiling.LOW)

    assert chart_ceiling_notice(picked) is None
    assert picked.chart_ceiling is ChartCeiling.LOW


def test_a_top_that_is_not_a_chart_ceiling_is_refused() -> None:
    with pytest.raises(TypeError, match="the axis top is a ChartCeiling, not float"):
        Preferences(chart_ceiling=3.0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="the axis top is a ChartCeiling, not str"):
        Preferences().with_chart_ceiling("HIGH")  # type: ignore[arg-type]


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
    path = _write(tmp_path, {"schema_version": 3, "anything": "a newer build wrote"})
    before = path.read_bytes()
    store = PreferencesStore(tmp_path)

    loaded = store.load()

    assert not loaded.writable
    assert dict(loaded.preferences.agent_prices) == {}
    # `PL-W312`: what went wrong, what it means, what the reader can do, and
    # the path last, in the reader's words. The sentences are written out here
    # rather than read from the module, so a change to them fails this test.
    assert loaded.notice == (
        "The application could not use your preferences file, because a newer version of the "
        "application saved the file as version 3, and this version reads files up to version 2. "
        f"{_UNUSABLE_EFFECT} To use your saved settings, open the newer version of the "
        "application. To start again without them, move the file out of its folder, then "
        f"restart this version. The file is {path}."
    )
    with pytest.raises(PreferencesFileError, match="saving is off"):
        store.save(Preferences().with_price(ISOFLURANE_PRICE))
    assert path.read_bytes() == before


#: What the notice for a file that cannot be used at all says after its
#: reason, written out rather than read from the module (`PL-W312`).
_UNUSABLE_EFFECT = (
    "None of your saved settings is in use, and the application does not save changes you "
    "make now, so the file stays as it is."
)
_UNUSABLE_NEXT_STEP = (
    "To use your saved settings again, correct the file, then restart the application. To "
    "start again without them, move the file out of its folder, then restart the application."
)


@pytest.mark.parametrize(
    ("text", "reason"),
    [
        (
            "{not json",
            "the file's text at line 1, column 2 is not in the format that the application saves",
        ),
        (
            '{"schema_version": 2,\n "agent_cost_unit": "millilitres of liquid",\n "agent_prices"',
            "the file's text at line 3, column 16 is not in the format that the application saves",
        ),
        ("", "the file is empty"),
        (" \n\t", "the file is empty"),
        (
            "[]",
            "the file does not hold a set of named settings, which is how the application "
            "saves them",
        ),
        ('{"schema_version": 0}', "the file's version, 0, is not a whole number from 1 up"),
        ('{"schema_version": true}', "the file's version, true, is not a whole number from 1 up"),
        ('{"schema_version": 1.5}', "the file's version, 1.5, is not a whole number from 1 up"),
        ('{"schema_version": 0.0}', "the file's version, 0.0, is not a whole number from 1 up"),
        (
            '{"schema_version": 2.0}',
            "the file's version, 2.0, is written with a decimal point, and the application reads "
            "a version only as a whole number written without one, such as 2",
        ),
        (
            '{"schema_version": 1.0}',
            "the file's version, 1.0, is written with a decimal point, and the application reads "
            "a version only as a whole number written without one, such as 1",
        ),
        ('{"agent_cost_unit": "millilitres of liquid"}', "the file gives no version"),
        (
            '{"schema_version": 1, "agent_cost_unit": "millilitres of liquid"}',
            "the file has no agent prices",
        ),
        (
            '{"schema_version": 1, "agent_cost_unit": "millilitres of liquid", '
            '"agent_prices": [], "theme": "dark"}',
            "the file holds settings that a version 1 file does not have: 'theme'",
        ),
        (
            '{"schema_version": 2, "agent_cost_unit": "millilitres of liquid", "agent_prices": []}',
            "the file has no axis top",
        ),
        (
            '{"schema_version": 1, "agent_cost_unit": "millilitres of liquid", '
            '"agent_prices": [], "chart_axis_top_mac": 3.0}',
            "the file holds settings that a version 1 file does not have: 'chart_axis_top_mac'",
        ),
        (
            '{"schema_version": 2, "colour": "red", "theme": "dark"}',
            "the file has no agent prices, no axis top and no choice of how agent amounts are "
            "shown, and holds settings that a version 2 file does not have: 'colour', 'theme'",
        ),
        (
            '{"schema_version": 1, "schema_version": 1, '
            '"agent_cost_unit": "millilitres of liquid", "agent_prices": []}',
            "the file writes the setting 'schema_version' twice in one place",
        ),
        (
            '{"schema_version": 1, "agent_cost_unit": "millilitres of liquid", "agent_prices": {}}',
            "the file's agent prices are not written as a list, which is how the application saves "
            "them",
        ),
        (
            '{"schema_version": 1, "agent_cost_unit": "millilitres of liquid", '
            '"agent_prices": [{"agent": "isoflurane", "bottle_price": NaN, '
            '"bottle_volume_ml": 100, "currency": "USD", "applies_on": "2008-03-05"}]}',
            "the file holds NaN, which is not a number a preference can hold",
        ),
        (
            '{"schema_version": 1, "agent_cost_unit": "millilitres of liquid", '
            '"agent_prices": [{"agent": "isoflurane", "bottle_price": 20.47, '
            '"bottle_volume_ml": 1e400, "currency": "USD", "applies_on": "2008-03-05"}]}',
            "the file holds 1e400, which is too large to be a number a preference can hold",
        ),
        (
            '{"schema_version": 1, "agent_cost_unit": "millilitres of liquid", '
            '"agent_prices": [{"agent": "isoflurane", "bottle_price": 20.47, '
            '"bottle_volume_ml": -' + "1" * 5000 + ', "currency": "USD", '
            '"applies_on": "2008-03-05"}]}',
            "the file holds a whole number 5,000 digits long, which is too long to be a number a "
            "preference can hold",
        ),
        (
            '{"schema_version": 1, "agent_cost_unit": "millilitres of liquid", '
            '"agent_prices": ["\\ud800"]}',
            "the file holds text that is not valid Unicode, so the application could not save it "
            "back unchanged",
        ),
        (
            '{"schema_version": 1, "agent_cost_unit": "millilitres of liquid", '
            '"agent_prices": [' + "[" * 8 + "]" * 8 + "]}",
            "the file's entries are nested more than 8 levels deep, and no preferences file "
            "that the application saves is",
        ),
    ],
    ids=[
        "not JSON",
        "cut off on line 3",
        "empty",
        "only blank space",
        "not an object",
        "version 0",
        "version true",
        "version 1.5",
        "version 0.0",
        "version 2.0",
        "version 1.0",
        "no version",
        "a key missing",
        "an unknown key",
        "a version 2 file with no top",
        "a version 1 file with a top",
        "three keys missing and two unknown",
        "a repeated key",
        "prices not a list",
        "NaN",
        "a number too large for a float",
        "a whole number too long to read",
        "a lone surrogate, which no UTF-8 file can hold",
        "a refused entry nested past the limit",
    ],
)
def test_a_document_that_cannot_be_checked_entry_by_entry_turns_saving_off(
    tmp_path: Path, text: str, reason: str
) -> None:
    """The notice says what is wrong in the reader's words, then what to do (`PL-W312`).

    No setting is named in Python's list notation. A missing setting is named
    as the View names it, and a setting the file's version does not have is
    named as the file writes it.
    """

    path = tmp_path / PREFERENCES_FILE_NAME
    path.write_text(text, encoding="utf-8")

    loaded = PreferencesStore(tmp_path).load()

    assert not loaded.writable
    assert dict(loaded.preferences.agent_prices) == {}
    assert loaded.notice == (
        f"The application could not use your preferences file, because {reason}. "
        f"{_UNUSABLE_EFFECT} {_UNUSABLE_NEXT_STEP} The file is {path}."
    )
    assert "[" not in loaded.notice
    assert path.read_text(encoding="utf-8") == text


#: What the notice says is missing from a file that holds only its version, for
#: each version this build reads, in the words the Views use (`PL-W312`).
_EVERY_SETTING_MISSING = {
    1: "no agent prices and no choice of how agent amounts are shown",
    2: "no agent prices, no axis top and no choice of how agent amounts are shown",
}


def test_every_version_this_build_reads_has_a_case_of_every_setting_missing() -> None:
    """A version added without a case below fails here, so its settings are checked too."""

    assert sorted(_EVERY_SETTING_MISSING) == list(range(1, PREFERENCES_SCHEMA_VERSION + 1))


@pytest.mark.parametrize(("version", "missing"), _EVERY_SETTING_MISSING.items())
def test_a_file_that_holds_only_its_version_names_every_setting_it_lacks(
    tmp_path: Path, version: int, missing: str
) -> None:
    """Each setting of each version has words for the notice that names it as missing.

    A setting added to a version without its words would make the store raise
    on such a file, although a load never raises because of what the file
    holds (blind review of `PL-W312`).
    """

    path = _write(tmp_path, {"schema_version": version})

    loaded = PreferencesStore(tmp_path).load()

    assert not loaded.writable
    assert loaded.notice == (
        f"The application could not use your preferences file, because the file has {missing}. "
        f"{_UNUSABLE_EFFECT} {_UNUSABLE_NEXT_STEP} The file is {path}."
    )


def test_a_file_nested_too_deeply_for_the_decoder_turns_saving_off(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A file the decoder gives up on is named as nested too deeply, in the reader's words.

    How deep the decoder can go depends on the stack of the platform and the
    thread it runs on. A file of 100,000 nested lists stopped it here and
    parsed under the mutation run's copy in CI. So the test makes the decoder
    give up, as it does on such a file.
    """

    path = _write(tmp_path, {"schema_version": PREFERENCES_SCHEMA_VERSION})

    def give_up(*args: object, **kwargs: object) -> object:
        raise RecursionError("maximum recursion depth exceeded while decoding a JSON array")

    monkeypatch.setattr(json, "loads", give_up)

    loaded = PreferencesStore(tmp_path).load()

    assert not loaded.writable
    assert loaded.notice == (
        "The application could not use your preferences file, because the file's entries are "
        f"nested too deeply for the application to read them. {_UNUSABLE_EFFECT} "
        f"{_UNUSABLE_NEXT_STEP} The file is {path}."
    )


def test_two_prices_for_one_agent_turn_saving_off(tmp_path: Path) -> None:
    _write(tmp_path, _document([SEVOFLURANE_PRICE_ENTRY, SEVOFLURANE_PRICE_ENTRY]))

    loaded = PreferencesStore(tmp_path).load()

    assert not loaded.writable
    assert loaded.notice is not None
    assert loaded.notice.startswith(
        "The application could not use your preferences file, because the file holds two prices "
        "for sevoflurane, so the application cannot tell which one applies. "
    )


def test_a_file_that_is_not_utf8_turns_saving_off(tmp_path: Path) -> None:
    (tmp_path / PREFERENCES_FILE_NAME).write_bytes(b'{"schema_version": 1, "x": "\xff"}')

    loaded = PreferencesStore(tmp_path).load()

    assert not loaded.writable
    assert loaded.notice is not None
    assert loaded.notice.startswith(
        "The application could not use your preferences file, because the file's text is not in "
        "UTF-8, the encoding that the application saves. "
    )


def test_a_file_that_cannot_be_read_turns_saving_off(tmp_path: Path) -> None:
    (tmp_path / PREFERENCES_FILE_NAME).mkdir()

    loaded = PreferencesStore(tmp_path).load()

    assert not loaded.writable
    assert loaded.notice is not None
    assert loaded.notice.startswith(
        "The application could not use your preferences file, because the file could not be read ("
    )


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


_WITHOUT_CURRENCY = {
    key: value for key, value in SEVOFLURANE_PRICE_ENTRY.items() if key != "currency"
}


@pytest.mark.parametrize(
    ("refused", "line"),
    [
        (
            {"agent": "isoflurane"},
            "• Your isoflurane price: it has no date, bottle price, bottle volume or currency.",
        ),
        (
            {**_WITHOUT_CURRENCY, "agent": "isoflurane", "colour": "red", "size": 1},
            "• Your isoflurane price: it has no currency, and it holds entries the simulator "
            "does not use: 'colour', 'size'.",
        ),
        (
            {**SEVOFLURANE_PRICE_ENTRY, "agent": "isoflurane", "currency": 7},
            "• Your isoflurane price: the currency must be a three-letter code in capital "
            "letters, such as USD, and it is 7.",
        ),
        (
            {**SEVOFLURANE_PRICE_ENTRY, "agent": "isoflurane", "bottle_price": "20.47"},
            "• Your isoflurane price: the bottle price must be a number above zero, and it is "
            "'20.47'.",
        ),
        (
            {**SEVOFLURANE_PRICE_ENTRY, "agent": "isoflurane", "bottle_volume_ml": 0},
            "• Your isoflurane price: the bottle volume in millilitres of liquid must be a "
            "number above zero, and it is 0.",
        ),
        (
            {**SEVOFLURANE_PRICE_ENTRY, "agent": "isoflurane", "applies_on": "03/05/2008"},
            "• Your isoflurane price: the date must be written as year-month-day, such as "
            "2008-03-05, and it is '03/05/2008'.",
        ),
        (
            {**SEVOFLURANE_PRICE_ENTRY, "agent": "halothane"},
            "• Your halothane price: the simulator has no agent called 'halothane'; it has "
            "desflurane, isoflurane, sevoflurane.",
        ),
        (
            {**SEVOFLURANE_PRICE_ENTRY, "agent": 7},
            "• Price 2 in the file: the agent must be named in words, and it is 7.",
        ),
    ],
)
def test_each_refused_price_is_explained_in_the_words_the_view_uses(
    tmp_path: Path, refused: dict[str, object], line: str
) -> None:
    """`PL-VT87`: a refused price names the field as the View does, and the value.

    The Microsoft Windows error-message guidelines ask for a message in the
    user's terms, with specific names and values. The expected lines are written
    out here rather than read from the module, so a change to one fails this
    test. The first case lists four missing fields, so a wrong join shows.
    """
    _write(tmp_path, _document([SEVOFLURANE_PRICE_ENTRY, refused]))

    notice = PreferencesStore(tmp_path).load().notice

    assert notice is not None
    assert line in notice.splitlines()


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
        '  "schema_version": 2,\n'
        '  "agent_cost_unit": "µL",\n'
        '  "agent_prices": [\n'
        "    {\n"
        '      "agent": "isoflurane",\n'
        '      "bottle_price": 20.47,\n'
        '      "bottle_volume_ml": 100.0,\n'
        '      "currency": "USD",\n'
        '      "applies_on": "2008-03-05"\n'
        "    }\n"
        "  ],\n"
        '  "chart_axis_top_mac": 3.0\n'
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
        (_document([_nested_lists(7), SEVOFLURANE_PRICE_ENTRY]), "more than 8 levels deep"),
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
