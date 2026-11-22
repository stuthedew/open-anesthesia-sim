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
from PySide6.QtWidgets import QAbstractButton, QApplication, QLabel, QWidget

from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app import views as views_module
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import CONTROL_TIMELINE_HEADING, run_label
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.view_registry import REGISTERED
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.supported_ranges import FreshGasFlow
from anesthesia_sim.layout.tree import AreaId
from tests.integration.simulation_view.simulation_view_support import (
    _advance_to,
    _case_view,
    _concentration,
    _failing_assembly,
    _fork_panel,
    _select_agent,
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


def _block_values(block: QWidget, name: str | None) -> tuple[str, ...]:
    """Every number a run's block shows, in reading order, with the run's own name taken out.

    A run's name is the only number that must differ between a compared run
    and a fresh run with the same settings, so it is removed before the
    numbers are read.
    """

    text = _block_text(block)

    if name is not None:
        text = text.replace(name, "")

    return tuple(re.findall(r"\d+(?:\.\d+)?", text))


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
