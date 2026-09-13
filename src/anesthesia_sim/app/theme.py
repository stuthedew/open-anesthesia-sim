"""Shared color and spacing constants for the Flet UI."""

from dataclasses import dataclass
from typing import Final

BACKGROUND = "#F4F7FA"
PANEL = "#FFFFFF"
PRIMARY = "#176B87"
# ACCENT is a *graphical* color: the sliders' active track. It is not legible
# as text - 2.93:1 on the panel - so text that wants to look like the accent
# uses ACCENT_TEXT below. One constant serving both roles is what PL-30P6
# found: the two roles carry different WCAG minima (4.5:1 for text under SC
# 1.4.3, 3:1 for graphical objects under SC 1.4.11) and no single value can be
# chosen against both without one of them losing.
#
# It was also the alveolar chart trace until PL-GVXP, which is the other half
# of that same split. A chart trace has to clear 3:1 against the panel under
# simulated dichromacy as well as under normal vision, and has five sibling
# traces to stay separable from; a slider track has neither constraint. The
# trace now carries its own value in `simulation_view.py`, so this one is
# bounded by nothing but the panel behind it - which is what PL-W8DQ needs to
# know before it darkens it, and why that item deferred to this one.
ACCENT = "#18A999"
# The accent, dark enough to be read as text: 5.00:1 on PANEL and 4.65:1 on
# BACKGROUND. A uniform darkening of ACCENT, so hue and saturation are
# unchanged (173 deg, 0.86) and the two still read as the same color family.
# Used for the affirmative status words - "Running" and "Valid" - whose
# counterpart is WARNING. Never use ACCENT for text, and never use this for a
# chart trace: the split is the point.
ACCENT_TEXT = "#127D71"
INK = "#243B53"
# Darkened from #627D98 (PL-X0RG), which reached only 4.28:1 on the panel and
# 3.98:1 on the page background - below WCAG 2.2 SC 1.4.3's 4.5:1 for text, and
# this is the color of the label naming every readout, of the run-status word,
# and of the chart's axis description. The page background is the binding
# surface, not the panel: the run-status text sits in the top-level column, so
# BACKGROUND shows through behind it. Now 5.00:1 on PANEL and 4.65:1 on
# BACKGROUND. The hue and saturation are unchanged (210 deg, 0.355) so the
# label/value hierarchy against INK reads as it did.
MUTED = "#59728A"
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
# colour sample." The ISO original is therefore the Munsell notation; the
# Pantone reference is already ISO's own nearest sample of it; and `fill` is a
# further sRGB approximation of the Pantone. Two of the three Munsell originals
# fall outside the sRGB gamut, so no display can reproduce them exactly.
# `docs/MODEL.md` records the measured deviation of each `fill` from its
# Munsell original.
#
# Desflurane's *dimensions* are not specified by ISO 5360 — the Scope excludes
# them and Table 2 gives "N.S." for its collar angle — but its *colour* is
# specified in that same row, and that is what is used here.
#
# Text colors are deliberately separate from the identification colors. Each
# pair exceeds WCAG 2.2's 4.5:1 minimum for normal text; the agent name remains
# visible everywhere the color appears, so color is never the only cue.
# https://www.w3.org/TR/WCAG22/#contrast-minimum
#
# That claim is about the pair *as rendered*, and it is not self-enforcing: a
# control drawn in `foreground` over `fill` can still reach the screen in some
# other colour entirely if a widget state overrides it. The agent selector did,
# for the whole of every run - Flet/Material paints a disabled control's label
# in the theme's disabled-content grey, which is a colour this file does not
# declare and `tools/contrast_check.py` therefore cannot measure, over a fill
# that stayed saturated (PL-61WW). The fix is in `app/simulation_view.py` and
# is structural rather than a colour: nothing carrying agent identity is
# disabled, so the pair measured here is the pair rendered. A new use of these
# colours owes the same question - is anything between this constant and the
# screen entitled to substitute its own?
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
# `ROADMAP.md`'s planned-milestone item 24 names consolidating them as its own
# prerequisite, and "Development pathway" Phase 2 orders it first, "because
# every control added before it spreads the same scattered defaults further" -
# which v0.5.0's bookmarks, MAC targets and two-run overlay were about to do.
#
# They are here rather than in a new module because this file already *was* the
# tokens module, holding the palette and the spacing constants; a third file
# beside it would be the "fourth scattered location" item 24 warns against. It
# also shortens `tools/contrast_check.py`, which read two files only because
# the six trace colours lived in the view.
#
# **This module stays free of Flet**, which is why two display constants did
# not come with them: `METRIC_GRID_COLUMNS` is typed on
# `ft.ResponsiveRowBreakpoint` and `AGENT_RENDER_STYLES` builds `ft.Border` and
# `ft.TextStyle` objects. `tools/contrast_check.py` and
# `tools/agent_identity_check.py` read this file with `ast` in a bare checkout
# precisely because it imports nothing they would need installed.
#
# **Order is load-bearing.** `contrast_check.read_palette` resolves a bare name
# against the palette built so far, in file order, so an alias must sit below
# what it aliases - `CIRCUIT_COLOR = PRIMARY` below `PRIMARY`,
# `WASH_IN_COLOR = ALVEOLAR_COLOR` below `ALVEOLAR_COLOR`. Move one above its
# referent and it resolves to `None`, drops out of the palette, and the
# requirement citing it reports as missing.

CHART_HEIGHT = 360

PAGE_PADDING = 16

PANEL_PADDING = 14

PANEL_RADIUS = 10

# The clinical gloss under a compartment name is deliberately smaller than the
# name above it. Which quantity the model computes is the primary claim; what
# a clinician would compare it against is a secondary one, and the type sizes
# say so. Same MUTED colour as the name, so this adds no pair to
# `tools/contrast_check.py`, and it stays normal text at WCAG's 4.5:1.
METRIC_NAME_SIZE = 14

METRIC_QUALIFIER_SIZE = 12

# The same gloss, one panel row up, under a *control* name rather than under a
# readout name (`_build_parameter_panel`). A reader meets the two as one idiom
# - the fine print that says what the name above it actually refers to - so
# they are the same size deliberately, and aliasing rather than writing 12
# twice is what stops the two drifting apart unnoticed.
PARAMETER_QUALIFIER_SIZE = METRIC_QUALIFIER_SIZE

# The MAC line under each reading, in the same relationship to the percent
# above it as the gloss is to the compartment name: smaller and MUTED, because
# it is the weaker of the two claims. Percent is what the model computes and
# what a monitor would show; a MAC multiple is that number divided by a
# population constant this model does not otherwise use, and on the four
# non-alveolar compartments it is a partial-pressure ratio rather than
# anything a clinician reads off a patient. Sized between the name and the
# gloss so the row reads value, then unit-conversion, then annotation.
METRIC_SECONDARY_VALUE_SIZE = 13

# The rest of the type scale, bare at its call sites until PL-2CS8 while the
# three sizes above were named - so the scale was half declared and half
# literal, and a reader could not see it whole. These complete it, at the
# values already shipping.
APP_TITLE_SIZE = 26
METRIC_VALUE_SIZE = 22

# Width held open for the simulated-time readout, which is the one metric
# whose string changes *length* while it updates. On the compound form
# `PL-Q4M4` and `PL-CZFY` put it on, the clock steps `59.9s` -> `1m` ->
# `1m0.1s` and `1h23m` -> `1h23m0.1s`, so an unreserved readout would shift
# its own panel every time a component appeared or fell away - and this is a
# value that redraws every render tick. `_build_trace_legend_item` records
# the same rule for the legend rows: a control a reader is looking at must
# not move under them.
#
# Derived rather than measured: the widest string the run length can reach is
# `23h59m59.9s`, eleven characters, and `tests/unit/test_formatting.py`
# asserts that so the premise fails loudly if the form or the envelope
# changes. At METRIC_VALUE_SIZE bold that is about 150 logical pixels in a
# proportional UI face. Nothing renders the interface in a check yet
# (`PL-7J96`), so this has not been confirmed by eye; it is set wide enough
# that being a little generous costs panel whitespace rather than a clipped
# clock.
ELAPSED_VALUE_WIDTH = 150
ACCOUNTING_STATUS_SIZE = 20

# The six compartment traces. Two things decide these values, and only one of
# them is a colour question.
#
# **Against the panel, each trace is held to 3:1 - and under simulated
# dichromacy as well as under normal vision.** SC 1.4.11 asks it of the
# displayed colour; this interface asks it of the Brettel 1997 simulation of
# that colour too, because a trace a protanope cannot find against white is not
# separable from the panel whatever the criterion measures. `ALVEOLAR_COLOR`
# and `MUSCLE_COLOR` were re-picked for that and nothing else (PL-GVXP): both
# keep their own hue and saturation exactly, darkened to the lightest shade
# clearing 3.2:1 in all four models - 3:1 plus two tenths, so the shipped value
# is not itself the boundary case the next edit trips over.
# `tools/contrast_check.py` measures all four and `docs/MODEL.md` records them.
#
# **Between traces, colour is not the channel and no palette could make it
# one.** Contrast composes along a bounded axis, and the 3:1 floor above caps
# every trace's luminance at 0.30, so six of them cannot all be more than
# 1.48 apart - and holding hue and saturation fixed, a search over lightness
# alone reaches 1.28 across the four models while driving four of the six to
# near-black. Both are far under the 3:1 that would make colour sufficient, so
# the separating channel is the line style below, and these hues are chosen to
# name their compartment rather than to win an arithmetic that cannot be won
# (`.claude/rules/ui-color.md`, judgment 3).
CIRCUIT_COLOR = PRIMARY

# Its own value rather than `ACCENT`, which it used to share. The two roles
# had different constraints the moment this one acquired a four-model floor
# five other traces also have to clear, and `ACCENT`'s remaining role - the
# sliders' active track - is bounded by nothing but the panel behind it. That
# is the question `PL-W8DQ` was waiting on: `ACCENT` is no longer a chart
# colour, so it is free to be darkened on the sliders' own terms.
ALVEOLAR_COLOR = "#159789"

MIXED_VENOUS_COLOR = "#7C3AED"

VESSEL_RICH_COLOR = "#DC2626"

MUSCLE_COLOR = "#D17206"

FAT_COLOR = "#64748B"

# The colour swatch every legend entry draws, at one size across all three
# legend rows so that a reader scanning down them compares marks rather than
# shapes. `_build_band_legend_item` is the one deliberate exception: a band's
# extent is exactly what distinguishes it from a line.
LEGEND_SWATCH_WIDTH = 24

LEGEND_SWATCH_HEIGHT = 4

# Two legend marks that are not a trace swatch and so cannot use the pair
# above: a control mark is a vertical tick, and the MAC-awake band is an
# interval rather than a line. Bare at their call sites until PL-2CS8.
CONTROL_MARK_SWATCH_WIDTH = 3
CONTROL_MARK_SWATCH_HEIGHT = 16
BAND_SWATCH_WIDTH = 24
BAND_SWATCH_HEIGHT = 12

# The rule between the concentration panel and the wash-in section below it.
SECTION_DIVIDER_HEIGHT = 16

# The two chart references are furniture rather than data, and are drawn in
# the interface's own ink and label colour rather than in a seventh and
# eighth hue. A new hue would enter the trace palette's separation problem
# (`.claude/rules/ui-color.md`, judgment 3: six traces already cannot all
# clear 3:1 against each other on a bounded axis) while implying the mark is
# another compartment. What separates a reference from a trace here is
# instead its *kind* — constant, horizontal, spanning the window — and its
# mark type, which is also what separates the two references from each
# other: a band for a measured population value with real spread, a line for
# a definitional anchor. That distinction survives greyscale and every
# colour-vision deficiency, which `.claude/rules/ui-color.md`'s judgment 2
# requires of any encoding that carries meaning.
#
# The ranking between them is deliberate and is INK against MUTED. After a
# long case at a steady setpoint the alveolar and vessel-rich traces have
# converged, so the 1 MAC anchor is robust to which trace it is read
# against; at MAC-awake they have not, so the band is the trace-critical
# mark and carries the heavier weight. Giving the easier mark equal weight
# is the failure PL-F52R names.
MAC_AWAKE_BAND_COLOR = INK

ONE_MAC_LINE_COLOR = MUTED

# The band's fill is decoration: both boundaries are carried by a stroke in
# `MAC_AWAKE_BAND_COLOR`, which is what `tools/contrast_check.py` measures.
# The fill is light enough for six traces to remain legible across it, which
# a fill at its own 3:1 would not be.
MAC_AWAKE_BAND_FILL_OPACITY = 0.14

# Both edges, and this is the geometry the mark type depends on rather than
# a styling choice. One standard deviation either side of the published mean
# is 3.3% of the plot height for sevoflurane and 4.2% for desflurane on the
# fixed `CHART_AXIS_TOP_MAC` axis, and `PL-90Y6` measured that no axis range
# the overpressure constraint allows makes that fill read as a band on its
# own: at a 2 MAC ceiling the band is unambiguous but the 1 MAC anchor sits
# at mid-plot with no room to show an overpressure induction, and at 4 MAC
# the band is back to the 2.50% it had on the old dial-maximum axis. So the
# fix is at the mark. A stroked upper edge over an unstroked fill is the
# geometry of a line with a shadow under it; two strokes with a gap between
# them is the geometry of an interval, and reads as one at any thickness.
#
# What is deliberately *not* done is giving the band a minimum drawn height.
# The band's extent is its claim - one standard deviation either side of a
# published mean - so drawing it thicker than the data would assert a wider
# population spread than the literature supports, trading this
# interpretability defect for a correctness one. Both strokes therefore sit
# on the true boundaries and the fill between them keeps its true extent.
MAC_AWAKE_BAND_EDGE_STROKE_WIDTH = 1.5

# Wider than any trace's dashes ([10, 4], [4, 3], [6, 6], [2, 3],
# [12, 4, 2, 4]), so the 1 MAC line does not read as a seventh compartment at
# a glance. The longest mark among the six is the alveolar trace's 10 px and
# the widest gap the vessel-rich trace's 6 px; this exceeds both.
ONE_MAC_LINE_DASH_PATTERN = [16, 8]

# Written bare at its call site until PL-2CS8, beside a named colour and a
# named dash pattern - the same 1.5 as the band edge, but a different line, so
# the two carry their own names rather than one standing in for both.
ONE_MAC_LINE_STROKE_WIDTH = 1.5

# A control-change mark is furniture like the two references, and takes the
# same MUTED ink for the same reason: it is not a compartment, and a hue of
# its own would enter the trace palette's separation problem while implying
# it were. It needs no second colour channel because it already has a
# stronger one - it is the only vertical thing on the chart, which no
# colour-vision deficiency and no greyscale rendering can take away.
# Reusing MUTED also declares no new pair for `tools/contrast_check.py`:
# MUTED on PANEL is already measured, as the 1 MAC line.
CONTROL_MARK_COLOR = MUTED

# Finer than either reference and than every trace, because a control mark
# annotates the run rather than showing any part of it: at the density of a
# case with a dozen adjustments, a mark as heavy as a trace would compete
# with the curves it exists to be read against. Heavier than the vertical
# grid lines, though, and dashed where they are solid: measured against a
# rendered frame, a mark at a hair's width beside a 60 s gridline is
# findable but not immediately separable from it, and a reader who cannot
# tell an annotation from an axis decoration reads the time off the wrong
# one.
CONTROL_MARK_STROKE_WIDTH = 1.5

CONTROL_MARK_DASH_PATTERN = [3, 5]

# Wide enough for the discard warning to fall in two or three lines rather
# than a column of fragments; the dialog is text and has no chart to size to.
NEW_CASE_DIALOG_WIDTH = 420

NEW_CASE_DIALOG_SPACING = 12

# One width for the selector and for the chip that stands in its place, so the
# transport controls beside them do not move when a run starts. A header that
# reflows on Start announces a mode change by motion in the wrong place, and
# the eye it pulls is the one that should be on the readouts.
AGENT_SELECTOR_WIDTH = 180

# The chart's two dropdowns, sized like the agent selector above and bare at
# their call sites until PL-2CS8. They differ from it and from each other
# because their longest option differs.
TIME_BASE_SELECTOR_WIDTH = 170
PLAYBACK_RATE_SELECTOR_WIDTH = 150

# The chip's inset. Slightly wider than the header badge's 6 because this one
# carries two lines rather than one and sits among controls rather than under
# the title.
RUNNING_AGENT_DISPLAY_PADDING = 8

# The wash-in trace takes the alveolar compartment's own colour, because it
# is that compartment expressed against the one filling it: the numerator is
# the alveolar fraction and nothing else on the second chart competes with
# it. Reusing it declares no new pair for `tools/contrast_check.py` -
# ALVEOLAR_COLOR on PANEL is already measured - and it is what lets a reader
# carry the alveolar curve from the chart above into the ratio below.
#
# This trace carries none of the six-way separation problem the chart above
# has, so PL-GVXP's arithmetic never bound it; what did bind it was that
# constant's own 2.93:1 against the panel, which it inherited. That is fixed
# at the source, so the single trace on this plot now clears 3:1 without the
# linkage having to be broken to get it.
WASH_IN_COLOR = ALVEOLAR_COLOR

# Shorter than the compartment chart. The ratio is one trace on a fixed
# 0-to-1 axis, so it needs no room to separate six curves, and the two plots
# have to be readable together without scrolling between them.
WASH_IN_CHART_HEIGHT = 200

# The wash-in trace is drawn heavier than the reference lines around it: it is
# the measured quantity and they are the ruling. Bare at the call site until
# PL-2CS8.
WASH_IN_STROKE_WIDTH = 3

# The wash-in curve's asymptote, drawn as the reference it is. A trace that
# simply halts in open space reads as clipped; one that halts *on a labelled
# line* reads as having arrived somewhere. It is a definitional anchor rather
# than a measured value with spread - F_A = F_I is where net uptake stops, by
# definition - so it is a line and not a band, on the distinction
# `docs/MODEL.md` § "MAC-awake as a chart reference" draws between the two.
# MUTED and a wide dash, matching the 1 MAC line on the chart above: this is
# furniture rather than a second compartment, and it declares no new pair for
# `tools/contrast_check.py`.
EQUILIBRIUM_LINE_COLOR = MUTED

EQUILIBRIUM_LINE_DASH_PATTERN = [16, 8]

# As above: bare at the call site until PL-2CS8, beside its own named colour
# and dash pattern.
EQUILIBRIUM_LINE_STROKE_WIDTH = 1.5

# Room for one axis label at `format_wash_in_ratio`'s two decimals. The chart's
# own default is sized for the single digits the percent axis carries, and
# wraps "0.25" onto two lines.
WASH_IN_AXIS_LABEL_SIZE = 34

# The chart gridlines and the divider under the concentration panel. Named by
# PL-2CS8; it was the bare literal "#D9E2EC" at five sites and defined nowhere,
# so `tools/contrast_check.py` - which reads named constants - could not see it
# at all, and the file it sat in reported as checked.
#
# **It carries no `REQUIREMENTS` entry, and that is a judgment rather than an
# omission.** Measured 1.31:1 on `PANEL` and 1.22:1 on `BACKGROUND`, so an
# entry at SC 1.4.11's 3:1 would fail - and `.claude/rules/ui-color.md` forbids
# a `KNOWN_SHORTFALLS` entry "to make a change go green". The criterion asks
# 3:1 of a graphical object *required to understand the content*, and WCAG's
# own line-graph example - quoted in `docs/MODEL.md` § "Color contrast" -
# treats the "graduated lines" as furniture the traces need not contrast
# against. The values a reader takes off this chart come from the axis labels,
# which are held to 4.5:1 as text.
#
# Whether the gridline should be darkened anyway is a design question, not a
# consolidation one: PL-2CS8 moved this literal without changing what it draws.
# PL-HKTB carries it.
GRIDLINE = "#D9E2EC"
