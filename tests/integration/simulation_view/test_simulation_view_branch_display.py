"""The dashboard, driven headless against real runs.

These tests cover a case's branch drawn beside its trunk, and the banners and panels that name each
run.

`simulation_view_support.py` describes the whole suite.
"""

import re
from typing import Any

import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QPushButton, QSplitter, QWidget

from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app.area_layout import AreaLayout
from anesthesia_sim.app.chart_frame import COMPARED_COMPARTMENT_CAP
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import (
    ACCOUNTING_HEADING,
    CONTROL_TIMELINE_HEADING,
    SIMULATION_STEP_S,
    run_label,
)
from anesthesia_sim.app.formatting import format_elapsed
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.run_view import RunView
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import PAGE_SPACING
from anesthesia_sim.app.unconditional_set import (
    INHALED_AGENT,
    UnconditionalValue,
    unconditional_set,
)
from anesthesia_sim.app.views import BranchView, ConcentrationView
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CaseInstant, FreshGasFlow
from anesthesia_sim.layout.tree import AreaId, Split
from tests.integration.simulation_view.simulation_view_support import (
    _BEHIND_MARK_LABEL,
    FIRST_RUN,
    RUN_IDS,
    SECOND_RUN,
    _accounting,
    _accounting_panel,
    _advance,
    _advance_to,
    _branched_case,
    _case_view,
    _concentration,
    _failing_assembly,
    _fork_panel,
    _halted_trunk_case,
    _paused_run_with_history,
    _rewind_case,
    _select_fork_entry,
    _setting_sections,
    _settle,
    _shown_view,
    _take_fork,
    _visible_strings,
    _wash_in,
    _widest_chord_px,
)

# ------------------------------------------------------------------ branching


def test_the_shipped_dashboard_opens_over_a_case_it_can_branch(application: QApplication) -> None:
    """`PL-VKJW`: every mechanism under v0.5.0's Goal had shipped and nothing called it.

    A dashboard given loose controllers cannot branch, and shows this by not
    offering the control. A dashboard opened over a case offers the control,
    at the trunk's own keyframes.
    """

    case = _branched_case()
    view = _case_view(application, case)

    assert view.case is case
    assert view.case.trunk is view.runs[0].controller
    assert _fork_panel(view).take_button.isHidden() is False

    branch = next(v for v in view.layout_container.views() if isinstance(v, BranchView))

    # The sentence that says no branch can be opened never shows beside a working control.
    assert branch.absent_notice.isHidden() is True


def test_a_dashboard_over_loose_runs_offers_no_branch_control(application: QApplication) -> None:
    """A control that could only refuse would present itself as working."""

    view = _shown_view(application, SimulationController())

    branch = next(v for v in view.layout_container.views() if isinstance(v, BranchView))

    assert view.case is None
    assert branch.panel is None
    assert branch.findChildren(QPushButton) == []
    assert branch.absent_notice.isHidden() is False
    assert branch.absent_notice.text() == (
        "These runs belong to no case, so no branch can be opened."
    )


def test_a_dashboard_refuses_a_case_rooted_in_another_run() -> None:
    """Two curves on one axis claim one patient, so a foreign case would misattribute it."""

    with pytest.raises(
        ValueError,
        match=re.escape(
            "a dashboard's case must be the one rooted in its first run, which is the "
            "trunk every branch of it is taken from"
        ),
    ):
        SimulationView((SimulationController(),), case=BranchedCase(SimulationController()))


def test_the_branch_control_offers_exactly_the_trunks_keyframes(application: QApplication) -> None:
    """`BranchedCase.fork_points_s`, rendered the way the clock renders time.

    Induction is offered rather than filtered out: a fork at zero is a second
    management of the whole case, and a case that has recorded nothing else
    would otherwise have an empty selector beside a live button.
    """

    case = _branched_case()
    view = _case_view(application, case)
    selector = _fork_panel(view).point_selector
    offered = [selector.itemData(index) for index in range(selector.count())]
    labels = [selector.itemText(index) for index in range(selector.count())]

    assert case.fork_points_s == (0.0, 60.0)
    assert offered == list(case.fork_points_s)
    assert labels == [format_elapsed(instant_s) for instant_s in case.fork_points_s]


def test_taking_a_fork_adds_the_branch_to_the_dashboard(application: QApplication) -> None:
    """The run added after construction: the case gains a run and so does the display.

    `SimulationView` fixed its run set at construction until `PL-VKJW`, so a
    branch taken during a session had nowhere to be drawn. The branch is
    added last, leaving the run that happened in the first position, which
    is where the ×MAC ruler and the clinical references are read from.
    """

    case = _branched_case()
    view = _case_view(application, case)

    assert len(view.runs) == 1

    _take_fork(view, 60.0)

    assert len(view.runs) == 2
    assert len(case.branches) == 1
    assert view.runs[0].controller is case.trunk
    assert view.runs[1].controller is case.branches[0]
    assert view.runs[1].controller.opened_from is not None
    assert view.runs[1].snapshot().elapsed_s == pytest.approx(60.0)
    assert view.runs[1].is_running is False


def test_taking_a_fork_redraws_the_chart_without_prompting(application: QApplication) -> None:
    """The press draws the frame the branch appears on, and nothing else has to ask for it.

    A fork is a discrete action, so it draws once and at once (`PL-R2YM`),
    rather than leaving the frame owed. Both runs are paused afterwards, so a
    frame left to the render tick would never be drawn. Nothing here presents
    after the press, so the frame read is the one the press drew. A fork that
    added the run without redrawing fails on the one-run frame that
    `_case_view` drew (`PL-624C`).

    The selection is narrowed, through the legend, to the pair that the cap
    would draw first, so the second run leaves it unchanged.
    `test_a_fork_from_the_default_selection_draws_one_frame` takes the fork
    from a selection that the second run reduces, which drew a second frame
    until `PL-B1R9`. Together the two tests show that a press draws once from
    either kind of selection.
    """

    case = _branched_case()
    view = _case_view(application, case)

    for quantity in _concentration(view).legend.shown[COMPARED_COMPARTMENT_CAP:]:
        _concentration(view).legend.set_compartment_shown(quantity, False)

    presented = view.presented_frames

    _take_fork(view, 60.0)

    assert view.presented_frames == presented + 1, "taking the branch did not draw it"

    frame = _concentration(view).chart.frame
    assert frame is not None
    assert len(frame.runs) == 2

    branch_times, _ = _concentration(view).chart.drawn_points(1, RecordedQuantity.ALVEOLAR)

    assert branch_times, "the chart holds no curve for the branch"
    assert min(branch_times) == pytest.approx(60.0)


def test_the_branch_is_drawn_beside_the_trunk_on_one_time_axis(application: QApplication) -> None:
    """One frame, both runs, and the branch's curve begins where it was taken.

    The frame read is the one the press drew, from the default selection
    rather than the narrowed one the test above takes the fork from. It used
    to present a frame itself first, which made every assertion below pass
    whether the fork redrew or not (`PL-624C`).
    """

    case = _branched_case()
    view = _case_view(application, case)
    _take_fork(view, 60.0)

    frame = _concentration(view).chart.frame
    assert frame is not None
    assert len(frame.runs) == 2

    trunk_times, _ = _concentration(view).chart.drawn_points(0, RecordedQuantity.ALVEOLAR)
    branch_times, _ = _concentration(view).chart.drawn_points(1, RecordedQuantity.ALVEOLAR)

    assert min(trunk_times) == pytest.approx(0.0)
    assert min(branch_times) == pytest.approx(60.0)
    assert max(branch_times) <= max(trunk_times) + SIMULATION_STEP_S


@pytest.mark.parametrize("door", ["keyframe", "here", "mark"])
def test_a_fork_from_the_default_selection_draws_one_frame(
    application: QApplication, door: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One press draws one frame, assembled once both runs know there are two, for both legends.

    The default selection is wider than `COMPARED_COMPARTMENT_CAP`, so the
    second run reduces it (`CompartmentSelection.with_run_count`), and the
    legend is shown the reduction. The reduction used to announce itself as a
    reader's change. The dashboard then drew a frame for it from inside
    `_rename_runs`, before the press drew its own frame. At that point the
    wash-in legend still counted one run, and neither run had been named.
    That made two assemblies for one discrete action, where `PL-R2YM` says
    one (`PL-B1R9`). Both legends are now told what a frame drew once it has
    been drawn (`PL-G3K7`). So the frame is assembled with each run named, and
    that frame is what brings both legends to two runs.
    `test_taking_a_fork_redraws_the_chart_without_prompting` checks the count
    from a selection that the cap leaves alone. This test checks it from a
    selection that the cap reduces, through every way a branch can be taken.
    """

    if door == "here":
        _, view = _halted_trunk_case(application)
    elif door == "mark":
        _, view, _ = _rewind_case(application)
    else:
        view = _case_view(application, _branched_case())

    assert len(_concentration(view).legend.shown) > COMPARED_COMPARTMENT_CAP, (
        "the default selection is inside the cap, so the press has nothing to reduce"
    )

    told: list[tuple[str, ...]] = []
    assemble = view._refresh_view

    def recording_assemble() -> None:
        told.append(tuple(run._run_name_text.text() for run in view.runs))
        assemble()

    monkeypatch.setattr(view, "_refresh_view", recording_assemble)
    presented = view.presented_frames

    if door == "here":
        _fork_panel(view).here_button.click()
    elif door == "mark":
        _select_fork_entry(view, _BEHIND_MARK_LABEL)
        _fork_panel(view).take_button.click()
    else:
        _take_fork(view, 60.0)

    assert len(view.runs) == 2
    assert len(_concentration(view).legend.shown) == COMPARED_COMPARTMENT_CAP, (
        "the cap reduced nothing"
    )
    assert view.presented_frames == presented + 1, "one press drew other than one frame"
    assert told == [(run_label(FIRST_RUN), run_label(SECOND_RUN))], (
        "the frame was assembled before the run set had been told it had grown"
    )
    assert _wash_in(view).legend._run_names == (run_label(FIRST_RUN), run_label(SECOND_RUN)), (
        "the frame did not tell the wash-in legend"
    )


def test_the_run_added_after_construction_is_named_and_given_its_own_sections(
    application: QApplication,
) -> None:
    """Everything that reads the run count follows the addition, not the construction.

    The dashboard uses this count to limit its compartment selection to the
    compared cap, and the legends name the runs from it. The panels carry the
    names that the legend entries use. Each run has a section of setting
    controls of its own, so a second run adds one, and its readouts join the
    region (`PL-NWTM`).
    """

    view = _case_view(application, _branched_case())
    sections_before = len(_setting_sections(view))

    _take_fork(view, 60.0)
    _settle(application)

    assert len(_setting_sections(view)) == sections_before + 1
    assert view.unconditional_region.isAncestorOf(view.runs[1]._readout_row)
    assert _concentration(view).legend._run_count == 2
    assert _concentration(view).legend._run_names == (run_label(FIRST_RUN), run_label(SECOND_RUN))
    assert _wash_in(view).legend._run_names == (run_label(FIRST_RUN), run_label(SECOND_RUN))
    assert view.runs[0]._run_name_text.text() == run_label(FIRST_RUN)
    assert view.runs[1]._run_name_text.text() == run_label(SECOND_RUN)
    assert view.runs[1]._run_name_text.isHidden() is False


def test_the_wash_in_state_and_off_scale_lines_name_their_run(application: QApplication) -> None:
    """Both lines sit in the chart column the runs share, so each says whose value it is.

    Once a branch is drawn, the column stacks one line per run, and the run
    names are in a different splitter section. So the only thing that tells
    the two lines apart is their stacking order, which nothing on screen
    declares. If the branch's F_A/F_I were read as the trunk's, it would
    invert the comparison the branch exists to teach. Its off-scale notice
    would report a clipped trace on a run that has none (`PL-25DD`).

    Sevoflurane's 8% dial is 4 MAC against a 3 MAC ceiling, and the branch
    inherits the trunk's dial. So both runs draw a clipped circuit trace, and
    both advisories are on screen at once. That is the case in which a line
    with no name is most easily taken for the other run's.

    The test drives no presentation beyond the one that `_handle_fork`
    makes. So the names arrive on the frame the branch appears on, not on
    some later tick.
    """

    trunk = SimulationController()
    trunk.start()
    trunk.set_delivered_concentration_percent(Percent(8.0))
    _advance_to(trunk, 600.0)
    trunk.set_fresh_gas_flow(FreshGasFlow(2.0))
    trunk.pause()
    view = _case_view(application, BranchedCase(trunk))
    selector = _fork_panel(view).point_selector
    _take_fork(view, selector.itemData(selector.count() - 1))
    _settle(application)

    assert len(view.runs) == 2

    states = _wash_in(view).states.lines
    off_scale = _concentration(view).off_scale.lines
    assert len(states) == len(off_scale) == 2

    for index in range(len(view.runs)):
        opening = f"{run_label(RUN_IDS[index])} — "
        assert states[index].text().startswith(opening)
        assert off_scale[index].isHidden() is False
        assert off_scale[index].text().startswith(opening)
        assert "Circuit" in off_scale[index].text()


def test_a_lone_run_leaves_the_shared_chart_lines_unnamed(application: QApplication) -> None:
    """One run has nothing to be told apart from, so the column carries no name.

    The run panels and both legends already follow this rule (`_rename_runs`).
    The test checks it here, so that the attribution `PL-25DD` adds does not
    become standing chrome on the display a learner opens.
    """

    controller = SimulationController()
    controller.start()
    controller.set_delivered_concentration_percent(Percent(8.0))
    _advance(controller, 600.0)
    view = _shown_view(application, controller)
    off_scale = _concentration(view).off_scale.lines[0]
    state = _wash_in(view).states.lines[0]

    assert off_scale.isHidden() is False
    assert off_scale.text().startswith("Above the top of the plot:")
    assert state.text().startswith("Now: F_A/F_I =")
    assert run_label(FIRST_RUN) not in off_scale.text()
    assert run_label(FIRST_RUN) not in state.text()


#: A dial position above every agent's calibrated vaporizer maximum, so the core
#: refuses it whichever agent the run is on. Tests drive it through the handler,
#: because the slider's own maximum makes it unreachable on the control.
_ABOVE_ANY_VAPORIZER_PERCENT = 50.0


def test_the_halt_and_refusal_banners_name_their_run(application: QApplication) -> None:
    """The notice column is shared, and all three banners assert something about a run.

    Read as a message about the whole dashboard, "Simulation stopped" says
    that the case has stopped while the other run is still going. "The
    simulation is unchanged and still running its previous setting" is false
    of the run it is not about. That is the misreading that the hazard table's
    halted-versus-paused row exists to prevent, arriving through attribution
    rather than through wording (`PL-TSZM`).

    The test drives one of each at once, on different runs. That is the case
    in which the column holds two banners and neither names its run.
    """

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)
    _settle(application)

    assert len(view.runs) == 2

    trunk, branch = view.runs
    branch.controller.start()
    branch._handle_delivered_concentration_change(_ABOVE_ANY_VAPORIZER_PERCENT)
    trunk._halt_run(RuntimeError("the shared render path raised"))
    _settle(application)

    trunk_notice = trunk._notice_text.notice()
    branch_notice = branch._notice_text.notice()

    assert trunk_notice is not None
    assert trunk_notice.startswith(f"{run_label(FIRST_RUN)}: Simulation stopped")
    assert branch_notice is not None
    assert branch_notice.startswith(f"{run_label(SECOND_RUN)}: Setting refused")
    assert "The simulation is unchanged" in branch_notice


def test_a_halt_stated_without_a_frame_still_names_the_run_it_stopped(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A halt is stated with no frame to read the run's name from, yet names the run it stopped.

    It is stated from the run's record alone, because the frame is what may
    have failed (`show_halt`, `PL-25KS`). Halting every run swallows the redraw that
    follows (`_halt_every_run`), so when the shared render path raises, the halt's banner
    is the last one written. If the run count came from the frame, the banner would name
    no run in exactly that case (`PL-TSZM`).

    Every frame fails here. A redraw that succeeded would write a banner of its own
    over the halt's, so the test would pass on a halt whose banner named no run
    (`PL-RF2S`).
    """

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)
    _settle(application)
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    for run in view.runs:
        run._presented = False

    view._halt_every_run(RuntimeError("the shared render path raised"))
    _settle(application)

    for index, run in enumerate(view.runs):
        notice = run._notice_text.notice()
        assert notice is not None
        assert notice.startswith(f"{run_label(RUN_IDS[index])}: Simulation stopped")


def test_a_banner_standing_when_a_branch_opens_is_named_from_that_frame(
    application: QApplication,
) -> None:
    """A refusal already on screen is about one run, and a fork puts a second beside it.

    "The simulation is unchanged and still running its previous setting" was
    true of the display while the trunk was alone. It is false of the branch
    the moment the branch appears. So the name has to arrive on the frame the
    branch appears on, not on some later tick (`PL-TSZM`).

    The presentation that `_handle_fork` drives delivers the name. It
    rewrites every run's banner through `show_presentation` after `_rename_runs`
    has named the runs. A rewrite attached to `set_run_name` would not be the
    mechanism. Such a rewrite was written and then removed. The fork's own
    presentation and the Reset that drops a branch both already rewrite the
    banner. So no scenario could tell that rewrite from its absence, and a
    guarantee that nothing can make fail is not a guarantee. This test is
    what keeps the presentation in that role.
    """

    case = _branched_case()
    view = _case_view(application, case)
    trunk = view.runs[0]
    trunk.controller.start()
    trunk._handle_delivered_concentration_change(_ABOVE_ANY_VAPORIZER_PERCENT)

    before = trunk._notice_text.notice()

    assert before is not None
    assert before.startswith("Setting refused")

    _take_fork(view, 60.0)
    _settle(application)

    after = trunk._notice_text.notice()

    assert after is not None
    assert after.startswith(f"{run_label(FIRST_RUN)}: Setting refused")


def test_a_lone_run_leaves_the_notice_banner_unnamed(application: QApplication) -> None:
    """One run has nothing to be told apart from, so the banner is not named.

    `_rename_runs` applies this rule to the run panels and both legends. The
    test checks it here, so that the attribution does not become standing
    chrome on the display a learner opens.
    """

    controller = SimulationController(agent_id="isoflurane")
    run = _shown_view(application, controller).runs[0]
    controller.start()

    run._handle_delivered_concentration_change(_ABOVE_ANY_VAPORIZER_PERCENT)

    notice = run._notice_text.notice()

    assert notice is not None
    assert notice.startswith("Setting refused")
    assert run_label(FIRST_RUN) not in notice


@pytest.mark.parametrize("compared", [False, True], ids=["one run", "two runs"])
def test_hidden_notice_banners_take_no_height(application: QApplication, compared: bool) -> None:
    """A banner with nothing to say takes no room, and a shown one sits under the transport rows.

    The unconditional region, the band of required values that no Workspace
    can remove, has little height to spare on a laptop screen. So every
    pixel it spends on a hidden banner is a pixel the concentration chart
    loses (`PL-T91K`). The expected gaps are the theme's page spacing, not a
    value read from the layout under test. With two runs, only the branch's
    banner is shown. The hidden trunk banner ahead of it must not push it
    down. The branch's banner sits where the trunk's banner would, so only
    its words say which run it belongs to (`PL-TSZM`).
    """

    if compared:
        view = _case_view(application, _branched_case())
        _take_fork(view, 60.0)
    else:
        view = _shown_view(application, SimulationController(agent_id="isoflurane"))

    _settle(application)
    transports = view._transport_column.parentWidget()
    readouts = view._readout_column.parentWidget()
    banners = [run._notice_text for run in view.runs]

    assert len(banners) == (2 if compared else 1)
    assert all(banner.isHidden() for banner in banners)
    assert readouts.y() == transports.geometry().bottom() + 1 + PAGE_SPACING

    run = view.runs[-1]
    run.controller.start()
    run._handle_delivered_concentration_change(_ABOVE_ANY_VAPORIZER_PERCENT)
    _settle(application)
    shown = banners[-1]

    assert shown.isVisible()
    assert shown.y() == transports.geometry().bottom() + 1 + PAGE_SPACING
    assert readouts.y() == shown.geometry().bottom() + 1 + PAGE_SPACING


def test_the_sidebar_panels_name_the_run_they_record(application: QApplication) -> None:
    """Both panels sit in a column the runs share, so each heading says whose.

    Once a branch is drawn, the sidebar stacks two accounting panels, and the
    unconditional region's record column stacks two control-change panels
    (`PL-NWTM`). Before that change, one column stacked all four, and nothing
    on any of them said which run it recorded. Both kinds of panel carry a
    claim about one run. One is a mass-balance status with litres of
    equivalent pure agent gas. The other is a list of settings under the
    words "What was changed during this run". If the second were read as the
    other run's, it would say that the trunk received an intervention it
    never got (`PL-C3GS`).

    The trunk is given a setting change before the fork, and the branch is
    given one after it. So the two control-change lists differ, and
    misattributing either list is a concrete wrong reading rather than a
    formal one.

    The test checks the attribution on the labels that the panels hold, not
    on freshly built ones. Each label is then found under the shared column,
    which shows that the named heading is the heading on screen.
    """

    trunk = SimulationController()
    trunk.start()
    _advance_to(trunk, 120.0)
    trunk.set_fresh_gas_flow(FreshGasFlow(2.0))
    _advance_to(trunk, 600.0)
    trunk.pause()
    view = _case_view(application, BranchedCase(trunk))
    selector = _fork_panel(view).point_selector
    _take_fork(view, selector.itemData(selector.count() - 1))
    _settle(application)

    assert len(view.runs) == 2

    branch = view.runs[1]
    branch.controller.set_alveolar_ventilation(AlveolarVentilation(6.0))
    view.present(False)
    columns = (_accounting(view), view._record_column.parentWidget())

    for index, run in enumerate(view.runs):
        name = run_label(RUN_IDS[index])
        headings = (
            _accounting_panel(run)._accounting_heading_text,
            run._control_timeline_heading_text,
        )

        assert headings[0].text() == f"{ACCOUNTING_HEADING} — {name}"
        assert headings[1].text() == f"{CONTROL_TIMELINE_HEADING} — {name}"

        for heading, column in zip(headings, columns, strict=True):
            assert heading.isVisible(), "a panel heading naming the run is not on screen"
            assert column is not None and column.isAncestorOf(heading), (
                "the named heading is not in the shared column"
            )

    assert view.runs[0]._control_timeline_text.text() != branch._control_timeline_text.text()


def test_no_unconditional_value_sits_inside_the_layout_container(application: QApplication) -> None:
    """Every value `docs/MODEL.md` requires in every layout is in the region, outside the Areas.

    The layout container holds the Areas that a reader resizes (`PL-W9P6`).
    So a reader could close away a value inside it once Areas can be closed
    (`PL-NWTM`). The test checks both runs of a compared case, because the
    second run's widgets are placed an hour after the first's. The halt
    banner is hidden while nothing has halted, so the test checks only its
    place. Every other value must be on screen.
    """

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)
    _settle(application)
    required = unconditional_set(INHALED_AGENT).values

    assert len(view.runs) == 2
    assert len(required) == 14, "five invariant, eight per-substance and the record"

    for run in view.runs:
        widgets = run.unconditional_widgets()

        assert set(widgets) == set(required)

        for value in required:
            widget = widgets[value]

            assert not view.layout_container.isAncestorOf(widget), (
                f"{value.value} is inside the layout container"
            )
            assert view.unconditional_region.isAncestorOf(widget), (
                f"{value.value} is outside the unconditional region"
            )

            if value is not UnconditionalValue.HALT_REASON:
                assert widget.isVisible(), f"{value.value} is not on screen"


def test_the_readout_heading_states_the_dial_and_the_mac_it_divides_by(
    application: QApplication,
) -> None:
    """The region carries the delivered concentration in both units and the 1 MAC (`PL-NWTM`).

    The expected text is worked out by hand. The dial opens at sevoflurane's
    own 1 MAC, 2.0% (`data/agents/sevoflurane.json`), which is 1.00 ×MAC.
    Moved to 3.0%, it is 1.50 ×MAC.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]

    assert run._delivered_text.text() == "Delivered 2.00% (1.00 ×MAC)"
    assert run._one_mac_text.text() == "1 MAC sevoflurane = 2.0%"

    controller.set_delivered_concentration_percent(
        Percent(3.0, name="delivered_concentration_percent")
    )
    view.present(False)

    assert run._delivered_text.text() == "Delivered 3.00% (1.50 ×MAC)"
    assert run._delivered_text.isVisible()
    assert run._one_mac_text.isVisible()


@pytest.mark.parametrize("misplaced", ["missing", "in a splitter"])
def test_a_run_whose_region_lacks_a_declared_value_is_refused(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, misplaced: str
) -> None:
    """The declaration decides what the region holds, so a run lacking a value is not shown.

    The test builds the dashboard in two ways. In the first, the 1 MAC
    statement is taken out of the run's mapping. In the second, the mapping
    points the statement at the first View inside the splitter tree. A
    dashboard built either way would draw ×MAC numbers whose divisor a reader
    could close away.
    """

    original = RunView.unconditional_widgets
    build_areas = AreaLayout.__init__
    built: list[AreaLayout] = []

    def recorded(areas: AreaLayout, *args: Any, **kwargs: Any) -> None:
        build_areas(areas, *args, **kwargs)
        built.append(areas)

    def short_of_one_mac(run: RunView) -> dict[UnconditionalValue, QWidget]:
        widgets = dict(original(run))

        if misplaced == "missing":
            del widgets[UnconditionalValue.ONE_MAC]
        else:
            widgets[UnconditionalValue.ONE_MAC] = built[-1].views()[0]

        return widgets

    monkeypatch.setattr(AreaLayout, "__init__", recorded)
    monkeypatch.setattr(RunView, "unconditional_widgets", short_of_one_mac)

    with pytest.raises(RuntimeError, match="does not hold one_mac"):
        SimulationView((SimulationController(),))


def test_a_run_refused_for_a_missing_unconditional_value_leaves_no_widgets(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A branch that the region check refuses leaves nothing of itself on the dashboard.

    `_place_run` puts a run's widgets in the shared layouts before it checks
    the region, because the check reads where they are. If a refusal left
    them there, the dashboard would show a second run frozen at its fork,
    with blank delivered and 1 MAC lines. No slot would refresh or remove
    that run (`PL-KDZW`). The test refuses only the branch, so the trunk is built
    normally and its widgets are the ones that must remain.
    """

    case = _branched_case()
    view = _case_view(application, case)
    branch = case.fork_at(CaseInstant(60.0))
    before = set(view.findChildren(QWidget))
    readings_before = [
        len(panel.findChildren(QWidget)) for panel in view.runs[0]._readout_row.panels
    ]
    original = RunView.unconditional_widgets

    def branch_short_of_one_mac(run: RunView) -> dict[UnconditionalValue, QWidget]:
        widgets = dict(original(run))

        if run.controller is branch:
            del widgets[UnconditionalValue.ONE_MAC]

        return widgets

    monkeypatch.setattr(RunView, "unconditional_widgets", branch_short_of_one_mac)

    with pytest.raises(RuntimeError, match="does not hold one_mac"):
        view.add_run(branch)

    assert set(view.findChildren(QWidget)) == before, (
        "the refused run left widgets on the dashboard"
    )
    assert [
        len(panel.findChildren(QWidget)) for panel in view.runs[0]._readout_row.panels
    ] == readings_before, "the refused run's readings stayed in the trunk's panels"
    assert len(view.runs) == 1


def test_a_lone_run_leaves_the_sidebar_panel_headings_unnamed(application: QApplication) -> None:
    """One run has nothing to be told apart from, so neither heading gains a name.

    `_rename_runs` already applies this rule to the run panels and both
    legends. The test checks it here, so that `PL-C3GS`'s attribution does not
    become standing chrome on the display a learner opens.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 120.0)
    view = _shown_view(application, controller)
    run = view.runs[0]

    assert _accounting_panel(run)._accounting_heading_text.text() == ACCOUNTING_HEADING
    assert run._control_timeline_heading_text.text() == CONTROL_TIMELINE_HEADING
    assert run_label(FIRST_RUN) not in _accounting_panel(run)._accounting_heading_text.text()
    assert run_label(FIRST_RUN) not in run._control_timeline_heading_text.text()


def test_dragging_the_border_beside_the_sidebar_changes_the_layout_model(
    application: QApplication,
) -> None:
    """A reader's drag of a border updates the layout model, not only the widgets.

    `_EVERY_VIEW` draws the chart panel and the sidebar as two Areas of one
    row (`PL-W9P6`), under the parameter controls' Area. The test drags the
    border between them 100 px to the left. The chart panel's share of the row
    then equals its new pixel width divided by the row's width, and the
    sidebar is wider by the same 100 px.
    """

    view = _shown_view(application, SimulationController())
    splitter = _sidebar_splitter(view)
    chart_px, sidebar_px = splitter.sizes()
    handle = splitter.handle(1)
    start = handle.rect().center()
    end = QPoint(start.x() - 100, start.y())

    QTest.mousePress(handle, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, start)
    QTest.mouseMove(handle, end)
    QTest.mouseRelease(handle, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, end)
    application.processEvents()

    column = view.layout_container.model.windows[0].tree
    assert isinstance(column, Split)
    tree = column.children[1]
    assert isinstance(tree, Split)
    assert splitter.sizes() == [chart_px - 100, sidebar_px + 100]
    assert tree.sizes[0] == pytest.approx((chart_px - 100) / (chart_px + sidebar_px), abs=1e-2)
    assert view.layout_container.frame(AreaId(1)).content is _concentration(view)


def test_splitting_and_closing_the_chart_area_leaves_the_unconditional_values_where_they_were(
    application: QApplication,
) -> None:
    """The Area menu changes only the Areas, so the region above them is untouched (`PL-2KXB`).

    The new half of a split builds a second concentration chart, and the
    first Area keeps its own. Closing the new half gives its place back.
    """

    from anesthesia_sim.app.area_layout import CLOSE_AREA_LABEL, SPLIT_STACKED_LABEL

    view = _shown_view(application, SimulationController())
    areas = view.layout_container
    before = areas.model
    region = view.unconditional_region
    first_chart = _concentration(view)
    shown_before = _visible_strings(view)

    (split,) = [op for op in areas.operations(AreaId(1)) if op.label == SPLIT_STACKED_LABEL]
    areas.perform(split)
    _settle(application)
    (new_area,) = [area.id for area in areas.model.areas() if area not in before.areas()]

    charts = [v for v in areas.views() if isinstance(v, ConcentrationView)]
    assert areas.frame(AreaId(1)).content is first_chart
    assert len(charts) == 2 and areas.frame(new_area).content in charts
    assert view.unconditional_region is region
    assert not areas.isAncestorOf(region)

    (close,) = [op for op in areas.operations(new_area) if op.label == CLOSE_AREA_LABEL]
    areas.perform(close)
    _settle(application)

    # The split and the close each rescale the sizes, so they come back
    # equal only to rounding.
    assert areas.model.areas() == before.areas()
    assert _visible_strings(view) == shown_before


def _sidebar_splitter(view: SimulationView) -> QSplitter:
    """The splitter whose one border lies between the chart panel and the sidebar.

    It is the row of `_EVERY_VIEW` that holds the chart, under the parameter
    controls' Area. The row of bookmarks and branch control is below it.
    """

    chart = _concentration(view)
    (splitter,) = (
        splitter
        for splitter in view.layout_container.findChildren(QSplitter)
        if splitter.orientation() == Qt.Orientation.Horizontal and splitter.isAncestorOf(chart)
    )

    return splitter


def _drag_area_border(application: QApplication, view: SimulationView, by_px: int) -> None:
    """Drag the border between the chart panel and the sidebar by `by_px`, as a mouse does."""

    splitter = _sidebar_splitter(view)
    handle = splitter.handle(1)
    start = handle.rect().center()
    end = QPoint(start.x() + by_px, start.y())

    QTest.mousePress(handle, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, start)
    QTest.mouseMove(handle, end)
    QTest.mouseRelease(handle, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, end)
    application.processEvents()


def test_resizing_one_chart_redraws_it_at_its_own_width(application: QApplication) -> None:
    """`PL-9LNF`: widening a chart's Area while paused redraws it, though the window kept its size.

    The frame on screen is sampled for the width it was drawn at (`PL-GS3R`).
    A drag of the Area border changes the chart's width but not the
    dashboard's, so a guard on the dashboard's own resize never fired. On
    `main` at `512fdaed`, the tick after the drag drew nothing, and the
    widened plot kept 2 px chords. The run has thirty minutes of history. So
    the frame has more instants than the narrowed plot has pixels, and the
    columns, not the run, set the chord.
    """

    controller = _paused_run_with_history(1800.0)
    view = _shown_view(application, controller)
    window_px = view.width()
    _drag_area_border(application, view, -400)
    view.present(False)
    narrowed_px = _concentration(view).chart.plot_width_px()
    presented = view.presented_frames

    _drag_area_border(application, view, 400)

    assert view.width() == window_px, "the drag resized the dashboard, not only the Area"
    assert _concentration(view).chart.plot_width_px() > narrowed_px + 300
    assert _widest_chord_px(view) > 1, "the drag did not widen the plot under the old frame"

    view.render_tick()

    assert view.presented_frames == presented + 1
    assert _widest_chord_px(view) <= 1

    view.render_tick()

    assert view.presented_frames == presented + 1, "the tick kept drawing with nothing owed"


def test_narrowing_a_chart_owes_no_frame(application: QApplication) -> None:
    """A plot narrower than its frame's width draws chords closer than a pixel, and needs nothing.

    So only a widening is owed a frame (`resample_owed`). While the run is
    paused, a tick after a narrowing drag draws nothing, and no drawn chord
    is wider than a pixel.
    """

    controller = _paused_run_with_history(1800.0)
    view = _shown_view(application, controller)
    view.render_tick()
    presented = view.presented_frames

    _drag_area_border(application, view, -400)
    view.render_tick()

    assert view.presented_frames == presented
    assert _widest_chord_px(view) <= 1
