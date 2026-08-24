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
    """Lock the reviewed mapping; a wrong agent color is worse than no color."""

    assert AGENT_COLOR_SCHEMES == {
        "sevoflurane": AgentColorScheme("#FEDB00", INK, "Yellow", "Pantone 108 C"),
        "isoflurane": AgentColorScheme("#981D97", "#FFFFFF", "Purple", "Pantone 254 C"),
        "desflurane": AgentColorScheme("#00629B", "#FFFFFF", "Blue", "Pantone 3015 C"),
    }


def test_every_builtin_agent_has_exactly_one_verified_color_scheme() -> None:
    assert set(AGENT_COLOR_SCHEMES) == set(AGENT_DATA_FILENAMES)


@pytest.mark.parametrize("scheme", AGENT_COLOR_SCHEMES.values())
def test_agent_color_text_meets_wcag_aa_contrast(scheme: AgentColorScheme) -> None:
    assert _contrast_ratio(scheme.fill, scheme.foreground) >= 4.5
