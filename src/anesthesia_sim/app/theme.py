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
PAGE_PADDING = 24
PANEL_PADDING = 20
PANEL_RADIUS = 12


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
