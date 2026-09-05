#!/usr/bin/env python3
"""Compute the interface's color-contrast ratios and hold them to WCAG 2.2 AA.

Every contrast claim in this repository used to be prose. `app/theme.py` states
that each agent fill/foreground pair "exceeds WCAG 2.2's 4.5:1 minimum for
normal text"; nothing computed it. `docs/MODEL.md` records the agent colors'
behaviour under simulated dichromacy; nothing recomputed it when a color
changed. A color edit could silently falsify a documented safety claim, and
the only thing between that and a reader was whoever remembered to re-measure.

Contrast ratio is closed-form arithmetic over two sRGB triples, so it is the
decidable half of the project's accessibility standard and belongs here rather
than in a session's head. `.claude/rules/ui-color.md` carries the other half.

**What this decides.** Whether a declared pair meets its declared ratio.

**What it must never decide.** Whether a color is text or a graphical object,
which pairs actually appear on screen together, whether a non-color channel is
genuinely redundant, or how far apart two chart traces ought to be. Those are
judgments; they live in `REQUIREMENTS` below, written by a person, and this
file only evaluates them. A tool that guesses the judgment half is worse than
no tool, because its output looks authoritative and is not.

**The arithmetic.** WCAG 2.2's relative-luminance and contrast-ratio
definitions, https://www.w3.org/TR/WCAG22/#dfn-relative-luminance and
https://www.w3.org/TR/WCAG22/#dfn-contrast-ratio. Validated against three
published reference values in `tests/unit/test_contrast_check.py`: black on
white is exactly 21:1, `#767676` on white is 4.54:1 (the darkest grey that
fails nothing at AA), and `#949494` on white is 3.03:1.

**Colors are read, not imported.** `app/simulation_view.py` imports Flet, so a
standard-library-only tool cannot import it. The constants are extracted with
`ast`, which also means this runs in a bare checkout with no virtualenv - the
promise every tool here makes.

**Known shortfalls, and why they do not simply fail the build.** The pairs
listed in `KNOWN_SHORTFALLS` do not meet their minimum today. Listing them
there against the item that closes each one keeps `make check` green while making the
gap visible and owned, which is the opposite of the comment-that-nobody-checks
this file replaces. The list cannot rot: a shortfall that starts *passing* is
an error too, so fixing one forces its entry out.
"""

from __future__ import annotations

import argparse
import ast
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

THEME = Path("src/anesthesia_sim/app/theme.py")
VIEW = Path("src/anesthesia_sim/app/simulation_view.py")

#: Ratios are compared at the precision they are printed at. A verdict that
#: disagrees with the number beside it ("it says 4.50 and it failed") is a
#: presentation-correctness problem in a tool whose whole subject is
#: presentation correctness, and the leniency this costs is 0.005 on a 4.5
#: threshold.
DISPLAY_DECIMALS = 2

#: WCAG 2.2 SC 1.4.3, Contrast (Minimum), Level AA: normal-size text.
#: https://www.w3.org/TR/WCAG22/#contrast-minimum
AA_TEXT = 4.5

#: WCAG 2.2 SC 1.4.11, Non-text Contrast, Level AA: user-interface components
#: and graphical objects required to understand the content.
#: https://www.w3.org/TR/WCAG22/#non-text-contrast
AA_NON_TEXT = 3.0


@dataclass(frozen=True)
class Requirement:
    """One pair that must hold, and the judgment behind holding it."""

    foreground: str
    background: str
    minimum: float
    criterion: str
    why: str


#: The specification. Every entry names a pair that actually appears on screen
#: together and the reason it is held to that number. Adding a color to the
#: interface means adding it here.
#:
#: **The surface is read from the widget tree, never assumed.** The first
#: version of this table put the run-status text on `PANEL`; it is not there.
#: `mount()` builds a top-level `Column` with no background of its own, so the
#: run-status word, the halted-run notice and the disclaimer all sit on
#: `BACKGROUND` (`app/main.py` sets `page.bgcolor`), while the metric labels,
#: the axis description and the accounting lines sit inside containers that do
#: set `bgcolor=PANEL`. `BACKGROUND` is the darker surface, so it is the
#: binding one wherever a color appears on both - which is what made `MUTED`
#: a worse failure than the panel measurement showed (PL-X0RG).
#:
#: `MUTED` is judged at the normal-text minimum rather than the large-text one
#: even where it is bold: WCAG's large-text exception starts at 18pt, or 14pt
#: bold (18.66px), and Flet's default text size is 14px. The one genuinely
#: large string, the 26px application title in `INK`, clears the stricter bar
#: anyway, so the exception is not claimed anywhere in this interface.
REQUIREMENTS: tuple[Requirement, ...] = (
    Requirement(
        "INK",
        "BACKGROUND",
        AA_TEXT,
        "1.4.3",
        "the application title in the page header (simulation_view.py:410-415)",
    ),
    Requirement(
        "INK",
        "PANEL",
        AA_TEXT,
        "1.4.3",
        "every numeric readout, its unit, and each panel heading "
        "(simulation_view.py:248-257, :519, :650, :690, :743, :1127). Also "
        "the six compartment checkboxes that show and hide the chart's "
        "traces, in both roles the pair has: the box itself is INK filled "
        "with a PANEL tick, and its label is INK text while that trace is "
        "drawn. The box is a user-interface component, so SC 1.4.11's 3:1 "
        "would suffice for it - the text minimum is met anyway, and is what "
        "the label needs. Deliberately not one of the six trace colours nor "
        "ACCENT: the legend row has already spent its colour budget on six "
        "compartments (.claude/rules/ui-color.md, judgment 3), so the "
        "control is drawn as furniture rather than competing with the "
        "swatch beside it (PL-CG7J). Also the title and the opening "
        "statement of the new-case confirmation (`_build_new_case_dialog`), "
        "whose surface is set to PANEL explicitly rather than left to the "
        "Flet theme, so that these three text colours stand on a background "
        "this table measures them against (PL-R3KB). Also the playback-rate "
        "dropdown beside the transport controls, whose fill is set to PANEL "
        "explicitly for the same reason - it names the rate the clock is "
        "advancing at, which docs/MODEL.md requires displayed, so it is read "
        "rather than merely operated (PL-SN2C)",
    ),
    Requirement(
        "MUTED",
        "BACKGROUND",
        AA_TEXT,
        "1.4.3",
        "the run-status word while paused, beside the transport controls "
        "(simulation_view.py:187, :394, :684). Also the border of the "
        "playback-rate dropdown drawn beside them, which is a user-interface "
        "component and so needs only SC 1.4.11's 3:1 - met with room to "
        "spare by the text minimum this pair already carries (PL-SN2C)",
    ),
    Requirement(
        "MUTED",
        "PANEL",
        AA_TEXT,
        "1.4.3",
        "the compartment name and the smaller clinical gloss under it on each "
        "readout, the chart's axis description, and the agent-accounting "
        "detail line (simulation_view.py:619, :622, :653, :242-244). The "
        "gloss is judged at the same 4.5:1 as the name above it: at 12px it "
        "is normal text by WCAG's definition, nowhere near the 18.66px the "
        "large-text exception starts at, and it is the same MUTED colour on "
        "the same PANEL surface, so it adds no pair to this table (PL-8M05). "
        "Also the line of the new-case confirmation saying what carries over "
        "into the new case (`_build_new_case_dialog`, PL-R3KB), and the "
        "playback rate drawn under the simulated-time readout, which shares "
        "the surface and the size of the MAC multiples beside it (PL-SN2C).",
    ),
    Requirement(
        "ACCENT_TEXT",
        "BACKGROUND",
        AA_TEXT,
        "1.4.3",
        "the run-status word while running (simulation_view.py:682)",
    ),
    Requirement(
        "ACCENT_TEXT",
        "PANEL",
        AA_TEXT,
        "1.4.3",
        "the agent-accounting status word when conservation holds. Rendered at "
        "20px bold, which is large text, so SC 1.4.3's 3:1 would suffice - the "
        "stricter bar is applied deliberately (simulation_view.py:208, :731)",
    ),
    Requirement(
        "ACCENT",
        "PANEL",
        AA_NON_TEXT,
        "1.4.11",
        "the active track and thumb of all four parameter sliders, which is how "
        "each control shows its current value (simulation_view.py:320, :336, :346, :356)",
    ),
    Requirement(
        "WARNING",
        "BACKGROUND",
        AA_TEXT,
        "1.4.3",
        "the halted-run notice, the run-status word while stopped, and the "
        "educational-use disclaimer (simulation_view.py:406, :417, :678)",
    ),
    Requirement(
        "WARNING",
        "PANEL",
        AA_TEXT,
        "1.4.3",
        "the agent-accounting status word when validation fails "
        "(`_build_agent_accounting_panel`), the notice naming a compartment "
        "trace that is above the top of the chart (`_off_scale_text`), and the "
        "line of the new-case confirmation stating what a switch would discard "
        "(`_build_new_case_dialog`, PL-R3KB)",
    ),
    Requirement(
        "sevoflurane.foreground",
        "sevoflurane.fill",
        AA_TEXT,
        "1.4.3",
        "the agent name over its ISO 5360 identification color",
    ),
    Requirement(
        "isoflurane.foreground",
        "isoflurane.fill",
        AA_TEXT,
        "1.4.3",
        "the agent name over its ISO 5360 identification color",
    ),
    Requirement(
        "desflurane.foreground",
        "desflurane.fill",
        AA_TEXT,
        "1.4.3",
        "the agent name over its ISO 5360 identification color",
    ),
    Requirement(
        "sevoflurane.fill",
        "BACKGROUND",
        AA_NON_TEXT,
        "1.4.11",
        "the identification swatch in the header, read as a shape",
    ),
    Requirement(
        "isoflurane.fill",
        "BACKGROUND",
        AA_NON_TEXT,
        "1.4.11",
        "the identification swatch in the header, read as a shape",
    ),
    Requirement(
        "desflurane.fill",
        "BACKGROUND",
        AA_NON_TEXT,
        "1.4.11",
        "the identification swatch in the header, read as a shape",
    ),
    Requirement("CIRCUIT_COLOR", "PANEL", AA_NON_TEXT, "1.4.11", "a plotted compartment trace"),
    Requirement("ALVEOLAR_COLOR", "PANEL", AA_NON_TEXT, "1.4.11", "a plotted compartment trace"),
    Requirement(
        "MIXED_VENOUS_COLOR", "PANEL", AA_NON_TEXT, "1.4.11", "a plotted compartment trace"
    ),
    Requirement("VESSEL_RICH_COLOR", "PANEL", AA_NON_TEXT, "1.4.11", "a plotted compartment trace"),
    Requirement("MUSCLE_COLOR", "PANEL", AA_NON_TEXT, "1.4.11", "a plotted compartment trace"),
    Requirement("FAT_COLOR", "PANEL", AA_NON_TEXT, "1.4.11", "a plotted compartment trace"),
    Requirement(
        "MAC_AWAKE_BAND_COLOR",
        "PANEL",
        AA_NON_TEXT,
        "1.4.11",
        "the MAC-awake reference band on the chart, and its legend swatch. The "
        "pair measured is the band's *boundary*: a 1.5px stroke on the upper "
        "edge and the fill's own cut-off on the lower, both this color at full "
        "opacity, which is what a reader has to perceive to know where the band "
        "is. The fill between them is this color at "
        "MAC_AWAKE_BAND_FILL_OPACITY and is decoration - it is deliberately "
        "light enough for six traces to stay legible across it, which a fill "
        "meeting 3:1 in its own right would not be. That is a fill judged by "
        "SC 1.4.11's own carve-out for a graphical object whose meaning another "
        "part carries, not a shortfall: no entry belongs in KNOWN_SHORTFALLS "
        "for it (PL-F52R)",
    ),
    Requirement(
        "ONE_MAC_LINE_COLOR",
        "PANEL",
        AA_NON_TEXT,
        "1.4.11",
        "the 1 MAC reference line on the chart, and its legend swatch. Held to "
        "the graphical-object minimum rather than to the 4.5:1 the same color "
        "meets as MUTED text elsewhere: this instance is a ruled line, not a "
        "string. It is deliberately quieter than MAC_AWAKE_BAND_COLOR - the two "
        "traces have converged by the time a run reaches 1 MAC and have not at "
        "MAC-awake, so the band is the trace-critical mark of the two (PL-F52R)",
    ),
)

#: Declared pairs that do not meet their minimum today, each against the item
#: that closes it. Not a suppression list: an entry here that starts passing is
#: reported as an error, so a fix cannot leave its excuse behind.
#:
#: `ACCENT` appears twice below with the same measured value and two different
#: owners, which is not duplication: the alveolar trace and the slider track are
#: separate on-screen elements that happen to share one constant. That sharing
#: is itself the defect each item describes, and listing them separately is what
#: makes it visible.
#:
#: The sevoflurane entry is a limitation of this tool rather than of the
#: interface. That swatch carries a border in its own foreground color, which
#: is 10.70:1 against the page - so it is perceivable, by a channel a
#: single-pair requirement cannot express. `PL-GNN1` adds the requirement kind
#: that says "fill or border" and removes this entry.
KNOWN_SHORTFALLS: dict[tuple[str, str], str] = {
    ("ACCENT", "PANEL"): "PL-W8DQ",
    ("sevoflurane.fill", "BACKGROUND"): "PL-GNN1",
    ("ALVEOLAR_COLOR", "PANEL"): "PL-GVXP",
}

#: The six chart traces, in the order `SimulationView._plotted_series` lists them.
TRACES: tuple[str, ...] = (
    "CIRCUIT_COLOR",
    "ALVEOLAR_COLOR",
    "MIXED_VENOUS_COLOR",
    "VESSEL_RICH_COLOR",
    "MUSCLE_COLOR",
    "FAT_COLOR",
)


def relative_luminance(hex_color: str) -> float:
    """Relative luminance of an sRGB color, per WCAG 2.2.

    Args:
        hex_color: Six-digit sRGB hex, with or without a leading `#`.

    Returns:
        Relative luminance in [0, 1].
    """
    digits = hex_color.lstrip("#")
    if len(digits) != 6:
        raise ValueError(f"expected a six-digit sRGB hex color, got {hex_color!r}")
    channels = [int(digits[index : index + 2], 16) / 255 for index in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first: str, second: str) -> float:
    """Contrast ratio between two sRGB colors, per WCAG 2.2.

    Args:
        first: Six-digit sRGB hex.
        second: Six-digit sRGB hex.

    Returns:
        A ratio in [1, 21]; order-independent.
    """
    a, b = relative_luminance(first), relative_luminance(second)
    lighter, darker = max(a, b), min(a, b)
    return (lighter + 0.05) / (darker + 0.05)


def separation_ceiling(count: int) -> float:
    """The largest ratio every adjacent pair of `count` traces can share.

    Ratios compose along the luminance axis, and the axis is bounded: black to
    white is 21:1 in total. Sorting `count` traces by luminance, the smallest
    adjacent gap is largest when the gaps are equal, so no arrangement can give
    every pair more than the `count - 1`-th root of 21. At six traces that is
    about 1.84 - well under SC 1.4.11's 3:1 - which is why luminance alone
    cannot carry this chart and a second, non-color channel is a requirement
    rather than an embellishment. Individual non-adjacent pairs exceed it; the
    bound is on the worst pair, which is the one that decides legibility.
    """
    if count < 2:
        raise ValueError("a separation ceiling needs at least two traces")
    return float(21.0 ** (1.0 / (count - 1)))


def _string_value(node: ast.expr, known: dict[str, str]) -> str | None:
    """Resolve a literal string or a reference to an already-known constant."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return known.get(node.id)
    return None


def _collect_agent_schemes(node: ast.expr, known: dict[str, str]) -> dict[str, str]:
    """Pull `<agent>.fill` and `<agent>.foreground` out of the scheme table."""
    found: dict[str, str] = {}
    if not isinstance(node, ast.Dict):
        return found
    for key, value in zip(node.keys, node.values, strict=True):
        if not (isinstance(key, ast.Constant) and isinstance(key.value, str)):
            continue
        if not isinstance(value, ast.Call):
            continue
        for keyword in value.keywords:
            if keyword.arg not in ("fill", "foreground"):
                continue
            resolved = _string_value(keyword.value, known)
            if resolved is not None:
                found[f"{key.value}.{keyword.arg}"] = resolved
    return found


def read_palette(root: Path) -> dict[str, str]:
    """Extract every named color from the two modules that define them.

    Read with `ast` rather than imported: `app/simulation_view.py` imports Flet,
    which a standard-library-only tool running in a bare checkout does not have.

    Args:
        root: Repository root.

    Returns:
        Color name to six-digit sRGB hex. Agent entries are keyed
        `<agent>.fill` and `<agent>.foreground`.
    """
    palette: dict[str, str] = {}
    for relative in (THEME, VIEW):
        path = root / relative
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for statement in tree.body:
            targets: list[ast.expr] = []
            value: ast.expr | None = None
            if isinstance(statement, ast.Assign):
                targets, value = list(statement.targets), statement.value
            elif isinstance(statement, ast.AnnAssign) and statement.value is not None:
                targets, value = [statement.target], statement.value
            if value is None:
                continue
            for target in targets:
                if not isinstance(target, ast.Name):
                    continue
                if target.id == "AGENT_COLOR_SCHEMES":
                    palette.update(_collect_agent_schemes(value, palette))
                    continue
                resolved = _string_value(value, palette)
                if resolved is not None and resolved.startswith("#"):
                    palette[target.id] = resolved
    return palette


@dataclass(frozen=True)
class Result:
    """One evaluated requirement."""

    requirement: Requirement
    ratio: float

    @property
    def rounded(self) -> float:
        return round(self.ratio, DISPLAY_DECIMALS)

    @property
    def meets(self) -> bool:
        return self.rounded >= self.requirement.minimum


@dataclass(frozen=True)
class Report:
    """Everything one run decided."""

    results: tuple[Result, ...]
    missing: tuple[str, ...]
    unexpected: tuple[Result, ...]
    repaired: tuple[Result, ...]
    trace_pairs: tuple[tuple[str, str, float], ...]

    @property
    def errors(self) -> bool:
        return bool(self.missing or self.unexpected or self.repaired)


def analyze(root: Path) -> Report:
    """Evaluate every declared requirement against the palette on disk."""
    palette = read_palette(root)
    results: list[Result] = []
    missing: list[str] = []

    for requirement in REQUIREMENTS:
        names = (requirement.foreground, requirement.background)
        absent = [name for name in names if name not in palette]
        if absent:
            missing.extend(absent)
            continue
        results.append(Result(requirement, contrast_ratio(palette[names[0]], palette[names[1]])))

    unexpected = tuple(
        result
        for result in results
        if not result.meets
        and (result.requirement.foreground, result.requirement.background) not in KNOWN_SHORTFALLS
    )
    repaired = tuple(
        result
        for result in results
        if result.meets
        and (result.requirement.foreground, result.requirement.background) in KNOWN_SHORTFALLS
    )
    trace_pairs = tuple(
        (first, second, contrast_ratio(palette[first], palette[second]))
        for first, second in combinations(TRACES, 2)
        if first in palette and second in palette
    )
    return Report(
        results=tuple(results),
        missing=tuple(sorted(set(missing))),
        unexpected=unexpected,
        repaired=repaired,
        trace_pairs=trace_pairs,
    )


def format_report(report: Report, *, matrix: bool) -> str:
    """Render a report the way `bin/docket check` renders one: verdict first."""
    met = sum(1 for result in report.results if result.meets)
    lines = [
        f"contrast: {met} of {len(report.results)} declared pairs meet WCAG 2.2 AA, "
        f"{len(KNOWN_SHORTFALLS)} known shortfalls, "
        f"{len(report.unexpected) + len(report.missing) + len(report.repaired)} errors"
    ]

    if report.missing:
        lines.append("")
        lines.append("Colors named in REQUIREMENTS but absent from the palette:")
        lines.extend(f"  {name}" for name in report.missing)
        lines.append("  A renamed or deleted constant leaves its requirement unchecked.")

    if report.unexpected:
        lines.append("")
        lines.append("Below the required ratio, and not a known shortfall:")
        for result in report.unexpected:
            requirement = result.requirement
            lines.append(
                f"  {requirement.foreground} on {requirement.background}: "
                f"{result.rounded:.2f} < {requirement.minimum} "
                f"(SC {requirement.criterion}) - {requirement.why}"
            )

    if report.repaired:
        lines.append("")
        lines.append("Listed as a known shortfall but now passing - remove the entry:")
        for result in report.repaired:
            pair = (result.requirement.foreground, result.requirement.background)
            lines.append(
                f"  {pair[0]} on {pair[1]}: {result.rounded:.2f}, tracked by "
                f"{KNOWN_SHORTFALLS[pair]}"
            )

    shortfalls = [result for result in report.results if not result.meets and not report.errors]
    if shortfalls:
        lines.append("")
        lines.append("Known shortfalls (tracked, not failing):")
        for result in shortfalls:
            pair = (result.requirement.foreground, result.requirement.background)
            lines.append(
                f"  {pair[0]} on {pair[1]}: {result.rounded:.2f} < "
                f"{result.requirement.minimum} - {KNOWN_SHORTFALLS.get(pair, '?')}"
            )

    if matrix and report.trace_pairs:
        ceiling = separation_ceiling(len(TRACES))
        lines.append("")
        lines.append(
            f"Chart-trace pairwise separation (not decided here; PL-GVXP sets the bar). "
            f"No arrangement of six traces gives every pair more than {ceiling:.2f} on "
            f"luminance alone, so a non-color channel is required, not optional."
        )
        for first, second, ratio in sorted(report.trace_pairs, key=lambda pair: pair[2]):
            lines.append(f"  {first:<20} {second:<20} {ratio:.2f}")

    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=None, help="path to the repository")
    parser.add_argument(
        "--matrix", action="store_true", help="also print the chart-trace pairwise ratios"
    )
    args = parser.parse_args(argv)

    root = (args.root or Path(__file__).resolve().parent.parent).resolve()
    report = analyze(root)
    print(format_report(report, matrix=args.matrix))
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
