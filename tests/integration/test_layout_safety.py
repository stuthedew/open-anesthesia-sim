"""Every layout operation a reader can perform keeps the required values on screen.

`docs/MODEL.md` § "Minimum displayed outputs" divides the display into an
unconditional set that no Workspace may remove, an agent accounting that must
stay reachable from every layout, and a conditional remainder. The
unconditional set is drawn in its own region outside the Areas (`PL-NWTM`), so
no operation on an Area should be able to take one of its values away. These
tests run headless. They drive each operation on a real dashboard, and after
every one they check that no value has been taken away (`PL-G5SX`).

After each operation the test checks three things:

- Every value of the unconditional set is on screen. "On screen" is decided
  by `SimulationView.visible_strings`, the one predicate that all the
  whole-interface tests share (`PL-904Y`). Each value's widget must also be
  shown, and its text must be among the strings a reader can see.
- No value of the set is drawn inside the Area container, so closing or
  replacing an Area cannot take one away with the surface that drew it.
- Every Area's View chooser offers the agent accounting. The chooser is the
  route to the accounting that `tests/integration/test_view_chooser.py`
  checks.

The expected set is read from the declaration in `app/unconditional_set.py`,
not from the dashboard under test. The dashboard shows the halt reason only
when a run has halted, so the run that never halts leaves it out of the set,
and a second test halts a run at the supported run length and requires it. Each test
also checks that every value on screen before an operation is on screen after
it. A third test rearranges a case with a branch, so the two compared runs are
checked through the same operations (`PL-ZK09`).
"""

from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel, QSplitter, QWidget

from anesthesia_sim.app.area_layout import (
    JOIN_WITH_LABEL,
    SPLIT_SIDE_BY_SIDE_LABEL,
    SWAP_WITH_LABEL,
    AreaOperation,
)
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import SIMULATION_STEP_S
from anesthesia_sim.app.main import open_workspaces
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.unconditional_set import (
    INHALED_AGENT,
    UnconditionalValue,
    unconditional_set,
)
from anesthesia_sim.app.views import ConcentrationView
from anesthesia_sim.core.supported_ranges import FreshGasFlow
from anesthesia_sim.layout.store import USER_DIRECTORY_VARIABLE, WORKSPACES_FILE_NAME
from anesthesia_sim.layout.tree import AreaId
from anesthesia_sim.layout.workspace import WorkspaceName, WorkspaceSet

# The chooser's entry for the accounting View, as a reader reads it.
_ACCOUNTING_ENTRY = "Agent accounting"

# The close entry's label in each Area's menu.
_CLOSE_LABEL = "Close Area"

# The values every operation must leave on screen for a run that has not
# halted. The declaration is the source, so a value added to it is checked
# here without any edit to this file.
_REQUIRED = frozenset(unconditional_set(INHALED_AGENT).values) - {UnconditionalValue.HALT_REASON}

_WINDOW_PX = (1400, 1000)

# Thirty minutes of history. With that much, a frame holds more instants
# than a narrowed plot has pixels, so its chord width is set by the plot's
# columns rather than by the run. `PL-9LNF`'s own test does the same.
_HISTORY_S = 1800.0


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


def _paused_run() -> SimulationController:
    """A real run, paused after `_HISTORY_S` of simulated time with one recorded change."""

    controller = SimulationController()
    controller.start()

    while controller.snapshot().elapsed_s < _HISTORY_S - SIMULATION_STEP_S / 2.0:
        controller.advance(SIMULATION_STEP_S)

    controller.set_fresh_gas_flow(FreshGasFlow(2.0))
    controller.pause()

    return controller


def _halted_run() -> SimulationController:
    """`_paused_run`'s run, halted at the end of the supported domain.

    The dashboard draws a halt reason only for a run that failed or reached the
    supported run length (`dashboard_frame.notice`). Stepping to the 24-hour
    limit would take 864,000 steps, so the halt is recorded the way the
    interface records one it caught on another path.
    """

    controller = _paused_run()
    controller.halt_at_supported_limit("reached 86400 s of simulated time")

    return controller


def _launch(
    application: QApplication,
    controller: SimulationController,
    directory: Path,
    case: BranchedCase | None = None,
) -> SimulationView:
    """Open a dashboard as `main()` does, with its Workspaces loaded from `directory`."""

    launch = open_workspaces("", {USER_DIRECTORY_VARIABLE: str(directory)})
    view = SimulationView(
        (controller,),
        case=case,
        workspaces=launch.workspaces,
        store=launch.store,
        notice=launch.notice,
    )
    view.resize(*_WINDOW_PX)
    view.show()
    application.processEvents()
    view.present(False)

    return view


def _close(application: QApplication, view: SimulationView) -> None:
    view.stop_timers()
    view.close()
    view.deleteLater()
    application.processEvents()


def _texts(widget: QWidget) -> tuple[str, ...]:
    """The text a value's widget draws: its own, or that of every label inside it."""

    labels = [widget] if isinstance(widget, QLabel) else widget.findChildren(QLabel)

    return tuple(label.text() for label in labels if isinstance(label, QLabel) and label.text())


def _on_screen_by_run(view: SimulationView) -> tuple[frozenset[UnconditionalValue], ...]:
    """Each run's unconditional values that a reader can see now, in drawing order.

    "Can see" is checked through `visible_strings`.
    """

    visible = set(view.visible_strings())
    by_run: list[frozenset[UnconditionalValue]] = []

    for run in view.runs:
        seen: set[UnconditionalValue] = set()

        for value, widget in run.unconditional_widgets().items():
            texts = _texts(widget)

            if widget.isVisible() and texts and all(text in visible for text in texts):
                seen.add(value)

        by_run.append(frozenset(seen))

    return tuple(by_run)


def _on_screen(view: SimulationView) -> frozenset[UnconditionalValue]:
    """The unconditional values a reader can see now, for any run."""

    return frozenset().union(*_on_screen_by_run(view))


def _check(
    application: QApplication,
    view: SimulationView,
    step: str,
    before: frozenset[UnconditionalValue],
    required: frozenset[UnconditionalValue] = _REQUIRED,
) -> frozenset[UnconditionalValue]:
    """Assert what every operation must leave true, and return the values on screen."""

    application.processEvents()
    seen = _on_screen(view)
    container = view.layout_container

    assert required <= seen, f"after {step}, these are not on screen: {sorted(required - seen)}"
    assert before <= seen, f"after {step}, these left the screen: {sorted(before - seen)}"

    for run in view.runs:
        for value, widget in run.unconditional_widgets().items():
            assert not container.isAncestorOf(widget), f"after {step}, {value} is inside an Area"

    for area in container.model.areas():
        menu = container.frame(area.id).chooser.menu()
        assert menu is not None, f"after {step}, Area {area.id} has no View chooser menu"
        entries = [action for action in menu.actions() if action.text() == _ACCOUNTING_ENTRY]
        assert len(entries) == 1, f"after {step}, Area {area.id} does not offer the accounting"
        assert entries[0].isEnabled(), f"after {step}, Area {area.id} offers it unavailable"

    return seen


def _operation(
    view: SimulationView, area_id: AreaId, group: str | None, label: str
) -> AreaOperation:
    """The first available entry of Area `area_id`'s menu in `group` whose label starts `label`."""

    for operation in view.layout_container.operations(area_id):
        if operation.group == group and operation.label.startswith(label) and operation.available:
            return operation

    raise AssertionError(f"Area {area_id} offers no available {group or ''} {label!r} entry")


def _area_showing_chart(view: SimulationView) -> AreaId:
    container = view.layout_container
    (chart,) = (v for v in container.views() if isinstance(v, ConcentrationView))

    return next(
        area.id for area in container.model.areas() if container.frame(area.id).isAncestorOf(chart)
    )


def _chart(view: SimulationView) -> ConcentrationView:
    return next(v for v in view.layout_container.views() if isinstance(v, ConcentrationView))


def _widest_chord_px(view: SimulationView) -> int:
    """The widest gap, in plot pixels, between two consecutive drawn alveolar instants."""

    chart = _chart(view).chart
    times, percents = chart.drawn_points(0, RecordedQuantity.ALVEOLAR)
    xs = [chart.plot_pixel(t, p)[0] for t, p in zip(times, percents, strict=True)]

    return max(right - left for left, right in zip(xs, xs[1:], strict=False))


def _drag_only_border(application: QApplication, view: SimulationView, by_px: int) -> None:
    """Drag the one side-by-side Area border by `by_px`, as a mouse does."""

    (splitter,) = (
        s
        for s in view.layout_container.findChildren(QSplitter)
        if s.orientation() == Qt.Orientation.Horizontal
    )
    handle = splitter.handle(1)
    start = handle.rect().center()
    end = QPoint(start.x() + by_px, start.y())

    QTest.mousePress(handle, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, start)
    QTest.mouseMove(handle, end)
    QTest.mouseRelease(handle, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, end)
    application.processEvents()


def _rearrange(
    application: QApplication, view: SimulationView, directory: Path, check: Callable[[str], None]
) -> WorkspaceSet:
    """Split, swap, join and close the chart's Area, switch Workspaces, then save the set.

    `check` runs after each operation and is given the operation's name. The
    saved file goes to `directory`, so a dashboard launched from it reloads
    what was arranged. Returns the Workspace set that was saved.
    """

    chart_area = _area_showing_chart(view)
    view.layout_container.perform(_operation(view, chart_area, None, SPLIT_SIDE_BY_SIDE_LABEL))
    assert len(view.layout_container.model.areas()) == 3
    check("a split")

    view.layout_container.perform(_operation(view, chart_area, SWAP_WITH_LABEL, ""))
    check("a swap")

    view.layout_container.perform(_operation(view, chart_area, JOIN_WITH_LABEL, ""))
    assert len(view.layout_container.model.areas()) == 2
    check("a join")

    view.layout_container.perform(_operation(view, chart_area, None, _CLOSE_LABEL))
    assert len(view.layout_container.model.areas()) == 1
    check("closing an Area")

    strip = view.tab_strip

    for name in ("Induction", "Maintenance", "Default"):
        strip.activate(view.workspaces.position_of(WorkspaceName(name)))
        assert view.workspaces.current.name == WorkspaceName(name)
        check(f"switching to {name}")

    saved = view.workspaces
    strip.save_as_default(strip.save_entry())
    question = strip.question
    assert question is not None, "Save as default did not ask"
    question.accept()
    assert (directory / WORKSPACES_FILE_NAME).is_file()
    check("saving")

    return saved


def test_every_layout_operation_leaves_the_unconditional_set_on_screen(
    application: QApplication, tmp_path: Path
) -> None:
    """Resize, split, swap, join, close, switch, save and reload each keep the required values.

    The run is paused throughout, so nothing but the layout changes between
    two checks. The resize step also checks `PL-9LNF`'s redraw. Widening the
    chart's Area while paused leaves a frame sampled for the narrower plot,
    and the next tick draws that frame again for the new width.
    """

    controller = _paused_run()
    view = _launch(application, controller, tmp_path)

    try:
        assert view.workspaces.current.name == WorkspaceName("Default")
        seen = _check(application, view, "launch", frozenset())

        # Narrow the chart to its least width, then widen it by less than it
        # was narrowed. Once the border has moved, the splitter keeps the
        # controls Area at its size hint, which is wider than the width the
        # Area opened at (`PL-4L8B`). That hint depends on the platform's
        # fonts. A short widening from the least width stays clear of it.
        _drag_only_border(application, view, -800)
        view.present(False)
        narrowed_px = _chart(view).chart.plot_width_px()
        seen = _check(application, view, "narrowing the chart's Area", seen)
        presented = view.presented_frames
        _drag_only_border(application, view, 150)
        assert _chart(view).chart.plot_width_px() > narrowed_px * 1.2
        assert _widest_chord_px(view) > 1, "the drag did not widen the plot under the old frame"
        view.render_tick()
        assert view.presented_frames == presented + 1, "the widened chart was not redrawn"
        assert _widest_chord_px(view) <= 1, "the redrawn frame is not sampled for the new width"
        seen = _check(application, view, "widening the chart's Area", seen)

        def check(step: str) -> None:
            nonlocal seen
            seen = _check(application, view, step, seen)

        saved = _rearrange(application, view, tmp_path, check)
    finally:
        _close(application, view)

    reloaded = _launch(application, controller, tmp_path)

    try:
        assert reloaded.workspaces == saved
        assert len(reloaded.layout_container.model.areas()) == 1
        _check(application, reloaded, "reloading the saved Workspaces", seen)
    finally:
        _close(application, reloaded)


def test_a_halted_run_keeps_its_halt_reason_on_screen(
    application: QApplication, tmp_path: Path
) -> None:
    """A halted run's halt reason survives every layout operation and a reload.

    The test above leaves the halt reason out of what it requires, because its
    run never halts. Here the run has halted at the end of the supported
    domain, so the reason is on screen at launch, and the same operations must
    leave it there (`PL-ZK09`).
    """

    controller = _halted_run()
    assert controller.snapshot().supported_limit_reason is not None
    required = _REQUIRED | {UnconditionalValue.HALT_REASON}
    view = _launch(application, controller, tmp_path)

    try:
        seen = _check(application, view, "launch", frozenset(), required)

        def check(step: str) -> None:
            nonlocal seen
            seen = _check(application, view, step, seen, required)

        _rearrange(application, view, tmp_path, check)
    finally:
        _close(application, view)

    reloaded = _launch(application, controller, tmp_path)

    try:
        _check(application, reloaded, "reloading the saved Workspaces", seen, required)
    finally:
        _close(application, reloaded)


def test_a_branched_case_keeps_both_runs_drawn_and_named(
    application: QApplication, tmp_path: Path
) -> None:
    """Two compared runs both stay drawn, named and complete through every layout operation.

    v0.6.0's Definition of done asks that everything a learner could do with
    two runs before the layout became the reader's still works (`PL-ZK09`).
    After each operation, each run's own unconditional values must be on
    screen, its alveolar curve must be drawn, and each run's name must be
    visible. The names are written as literals rather than read from
    `run_label`, which the dashboard also reads.
    """

    case = BranchedCase(_paused_run())
    view = _launch(application, case.trunk, tmp_path, case=case)

    try:
        panel = view._fork_panel
        index = panel.point_selector.findData(_HISTORY_S)
        assert index >= 0, f"the branch control does not offer {_HISTORY_S} s"
        panel.point_selector.setCurrentIndex(index)
        panel.take_button.click()
        application.processEvents()
        view.present(False)
        assert len(view.runs) == 2

        def check(step: str) -> None:
            _check(application, view, step, frozenset())
            view.present(False)
            application.processEvents()

            for run, seen in enumerate(_on_screen_by_run(view)):
                assert _REQUIRED <= seen, (
                    f"after {step}, run {run + 1} lacks on screen: {sorted(_REQUIRED - seen)}"
                )

            visible = set(view.visible_strings())

            for name in ("Run 1", "Run 2"):
                assert name in visible, f"after {step}, {name!r} is not named on screen"

            for chart in (
                v for v in view.layout_container.views() if isinstance(v, ConcentrationView)
            ):
                for run in (0, 1):
                    times, _ = chart.chart.drawn_points(run, RecordedQuantity.ALVEOLAR)
                    assert times, f"after {step}, run {run + 1}'s alveolar curve is not drawn"

        check("taking the branch")
        _rearrange(application, view, tmp_path, check)
    finally:
        _close(application, view)
