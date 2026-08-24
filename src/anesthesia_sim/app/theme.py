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
    standard_color_reference: str


# ISO 5360:2016, Table 2 specifies agent-identification colors for anaesthetic
# vaporizer filling systems. The ISO standard gives
# print color-system references rather than sRGB values, so these fills are the
# nearest commonly published sRGB equivalents of its Pantone references:
# https://www.iso.org/standard/68417.html
# Status checked 2026-08-23: edition 4 remains published/current while under
# systematic review; re-check this mapping if ISO publishes a successor.
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
        standard_color_reference="Pantone 108 C",
    ),
    "isoflurane": AgentColorScheme(
        fill="#981D97",
        foreground="#FFFFFF",
        standard_color_name="Purple",
        standard_color_reference="Pantone 254 C",
    ),
    "desflurane": AgentColorScheme(
        fill="#00629B",
        foreground="#FFFFFF",
        standard_color_name="Blue",
        standard_color_reference="Pantone 3015 C",
    ),
}
