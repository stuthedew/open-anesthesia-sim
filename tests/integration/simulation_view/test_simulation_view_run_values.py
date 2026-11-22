"""Each run's values travel with its name, and a chart shows only a frame of the runs it holds.

The third pull request of `PL-RF2S` (one value for the whole screen) took the
runs' snapshots off the View tick, made a run's name part of the value its
panel and its Views are written from, and made each chart's frame on a tick
that draws none either the kept last frame or a withheld one. These tests
check those three things through the whole dashboard. Each expected value is
written out by hand, or is read from a run built directly with the settings
the test is about (`.claude/rules/test-oracles.md`, rules 1 and 2).
"""

from __future__ import annotations

import re
from dataclasses import replace

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QAbstractButton, QApplication, QLabel, QWidget

from anesthesia_sim.app import run_presentation as run_presentation_module
from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app import views as views_module
from anesthesia_sim.app.chart_time_base import time_base_for_span
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import CONTROL_TIMELINE_HEADING, run_label, slider_position
from anesthesia_sim.app.formatting import FLOW_DISPLAY_DECIMALS, format_elapsed
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.view_registry import CONCENTRATION_CHART, PARAMETER_CONTROLS, REGISTERED
from anesthesia_sim.app.views import CompartmentSchematicView
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.supported_ranges import FreshGasFlow
from anesthesia_sim.layout.run_identity import RunId, SessionToken
from anesthesia_sim.layout.tree import AreaId
from anesthesia_sim.layout.workspace import WorkspaceName
from tests.integration.simulation_view.simulation_view_support import (
    _CLOCK_INDEX,
    _EVERY_VIEW,
    _advance_to,
    _case_view,
    _concentration,
    _dials,
    _failing_assembly,
    _fork_panel,
    _no_setting,
    _select_agent,
    _select_time_base,
    _settle,
    _shown_view,
    _wash_in,
)

#: What the legend's 1 MAC entry reads while the chart's frame is withheld,
#: written out by hand: the placeholder dash in place of the agent's 1 MAC.
_WITHHELD_ONE_MAC_ENTRY = "—, reference adult (alveolar, wide dash)"

#: The instant the trunk is branched at, and the instant both runs are then
#: advanced to, in simulated seconds.
_FORK_S = 300
_COMPARED_AT_S = 600


def _run_at(elapsed_s: int) -> SimulationController:
    """A sevoflurane run delivering 2%, advanced to `elapsed_s` and paused."""

    controller = SimulationController()
    controller.set_delivered_concentration_percent(Percent(2.0))
    controller.start()
    _advance_to(controller, elapsed_s)
    controller.pause()

    return controller


def test_a_reset_whose_first_frame_fails_withholds_each_chart_s_frame(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """After a Reset that no frame draws, no chart shows the discarded run's traces.

    Before `PL-RF2S`'s third pull request each chart kept the last frame it
    drew. So after a Reset whose first frame failed, the plots showed the
    discarded run's ten minutes beside readouts that were withheld because the
    run had started over. The plot is now empty, and a line says why.
    """

    view = _shown_view(application, _run_at(_COMPARED_AT_S))
    assert _concentration(view).chart.frame is not None
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.runs[0]._reset_button.click()
    _settle(application)

    assert view.runs[0].controller.has_failed is True
    assert _concentration(view).chart.frame is None, "the chart kept the discarded run's frame"
    assert _wash_in(view).chart.frame is None, "the wash-in plot kept the discarded run's frame"
    assert not _concentration(view).withheld_text.isHidden()
    assert not _wash_in(view).withheld_text.isHidden()
    assert _concentration(view).legend.one_mac_text == _WITHHELD_ONE_MAC_ENTRY
    assert _concentration(view).off_scale.lines == ()
    assert _wash_in(view).states.lines == ()


def test_an_agent_change_whose_first_frame_fails_leaves_no_line_of_the_old_agent(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """After an agent change that no frame draws, no 1 MAC line or entry is the old agent's.

    The 1 MAC line and the MAC-awake band are placed from the agent's own
    values. A chart that kept sevoflurane's frame after a change to
    desflurane went on drawing sevoflurane's 1 MAC line, and its legend named
    sevoflurane, under a panel that already named desflurane.
    """

    view = _shown_view(application, SimulationController())
    assert "sevoflurane" in _concentration(view).legend.one_mac_text.lower()
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    _select_agent(view.runs[0], "desflurane")
    _settle(application)

    assert view.runs[0].controller.has_failed is True
    assert "sevoflurane" not in _concentration(view).legend.one_mac_text.lower()
    assert _concentration(view).chart.frame is None
    assert _concentration(view).legend.one_mac_text == _WITHHELD_ONE_MAC_ENTRY


def test_a_branch_dropped_while_frames_fail_leaves_none_of_its_curves(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A Reset of the trunk that drops the branch takes the branch's curves off both plots.

    The chart used to keep the frame of both runs, with the branch's curves
    and its legend entry, beside a dashboard that held the trunk alone.
    """

    view = _case_view(application, BranchedCase(_run_at(_COMPARED_AT_S)))
    _fork_panel(view).here_button.click()
    _settle(application)
    assert len(view.runs) == 2
    assert len(_concentration(view).chart.frame.runs) == 2  # type: ignore[union-attr]
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.runs[0]._reset_button.click()
    _settle(application)

    assert len(view.runs) == 1
    assert _concentration(view).chart.frame is None, "the chart kept the dropped branch's curves"
    assert _wash_in(view).chart.frame is None, "the wash-in plot kept the dropped branch's curves"
    assert _wash_in(view).legend._run_names == (run_label(view.runs[0].run_id),)


def test_a_halt_with_no_start_over_keeps_each_chart_s_frame(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A halt of the run the charts drew leaves both plots as the last frame drew them.

    What a learner sees after a halt does not change: the plot keeps the
    last frame, which is the same run and the same case as the readouts.
    """

    view = _shown_view(application, _run_at(_COMPARED_AT_S))
    concentration = _concentration(view).chart.frame
    wash_in = _wash_in(view).chart.frame
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.present(False)
    _settle(application)

    assert view.runs[0].controller.has_failed is True
    assert _concentration(view).chart.frame is concentration
    assert _wash_in(view).chart.frame is wash_in
    assert _concentration(view).withheld_text.isHidden()
    assert _wash_in(view).withheld_text.isHidden()


def test_a_dragged_dial_leaves_each_chart_s_frame_until_the_render_tick(
    application: QApplication,
) -> None:
    """A coalesced setting change hands every View the runs with no frame, and the plots wait.

    The run's own readouts move at once and the chart waits for the render
    tick (`PL-018`, `PL-R2YM`). The kept frame that the tick carries is the
    one each chart already shows, so the chart draws nothing.
    """

    view = _shown_view(application, _run_at(_COMPARED_AT_S))
    drawn = _concentration(view).chart.frame
    presented = view.presented_frames

    view.runs[0]._apply_setting(
        lambda: view.runs[0].controller.set_fresh_gas_flow(FreshGasFlow(4.0)), coalesce=True
    )

    assert view.presented_frames == presented
    assert _concentration(view).chart.frame is drawn
    assert _concentration(view).withheld_text.isHidden()


def test_a_run_s_panel_names_the_run_from_the_presentation_it_shows(
    application: QApplication,
) -> None:
    """The run's own panel writes its name from the same presentation as its values.

    Before, a separate call wrote the name whenever the run set changed, and
    the panel kept it whatever presentation it was then shown. The panel is
    shown a presentation of the trunk built with no name, while two runs are
    drawn. Every place the panel names the run must then name none.
    """

    view = _case_view(application, BranchedCase(_run_at(_COMPARED_AT_S)))
    _fork_panel(view).here_button.click()
    _settle(application)
    trunk = view.runs[0]
    assert trunk._run_name_text.text() == run_label(trunk.run_id)

    trunk.show_presentation(replace(trunk.presentation(trunk.snapshot()), name=None))

    assert trunk._run_name_text.isHidden(), "the panel kept a name its presentation did not hold"
    assert trunk._control_timeline_heading_text.text() == CONTROL_TIMELINE_HEADING


# ------------------------- blind review of the third pull request (PL-RF2S)

#: The part of the banner that says the charts are withheld while the readouts
#: are kept, written out by hand from the approved wording.
_CHARTS_WITHHELD_BANNER = (
    "No frame of the stopped run could be drawn: the readouts show the last frame "
    "drawn before it stopped, the charts are withheld, and the run itself stands at "
    "its last completed step."
)


def _clock_text(view: SimulationView, run: int) -> str:
    """The elapsed time that one run's own readout row shows."""

    return view.runs[run]._readout_row.panels[_CLOCK_INDEX].value_label.text()


def test_a_panel_that_refuses_a_drawn_frame_leaves_each_chart_on_that_frame(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A run's panel that refuses a frame after the Views drew it leaves the charts on that frame.

    The run's own panel writes the readouts and the clock before it raises
    the refusal of its dials. So after the halt the readouts show the refused
    frame's instant. The charts kept frames were recorded only after every
    panel had been written, so the halt handed the charts the frame before,
    and the plots stepped back by one render tick behind the clock beside
    them (blind review of `PL-RF2S`'s third pull request, pass 1 F2 and
    pass 2 F2). The expected instant is the one the test advanced the run
    to.
    """

    controller = _run_at(_FORK_S)
    view = _shown_view(application, controller)
    assert _concentration(view).chart.frame.runs[0].elapsed_s == _FORK_S  # type: ignore[union-attr]
    controller.start()
    _advance_to(controller, _COMPARED_AT_S)
    controller.pause()
    monkeypatch.setattr(run_presentation_module, "setting_readouts", _no_setting)

    with pytest.raises(ValueError, match="this control can offer no setting"):
        view.present(False)

    _settle(application)

    assert controller.has_failed is True
    assert _clock_text(view, 0) == format_elapsed(_COMPARED_AT_S)

    for chart in (_concentration(view).chart, _wash_in(view).chart):
        frame = chart.frame
        assert frame is not None
        assert frame.runs[0].elapsed_s == _COMPARED_AT_S, (
            "the chart stepped back to the frame before the one the readouts show"
        )


def test_every_run_s_panel_shows_a_frame_that_one_run_s_panel_refused(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When the first run's panel refuses a frame, the second run's panel still shows that frame.

    The charts keep the frame that the Views drew. So each run's own panel
    must show it too, or the second run's readouts stand one render tick
    behind its own traces. The refusal comes from the first run's dials, and
    it used to stop the second run's panel from being written at all. The
    expected instant is the one the test advanced both runs to.
    """

    view = _case_view(application, BranchedCase(_run_at(_FORK_S)))
    _fork_panel(view).here_button.click()
    _settle(application)
    assert len(view.runs) == 2

    for run in view.runs:
        run.controller.start()
        _advance_to(run.controller, _COMPARED_AT_S)
        run.controller.pause()

    monkeypatch.setattr(run_presentation_module, "setting_readouts", _no_setting)

    with pytest.raises(ValueError, match="this control can offer no setting"):
        view.present(False)

    _settle(application)

    assert _clock_text(view, 1) == format_elapsed(_COMPARED_AT_S), (
        "the second run's panel was not written from the frame that the charts show"
    )
    frame = _concentration(view).chart.frame
    assert frame is not None
    assert [run.elapsed_s for run in frame.runs] == [_COMPARED_AT_S, _COMPARED_AT_S]


def test_a_panel_that_refuses_the_first_frame_after_an_agent_change_keeps_that_frame(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A frame drawn for a new agent and then refused by the run's panel stays on each chart.

    The Views drew the new agent's first frame, and the run's panel wrote its
    readouts from it before it refused the dials. The kept frames were still
    the old agent's, so the halt withheld every chart: the plot emptied and
    said that no frame could be drawn, although one had been drawn. The chart
    then owed a frame, so every render tick drew it again, was refused by the
    panel again and halted every run again (pass 2 F1).
    """

    view = _shown_view(application, SimulationController())
    monkeypatch.setattr(run_presentation_module, "setting_readouts", _no_setting)

    _select_agent(view.runs[0], "desflurane")
    _settle(application)

    assert view.runs[0].controller.has_failed is True
    frame = _concentration(view).chart.frame
    assert frame is not None, "the chart withheld a frame that it had drawn"
    assert frame.runs[0].agent_id == "desflurane"
    assert _concentration(view).withheld_text.isHidden()

    halts: list[BaseException] = []
    monkeypatch.setattr(view, "_halt_every_run", halts.append)

    view.render_tick()
    view.render_tick()

    assert halts == [], "each render tick drew the refused frame again and halted every run"


def test_a_frame_from_before_a_workspace_pinned_to_a_closed_run_is_not_kept(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A chart shown after a pinned Workspace never draws a frame from before the pin.

    While the current Workspace is pinned to a run that is not open, no View
    is drawn, but the runs go on. The frames drawn before the pin used to
    stay recorded as kept. So when frames then failed and the reader went
    back to a Workspace that shows the run, its charts drew a frame from
    before the pin, minutes behind the readouts (pass 1 F3).
    """

    every_view = _EVERY_VIEW.current
    earlier = RunId(SessionToken("f" * 32), 1)
    workspaces = _EVERY_VIEW.add(
        every_view.renamed(WorkspaceName("Pinned")).pinned_to(earlier)
    ).activate(0)
    controller = _run_at(_FORK_S)
    view = _shown_view(application, controller, workspaces=workspaces)
    assert _concentration(view).chart.frame.runs[0].elapsed_s == _FORK_S  # type: ignore[union-attr]

    QTest.mouseClick(view.tab_strip.tab_at(1), Qt.MouseButton.LeftButton)
    _settle(application)
    controller.start()
    _advance_to(controller, _COMPARED_AT_S)
    controller.pause()
    view.present(False)
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    view.present(False)
    assert controller.has_failed is True

    QTest.mouseClick(view.tab_strip.tab_at(0), Qt.MouseButton.LeftButton)
    _settle(application)

    for chart in (_concentration(view).chart, _wash_in(view).chart):
        assert chart.frame is None, "the chart drew a frame from before the pinned Workspace"

    assert not _concentration(view).withheld_text.isHidden()


def test_a_branch_taken_while_frames_fail_says_the_charts_are_withheld(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The trunk's banner says the charts are withheld when a new branch withholds them.

    The last frame drew the trunk alone, so it is withheld once the branch is
    open. The trunk has not started over, and its banner said that "the
    chart and the readouts show the last frame drawn", above empty plots
    (pass 1 F1).
    """

    view = _case_view(application, BranchedCase(_run_at(_COMPARED_AT_S)))
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    _fork_panel(view).here_button.click()
    _settle(application)

    assert len(view.runs) == 2
    assert view.runs[0].controller.has_failed is True
    assert _concentration(view).chart.frame is None
    banner = view.runs[0]._notice_text.notice()
    assert banner is not None
    assert "the chart and the readouts show the last frame" not in banner, (
        "the banner says the chart shows the last frame, but the charts are withheld"
    )
    assert _CHARTS_WITHHELD_BANNER in banner


def test_a_withheld_chart_shows_no_axis_label_of_the_discarded_frame(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """After an agent change that no frame draws, no axis is labelled from the old agent's frame.

    The left axis is labelled in percent at multiples of the agent's 1 MAC.
    A withheld chart kept sevoflurane's percent labels and the discarded
    run's window in the time axis's title, under a panel that named
    desflurane (pass 2 F3).
    """

    view = _shown_view(application, SimulationController())
    chart = _concentration(view).chart
    assert chart.axis_ticks("left") != ()
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    _select_agent(view.runs[0], "desflurane")
    _settle(application)

    assert chart.frame is None
    assert chart.axis_ticks("left") == (), "the percent axis kept the old agent's labels"
    assert chart.axis_ticks("right") == ()
    assert chart.axis_ticks("bottom") == ()
    assert chart.time_axis_title == "simulated time"
    wash_in = _wash_in(view).chart
    assert wash_in.axis_ticks("bottom") == ()
    assert wash_in.time_axis_title == "simulated time"


def _chosen_chart(view: SimulationView, area: AreaId) -> views_module.ConcentrationView:
    """Choose a concentration chart for `area`, and return the View built there."""

    view.layout_container.choose_view(area, CONCENTRATION_CHART)
    chosen = view.layout_container.frame(area).content
    assert isinstance(chosen, views_module.ConcentrationView)

    return chosen


def _assert_withheld(chart_view: views_module.ConcentrationView) -> None:
    """Check that a concentration chart shows the withheld state: empty, explained, unlabelled."""

    chart = chart_view.chart
    assert chart.frame is None
    assert not chart_view.withheld_text.isHidden(), "the chart does not say why it is empty"
    assert chart.axis_ticks("left") == ()
    assert chart.axis_ticks("right") == ()
    assert not chart._one_mac_line.isVisible()
    assert not chart._band.isVisible()


def test_a_chart_opened_while_frames_fail_at_a_window_never_drawn_is_withheld(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A chart chosen during a halt, at a window that no kept frame has, shows the withheld state.

    The only kept frame is at 15 minutes. A new chart opens at "Fit run",
    for which no frame was kept. It used to be left as it was built: no
    trace, a 1 MAC line and a band parked at 0, default numbers under the
    "%" and "×MAC" axis titles, and no line saying why, under a banner that
    said the chart showed the last frame (blind review pass 3, F1).
    """

    view = _shown_view(application, _run_at(_COMPARED_AT_S))
    _select_time_base(view, "900.0")
    view.layout_container.choose_view(AreaId(3), PARAMETER_CONTROLS)
    _settle(application)
    assert view.layout_container.frame_requests().keys() == {time_base_for_span(900.0)}
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    view.present(False)
    assert view.runs[0].controller.has_failed is True

    chosen = _chosen_chart(view, AreaId(2))
    _settle(application)

    _assert_withheld(chosen)
    banner = view.runs[0]._notice_text.notice()
    assert banner is not None
    assert "the chart and the readouts show the last frame" not in banner


def test_a_chart_opened_while_frames_fail_never_draws_a_frame_sampled_for_a_narrower_plot(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A kept frame sampled for a narrower plot is withheld from a chart that opens during a halt.

    With no chart shown, the frame is sampled at the narrowest width. A chart
    opened while frames fail used to draw that frame, with chords several
    pixels wide, which breaks the one-pixel chord rule in `docs/INTERFACE.md`
    (blind review pass 3, F2).
    """

    view = _shown_view(application, _run_at(_COMPARED_AT_S))

    for area in (AreaId(1), AreaId(3)):
        view.layout_container.choose_view(area, PARAMETER_CONTROLS)

    _settle(application)
    view.present(False)
    assert view.layout_container.frame_requests() == {}
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    view.present(False)
    assert view.runs[0].controller.has_failed is True

    chosen = _chosen_chart(view, AreaId(1))
    _settle(application)

    assert chosen.chart.frame is None, "the chart drew a frame sampled for a narrower plot"
    _assert_withheld(chosen)


def test_a_halt_while_a_thumb_is_held_leaves_no_preview_on_any_chart(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A preview drawn before a halt is not kept, because the halted run refuses that setting.

    The kept frame used to carry the held drag's preview trace and label.
    So after the halt, and after the release, each chart went on showing a
    predicted future for a setting that the stopped run would refuse (blind
    review pass 3, F3).
    """

    view = _shown_view(application, _run_at(_FORK_S))
    control = _dials(view.runs[0])._fresh_gas_flow_slider
    control.slider.setSliderDown(True)
    control.slider.setSliderPosition(slider_position(6.0, FLOW_DISPLAY_DECIMALS))
    view.render_tick()
    assert _concentration(view).chart.preview_label(0) is not None
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.present(False)
    _settle(application)

    assert view.runs[0].controller.has_failed is True

    for chart in (_concentration(view).chart, _wash_in(view).chart):
        assert chart.preview_label(0) is None, "a chart kept the preview of a refused setting"

    control.slider.setSliderDown(False)
    _settle(application)
    chosen = _chosen_chart(view, AreaId(2))
    _settle(application)

    assert chosen.chart.frame is None, "a chart opened after the halt drew the kept preview"


# ------------------------------------------------- PL-G2WC: values under their run


def _run_blocks(view: QWidget) -> tuple[QWidget, ...]:
    """Each displayed run's block in one View, in drawing order, found from the View itself.

    A View that shows a run's values holds one widget per run in a
    `_RunWidgets`, directly or inside a `_RunLines`. So this walks the View's
    attributes for either, which finds the blocks of a View kind added later
    without naming it here.
    """

    blocks: list[QWidget] = []

    for value in vars(view).values():
        if isinstance(value, views_module._RunLines):
            value = value._lines

        if isinstance(value, views_module._RunWidgets):
            blocks.extend(value.widgets)

    return tuple(blocks)


def _run_block_groups(view: QWidget) -> tuple[tuple[QWidget, ...], ...]:
    """Each group of per-run blocks in one View, each group in drawing order.

    A View that shows a run's values holds one widget per run in a
    `_RunWidgets`, directly or inside a `_RunLines`, and a chart holds more
    than one such group. So this walks the View's attributes for either,
    which finds the blocks of a View kind added later without naming it here.
    """

    groups: list[tuple[QWidget, ...]] = []

    for value in vars(view).values():
        if isinstance(value, views_module._RunLines):
            value = value._lines

        if isinstance(value, views_module._RunWidgets):
            groups.append(value.widgets)

    return tuple(groups)


def _block_text(block: QWidget) -> str:
    """Every string a run's block shows: its labels, its buttons and what it paints."""

    texts = [block.text()] if isinstance(block, QLabel) else []
    texts.extend(label.text() for label in block.findChildren(QLabel))
    texts.extend(button.text() for button in block.findChildren(QAbstractButton))
    canvas = getattr(block, "canvas", None)

    if canvas is not None:
        texts.extend(canvas.painted_strings())

    return "\n".join(texts)


# regex: finds each decimal number in a block's free text, such as "4.2" in
# "4.2% sevoflurane". The text is prose with units around the numbers, so no
# parser reads it, and a string method cannot pick the numbers out of words.
_DECIMAL_NUMBER = re.compile(r"\d+(?:\.\d+)?")


def _block_values(block: QWidget, name: str | None) -> tuple[str, ...]:
    """Every number a run's block shows, in reading order, with the run's own name taken out.

    A run's name is the only number that must differ between a compared run
    and a fresh run with the same settings, so it is removed before the
    numbers are read.
    """

    text = _block_text(block)

    if name is not None:
        text = text.replace(name, "")

    return tuple(_DECIMAL_NUMBER.findall(text))


def _branched_at_a_higher_flow() -> tuple[SimulationController, SimulationController]:
    """Return a trunk and, built directly, a run with the settings the branch will hold.

    The trunk delivers 2% at the default fresh gas flow. The branch opens at
    `_FORK_S` and raises the fresh gas flow to 6 L/min. The second run is not
    a branch: it is a fresh run given the same settings at the same instants,
    so its values are worked out without the dashboard or the case.
    """

    trunk = _run_at(_FORK_S)
    fresh = _run_at(_FORK_S)
    fresh.set_fresh_gas_flow(FreshGasFlow(6.0))
    fresh.start()
    _advance_to(fresh, _COMPARED_AT_S)
    fresh.pause()

    return trunk, fresh


def test_each_compared_value_is_shown_under_its_own_run(application: QApplication) -> None:
    """In compare mode every View shows each run's values in the block that names that run.

    Two compared runs hold different values: the branch runs at a higher
    fresh gas flow. Every registered View kind is shown in turn. For each one
    that shows a block per run, each block's numbers must be the numbers that
    the same View shows for a fresh single run with that run's settings, and
    each block must name its run. The fresh runs are built directly, so the
    expected values do not come from the compared dashboard (`PL-G2WC`).
    The two runs share one agent, because a dashboard refuses two agents on
    one axis.
    """

    trunk, branch_alone = _branched_at_a_higher_flow()
    trunk_alone = _run_at(_FORK_S)
    trunk_alone.start()
    _advance_to(trunk_alone, _COMPARED_AT_S)
    trunk_alone.pause()

    compared = _case_view(application, BranchedCase(trunk))
    _fork_panel(compared).here_button.click()
    branch = compared.runs[1]
    branch.controller.set_fresh_gas_flow(FreshGasFlow(6.0))
    branch.controller.start()
    _advance_to(branch.controller, _COMPARED_AT_S)
    branch.controller.pause()
    trunk.start()
    _advance_to(trunk, _COMPARED_AT_S)
    trunk.pause()
    compared.present(False)
    names = tuple(run_label(run.run_id) for run in compared.runs)

    alone = []

    for controller in (trunk_alone, branch_alone):
        single = SimulationView((controller,))
        single.resize(compared.size())
        single.show()
        application.processEvents()
        alone.append(single)

    checked: list[str] = []

    try:
        for kind in REGISTERED:
            for dashboard in (compared, *alone):
                dashboard.layout_container.choose_view(AreaId(2), kind)
                dashboard.present(False)
                _settle(application)

            groups = _run_block_groups(compared.layout_container.frame(AreaId(2)).content)
            expected_groups = [
                _run_block_groups(single.layout_container.frame(AreaId(2)).content)
                for single in alone
            ]
            told_apart = False

            for index, blocks in enumerate(groups):
                assert len(blocks) == 2, f"{kind}: {len(blocks)} block(s) for two compared runs"
                values = [
                    _block_values(block, name) for block, name in zip(blocks, names, strict=True)
                ]

                for block, name, run_values, single in zip(
                    blocks, names, values, expected_groups, strict=True
                ):
                    (expected,) = single[index]
                    assert run_values == _block_values(expected, None), (
                        f"{kind}: the block that names {name} does not show that run's values"
                    )

                    if run_values:
                        assert name in _block_text(block), f"{kind}: a block does not name {name}"

                told_apart = told_apart or values[0] != values[1]

            if told_apart:
                checked.append(str(kind))
    finally:
        for single in alone:
            single.stop_timers()
            single.deleteLater()

    # The accounting panel, the dials, the schematic and the agent cost panel
    # each show numbers that differ between the two runs. The charts' lines
    # per run are compared too, but at these settings they read the same for
    # both runs. A walk that found fewer kinds would check too little.
    assert len(checked) >= 4, f"only {checked} showed the two runs' different values"


def _painted_amounts(view: SimulationView) -> tuple[str, ...]:
    """The text that every compartment schematic in the dashboard paints, in reading order.

    The schematic paints each container's name, tension and amount without a
    label, so the walk of a dashboard's labels cannot read them. Each canvas
    returns the strings that it paints (`SchematicCanvas.painted_strings`).
    """

    return tuple(
        text
        for drawn in view.layout_container.views()
        if isinstance(drawn, CompartmentSchematicView)
        for text in drawn.painted_strings()
    )


def _start_over(view: SimulationView, how: str) -> None:
    """Make the dashboard's one run start over by a Reset, or by a change to desflurane.

    The run has recorded ten minutes, so a change of agent asks first, and
    the reader discards the run.
    """

    run = view.runs[0]

    if how == "reset":
        run._reset_button.click()
    else:
        _select_agent(run, "desflurane")
        dialog = run._new_case_dialog
        assert dialog is not None, "the change of agent did not ask before discarding the run"
        dialog.discard_button.click()


def _fresh_run_after(how: str, changed: SimulationController) -> SimulationController:
    """A run built directly in the state that a start over by `how` is meant to produce.

    A Reset keeps every setting and goes back to 0 s. A change of agent goes
    back to 0 s with the new agent, at the delivered concentration that the
    changed run now holds, which is the reader's setting and not a value
    under test.
    """

    if how == "reset":
        return _run_at(0)

    fresh = SimulationController("desflurane")
    fresh.set_delivered_concentration_percent(
        Percent(float(changed.settings().delivered_concentration_percent))
    )

    return fresh


@pytest.mark.parametrize("how", ["reset", "agent change"])
@pytest.mark.parametrize("frame_drawn", [True, False], ids=["drawn", "halted"])
def test_the_schematic_paints_no_amount_left_from_before_a_start_over(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, how: str, frame_drawn: bool
) -> None:
    """After a Reset or an agent change, each painted amount is the one a fresh run paints.

    The schematic paints its amounts on a canvas rather than in labels, so
    the tests that read every label could not see an amount left from the
    run before it started over (`PL-0G2P`). The run here has delivered
    sevoflurane for ten minutes, so every compartment holds agent. After the
    start over, the dashboard is compared with one built afresh over a run in
    the state the start over is meant to produce. Where no frame draws after
    the start over, both dashboards halt on their first frame, so each
    schematic withholds its amounts rather than painting the discarded
    run's.
    """

    view = _shown_view(application, _run_at(_COMPARED_AT_S))
    before = _painted_amounts(view)
    assert before, "the dashboard shows no schematic, so the test reads nothing"

    if not frame_drawn:
        monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    _start_over(view, how)
    _settle(application)
    after = _painted_amounts(view)
    changed = view.runs[0].controller
    assert changed.has_failed is not frame_drawn
    assert changed.agent_id == ("sevoflurane" if how == "reset" else "desflurane")
    # Building the fresh dashboard deletes this one.
    fresh = _shown_view(application, _fresh_run_after(how, changed))

    assert fresh.runs[0].controller.has_failed is not frame_drawn
    assert after != before, "the schematic still paints the run from before the start over"
    assert after == _painted_amounts(fresh)
