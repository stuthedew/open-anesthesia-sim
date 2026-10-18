"""The agent accounting can be brought on screen from every Workspace, through the interface.

`docs/MODEL.md` § "Minimum displayed outputs" lets a Workspace leave the agent
accounting out, and requires it to "stay reachable in every layout". The
document defines reachable: a reader can bring the View on screen from the
Workspace through the interface alone, in a bounded number of steps, without
a drag or a file edit. Every Area's header carries a View chooser listing
every registered kind, so one choice in any Area is that route (`PL-50PZ`).

None of the three shipped Workspaces names the accounting View (`PL-KXTL`), so
the chooser is its only route in the shipped set, and these tests are what
guard it. Each loads a Workspace's layout into a real dashboard, checks the
accounting is not on screen, chooses it in one Area by triggering the
chooser's menu entry, and checks its five amounts are then on screen in that
Area. "On screen" here is Qt's `isVisible` on the label under a shown window,
until `PL-904Y`'s predicate replaces it. The amounts' own values are held by
the accounting panel's tests; these hold only that the reader can reach them.
"""

from collections.abc import Iterator

import pytest
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from anesthesia_sim.app.area_layout import AreaFrame
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.shipped import SHIPPED_WORKSPACE_IDS, shipped_workspace
from anesthesia_sim.layout.tree import Area, AreaId, Orientation, Split, ViewKind, Window

# The chooser's entry for the accounting View, as a reader reads it.
_ACCOUNTING_ENTRY = "Agent accounting"

# The first word of each of the accounting panel's five lines: the four
# quantities `docs/MODEL.md` names and the residual's absolute error.
_AMOUNT_LINES = ("Delivered: ", "Exhausted: ", "Stored: ", "Unaccounted: ", "Absolute error: ")

_WINDOW_PX = (1366, 900)

# A Workspace naming no accounting View and none of the shipped ones' layouts:
# two charts side by side.
_TWO_CHARTS = LayoutModel(
    (
        Window(
            Split(
                Orientation.ROW,
                (0.5, 0.5),
                (
                    Area(AreaId(1), ViewKind("concentration_chart")),
                    Area(AreaId(2), ViewKind("wash_in")),
                ),
            )
        ),
    ),
    AreaId(3),
)


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


@pytest.fixture
def dashboard(application: QApplication) -> Iterator[SimulationView]:
    view = SimulationView((SimulationController(),))
    view.resize(*_WINDOW_PX)
    view.show()
    application.processEvents()
    view.present(False)

    yield view

    view.stop_timers()
    view.close()
    view.deleteLater()
    application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    application.processEvents()


def _amount_labels(view: SimulationView) -> list[QLabel]:
    """The labels showing the accounting's five amounts, hidden ones included."""

    return [label for label in view.findChildren(QLabel) if _is_amounts(label.text())]


def _is_amounts(text: str) -> bool:
    lines = text.split("\n")

    return len(lines) == len(_AMOUNT_LINES) and all(
        line.startswith(start) for line, start in zip(lines, _AMOUNT_LINES, strict=True)
    )


def _on_screen(widget: QWidget) -> bool:
    return widget.isVisible() and widget.window().isVisible()


def _choose_accounting(
    application: QApplication, view: SimulationView, area_id: AreaId
) -> AreaFrame:
    """Pick the accounting entry in `area_id`'s chooser, as a reader does; its frame after."""

    chooser = view.layout_container.frame(area_id).chooser
    menu = chooser.menu()
    assert menu is not None, "the chooser has no menu"
    entries = [action for action in menu.actions() if action.text() == _ACCOUNTING_ENTRY]
    assert len(entries) == 1, f"the chooser lists {[a.text() for a in menu.actions()]}"

    entries[0].trigger()
    application.processEvents()

    return view.layout_container.frame(area_id)


def _layouts() -> list[tuple[str, LayoutModel]]:
    shipped = [(str(i), shipped_workspace(i).layout) for i in SHIPPED_WORKSPACE_IDS]

    return [*shipped, ("two charts", _TWO_CHARTS)]


@pytest.mark.parametrize(("name", "layout"), _layouts(), ids=[name for name, _ in _layouts()])
def test_the_accounting_can_be_brought_on_screen_in_any_area_of_any_workspace(
    application: QApplication, dashboard: SimulationView, name: str, layout: LayoutModel
) -> None:
    """From each Workspace, every Area's chooser brings the five amounts on screen in that Area."""

    assert all(area.view != "agent_accounting" for area in layout.areas()), name

    for area in layout.areas():
        dashboard.layout_container.set_model(layout)
        application.processEvents()

        assert not any(_on_screen(label) for label in _amount_labels(dashboard)), (
            f"{name}: the accounting is on screen before it was chosen"
        )

        frame = _choose_accounting(application, dashboard, area.id)
        shown = [label for label in _amount_labels(dashboard) if _on_screen(label)]

        assert len(shown) == 1, f"{name}, Area {area.id}: {len(shown)} accounting panels shown"
        assert frame.isAncestorOf(shown[0]), f"{name}, Area {area.id}: shown in another Area"
        assert dashboard.layout_container.model.area(area.id).view == "agent_accounting"


def test_the_dashboard_still_draws_a_frame_once_the_charts_have_left_the_screen(
    application: QApplication, dashboard: SimulationView
) -> None:
    """Choosing the accounting in the chart's Area leaves no run halted by a chart off screen."""

    _choose_accounting(application, dashboard, AreaId(1))
    dashboard.present(False)
    application.processEvents()

    assert not any(run.controller.has_failed for run in dashboard.runs)
