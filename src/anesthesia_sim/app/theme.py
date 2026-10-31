"""Shared color and spacing constants for the interface."""

from dataclasses import dataclass
from typing import Final

BACKGROUND = "#F4F7FA"
PANEL = "#FFFFFF"
PRIMARY = "#176B87"
# ACCENT is a *graphical* color: it draws the sliders' active track. It is too
# light to be read as text. It measures 3.21:1 on the panel, and SC 1.4.3 asks
# 4.5:1 of text. So text that should look like the accent uses ACCENT_TEXT
# below. PL-30P6 found one constant serving both roles. The two roles have
# different WCAG minimum ratios (4.5:1 for text under SC 1.4.3, 3:1 for
# graphical objects under SC 1.4.11). No single value can be chosen to suit both
# roles without one of them losing out.
#
# ACCENT was also the alveolar chart trace until PL-GVXP, which made the other
# half of the same split. A chart trace has to reach 3:1 against the panel
# under simulated dichromacy as well as under normal vision. It also has to
# stay separable from five sibling traces. A slider track has neither
# constraint. The trace now has its own value, `ALVEOLAR_COLOR` below, so
# ACCENT is limited only by its contrast with the panel behind it. PL-W8DQ
# needed to know that before it darkened ACCENT, which is why PL-W8DQ waited
# for PL-GVXP.
#
# Darkened from #18A999 on 2026-09-16 (PL-W8DQ). The old value measured 2.93:1
# against the panel. That is less than SC 1.4.11's 3:1 for a user-interface
# component, by an amount no reader would ever spot by eye. The four parameter
# sliders are the simulator's entire input surface. The active track is the
# only continuous cue to where a value sits in its range. So a reader who
# cannot tell the filled part of the track from the unfilled part has to read
# the number twice.
#
# Now 3.21:1. Hue and saturation are unchanged to two decimal places: 173.4 deg
# and 0.858 become 173.5 and 0.857, which is 8-bit rounding. So this is a
# uniform darkening, in the same sense that ACCENT_TEXT is one, and the accent
# family still looks like one color. The target was the *lightest* value that
# reaches 3.2:1 rather than 3.0:1. That is the same margin of two tenths that
# the six traces were re-picked with, so the shipped value is not itself the
# boundary case that the next edit trips over.
#
# One requirement now limits ACCENT, and no other role uses ACCENT. PL-GVXP gave
# the alveolar trace its own ALVEOLAR_COLOR, so darkening ACCENT changes the
# four slider tracks and nothing else. A trace would also have to reach 3:1
# under simulated dichromacy and stay separable from five siblings, and ACCENT
# has neither constraint. The filled track sits in the GRIDLINE groove, and
# darkening only increases its separation from that groove.
ACCENT = "#17A192"
# The accent, dark enough to be read as text: 5.00:1 on PANEL and 4.65:1 on
# BACKGROUND. It is a uniform darkening of ACCENT, so hue and saturation are
# unchanged (173 deg, 0.86) and the two still look like one color family. It
# colors the affirmative status words, "Running" and "Valid", whose counterpart
# is WARNING. Never use ACCENT for text, and never use ACCENT_TEXT for a chart
# trace. Keeping the two roles apart is the reason both constants exist.
ACCENT_TEXT = "#127D71"
INK = "#243B53"
# Darkened from #627D98 (PL-X0RG). The old value reached only 4.28:1 on the
# panel and 3.98:1 on the page background. Both are less than WCAG 2.2 SC
# 1.4.3's 4.5:1 for text. MUTED colors the label naming every readout, the
# run-status word and the chart's axis description. The page background, not
# the panel, is the surface that limits the choice. The run-status text sits in
# the top-level column, so BACKGROUND shows through behind it. Now 5.00:1 on
# PANEL and 4.65:1 on BACKGROUND. The hue and saturation are unchanged (210 deg,
# 0.355), so the label/value hierarchy against INK looks as it did.
MUTED = "#59728A"
# WARNING is the one signal this interface has. It deliberately does NOT follow
# the medical alarm-colour convention (project owner, 2026-09-14, on PL-LL9Y).
#
# IEC 60601-1-8 governs *visual alarm signals*. Those are indicators that
# encode priority by colour together with a flash rate, and this interface has
# none. Every use of WARNING is bold, coloured text: the run-status word, the
# transient notice line, the agent-accounting status word, the permanent
# educational disclaimer, and the case-discard dialog. There is no indicator
# lamp, no filled banner, no flashing element and no priority tier.
#
# The disclaimer is the use that settles the question, and it argues against
# adopting the convention. WARNING colours a line that is on screen *always*.
# A monitor's alarm colours carry their meaning precisely because they are
# absent until something is wrong. Painting a permanent element in a high- or
# medium-priority alarm colour would teach the opposite of the convention it
# borrowed: an alarm colour that means nothing, from the moment the app opens.
# The deliberate divergence also keeps a teaching tool from being mistaken for
# a monitor, which is the reason the owner chose it.
#
# This rule applies to the Qt port as much as to this file. The port decides
# the palette again, and it is where an indicator-shaped surface could first
# appear. The port must not bring in a monitor's priority palette. Two things
# are unaffected. PL-MMYM's contrast target applies to whatever colour is
# chosen. The ISO 5360 agent colours below are also unchanged, because they
# identify an agent and carry no urgency. That is why ISO 5360 Table 2
# footnote b places an obligation on the agent colours, while nothing places
# one on WARNING.
#
# The interface already applies this economy of signals one level down, in
# `dashboard_frame.py`'s supported-run-length status word. That boundary is
# shown in MUTED, not WARNING. Colouring a correct model's declared boundary as
# a fault would teach a reader to distrust a number that is sound. It would also
# spend the interface's one signal, which is kept for a real fault.
WARNING = "#8A4B08"


@dataclass(frozen=True)
class AgentColorScheme:
    """Screen approximation and accessible text color for one agent code."""

    fill: str
    foreground: str
    standard_color_name: str
    standard_color_munsell: str
    standard_color_pantone: str


# Agent-identification colors from ISO 5360:2016 (fourth edition, 2016-02-15,
# which cancels and replaces ISO 5360:2012), Table 2, "Dimensions and colours
# of agent-specific bottle collars and connectors".
# https://www.iso.org/standard/68417.html
#
# Table 2 footnote b is why these colors belong in this UI at all: "If a colour
# is used on a vaporizer, bottle, or package label to facilitate correct
# identification, it is important that only the colour for the appropriate
# anaesthetic agent be used." Displaying a color obligates displaying the right
# one, which makes a wrong mapping here a safety defect rather than a styling
# defect.
#
# Provenance chain, most authoritative first. Table 2 footnote c: "Munsell
# colour is the original. Other colour systems show the nearest available
# colour sample." So the ISO original is the Munsell notation. The Pantone
# reference is already ISO's own nearest sample of it, and `fill` is a further
# sRGB approximation of the Pantone. Two of the three Munsell originals fall
# outside the sRGB gamut, so no display can reproduce them exactly.
# `docs/MODEL.md` records the measured deviation of each `fill` from its
# Munsell original.
#
# ISO 5360 does not specify desflurane's *dimensions*. Its Scope excludes them,
# and Table 2 gives "N.S." for the desflurane collar angle. But the same row of
# Table 2 does specify its *colour*, and that colour is what is used here.
#
# Text colors are deliberately separate from the identification colors. Each
# pair exceeds WCAG 2.2's 4.5:1 minimum for normal text; the agent name remains
# visible everywhere the color appears, so color is never the only cue.
# https://www.w3.org/TR/WCAG22/#contrast-minimum
#
# That claim is about the pair *as rendered*, and nothing enforces it
# automatically. A control drawn in `foreground` over `fill` can still reach
# the screen in another colour entirely if a widget state overrides it. The
# agent selector did this for the whole of every run (PL-61WW). Flet/Material
# paints a disabled control's label in the theme's disabled-content grey. This
# file does not declare that colour, so `tools/contrast_check.py` cannot
# measure it, and the fill under the label stayed saturated. The fix is in
# `app/run_view.py`, and it is structural rather than a colour change. Nothing
# that carries agent identity is disabled, so the pair measured here is the
# pair rendered. A new use of these colours must answer the same question: can
# anything between this constant and the screen substitute a colour of its own?
AGENT_COLOR_SCHEMES: Final[dict[str, AgentColorScheme]] = {
    "sevoflurane": AgentColorScheme(
        fill="#FEDB00",
        foreground=INK,
        standard_color_name="Yellow",
        standard_color_munsell="6.25Y 8.5/12",
        standard_color_pantone="Pantone 108 C",
    ),
    "isoflurane": AgentColorScheme(
        fill="#981D97",
        foreground="#FFFFFF",
        standard_color_name="Purple",
        standard_color_munsell="7.5P 4/12",
        standard_color_pantone="Pantone 254 C",
    ),
    "desflurane": AgentColorScheme(
        fill="#00629B",
        foreground="#FFFFFF",
        standard_color_name="Blue",
        standard_color_munsell="10B 4/10",
        standard_color_pantone="Pantone 3015 C",
    ),
}

# --- Display tokens ---------------------------------------------------------
#
# Everything below was module-level in `app/simulation_view.py` until PL-2CS8.
# `ROADMAP.md`'s planned-milestone item 24 names gathering these values in one
# place as its own prerequisite. The roadmap's "Development pathway" Phase 2
# puts that step first, "because every control added before it spreads the
# same scattered defaults further". v0.5.0's bookmarks, MAC targets and two-run
# overlay were about to do exactly that.
#
# The values are here rather than in a new module because this file already
# *was* the tokens module: it held the palette and the spacing constants. A
# third file beside it would be the "fourth scattered location" that item 24
# warns against. The move also shortened `tools/contrast_check.py`, which read
# two files only because the six trace colours lived in the view.
#
# **This module stays free of any toolkit.** A display constant that needs a
# toolkit type belongs in the module that draws it. The Flet build's
# `METRIC_GRID_COLUMNS` and `AGENT_RENDER_STYLES` stayed out of this file for
# that reason.
#
# Until 2026-09-16, the reason given here was that `tools/contrast_check.py`
# and `tools/agent_identity_check.py` read this file in a bare checkout, so the
# file must import nothing they would have to install. That reason does not
# support the rule. Both tools call `ast.parse` on the file's *text*
# (`contrast_check.read_palette`, `agent_identity_check.read_modules`).
# `ast.parse` executes nothing and resolves no import, so a `from PySide6...`
# line at the top would leave both tools working exactly as they do. The
# correction matters because a rule defended by a reason that a reader can
# check and find false is a rule that the next session deletes (`PL-Y4YX`).
#
# The real reason is this. This file is the one place where a *value* that
# could mislead a clinician is written down. So it is worth being able to
# import and test it without a display, a Qt event loop or a plugin. `tests/`
# reads it directly, and so can any code that never draws.
#
# **The stylesheets that draw these values are composed beside this file, in
# `app/stylesheets.py`, and not in it** (project owner, 2026-10-03, ratified,
# over composing them here, `PL-Y4YX`). The toolkit-free rule and the aim to
# "make each visual decision once" turned out not to conflict. A composer takes
# these values and returns a string, so it needs no toolkit either, and every
# `setStyleSheet` call under `app/` passes one. Tokens are values, and
# composers are strings. They stay in separate files for two reasons. First, a
# composer is written in Qt's selector vocabulary, which is the toolkit's
# styling language even where nothing imports the toolkit. Second,
# `contrast_check.read_palette` reads this file as tokens in file order, and
# functions among the constants would make that reading harder to follow.
#
# **The order of the constants matters.** `contrast_check.read_palette`
# resolves a bare name against the palette built so far, in file order. So an
# alias must sit below the constant it aliases: `CIRCUIT_COLOR = PRIMARY` below
# `PRIMARY`, and `WASH_IN_COLOR = ALVEOLAR_COLOR` below `ALVEOLAR_COLOR`. If an
# alias moves above its referent, it resolves to `None` and drops out of the
# palette, and the requirement that cites it is reported as missing.

CHART_HEIGHT = 360

PAGE_PADDING = 16

PANEL_PADDING = 14

# VIEW_ROW_SPACING is the gap between the rows that a View stacks inside its
# Area. VIEW_HEADING_SPACING is the gap between a chart View's heading and the
# time-base control beside it.
VIEW_ROW_SPACING = 6

VIEW_HEADING_SPACING = 8

PANEL_RADIUS = 10

# The size of the arrow that marks the View chooser's menu, and the space on
# each side of it, in px (`PL-R5G4`). Both are placeholders until the visual
# pass.
MENU_ARROW_SIZE = 8
MENU_ARROW_GAP = 4

# The gap between the rows of the control-change panel: its heading, caption,
# entries and overflow line.
CONTROL_TIMELINE_ROW_SPACING = 4

# The clinical gloss under a compartment name is deliberately smaller than the
# name above it. The name says which quantity the model computes, and that is
# the main claim. The gloss says what a clinician would compare it against,
# which is a secondary claim, and the type sizes show that order. The gloss
# uses the same MUTED colour as the name, so it adds no pair to
# `tools/contrast_check.py`. It is still normal text, so it must meet WCAG's
# 4.5:1.
METRIC_NAME_SIZE = 14

METRIC_QUALIFIER_SIZE = 12

# The same kind of gloss, one panel row up, under a *control* name rather than
# a readout name (`_build_parameter_panel`). A reader meets the two as one
# idiom: the fine print that says what the name above it actually refers to.
# So they are deliberately the same size. Aliasing the constant, rather than
# writing 12 twice, stops the two sizes drifting apart unnoticed.
PARAMETER_QUALIFIER_SIZE = METRIC_QUALIFIER_SIZE

# The MAC line under each reading, in the same relationship to the percent
# above it as the gloss is to the compartment name: smaller and MUTED, because
# it is the weaker of the two claims. Percent is what the model computes and
# what a monitor would show; a MAC multiple is that number divided by a
# population constant this model does not otherwise use, and on the four
# non-alveolar compartments it is a partial-pressure ratio rather than
# anything a clinician reads off a patient. Its size falls between the name's
# and the gloss's, so the type sizes rank the row as value, then unit
# conversion, then annotation.
METRIC_SECONDARY_VALUE_SIZE = 13

# The rest of the type scale. Until PL-2CS8 these sizes were bare literals at
# their call sites, while the three sizes above were named. So the scale was
# half declared and half literal, and a reader could not see it whole. These
# constants complete it, at the values already shipping.
METRIC_VALUE_SIZE = 22
ACCOUNTING_STATUS_SIZE = 20

# The six compartment traces. Two things decide these values, and only one of
# them is a colour question.
#
# **Against the panel, each trace must reach 3:1, under simulated dichromacy
# as well as under normal vision.** SC 1.4.11 asks this of the displayed
# colour. This interface also asks it of the Brettel 1997 simulation of that
# colour, because a trace that a protanope cannot find against white is not
# separable from the panel, whatever the criterion measures. `ALVEOLAR_COLOR`
# and `MUSCLE_COLOR` were re-picked for that reason alone (PL-GVXP). Both keep
# their own hue and saturation exactly. Each was darkened to the lightest shade
# that reaches 3.2:1 in all four models. That is 3:1 plus two tenths, so the
# shipped value is not itself the boundary case that the next edit trips over.
# `tools/contrast_check.py` measures all four and `docs/MODEL.md` records them.
#
# **Between traces, colour is not the separating channel, and no palette could
# make it one.** Contrast ratios compose along a single bounded axis. The 3:1
# minimum above caps every trace's luminance at 0.30, so six traces cannot all
# be more than 1.48 apart. With hue and saturation held fixed, a search over lightness alone
# reaches 1.28 across the four models, and it drives four of the six traces to
# near-black. Both figures are far less than the 3:1 that would make colour
# sufficient. So the line style below is what separates the traces, and these
# hues are chosen to name their compartment rather than to win an arithmetic
# that cannot be won (`.claude/rules/ui-color.md`, judgment 3).
CIRCUIT_COLOR = PRIMARY

# The alveolar trace has its own value rather than sharing `ACCENT`, as it used
# to. The two roles gained different constraints when the trace acquired the
# 3:1 minimum in all four models, which five other traces also have to meet.
# `ACCENT`'s remaining role, the sliders' active track, is limited only by its
# contrast with the panel behind it. That is the question `PL-W8DQ` was
# waiting on: `ACCENT` is no longer a chart colour, so it can be darkened on
# the sliders' own terms.
ALVEOLAR_COLOR = "#159789"

MIXED_VENOUS_COLOR = "#7C3AED"

VESSEL_RICH_COLOR = "#DC2626"

MUSCLE_COLOR = "#D17206"

FAT_COLOR = "#64748B"

# This is the width of the colour swatch that every line's legend entry draws.
# Every such swatch has this width, in any of the four legend rows, so that a
# reader scanning down them compares marks rather than shapes. Its height is
# `LEGEND_SWATCH_HEIGHT` or the line's own stroke width rounded up, whichever
# is greater. The control mark, the fork mark and the MAC-awake band are the
# exceptions, with the sizes below, because a tick and a band are not lines.
LEGEND_SWATCH_WIDTH = 24

LEGEND_SWATCH_HEIGHT = 4

# Two legend marks that are not a trace swatch, and so cannot use the pair
# above. A control mark is a vertical tick, and the MAC-awake band is an
# interval rather than a line. These sizes were bare literals at their call
# sites until PL-2CS8.
CONTROL_MARK_SWATCH_WIDTH = 3
CONTROL_MARK_SWATCH_HEIGHT = 16
BAND_SWATCH_WIDTH = 24
BAND_SWATCH_HEIGHT = 12

# The gaps inside a legend, in px. This one is between an entry's swatch and
# the words that name it.
LEGEND_SWATCH_SPACING = 6

# This gap separates two entries side by side on one line of a legend row. It
# also separates a row's caption from its first entry. It is wider than the
# swatch gap above, so each swatch looks like part of the words to its right and
# not part of the entry before it.
LEGEND_ENTRY_SPACING = 16

# This gap separates two lines of a legend. It is the same whether the second
# line starts a new row or continues a row that wrapped, so a wrapped row is
# spaced like the rows around it. The three legend gaps are placeholders until
# planned-milestone item 33's visual pass.
LEGEND_LINE_SPACING = 6

# The rule between the concentration panel and the wash-in section below it.
SECTION_DIVIDER_HEIGHT = 16

# The two chart references are furniture, meaning chart marks that are not
# data. They are drawn in the interface's own ink and label colours rather
# than in a seventh and eighth hue. A new hue would join the trace palette's
# separation problem (`.claude/rules/ui-color.md`, judgment 3: six traces
# already cannot all reach 3:1 against each other on a bounded axis). It would
# also imply that the mark is another compartment. Instead, a reference is
# separated from a trace by its *kind*: it is constant and horizontal, and it
# spans the window. It is also separated by its mark type, and the mark type is
# what separates the two references from each other. A band marks a measured
# population value with real spread, and a line marks a definitional anchor.
# That distinction survives greyscale and every colour-vision deficiency, which
# `.claude/rules/ui-color.md`'s judgment 2 requires of any encoding that
# carries meaning.
#
# The ranking between the two references is deliberate: INK for the band
# against MUTED for the line. After a long case at a steady setpoint, the
# alveolar and vessel-rich traces have converged, so it matters little which
# trace the 1 MAC anchor is read against. At MAC-awake the traces have not
# converged, so the band is the mark whose reading depends on the trace, and
# it carries the heavier weight. Giving the easier mark equal weight is the
# failure that PL-F52R names.
MAC_AWAKE_BAND_COLOR = INK

ONE_MAC_LINE_COLOR = MUTED

# The band's fill is decoration. Each of the band's two boundaries is drawn as
# a stroke in `MAC_AWAKE_BAND_COLOR`, and that colour is what
# `tools/contrast_check.py` measures. The fill is light enough for six traces
# to stay legible across it. A fill that met 3:1 on its own would not be.
MAC_AWAKE_BAND_FILL_OPACITY = 0.14

# The band is stroked on both edges. That is the geometry its mark type
# depends on, not a styling choice. One standard deviation either side of the
# published mean is 3.3% of the plot height for sevoflurane and 4.2% for
# desflurane on the fixed `CHART_AXIS_TOP_MAC` axis. `PL-90Y6` measured that
# no axis range allowed by the overpressure constraint makes that fill read as
# a band on its own. At a 2 MAC ceiling the band is unambiguous, but the 1 MAC
# anchor sits at mid-plot with no room to show an overpressure induction. At 4
# MAC the band is back to the 2.50% it had on the old dial-maximum axis. So the
# fix is in the mark. A stroked upper edge over an unstroked fill looks like a
# line with a shadow under it. Two strokes with a gap between them look like
# an interval, at any thickness.
#
# The band is deliberately *not* given a minimum drawn height. The band's
# extent is its claim: one standard deviation either side of a published mean.
# Drawing it thicker than the data would assert a wider population spread than
# the literature supports. That would trade this interpretability defect for a
# correctness defect. So both strokes sit on the true boundaries, and the fill
# between them keeps its true extent.
MAC_AWAKE_BAND_EDGE_STROKE_WIDTH = 1.5

# The dashes and gaps are wider than any trace's dashes ([10, 4], [4, 3],
# [6, 6], [2, 3], [12, 4, 2, 4]), so the 1 MAC line does not look like a
# seventh compartment at a glance. The longest mark among the six traces is the
# alveolar trace's 10 px, and the widest gap is the vessel-rich trace's 6 px.
# This pattern exceeds both.
ONE_MAC_LINE_DASH_PATTERN = [16, 8]

# This was a bare literal at its call site until PL-2CS8, beside a named colour
# and a named dash pattern. It is the same 1.5 as the band edge, but it belongs
# to a different line. So each width has its own name, rather than one constant
# standing in for both.
ONE_MAC_LINE_STROKE_WIDTH = 1.5

# A control-change mark is chart furniture, like the two references, and it
# takes the same MUTED ink for the same reason. It is not a compartment. A hue
# of its own would add one more colour that the traces must be told apart
# from, and it would imply that the mark is a compartment. The mark needs no
# colour of its own to be told apart, because it already has a stronger cue:
# it is vertical, while both references and every trace run along the time
# axis. The gridlines are vertical too, but they are solid, finer and drawn in
# their own grey. The fork mark is the one other vertical line in this ink,
# and `BRANCH_POINT_STROKE_WIDTH`'s comment says how the two are told apart.
# No colour-vision deficiency and no greyscale rendering can take these cues
# away. Reusing MUTED also adds no new colour pair for
# `tools/contrast_check.py` to measure, because MUTED on PANEL is already
# measured for the 1 MAC line.
CONTROL_MARK_COLOR = MUTED

# The mark is finer than every trace, because a control mark annotates the run
# rather than showing any part of it. It has the same width as the two
# references, 1.5 px, and is told apart from them by its direction. In a case
# with a dozen adjustments, a mark as heavy as a trace would compete with the
# curves it exists to be read against. It is heavier than the vertical grid lines,
# though, and dashed where they are solid. Measured against a rendered frame, a
# mark of a hair's width beside a 60 s gridline can be found, but it is not
# immediately separable from the gridline. A reader who cannot tell an
# annotation from an axis decoration reads the time off the wrong one.
CONTROL_MARK_STROKE_WIDTH = 1.5

CONTROL_MARK_DASH_PATTERN = [3, 5]

# How much wider the first of two compared runs is drawn than the compartment's
# own width, in display pixels. While two runs are shown, line width is the
# only channel that tells the runs apart (`PL-HLD5`: line style and colour mark
# the compartment, and line width marks the run). The step is *added* to each
# compartment's width rather than replacing it. So the two runs' widths stay
# the same distance apart whichever pair of compartments the cap leaves drawn:
# 2 px against 4, and 3 px against 5.
#
# **The first run is the wider one, not the second. That is a legibility
# requirement, not an arbitrary choice of which end of the scale to use.** A
# branch reproduces its parent element by element up to the fork (`PL-Z3W6`).
# So before the branch point the two curves are not merely close together.
# They coincide exactly. Whichever run is drawn thicker hides the other
# completely over that stretch, so the thin curve has to be drawn last, on top.
# The second run keeps the width that the single-run chart draws it at, and it
# sits inside the first run's line, so both are visible everywhere. Widening
# rather than narrowing also keeps the contrast minimum intact. Nothing is
# drawn thinner than 2 px. A 1 px antialiased line renders lighter than its
# declared colour, and would fall below 3:1 against the panel.
# `.claude/rules/ui-color.md` treats a fall below that 3:1 as an error.
COMPARED_RUN_WIDTH_STEP = 2

# The fork that a branch opened at, marked on both plots. The mark is vertical
# like a control mark, because both marks name an instant. Two channels other
# than colour separate it from a control mark. It is solid where a control mark
# is dashed, and it carries a word where a control mark carries none. It
# declares no new colour, because `CONTROL_MARK_COLOR` is already measured
# against the panel. A reader must not confuse this mark with a control change,
# and declaring no new colour means that telling the two apart never rests on a
# hue at all.
BRANCH_POINT_STROKE_WIDTH = 1.5

# The thinnest any trace is drawn, in display pixels. A 1 px antialiased line
# renders lighter than its declared colour and falls below the 3:1 minimum
# against the panel (`docs/MODEL.md` § "The six compartment traces"). So no
# trace and no preview of one is drawn thinner than this.
MINIMUM_TRACE_STROKE_WIDTH = 2

# How much thinner a preview curve is drawn than the run's own curve of the
# same compartment, in display pixels, down to `MINIMUM_TRACE_STROKE_WIDTH`.
# A preview is the trajectory a dragged control *would* give, which the
# learner has not applied (`PL-5B1N`). Drawing it as heavy as the run would
# give a prediction the visual weight of something that happened. Width is
# the backup cue. The region, its edge at the run's reach and the label in the
# plot are what say "preview", so a preview of a 2 px trace that cannot be
# drawn thinner is still marked. Colour and dash pattern stay the
# compartment's own, because they are what tells the six traces apart
# (`PL-GVXP`), and a preview a reader cannot attribute to its compartment
# would be worse than none.
PREVIEW_WIDTH_STEP = 1

# The region a preview is drawn in, from the run's reach to the axis's right
# edge. Its edges are stroked in MUTED, as the references and the marks are,
# so the left edge marks where the run stands now and adds no new colour pair
# for `tools/contrast_check.py` to measure. The fill is decoration on the
# ground that the MAC-awake band's fill is (`PL-HKTB`): the edge and the label
# carry the information, and the fill is light enough for every trace to stay
# legible across it.
PREVIEW_REGION_COLOR = MUTED
PREVIEW_REGION_FILL_OPACITY = 0.10
PREVIEW_REGION_EDGE_STROKE_WIDTH = 1.5

# The bookmark editor. Wider than the new-case dialog because it carries two
# forms and two lists rather than three sentences, and each target row states
# a compartment, a height, a direction and a name.
BOOKMARK_DIALOG_WIDTH = 480

# The gap between a collection's heading and its rows. It is the tighter of the
# two gaps, so the heading looks like part of the rows under it rather than
# floating between the two collections.
BOOKMARK_ROW_SPACING = 4

# The gap between the two collections, and between a form and the list under
# it. It is wider than the row spacing above. That difference is what makes
# the two collections look like two lists rather than one long list with words
# in it.
BOOKMARK_SECTION_SPACING = 12

# The bullet of a mark row. It is drawn in a column of its own, so a row that
# wraps continues under its own text rather than at the margin where every row
# starts (`PL-FPY2`). `tools/glyph_check.py` confirms that it renders.
MARK_ROW_BULLET = "•"

# The gap between the bullet and the row's text. It is also how far a wrapped
# continuation line sits in from where the next row starts, and that indent is
# the only thing that tells the two apart.
MARK_ROW_BULLET_SPACING = 6

# The gap between one mark's row and the next. It is tighter than the
# heading's spacing, so the rows look like one list. It is not zero, so a
# continuation line sits closer to its own first line than to the row below it.
MARK_ROW_SPACING = 2

# The greatest height that each of the editor's two lists may grow to: about
# six rows, after which the list scrolls. It is a fixed limit rather than a
# stretch, because a list widget allowed to grow freely takes the whole dialog.
# The list then leaves its form floating above a field of white. The
# lists only confirm what was just added, while the form is what the reader
# came to use.
BOOKMARK_LIST_MAX_HEIGHT = 120

# Wide enough for the discard warning to fall in two or three lines rather
# than a column of fragments. The dialog holds only text, so it has no chart to
# take its size from.
NEW_CASE_DIALOG_WIDTH = 420

NEW_CASE_DIALOG_SPACING = 12

# The gap between the dashboard page's stacked sections, and between the panels
# each of its columns stacks, in px: the band at the top, the run rows and the
# record column inside it, and the sidebar.
PAGE_SPACING = 12

# This gap, in px, separates neighbouring controls in a row. It applies to the
# buttons and selectors of a run's transport row and to those of the Branch
# panel. Both rows use the same value, so the two rows of controls that a reader
# uses to operate a run are spaced alike.
CONTROL_ROW_SPACING = 8

# The gap between the four setting sliders, in px.
PARAMETER_SLIDER_SPACING = 12

# This gap, in px, separates a run's readout heading from the row of readouts
# under it. The heading names the substance, says the values are modelled, and
# gives the delivered concentration and 1 MAC. The gap is small, so the heading
# looks like part of the readouts it introduces.
READOUT_SECTION_SPACING = 4

# The gap between the texts along that heading, in px.
READOUT_HEADING_SPACING = 12

# The gap between two Areas, in px, which is also what a reader grabs to resize
# them (`PL-RQT1` Q1). It draws nothing at rest, so the page's BACKGROUND shows
# between two PANEL surfaces. 8 px is Blender's 10 px hit band, minus the
# rounded corners that this interface does not draw. The width, and the line
# below, are placeholders for planned-milestone item 33's visual pass.
AREA_HANDLE_WIDTH = 8

# The line drawn down the middle of each handle a drag would move, in px, while
# the pointer is over one of them (`PL-RQT1` Q2). It is drawn in PRIMARY.
AREA_HANDLE_LINE_WIDTH = 2

# One arrow-key press moves a border that has the keyboard focus by this many px
# (`PL-M352`). The value is a placeholder. It was chosen under the project owner's
# rule of 2026-10-18, which treats look and placement as placeholders while the
# structure is built.
AREA_KEYBOARD_STEP = 20

# The side, in px, of the square at each corner of an Area that a reader drags to
# split or join it (`PL-30L5` Q1). It is twice Blender's size, and less than the
# 24 px target size that WCAG 2.2 SC 2.5.8 asks for. The Area menu is the
# equivalent route that lets the layout meet that criterion, because a
# right-click anywhere on the Area's header opens it (`PL-R5G4`). The header's
# end margins are this wide too, so a zone never takes a click meant for a
# header control.
AREA_CORNER_ZONE = 16

# The grip a corner draws while the pointer is in its Area: this many strokes,
# this long and this thick, in px, in MUTED. `PL-30L5` Q1 had it at 40 % alpha.
# It is drawn opaque so that it meets SC 1.4.11's 3:1 against PANEL, which a
# reader needs to find the zone. It is a placeholder for planned-milestone item
# 33.
AREA_GRIP_STROKE_LENGTH = 6
AREA_GRIP_STROKE_WIDTH = 1
AREA_GRIP_STROKES = 3

# The line a corner drag draws across an Area where a split will fall, in px
# (`PL-30L5` Q2). PRIMARY while the split can be made, WARNING where a half
# would be too small. The same width outlines the Area a join would make.
AREA_PREVIEW_LINE_WIDTH = 2

# How opaque the tint is over an Area a join would close (`PL-30L5` Q2). The
# PRIMARY outline around the joined Area is what carries the preview; the tint
# only marks which of the two goes.
AREA_CLOSING_TINT_ALPHA = 0.4

# One width for the agent selector and for the chip that takes its place, so
# the transport controls beside them do not move when a run starts. A header
# that reflows on Start announces a mode change by motion in the wrong place.
# The motion pulls the reader's eye away from the readouts, where it should be.
AGENT_SELECTOR_WIDTH = 180

# The widths of the chart's two dropdowns, set like the agent selector's width
# above. They were bare literals at their call sites until PL-2CS8. Their
# widths differ from the agent selector's and from each other's because their
# longest options differ.
TIME_BASE_SELECTOR_WIDTH = 170
PLAYBACK_RATE_SELECTOR_WIDTH = 150

# The chip's inset. It is slightly wider than the header badge's 6, because the
# chip carries two lines rather than one, and it sits among controls rather
# than under the title.
RUNNING_AGENT_DISPLAY_PADDING = 8

# The wash-in trace takes the alveolar compartment's own colour, because it
# shows that compartment relative to the gas that fills it. The numerator is
# the alveolar fraction, and nothing else on the second chart competes with it.
# Reusing the colour declares no new pair for `tools/contrast_check.py`,
# because ALVEOLAR_COLOR on PANEL is already measured. It also lets a reader
# follow the alveolar curve from the chart above to the ratio below.
#
# This trace has none of the six-way separation problem of the chart above, so
# PL-GVXP's arithmetic never constrained it. What did constrain it was the
# contrast it inherited from ALVEOLAR_COLOR, which measured 2.93:1 against the
# panel. That shortfall is now fixed at the source, ALVEOLAR_COLOR, so the
# single trace on this plot reaches 3:1 without breaking the link between the
# two colours.
WASH_IN_COLOR = ALVEOLAR_COLOR

# Shorter than the compartment chart. The ratio is one trace on a fixed
# 0-to-1 axis, so it needs no room to separate six curves, and the two plots
# have to be readable together without scrolling between them.
WASH_IN_CHART_HEIGHT = 200

# The wash-in trace is drawn heavier than the reference lines around it,
# because it is the modelled quantity and they are the ruling. It was a bare
# literal at the call site until PL-2CS8.
WASH_IN_STROKE_WIDTH = 3

# The wash-in curve's asymptote, drawn as the reference it is. A trace that
# simply halts in open space looks clipped. One that halts *on a labelled
# line* looks as if it has arrived somewhere. The asymptote is a definitional
# anchor rather than a measured value with spread: by definition, F_A = F_I is
# where net uptake stops. So it is a line and not a band, on the distinction
# that `docs/MODEL.md` § "MAC-awake as a chart reference" draws between the
# two. It uses MUTED and a wide dash, matching the 1 MAC line on the chart
# above. It is furniture rather than a second compartment, and it declares no
# new pair for `tools/contrast_check.py`.
EQUILIBRIUM_LINE_COLOR = MUTED

EQUILIBRIUM_LINE_DASH_PATTERN = [16, 8]

# Like the widths above, this was a bare literal at the call site until
# PL-2CS8, beside its own named colour and dash pattern.
EQUILIBRIUM_LINE_STROKE_WIDTH = 1.5

# The room given to one axis label, enough for `format_wash_in_ratio`'s two
# decimal places. The chart's own default is sized for the single digits on
# the percent axis, and it wraps "0.25" onto two lines.
WASH_IN_AXIS_LABEL_SIZE = 34

# GRIDLINE colours the chart gridlines and axis lines, the rule between sections
# of the chart column, and the sliders' unfilled groove. PL-2CS8 named it.
# Before that, it was the bare literal "#D9E2EC" at five sites and was defined
# nowhere. `tools/contrast_check.py` reads named constants, so it could not see
# the colour at all, and it reported the file the colour sat in as checked.
#
# **GRIDLINE has no `REQUIREMENTS` entry. `tools/contrast_check.py`'s `EXEMPT`
# table records it as exempt from SC 1.4.11 in all four uses** (project owner,
# 2026-09-27, ratified, over darkening the grey to 3:1; PL-HKTB). It measures
# 1.31:1 on `PANEL`, so an entry at the criterion's 3:1 would fail.
# `.claude/rules/ui-color.md` forbids a `KNOWN_SHORTFALLS` entry "to make a
# change go green". A shortfall is a pair that should meet a minimum and does
# not, and this pair is one that the minimum does not apply to.
#
# This is what the criterion says, read at the source on 2026-09-27 (w3c/wcag,
# `understanding/21/non-text-contrast.html`). Its line-graph example counts the
# "background lines for the values" as graphical objects, and asks 3:1 of them
# against the background. Another clause says that lines need not contrast
# "with each other or the graduated lines". That clause is about the traces
# against the rulings, which is a different pair. Until PL-HKTB, this comment
# misread it as exempting the rulings themselves. What does exempt the rulings
# is stated under "Required for understanding": the requirement does not apply
# where "a graphic with text embedded or overlaid conveys the same information,
# such as labels and values on a chart". In the example, the rulings are how a
# value is perceived at all. This chart gives a reader three other carriers.
# Every ruling stands at a tick that has an axis label in `MUTED` at 5.00:1. The
# readouts state every compartment's value. The hover states the exact value at
# any drawn point. The chart passes the criterion's own test, which is to
# assume the area is invisible and ask whether the graphic is still understood.
# Without the rulings, the chart is six labelled traces against two labelled
# axes. The axis lines, the section rule and the groove each have their own
# grounds for exemption, given for each use in `EXEMPT`.
#
# The grey is not darkened, and that decision comes from the chart's hierarchy
# rather than from the criterion. The lightest trace, `MUSCLE_COLOR`, is 3.43:1
# on the panel. So a ruling at 3:1 would be 87% as dark as the lightest data
# line, and only a hue step away from `FAT_COLOR` at 4.76:1. Furniture would
# then weigh as much as data. The chart rests on an order: this ruling sits
# under the `MUTED` reference lines at 5.00:1, which sit under the traces at
# 3.43-6.02:1, and widths of 1 / 1.5 / 2-3 px say the same. A ruling at 3:1
# would collapse the bottom rung of that order. 1.31:1 is where charting
# practice puts a ruling on purpose. ggplot2's `theme_bw` rules its panel at
# grey92, which is 1.19:1 on white. Matplotlib's default `grid.color` is
# `#b0b0b0`, which is 2.17:1. It is the darker of the two and still less than
# 3:1 (both read at the source, 2026-09-27). Making the grey a little darker
# without claiming 3:1 was also refused, because it would be a change with no
# standard behind it, which is the state this record exists to end.
GRIDLINE = "#D9E2EC"
