"""Every stylesheet a widget under `app/` is given, composed from `app/theme.py`'s values.

A visual decision is made once, here: how a panel's surface is drawn, what a
selector's popup looks like, which theme colour each state of a control takes.
Each function returns the text that is passed to a `setStyleSheet` call.
Every such call under `app/` passes the result of one of these functions, and
`tests/unit/test_stylesheets.py` enforces that. Where a widget's role decides
its colour, the widget still names the colour, as a caption does with
`foreground_stylesheet(MUTED)`. So the method that `tools/contrast_check.py`
cites for a colour pair is still the place where that pair is chosen.

**Nothing here imports a toolkit, and nothing needs one** (`PL-Y4YX`; project
owner, 2026-10-03, ratified, over composing these in `app/theme.py`, and over
that file importing the toolkit to become the styling layer). Each composer
takes the theme's values and returns a string, so it can be imported and
tested without a display, as the values can. This module sits beside
`theme.py` rather than inside it because the strings are written in Qt's
selector vocabulary, such as `QComboBox QAbstractItemView` and
`QSlider::handle:horizontal`. That vocabulary is the toolkit's styling
language even where nothing imports the toolkit, while `theme.py` is meant to
hold values alone. The few bare pixel spacings inside the strings are the
interim decision that D9 accepts. The interface pass, planned-milestone item
33 in `ROADMAP.md`, will decide the spacing rhythm that replaces them.
"""

from anesthesia_sim.app.theme import (
    ACCENT,
    BACKGROUND,
    GRIDLINE,
    INK,
    MENU_ARROW_GAP,
    MENU_ARROW_SIZE,
    MUTED,
    PANEL,
    PANEL_RADIUS,
    PRIMARY,
    AgentColorScheme,
)


def foreground_stylesheet(color: str) -> str:
    """A widget's foreground in one theme colour: a label's text, a check box's, a rule's line.

    Args:
        color: The value of a `theme.py` colour name. The colour reaches the
            widget through this string, never as a literal.

    Returns:
        The stylesheet.
    """

    return f"color: {color};"


def page_stylesheet(object_name: str) -> str:
    """The page behind the panels: BACKGROUND, scoped to one widget so its children keep theirs."""

    return f"QWidget#{object_name} {{ background-color: {BACKGROUND}; }}"


def scroll_area_stylesheet() -> str:
    """A scroll area in BACKGROUND, the page's own colour."""

    return f"QScrollArea {{ background-color: {BACKGROUND}; }}"


def panel_stylesheet(object_name: str) -> str:
    """The panel surface: PANEL, rounded, scoped to one widget so its children keep their own."""

    return (
        f"QWidget#{object_name} {{ background-color: {PANEL}; border-radius: {PANEL_RADIUS}px; }}"
    )


def slider_stylesheet() -> str:
    """The slider's track and thumb in the theme's colours.

    The filled part of the track is `ACCENT`, the colour that `PL-W8DQ`
    measures for it. Qt paints a styled sub-page only inside a groove that
    is itself styled, and a styled groove draws no thumb of its own. So
    this stylesheet styles all three parts: the unfilled track in
    `GRIDLINE`, the colour of the chart's grid lines, and the thumb as a
    `PANEL` disc edged in `MUTED`.
    """

    return (
        f"QSlider::groove:horizontal {{ background: {GRIDLINE}; height: 4px; "
        f"border-radius: 2px; }} "
        f"QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 2px; }} "
        f"QSlider::handle:horizontal {{ background: {PANEL}; border: 1px solid {MUTED}; "
        f"width: 14px; margin: -6px 0; border-radius: 8px; }}"
    )


def popup_stylesheet() -> str:
    """The list a selector opens: PANEL fill, INK rows, a PRIMARY selection.

    A combo box declares its *closed* surface in a stylesheet. The two view
    controls use `selector_stylesheet`, and the agent selector uses the
    running agent's ISO 5360 pair, `agent_selector_stylesheet`. A stylesheet
    on a widget makes everything inside the widget take its colours from the
    application palette rather than from the widget. The popup is a child
    item view, so it drew the host appearance's surface however the selector
    itself was styled. That was the defect in `PL-0NVN`.

    **This is a stylesheet rule rather than a palette on the view, because a
    palette there does not survive the widget being laid out.** A palette set
    on `QComboBox.view()` where the selector is built reads back correctly
    until the selector is added to a layout. At that point the popup is
    reparented, its palette re-resolves from the application's palette, and
    the declaration silently disappears. This was measured, after first
    shipping that way. Reparenting cannot undo a rule, and a rule is Qt's own
    documented idiom for the popup.

    The rule does not change the colour of each item. The three agent rows
    carry their ISO 5360 fill and foreground as `BackgroundRole` and
    `ForegroundRole`. The item delegate paints those colours from the model
    over whatever the view's own background is.
    """

    return (
        f"QComboBox QAbstractItemView {{ background-color: {PANEL}; color: {INK}; "
        f"selection-background-color: {PRIMARY}; selection-color: {PANEL}; }}"
    )


def selector_stylesheet() -> str:
    """A combo box a reader reads rather than merely operates: PANEL fill, MUTED edge, INK text.

    The playback-rate and time-base selectors name the rate at which the
    clock is advancing and how much of the run is on screen. `docs/MODEL.md`
    requires both to be displayed (`PL-SN2C`), so their surface is set here
    rather than left to the platform style. `tools/contrast_check.py`
    measures INK on PANEL for the text, and MUTED against each selector's own
    surroundings for the border. Both measurements are valid only because
    the colours are these.
    """

    return (
        f"QComboBox {{ background-color: {PANEL}; color: {INK}; border: 1px solid {MUTED}; "
        f"border-radius: {PANEL_RADIUS}px; padding: 4px 8px; }} " + popup_stylesheet()
    )


def view_chooser_stylesheet() -> str:
    """Return the style sheet for the View chooser, a flat menu button in an Area's header.

    `PL-RBXL` Q1 decided its look. At rest it has no frame and no fill, so the
    title looks like the header's own text, INK on the header's PANEL. Under the
    pointer, and while its menu is open, it is filled in BACKGROUND, the
    page's colour, with the title still in INK. While it has the keyboard
    focus, it has a 1px INK border. At rest the border is 1px and transparent,
    so the title does not move when the focus border appears.
    `tools/contrast_check.py` measures INK on both surfaces.

    The arrow that marks the menu sits in the right padding, centred on the
    title's line, as Blender's Editor Type selector draws its arrow after the
    icon. When the platform style placed the arrow, it sat at the bottom right
    corner, over the title's last letters (`PL-R5G4`). The arrow's size and gap
    are placeholders.
    """

    return (
        f"QToolButton {{ color: {INK}; background-color: transparent; "
        f"border: 1px solid transparent; border-radius: {PANEL_RADIUS}px; "
        f"padding: 2px {MENU_ARROW_SIZE + 2 * MENU_ARROW_GAP}px 2px 6px; }} "
        f"QToolButton:hover, QToolButton:open {{ background-color: {BACKGROUND}; }} "
        f"QToolButton:focus {{ border-color: {INK}; }} "
        "QToolButton::menu-indicator { subcontrol-origin: padding; "
        f"subcontrol-position: center right; right: {MENU_ARROW_GAP}px; "
        f"width: {MENU_ARROW_SIZE}px; height: {MENU_ARROW_SIZE}px; }}"
    )


def workspace_tab_stylesheet() -> str:
    """Return the style of a Workspace tab, with the active tab in bold INK over a PRIMARY line.

    `PL-QW1Z` Q2 decided its look. A tab has no fill, so its label sits on the
    page's BACKGROUND. An inactive tab is MUTED and regular, and turns INK
    under the pointer. The active tab is INK and bold, with a 2px PRIMARY line
    along its lower edge, so weight and shape tell it apart as well as colour.
    A tab with the keyboard focus has a 1px INK edge on its other three sides.
    At rest those sides have a transparent edge of the same width, so the
    label does not move when the focus arrives. `tools/contrast_check.py`
    measures each pair on BACKGROUND.
    """

    return (
        f"QToolButton {{ color: {MUTED}; background-color: transparent; font-weight: normal; "
        "border: 1px solid transparent; border-bottom: 2px solid transparent; "
        "padding: 2px 10px; } "
        f"QToolButton:hover {{ color: {INK}; }} "
        f"QToolButton:checked {{ color: {INK}; font-weight: bold; "
        f"border-bottom-color: {PRIMARY}; }} "
        f"QToolButton:focus {{ border-left-color: {INK}; border-top-color: {INK}; "
        f"border-right-color: {INK}; }}"
    )


def workspace_separator_stylesheet() -> str:
    """The rule between the shipped Workspaces' tabs and the reader's own, in MUTED.

    `PL-QW1Z` Q4 asked for a GRIDLINE rule. But GRIDLINE's contrast on
    BACKGROUND is less than the 3:1 that WCAG SC 1.4.11 requires, and this rule
    is the one thing on screen that shows where the shipped tabs end. So it is
    drawn in MUTED, which `tools/contrast_check.py` measures on BACKGROUND
    (`PL-2KXB`).
    """

    return f"background-color: {MUTED};"


def menu_stylesheet() -> str:
    """A menu a button opens: PANEL fill, INK entries, a PRIMARY selection, as a popup draws.

    An entry that is unavailable, such as a join the layout cannot make, is
    drawn in MUTED, so it looks unavailable rather than like an entry that
    does nothing (`PL-2KXB`). `tools/contrast_check.py` measures MUTED on
    PANEL at the full text minimum.
    """

    return (
        f"QMenu {{ background-color: {PANEL}; color: {INK}; border: 1px solid {MUTED}; }} "
        f"QMenu::item:selected {{ background-color: {PRIMARY}; color: {PANEL}; }} "
        f"QMenu::item:disabled {{ color: {MUTED}; }}"
    )


def transport_button_stylesheet() -> str:
    """Start, Pause and Reset in both states: PANEL fill, MUTED edge, INK or MUTED label.

    These colours are declared rather than left to the platform style,
    because leaving them to it caused `PL-DHBX`. A button that sets no
    foreground takes one from the `ButtonText` role of Qt's palette, and that
    role holds the *host appearance's* value rather than this interface's.
    Under macOS Dark it is near-white, while every surface this interface
    draws around the button stays in the light theme. So the labels became
    white on white, and the run controls could not be read.

    **Both states are declared, because the project owner's screenshots
    showed the second state failing the same way.** The first fix declared
    `:enabled` only. It left the disabled button entirely to the platform, on
    `PL-NGF7`'s decision of 2026-09-16 and on the exemption in WCAG 2.2 SC
    1.4.3 for text in an inactive component. On `0.4.26+g22bc6d82` the
    disabled button was then the invisible one: Start while running, and
    Pause while paused. That decision's case did not account for this cost.
    Under a dark host appearance, the platform's disabled grey is not merely
    low in contrast. It is absent. An exemption from a contrast *minimum*
    does not permit a control to disappear.

    So the disabled label is `MUTED`, which is **5.00:1 on PANEL**. That
    fully meets the 4.5:1 that SC 1.4.3 requires for normal text, so no
    exemption is claimed for it. This matters, because the wording of SC
    1.4.11 on inactive components has never been read at its source from
    this container (`PL-JX0Z`; `w3.org` was still refused at the CONNECT on
    2026-10-06). So nothing in this interface may depend on that wording.

    **The two states are not told apart by colour alone.** Judgment 2 in
    `.claude/rules/ui-color.md` asks for a second channel, and the row
    already carries one in text. `_status_text`, beside these three buttons,
    says "Running" or "Paused", and that state is what decides which button
    is unavailable. `dashboard_frame.transport` derives both the word and the
    unavailable button from the same flag. A reader who cannot tell INK from
    MUTED can read the state from the word instead of from the buttons.

    The edge stays `MUTED` in both states, because the edge is what shows the
    control's boundary. The fill cannot show it, since `PANEL` on
    `BACKGROUND` is 1.07:1. A user-interface component needs the 3:1 that SC
    1.4.11 sets, and `MUTED` meets it at 4.65:1 against the row behind it.
    Softening the edge for the disabled state would have added a second
    visual channel but lost the boundary.

    `tools/contrast_check.py` measures all three pairs, and
    `check_disabled_states_are_the_style_s` enforces that. It accepts a
    `:disabled` rule only from a function that a requirement cites.
    """

    return (
        f"QPushButton {{ background-color: {PANEL}; border: 1px solid {MUTED}; "
        f"border-radius: {PANEL_RADIUS}px; padding: 4px 12px; }} "
        f"QPushButton:enabled {{ color: {INK}; }} "
        f"QPushButton:disabled {{ color: {MUTED}; }}"
    )


def outlined_button_stylesheet() -> str:
    """The secondary action: INK on PANEL inside an INK border.

    `NewCaseDialog`'s discard button is drawn in this style, and
    `tools/contrast_check.py` measures the style's colours on that button. So
    the other buttons drawn the same way declare no colour of their own.
    """

    return (
        f"QPushButton {{ color: {INK}; background-color: {PANEL}; "
        f"border: 1px solid {INK}; border-radius: {PANEL_RADIUS}px; padding: 6px 12px; }}"
    )


def filled_button_stylesheet() -> str:
    """The primary action: PANEL on PRIMARY, as `NewCaseDialog`'s keep button draws."""

    return (
        f"QPushButton {{ color: {PANEL}; background-color: {PRIMARY}; "
        f"border: 1px solid {PRIMARY}; border-radius: {PANEL_RADIUS}px; padding: 6px 12px; }}"
    )


def agent_surface_stylesheet(object_name: str, scheme: AgentColorScheme) -> str:
    """A frame filled in the agent's colour and edged in its foreground.

    The edge is what keeps a sevoflurane badge visible at all. The badge's
    fill is 1.27:1 against the page, so without a border the coloured region
    that a reader is meant to recognise loses its shape (`PL-GNN1`).
    """

    return (
        f"QFrame#{object_name} {{ background-color: {scheme.fill}; color: {scheme.foreground}; "
        f"border: 1px solid {scheme.foreground}; border-radius: {PANEL_RADIUS}px; }}"
    )


def agent_text_stylesheet(scheme: AgentColorScheme) -> str:
    """A label in the agent's foreground over its fill."""

    return f"color: {scheme.foreground}; background-color: {scheme.fill};"


def agent_selector_stylesheet(scheme: AgentColorScheme) -> str:
    """The agent selector in the running agent's pair, edged in its foreground.

    The popup that the selector opens is not in the agent's colours and does
    not change with the agent. It lists all three agents, and each row
    carries its own ISO 5360 fill as item data. So the list's own surface
    uses the interface's colours (`popup_stylesheet`). The popup rule is
    appended here, rather than set once at construction, so that it
    survives the selector being laid out (`PL-0NVN`).
    """

    return (
        f"QComboBox {{ background-color: {scheme.fill}; color: {scheme.foreground}; "
        f"border: 1px solid {scheme.foreground}; border-radius: {PANEL_RADIUS}px; "
        f"padding: 4px 8px; font-weight: bold; }} " + popup_stylesheet()
    )
