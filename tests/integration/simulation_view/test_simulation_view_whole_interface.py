"""The dashboard, driven headless against real runs.

These tests cover the whole interface walked at once.

`simulation_view_support.py` describes the whole suite.
"""

import re

import pytest
from PySide6.QtWidgets import QApplication

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.formatting import format_mac_awake_reference, format_mac_reference
from anesthesia_sim.app_metadata import APP_DISPLAY_NAME
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES, load_agent_parameters
from tests.integration.simulation_view.simulation_view_support import (
    _ALVEOLAR_METRIC_QUALIFIER,
    _UNHEDGED_END_TIDAL,
    _advance,
    _concentration,
    _interface_strings,
    _shown_view,
    _strings_between,
    _unhedged_wake_predictions,
    _visible_strings,
    _wash_in,
)

# ------------------------------------------- the whole interface, walked


def test_the_page_leaves_the_application_name_to_the_window_title(
    application: QApplication,
) -> None:
    """The page no longer restates the name the window's title bar carries (`PL-J8K2` Q2).

    `PL-HK75` put the name on screen from `app_metadata`. The name is now in
    the title bar, and `test_bootstrap` checks that the window title shows
    it. The in-page title row cost 44 px that the chart cannot spare on a
    laptop (`PL-84QX`).
    """

    view = _shown_view(application, SimulationController())

    assert APP_DISPLAY_NAME not in _interface_strings(view)


def test_no_interface_string_drops_the_end_tidal_equivalent_hedge(
    application: QApplication,
) -> None:
    """`PL-NV9W`: nothing on screen says "end-tidal" without "-equivalent"."""

    strings = _interface_strings(_shown_view(application, SimulationController()))

    for value in strings:
        assert _UNHEDGED_END_TIDAL.search(value) is None, value

    assert _ALVEOLAR_METRIC_QUALIFIER in strings, (
        "the interface walk did not reach the concentration readouts, so the assertion "
        "above proved nothing"
    )


def test_the_interface_states_the_mac_divisor_and_writes_the_unit_as_a_ratio(
    application: QApplication,
) -> None:
    view = _shown_view(application, SimulationController())
    strings = _visible_strings(view)

    assert "1 MAC sevoflurane = 2.0%" in " ".join(sorted(strings))
    # The readouts write the unit as a ratio, never as a bare "MAC".
    assert any(value.endswith(" ×MAC") for value in strings)


def test_the_screen_states_the_band_fraction_and_the_divisor_for_every_agent(
    application: QApplication,
) -> None:
    """`PL-F52R`: both free parameters are named on screen, for every agent."""

    for agent_id in AGENT_DATA_FILENAMES:
        agent = load_agent_parameters(agent_id)
        view = _shown_view(application, SimulationController(agent_id=agent_id))
        strings = _visible_strings(view)

        assert (
            format_mac_awake_reference(
                agent.display_name,
                fraction_of_mac=agent.mac_awake.fraction_of_mac,
                standard_deviation_fraction_of_mac=agent.mac_awake.standard_deviation_fraction_of_mac,
                mac_percent=agent.mac_percent,
            )
            in strings
        )
        assert format_mac_reference(agent.display_name, agent.mac_percent) in strings


def test_the_interface_says_which_trace_the_band_is_read_against(application: QApplication) -> None:
    prose = " ".join(_visible_strings(_shown_view(application, SimulationController())))

    assert "vessel-rich trace" in prose
    assert "±1 SD" in prose
    assert "population" in prose


def test_nothing_between_the_chart_heading_and_the_plot_is_a_sentence(
    application: QApplication,
) -> None:
    """`PL-6580`: the panel above the compartment plot is legend and labels, not prose.

    The two state advisories are exempt, and the walk skips them by identity.
    They are empty here and show text only when they apply. That is the
    distinction this test draws: a message at the moment of need is not a
    standing paragraph.
    """

    view = _shown_view(application, SimulationController())
    strings = _strings_between(
        None,
        _concentration(view).chart,
        skip=(
            _concentration(view).hidden_traces_text,
            *_concentration(view).off_scale.lines,
            *_concentration(view).unmarked_changes.lines,
        ),
    )

    for value in strings:
        assert ". " not in value, value
        assert not value.rstrip().endswith("."), value

    joined = " ".join(sorted(strings))
    assert "1 MAC sevoflurane = 2.0%" in joined
    assert "read against vessel-rich trace" in joined
    assert "1 MAC, reference adult (alveolar)" in joined
    assert "Compartments:" in joined
    assert "Clinical references:" in joined
    assert "Run record:" in joined
    assert "Time base" in joined


def test_nothing_between_the_wash_in_heading_and_its_plot_is_a_sentence(
    application: QApplication,
) -> None:
    """`PL-F9TQ`: the same rule as the panel above, applied to the panel below."""

    view = _shown_view(application, SimulationController())
    strings = _strings_between(
        None,
        _wash_in(view).chart,
        skip=(*_wash_in(view).states.lines, *_wash_in(view).unmarked_changes.lines),
    )

    for value in strings:
        assert ". " not in value, value
        assert not value.rstrip().endswith("."), value

    joined = " ".join(sorted(strings))
    assert "not the vaporizer dial" in joined
    assert "Modelled, not measured" in joined
    assert "dimensionless ratio" not in joined


def test_the_wash_in_plot_says_what_its_denominator_is(application: QApplication) -> None:
    """`PL-F9TQ`: F_I is the modelled circuit, and the plot says so where it is read."""

    prose = " ".join(_visible_strings(_shown_view(application, SimulationController())))

    assert "not the vaporizer dial" in prose
    assert "denominator moving" in prose
    assert "Equilibrium, F_A = F_I" in prose


def test_the_screen_says_a_control_mark_is_an_input_not_a_measurement(
    application: QApplication,
) -> None:
    prose = " ".join(_visible_strings(_shown_view(application, SimulationController())))

    assert "Settings only — not a measurement." in prose
    assert "Control change" in prose
    assert "Run record:" in prose


@pytest.mark.parametrize(
    "label",
    [
        "end-tidal sevoflurane",
        "End tidal 1.8%",
        "ET sevo 2.1 %",
        "Et 1.8",
        "EtSevo",
        "FET",
        "ET2.1%",
        "Et1.8 %",
        "EtSevo2.1",
        "ETsevo",
        "EtSEV",
        "EtAA",
        "etSev",
    ],
)
def test_the_end_tidal_check_refuses_each_spelling_and_abbreviation(label: str) -> None:
    """A readout labelled "ET sevo", or with any other end-tidal spelling, fails (`PL-86VL`)."""

    assert _UNHEDGED_END_TIDAL.search(label) is not None


@pytest.mark.parametrize(
    "label",
    ["Alveolar (end-tidal-equivalent)", "Reset", "Settings", "FETCH", "Delivered", "Etc", "ETA"],
)
def test_the_end_tidal_check_passes_the_hedge_and_words_that_contain_et(label: str) -> None:
    assert _UNHEDGED_END_TIDAL.search(label) is None


def test_the_wake_up_check_reads_the_hedge_from_the_phrase_s_own_clause() -> None:
    """A negation just before the phrase in its clause hedges it, and any other negation does not.

    The check used to look at the 12 characters before the phrase. It passed
    "not shown; predicted wake time", where the negation belongs to another
    clause, and failed "this is never a time to wake", which is hedged
    (`PL-86VL`). A comma or a dash also ends a clause, and a negation more
    than four words back belongs to something else.
    """

    assert _unhedged_wake_predictions("not shown; predicted wake time") == ["predicted wake"]
    assert _unhedged_wake_predictions("this is never a time to wake") == []
    assert _unhedged_wake_predictions("This model does not predict a time to wake.") == []
    assert _unhedged_wake_predictions("Band shown. Time to wake: 14 min") == ["time to wake"]
    assert _unhedged_wake_predictions("Not a clinical tool \u2014 predicted wake at 0.68%") == [
        "predicted wake"
    ]
    assert _unhedged_wake_predictions("Modelled, not measured, predicted wake at 0.34") == [
        "predicted wake"
    ]
    assert _unhedged_wake_predictions("No agent in the circuit, so the patient will wake soon") == [
        "will wake"
    ]
    assert _unhedged_wake_predictions("No figure here is a reading or a time to wake") == [
        "time to wake"
    ]


def test_the_interface_never_predicts_a_time_to_wake_up(application: QApplication) -> None:
    """`PL-F52R`: the claim the band exists *instead of*, checked against the whole tree.

    A readout of the form "time to wake-up: 14 min" looks like a per-patient
    prediction that this model does not support, and no surrounding
    disclaimer undoes that.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 600.0)
    strings = _interface_strings(_shown_view(application, controller))
    prose = " ".join(strings).lower()

    duration = re.compile(
        r"\d+(?:\.\d+)?\s*(?:s|sec|secs|second|seconds|min|mins|minute|minutes|h|hr|hour|hours)\b"
    )

    for value in strings:
        lowered = value.lower()
        if any(word in lowered for word in ("wake", "awaken", "arousal", "emergence")):
            assert duration.search(lowered) is None, value

    for value in strings:
        assert _unhedged_wake_predictions(value) == [], value

    assert "population" in prose
    assert "±1 sd" in prose
