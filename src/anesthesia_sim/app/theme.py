"""Shared color and spacing constants for the Flet UI."""

from dataclasses import dataclass
from typing import Final

BACKGROUND = "#F4F7FA"
PANEL = "#FFFFFF"
PRIMARY = "#176B87"
ACCENT = "#18A999"
INK = "#243B53"
MUTED = "#627D98"
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
