"""Tests for safety-relevant presentation colors."""

import pytest

from anesthesia_sim.app.theme import AGENT_COLOR_SCHEMES, INK, AgentColorScheme
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES


def _relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255.0 for index in (1, 3, 5)]
    linear = [
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(first: str, second: str) -> float:
    lighter, darker = sorted(
        (_relative_luminance(first), _relative_luminance(second)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def test_agent_colors_match_iso_5360_2016_table_2() -> None:
    """Lock the reviewed mapping; a wrong agent color is worse than no color.

    Verified against ISO 5360:2016 Table 2 directly. The Munsell notation is
    the standard's original value (Table 2 footnote c); the Pantone reference
    is ISO's own nearest sample of it.
    """

    assert AGENT_COLOR_SCHEMES == {
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


@pytest.mark.parametrize("scheme", AGENT_COLOR_SCHEMES.values())
def test_every_agent_color_records_both_standard_references(
    scheme: AgentColorScheme,
) -> None:
    """Provenance must survive; an uncited fill cannot be re-verified later."""

    assert scheme.standard_color_name
    assert scheme.standard_color_munsell
    assert scheme.standard_color_pantone.startswith("Pantone ")


def test_every_builtin_agent_has_exactly_one_verified_color_scheme() -> None:
    assert set(AGENT_COLOR_SCHEMES) == set(AGENT_DATA_FILENAMES)


@pytest.mark.parametrize("scheme", AGENT_COLOR_SCHEMES.values())
def test_agent_color_text_meets_wcag_aa_contrast(scheme: AgentColorScheme) -> None:
    assert _contrast_ratio(scheme.fill, scheme.foreground) >= 4.5
