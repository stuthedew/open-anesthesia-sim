"""Every stylesheet a widget under `app/` is given, composed from `app/theme.py`'s values.

A visual decision is made once, here: how a panel's surface is drawn, what a
selector's popup looks like, which theme colour each state of a control takes.
Each function returns the text a `setStyleSheet` call is passed, and every such
call under `app/` passes one of them, which `tests/unit/test_stylesheets.py`
holds. Where a widget's role decides its colour, the widget still names it - a
caption's `foreground_stylesheet(MUTED)` - so the method
`tools/contrast_check.py` cites for a pair is still where the pair is chosen.

**Nothing here imports a toolkit, and nothing needs one** (`PL-Y4YX`; project
owner, 2026-10-03, ratified, over composing these in `app/theme.py`, and over
that file importing the toolkit to become the styling layer). A composer takes
the theme's values and returns a string, so it imports and tests without a
display, as the values do. It sits beside `theme.py` rather than in it because
the string is written in Qt's selector vocabulary - `QComboBox
QAbstractItemView`, `QSlider::handle:horizontal` - which is the toolkit's
styling even where nothing imports it, while `theme.py` is read as values
alone. The few bare pixel spacings inside the strings are the interim decision
D9 accepts; the interface pass, planned-milestone item 33 in `ROADMAP.md`,
decides the spacing rhythm that replaces them.
"""

from anesthesia_sim.app.theme import (
    ACCENT,
    BACKGROUND,
    GRIDLINE,
    INK,
    MUTED,
    PANEL,
    PANEL_RADIUS,
    PRIMARY,
    AgentColorScheme,
)


def foreground_stylesheet(color: str) -> str:
    """A widget's foreground in one theme colour: a label's text, a check box's, a rule's line.

    Args:
        color: A `theme.py` colour name's value; it reaches the widget through
            this string, never as a literal.

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

    The active track is `ACCENT`, the colour `PL-W8DQ` measures for it. Qt
    paints a styled sub-page only inside a groove that is itself styled,
    and a styled groove draws no thumb of its own, so all three parts are
    given here: the unfilled track in `GRIDLINE`, the ruling colour, and
    the thumb as a `PANEL` disc edged in `MUTED`.
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

    A combo box declares its *closed* surface in a stylesheet -
    `selector_stylesheet` for the two view controls, the running agent's
    ISO 5360 pair, `agent_selector_stylesheet`, for the agent selector - and
    a stylesheet on a widget makes everything inside it resolve from the
    application palette rather than from the widget. The popup is a child
    item view, so it drew the host appearance's surface however the selector
    itself was styled, which is `PL-0NVN`.

    **A rule rather than a palette on the view, because a palette there does
    not survive the widget being laid out.** Setting one on
    `QComboBox.view()` where the selector is built reads back correctly
    until the selector is added to a layout, at which point the popup is
    reparented, its palette re-resolves from the application's, and the
    declaration is silently gone - measured, having first shipped that way.
    A rule cannot be undone by reparenting, and this is Qt's own documented
    idiom for the popup.

    Per-item colour is untouched by it: the three agent rows carry their
    ISO 5360 fill and foreground as `BackgroundRole` and `ForegroundRole`,
    which the item delegate paints from the model over whatever the view's
    own background is.
    """

    return (
        f"QComboBox QAbstractItemView {{ background-color: {PANEL}; color: {INK}; "
        f"selection-background-color: {PRIMARY}; selection-color: {PANEL}; }}"
    )


def selector_stylesheet() -> str:
    """A combo box a reader reads rather than merely operates: PANEL fill, MUTED edge, INK text.

    The playback-rate and time-base selectors name the rate the clock is
    advancing at and how much of the run is on screen, which
    `docs/MODEL.md` requires displayed (`PL-SN2C`), so their surface is set
    here rather than left to the platform style: `tools/contrast_check.py`
    measures INK on PANEL for the text and MUTED against each selector's own
    surroundings for the border, and both claims hold only because the
    colours are these.
    """

    return (
        f"QComboBox {{ background-color: {PANEL}; color: {INK}; border: 1px solid {MUTED}; "
        f"border-radius: {PANEL_RADIUS}px; padding: 4px 8px; }} " + popup_stylesheet()
    )


def view_chooser_stylesheet() -> str:
    """The View chooser in an Area's header: a flat menu button, INK on its surface.

    `PL-RBXL` Q1 decided its look. At rest it has no frame and no fill, so the
    title reads as the header's own text, INK on the header's PANEL. Under the
    pointer, and while its menu is open, it is filled in BACKGROUND, the
    page's colour, with the title still in INK. With the keyboard focus it
    carries a 1px INK edge, which the transparent edge at rest keeps from
    moving the title. `tools/contrast_check.py` measures INK on both surfaces.
    """

    return (
        f"QToolButton {{ color: {INK}; background-color: transparent; "
        f"border: 1px solid transparent; border-radius: {PANEL_RADIUS}px; padding: 2px 6px; }} "
        f"QToolButton:hover, QToolButton:open {{ background-color: {BACKGROUND}; }} "
        f"QToolButton:focus {{ border-color: {INK}; }}"
    )


def workspace_tab_stylesheet() -> str:
    """A Workspace tab: MUTED text on the page, the active one INK bold over a PRIMARY line.

    `PL-QW1Z` Q2 decided its look. A tab has no fill, so its label stands on
    the page's BACKGROUND. An inactive tab is MUTED and regular, and the
    pointer lifts it to INK. The active tab is INK and bold, with a 2px
    PRIMARY line along its lower edge, so weight and a shape tell it apart as
    well as colour. With the keyboard focus a tab carries a 1px INK edge on
    its other three sides, which a transparent edge at rest keeps from moving
    the label. `tools/contrast_check.py` measures each pair on BACKGROUND.
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

    `PL-QW1Z` Q4 asked for a GRIDLINE rule. GRIDLINE measures under SC
    1.4.11's 3:1 on BACKGROUND, and here the rule is the one thing on screen
    that shows where the shipped tabs end. So it is drawn in MUTED, which
    `tools/contrast_check.py` measures on BACKGROUND (`PL-2KXB`).
    """

    return f"background-color: {MUTED};"


def menu_stylesheet() -> str:
    """A menu a button opens: PANEL fill, INK entries, a PRIMARY selection, as a popup draws.

    An entry that is unavailable, such as a join the layout cannot make, is
    drawn in MUTED, so it reads as unavailable rather than as an entry that
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

    Declared rather than left to the platform style, which is what `PL-DHBX`
    was: a button that sets no foreground takes one from Qt's palette
    `ButtonText` role, and that role is the *host appearance's* value rather
    than this interface's. Under macOS Dark it is near-white, while every
    surface this interface draws around it stays the light theme's - so the
    labels went to white-on-white and the run controls could not be read.

    **Both states, because the project owner's screenshots showed the second
    half failing the same way.** The first fix declared `:enabled` only and
    left the disabled button whole to the platform, on `PL-NGF7`'s decision of
    2026-09-16 and on WCAG 2.2 SC 1.4.3's exemption for text in an inactive
    component. On `0.4.26+g22bc6d82` the disabled button was then the invisible
    one - Start while running, Pause while paused - which is the cost that
    decision's case did not carry: the platform's disabled grey is not merely
    low-contrast under a dark host appearance, it is absent. An exemption from
    a contrast *minimum* is not a licence for a control to disappear.

    So the disabled label is `MUTED`, which is **5.00:1 on PANEL** and clears
    SC 1.4.3's 4.5:1 for normal text outright. No exemption is claimed for it,
    which matters here: SC 1.4.11's own inactive-component wording has never
    been read at the source from this container (`PL-JX0Z`; `w3.org` was still
    refused at the CONNECT on 2026-10-06), so nothing in this interface may rest
    on it.

    **The two states are not separated by colour alone.** `.claude/rules/ui-color.md`
    judgment 2 asks for a second channel, and the row already carries one in
    text: `_status_text` beside these three says "Running" or "Paused", which
    is what decides which button is unavailable - `dashboard_frame.transport`
    derives both from the same flag. A reader who cannot resolve INK from MUTED
    reads the state from the word, not from the buttons.

    The edge stays `MUTED` in both states. It is what identifies the control's
    boundary - `PANEL` on `BACKGROUND` is 1.07:1, so the fill does not - and a
    user-interface component needs SC 1.4.11's 3:1, which `MUTED` meets at
    4.65:1 against the row behind it. Softening it for the disabled state would
    have bought a second visual channel at the price of the boundary.

    `tools/contrast_check.py` measures all three pairs, and
    `check_disabled_states_are_the_style_s` is what requires that: a
    `:disabled` rule is admitted only from a function a requirement cites.
    """

    return (
        f"QPushButton {{ background-color: {PANEL}; border: 1px solid {MUTED}; "
        f"border-radius: {PANEL_RADIUS}px; padding: 4px 12px; }} "
        f"QPushButton:enabled {{ color: {INK}; }} "
        f"QPushButton:disabled {{ color: {MUTED}; }}"
    )


def outlined_button_stylesheet() -> str:
    """The secondary action: INK on PANEL inside an INK border.

    `NewCaseDialog`'s discard button is drawn in it, which
    `tools/contrast_check.py` measures, so the buttons drawn the same way
    declare no colour of their own.
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

    The edge is the channel that keeps a sevoflurane badge visible at all:
    its fill is 1.27:1 against the page, so without a border the coloured
    region a reader is meant to recognise loses its shape (`PL-GNN1`).
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

    The popup it opens is not in the agent's colours and does not vary with
    the agent: it lists all three, each row carrying its own ISO 5360 fill
    as item data, so the list's own surface is the interface's
    (`popup_stylesheet`). Appending it here rather than setting it once at
    construction is what makes it survive the selector being laid out
    (`PL-0NVN`).
    """

    return (
        f"QComboBox {{ background-color: {scheme.fill}; color: {scheme.foreground}; "
        f"border: 1px solid {scheme.foreground}; border-radius: {PANEL_RADIUS}px; "
        f"padding: 4px 8px; font-weight: bold; }} " + popup_stylesheet()
    )
