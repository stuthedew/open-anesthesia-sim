"""The dashboard, driven headless against real runs.

These tests cover that every control declares its own foreground colour.

`simulation_view_support.py` describes the whole suite.
"""

import re
from collections.abc import Iterator

import pytest
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QAbstractButton,
    QAbstractItemView,
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QFrame,
    QGroupBox,
    QLabel,
    QLineEdit,
    QWidget,
)

from anesthesia_sim.app import theme
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.simulation_view import SimulationView
from tests.integration.simulation_view.simulation_view_support import (
    _delete_shown_views,
    _shown_view,
)

# ------------------------------------------- what declares its own foreground


#: Every control kind on the built dashboard that paints its own content and
#: declares no foreground, mapped to the reason it is allowed not to.
#: `tools/contrast_check.py` reads this mapping and counts its entries in its
#: report line. That tool measures declared pairs, so a control that declares
#: nothing is absent from its numerator *and* its denominator, and looks
#: covered there. What nothing measures has to be stated somewhere, and this
#: is the place.
#:
#: A name here is a claim about a kind, not an excuse for one. The test below
#: fails on an entry that names a kind the dashboard no longer builds, and on
#: an entry whose kind has since been given a foreground. So an entry cannot
#: outlive the reason beside it.
FOREGROUND_NOT_DECLARED: dict[str, str] = {
    "PlotWidget": (
        "the concentration chart and the wash-in plot. Their axis ticks and "
        "labels are text, and pyqtgraph draws them from a pen rather than from "
        "the palette: `qt_chart._plot` sets setTextPen(mkPen(MUTED)) on every "
        "axis and passes color=MUTED to each setLabel. So the colour is "
        "declared and contrast_check measures it as MUTED on PANEL; it is "
        "only unreachable through the palette this test reads."
    ),
    "ViewScroll": (
        "the scroll box that holds an Area's View under its header "
        "(`area_layout.ViewScroll`, `PL-CBYS`). Its viewport fills no background, "
        "so the Area's surface shows through, and it draws no text: every string "
        "inside it belongs to the View's own widgets."
    ),
    "_KeyScroll": (
        "the box that scrolls a chart View's window statement, reference values "
        "and legend above the plot (`views._KeyScroll`, `PL-CBYS`). It paints no "
        "surface, through `stylesheets.clear_scroll_area_stylesheet`, and draws no "
        "text: every row inside it is a widget of its own."
    ),
    "QScrollArea": (
        "the page's scroll area. It paints the viewport surface, which "
        "`SimulationView` declares as BACKGROUND in a stylesheet, and no text: "
        "every string inside it belongs to a widget of its own."
    ),
    "QScrollBar": (
        "Qt's own chrome, on the page and inside each selector's popup. It "
        "draws no text, and its groove and handle come from the platform "
        "style rather than from the foreground role. Whether this interface "
        "should declare a colour scheme so the chrome follows it is PL-KRZW, "
        "which is the project owner's decision and open."
    ),
    "QSlider": (
        "the four setting sliders. Each draws no text - the value beside it is "
        "a label of its own - and `slider_stylesheet` declares the groove, "
        "the filled track and the handle, none of which is painted from the "
        "foreground role."
    ),
    "_AreaHandle": (
        "the border between two Areas, the chart column and the sidebar. It draws "
        "no text: nothing at rest, and under the pointer a PRIMARY line that "
        "`tools/contrast_check.py` measures against BACKGROUND (PL-RQT1)."
    ),
    "_CornerZone": (
        "an Area's corner, where a drag splits or joins it. It draws no text: "
        "nothing at rest, and while the pointer is in its Area a grip of three "
        "strokes in MUTED, which `tools/contrast_check.py` measures against "
        "PANEL (PL-30L5)."
    ),
    "_LayoutOverlay": (
        "what a corner drag shows before release, drawn over the Areas. It "
        "draws no text: a split line or a joined Area's outline in PRIMARY or "
        "WARNING, and a MUTED tint, each measured against PANEL by "
        "`tools/contrast_check.py` (PL-30L5)."
    ),
    "_LineSwatch": (
        "the legend's line samples. Each paints with the pen of the trace it "
        "stands for and never reads its foreground role; contrast_check holds "
        "every trace colour to TRACE_FLOOR against PANEL, in all four vision "
        "models."
    ),
    "_BandSwatch": (
        "the MAC-awake band's legend mark, painted with the band's own edge "
        "pen and fill for the reason the line swatches are."
    ),
}

#: A six-digit sRGB hex literal, the form every colour in `app/theme.py`
#: takes and the form `QColor.name` returns.
_HEX_COLOUR = re.compile(r"#[0-9A-Fa-f]{6}")

#: A foreground colour that nothing in this interface declares, installed on
#: the application palette before the dashboard is built. A control that
#: declares no colour of its own resolves to this one. That makes
#: "undeclared" a value to read rather than an absence to infer. It also
#: stops a host whose own default happened to match a theme colour from
#: making the walk prove nothing.
_ALIEN_FOREGROUND = "#FF00FF"

#: The palette roles in which a control on this dashboard draws its content.
#: All of them are changed together, because `QWidget.foregroundRole` differs
#: by control: WindowText for a label, ButtonText for a button and Text for a
#: list. A role left at the platform's value would be treated as declared.
_ALIEN_ROLES = (
    QPalette.ColorRole.WindowText,
    QPalette.ColorRole.Text,
    QPalette.ColorRole.ButtonText,
    QPalette.ColorRole.BrightText,
    QPalette.ColorRole.ToolTipText,
    QPalette.ColorRole.PlaceholderText,
    QPalette.ColorRole.HighlightedText,
    QPalette.ColorRole.Link,
    QPalette.ColorRole.LinkVisited,
)

#: The Qt classes that paint a string of their own. Each must declare a
#: foreground, whatever it is painting today. A label built empty and filled
#: on the first frame draws text just as one built with its string does, and a
#: check that read `text()` would pass the label while it was empty.
_TEXT_CONTROLS = (
    QAbstractButton,
    QAbstractItemView,
    QAbstractSpinBox,
    QComboBox,
    QGroupBox,
    QLabel,
    QLineEdit,
)

#: The frame shapes whose lines Qt draws in the foreground role. A `NoFrame`
#: frame draws no line at all, and the style draws a `StyledPanel` from its
#: bevel roles. So neither shape says anything about a foreground. That is
#: what keeps every panel and column container out of the walk without
#: naming one.
_PLAIN_LINE_SHAPES = (
    QFrame.Shape.Box,
    QFrame.Shape.Panel,
    QFrame.Shape.WinPanel,
    QFrame.Shape.HLine,
    QFrame.Shape.VLine,
)


def _declared_colours() -> frozenset[str]:
    """Every colour `app/theme.py` declares, including both agent pairs.

    The colours are read from the module rather than listed here.
    `contrast_check`'s `check_colors_live_in_the_theme` requires every colour
    to be declared there, so the module holds the complete set by
    construction.
    """

    colours = {
        value.upper()
        for value in vars(theme).values()
        if isinstance(value, str) and _HEX_COLOUR.fullmatch(value)
    }

    for scheme in theme.AGENT_COLOR_SCHEMES.values():
        colours.update({scheme.fill.upper(), scheme.foreground.upper()})

    return frozenset(colours)


def _paints_its_own_content(widget: QWidget) -> bool:
    """Whether `widget` draws anything of its own in its foreground role.

    The function asks three questions in order, because asking them in
    another order gives wrong results. A text control is included whatever it
    inherits from. `QLabel` is a `QFrame`, so asking the frame question first
    would drop every label on the dashboard. A frame that is not a plain line
    is a container or is drawn by the style. So it is excluded unless its
    class paints below `QFrame`. That rule keeps `MetricPanel`, `QSplitter`
    and the panels out of the walk. It still keeps `PlotWidget`, which is a
    `QGraphicsView` and paints its own scene. Every other widget is included
    exactly when its class overrides `paintEvent`. That is the decidable form
    of "draws something nobody else declares".
    """

    if isinstance(widget, _TEXT_CONTROLS):
        return True

    if isinstance(widget, QFrame):
        plain_line = (
            widget.frameShape() in _PLAIN_LINE_SHAPES
            and widget.frameShadow() is QFrame.Shadow.Plain
        )

        return plain_line or type(widget).paintEvent is not QFrame.paintEvent

    return type(widget).paintEvent is not QWidget.paintEvent


def _content_painters(view: SimulationView) -> list[QWidget]:
    """Every widget of the built dashboard that paints its own content.

    A selector's popup is reached through `view()` rather than by the child
    walk: it is a window of its own, so `findChildren` never returns it, and
    it is where `PL-0NVN`'s rows were drawn from the host palette.
    """

    widgets: list[QWidget] = [view, *view.findChildren(QWidget)]

    for widget in list(widgets):
        if isinstance(widget, QComboBox):
            widgets.append(widget.view())

    return [widget for widget in widgets if _paints_its_own_content(widget)]


def _resolved_foreground(widget: QWidget) -> str:
    widget.ensurePolished()

    return widget.palette().color(widget.foregroundRole()).name().upper()


@pytest.fixture
def alien_foreground(application: QApplication) -> Iterator[QApplication]:
    """The application with every foreground role set to `_ALIEN_FOREGROUND`.

    The palette is set on the application rather than on a widget. That is
    the same reason `tests/integration/test_dark_appearance.py` sets a host
    appearance there: a palette assigned to the widget under test would
    overwrite the declaration being tested instead of exercising it. The
    dashboard is built inside the fixture's scope, so that every stylesheet
    resolves against this palette. The views are deleted before the original
    palette is restored, because the modules in this tree share one
    `QApplication`.
    """

    original = QPalette(application.palette())
    alien = QPalette(original)

    for role in _ALIEN_ROLES:
        alien.setColor(QPalette.ColorGroup.All, role, QColor(_ALIEN_FOREGROUND))

    application.setPalette(alien)

    yield application

    _delete_shown_views(application)
    application.setPalette(original)


def test_every_control_that_paints_its_own_content_declares_a_foreground(
    alien_foreground: QApplication,
) -> None:
    """`PL-4L49`: what declares nothing is drawn by the host, and says nothing.

    `tools/contrast_check.py` measures the pairs that somebody wrote down. A
    control that writes none adds to neither side of its count. So its report
    line is the same whether the interface is covered or has three invisible
    controls on it. That was the state in which the project owner found
    `PL-DHBX`, on his own screen. That tool cannot answer the question this
    test asks, and the question needs a built tree rather than an `ast` walk.
    Qt, not the source, decides which widget a stylesheet actually applies to.

    So every foreground role is set to a colour this interface never uses,
    the dashboard is built under it, and each content-painting widget is asked
    what colour it resolves to. A declared control returns its own colour.
    Qt folds a stylesheet's `color` into the widget's palette when it polishes
    the widget. Qt also passes the colour down from an ancestor's stylesheet,
    exactly as it would on screen. That is why no rule here has to parse CSS
    or decide which selector applied to which widget.
    """

    view = _shown_view(alien_foreground, SimulationController())
    declared = _declared_colours()
    painters = _content_painters(view)

    undeclared = sorted(
        {
            f"{type(widget).__name__} draws in {_resolved_foreground(widget)}"
            for widget in painters
            if type(widget).__name__ not in FOREGROUND_NOT_DECLARED
            and _resolved_foreground(widget) not in declared
        }
    )

    assert undeclared == [], (
        "these controls take their foreground from the host palette; declare each "
        "colour in app/theme.py with a requirement in tools/contrast_check.py, or "
        "name the kind in FOREGROUND_NOT_DECLARED with the reason it draws no text: "
        f"{undeclared}"
    )

    status = view.runs[0]._status_text
    status.setStyleSheet("")

    assert _resolved_foreground(status) == _ALIEN_FOREGROUND, (
        "a control stripped of its own declaration still read as a theme colour, so "
        "the walk above proved nothing"
    )


def test_no_control_kind_is_exempted_from_declaring_a_foreground_without_cause(
    alien_foreground: QApplication,
) -> None:
    """Every entry in `FOREGROUND_NOT_DECLARED` still names a live exemption.

    This test keeps the list from becoming a comment that nobody checks, in the
    same way that `tools/contrast_check.py` checks `KNOWN_SHORTFALLS`. An entry for a
    kind the dashboard stopped building fails here. So does an entry for a
    kind that has since been given a foreground. Neither stays on as an
    exemption that nothing needs. Both directions matter to the count that
    the report line prints, because the count is the size of this mapping. An
    entry that has stopped being true overstates what nothing measures, just
    as a missing entry understates it.
    """

    view = _shown_view(alien_foreground, SimulationController())
    painters = _content_painters(view)
    built = {type(widget).__name__ for widget in painters}

    absent = sorted(set(FOREGROUND_NOT_DECLARED) - built)

    assert absent == [], (
        "these kinds are exempted and the dashboard no longer builds them - remove "
        f"the entry: {absent}"
    )

    declared = _declared_colours()
    now_declaring = sorted(
        {
            type(widget).__name__
            for widget in painters
            if type(widget).__name__ in FOREGROUND_NOT_DECLARED
            and _resolved_foreground(widget) in declared
        }
    )

    assert now_declaring == [], (
        "these kinds declare a foreground now, so their exemption is stale - remove "
        f"the entry: {now_declaring}"
    )
