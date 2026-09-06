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

**What this decides.** Whether a declared requirement meets its declared
ratio. Most are one foreground against one background (`Requirement`); an
element whose edge is carried by either of two channels declares both and is
held to the better of them (`EitherRequirement`), because measuring such an
element one channel at a time reports a shortfall on a badge that is legible
and would report one on the others if the other channel were picked.

**What it must never decide.** Whether a color is text or a graphical object,
which pairs actually appear on screen together, whether a non-color channel is
genuinely redundant, *which* channels an element really has, or how far apart
two chart traces ought to be. Those are judgments; they live in `REQUIREMENTS`
below, written by a person, and this file only evaluates them - taking the
maximum over channels somebody else declared is arithmetic, not judgment. A
tool that guesses the judgment half is worse than no tool, because its output
looks authoritative and is not.

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

**Descriptions cite code by symbol, and the citation is checked.** A `why`
below names where its pair is drawn by putting a symbol from `app/theme.py` or
`app/simulation_view.py` in backticks. It used to give line numbers, and every
one of them rotted: on 2026-09-05 fourteen cited lines were read and not one
landed on what its entry claimed - `:682`, cited as the run-status word, was a
list of chart control marks (PL-GJDW). A wrong citation is worse than none,
because it looks authoritative and quietly makes the check's own coverage
unauditable. `check_citations` now refuses a line number outright and resolves
every cited symbol against the two modules, so the form that rotted cannot come
back. Whether the named symbol is really where that color matters stays a
person's judgment, exactly as the pair itself does.

**Known shortfalls, and why they do not simply fail the build.** The
requirements listed in `KNOWN_SHORTFALLS` do not meet their minimum today. Listing them
there against the item that closes each one keeps `make check` green while making the
gap visible and owned, which is the opposite of the comment-that-nobody-checks
this file replaces. The list cannot rot: a shortfall that starts *passing* is
an error too, so fixing one forces its entry out.
"""

from __future__ import annotations

import argparse
import ast
import re
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

THEME = Path("src/anesthesia_sim/app/theme.py")
VIEW = Path("src/anesthesia_sim/app/simulation_view.py")

#: How a requirement description cites the code its pair is drawn in: a bare
#: symbol from one of the two modules above, in backticks. Bare, so `mount` and
#: not `mount()`; a span holding anything else - a path, a prose word, an item
#: id - is left alone, which is what keeps `.claude/rules/ui-color.md` and
#: `docs/MODEL.md` readable as the citations they are.
SYMBOL_SPAN_RE = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)`")

#: `simulation_view.py:320`, and the ranged form `:248-257`. Refused rather
#: than merely discouraged: a convention against it is exactly what failed
#: before, and the rotting is silent (PL-GJDW).
LINE_CITATION_RE = re.compile(r"\b[\w./]+\.py:\d+(?:-\d+)?")

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
    """One pair that must hold, and the judgment behind holding it.

    The right model for text, which has one channel and no fallback: the
    string is drawn in `foreground` and there is nothing else to read it by.
    `EitherRequirement` is the model for an element carrying two.
    """

    foreground: str
    background: str
    minimum: float
    criterion: str
    why: str

    @property
    def candidates(self) -> tuple[str, ...]:
        """The foregrounds measured against the background - here, the one."""
        return (self.foreground,)

    @property
    def label(self) -> str:
        """How the foreground side is named in a report line."""
        return self.foreground

    @property
    def key(self) -> tuple[str, str]:
        """This requirement's identity in `KNOWN_SHORTFALLS`."""
        return (self.foreground, self.background)


@dataclass(frozen=True)
class EitherRequirement:
    """Several candidate foregrounds against one background, best one held.

    For an element whose edge is carried by more than one channel, where
    perceiving *any* of them is enough to locate it. The header agent badge
    is the case this exists for: a rectangle filled in the agent's
    identification color and outlined 1px in the agent's own text color
    (`AGENT_RENDER_STYLES` builds the border, `_agent_header_badge` is the
    container it is set on), so a reader finds its shape by the fill or by
    the outline, and it is perceivable if either clears the minimum.

    **Measuring such an element one channel at a time is wrong in both
    directions.** Against the page, the sevoflurane fill is 1.27:1 and its
    border 10.70:1; for isoflurane and desflurane the fill clears the bar
    and the white border does not. Held to the fill alone, one of the three
    reads as a shortfall; held to the border alone, the other two do. All
    three badges have a perceivable boundary, and a checker reporting
    otherwise is the failure this module's own docstring names - output that
    looks authoritative and is not (PL-GNN1).

    **A disjunction over channels, and deliberately not a boolean language.**
    Two-channel redundancy is the case this interface has. Whether a channel
    is genuinely redundant is a judgment, written into `why` by a person,
    exactly as a single pair's surface is; this only takes the maximum of
    what it is told to measure. An arbitrary requirement grammar would move
    that judgment into the tool, which is the line the module does not cross.
    """

    foregrounds: tuple[str, ...]
    background: str
    minimum: float
    criterion: str
    why: str

    @property
    def candidates(self) -> tuple[str, ...]:
        """The foregrounds measured against the background, the best one taken."""
        return self.foregrounds

    @property
    def label(self) -> str:
        """How the foreground side is named in a report line."""
        return " or ".join(self.foregrounds)

    @property
    def key(self) -> tuple[str, str]:
        """This requirement's identity in `KNOWN_SHORTFALLS`."""
        return (self.label, self.background)


#: Either kind. Two types rather than one with an optional second foreground:
#: text has no second channel, and a model letting it declare one would invite
#: a fallback that is not on the screen.
AnyRequirement = Requirement | EitherRequirement


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
REQUIREMENTS: tuple[AnyRequirement, ...] = (
    Requirement(
        "INK",
        "BACKGROUND",
        AA_TEXT,
        "1.4.3",
        "the application title in the page header, which `mount` builds inline",
    ),
    Requirement(
        "INK",
        "PANEL",
        AA_TEXT,
        "1.4.3",
        "every numeric readout and its unit (`_build_metric_value` for the "
        "compartment grid, `_build_parameter_panel` for the four settings "
        "beside their sliders), each panel heading (`_build_parameter_panel`, "
        "`_build_chart_panel`, `_build_wash_in_section`, "
        "`_build_control_timeline_panel`, `_build_agent_accounting_panel`), and "
        "every legend label beside a swatch (`_build_legend_item`, "
        "`_build_control_mark_legend_item`, `_build_band_legend_item`). Also "
        "the six compartment checkboxes that show and hide the chart's traces "
        "(`_build_compartment_trace`), in both roles the pair has: the box "
        "itself is INK filled with a PANEL tick, and its label is INK text "
        "while that trace is drawn - `_apply_trace_visibility` is the one "
        "writer of that. The box is a user-interface component, so SC 1.4.11's "
        "3:1 would suffice for it - the text minimum is met anyway, and is what "
        "the label needs. Deliberately not one of the six trace colours nor "
        "ACCENT: the legend row has already spent its colour budget on six "
        "compartments (.claude/rules/ui-color.md, judgment 3), so the "
        "control is drawn as furniture rather than competing with the "
        "swatch beside it (PL-CG7J). Also the title and the opening "
        "statement of the new-case confirmation (`_build_new_case_dialog`), "
        "whose surface is set to PANEL explicitly rather than left to the "
        "Flet theme, so that these three text colours stand on a background "
        "this table measures them against (PL-R3KB). Also both dropdowns whose "
        "fill is set to PANEL explicitly for that same reason: the playback "
        "rate beside the transport controls (`_playback_rate_dropdown`), which "
        "names the rate the clock is advancing at, which docs/MODEL.md requires "
        "displayed, so it is read rather than merely operated (PL-SN2C); and "
        "the chart's time base (`_time_base_dropdown`), which names how much of "
        "the run is on screen and is read the same way",
    ),
    Requirement(
        "MUTED",
        "BACKGROUND",
        AA_TEXT,
        "1.4.3",
        "the run-status word while paused, beside the transport controls "
        "(`_status_text`, whose colour `_refresh_view` writes for every run "
        "state). Also the border of the playback-rate dropdown drawn beside "
        "them (`_playback_rate_dropdown`), which is a user-interface component "
        "and so needs only SC 1.4.11's 3:1 - met with room to spare by the text "
        "minimum this pair already carries (PL-SN2C)",
    ),
    Requirement(
        "MUTED",
        "PANEL",
        AA_TEXT,
        "1.4.3",
        "the compartment name and the smaller clinical gloss under it on each "
        "readout (`_build_metric_panel`), the MAC multiple under the value "
        "(`_build_metric_secondary_value`), both chart axis descriptions "
        "(`_time_axis_caption`, `_wash_in_time_axis_caption`), the sub-headings "
        "and status lines the chart and its neighbours hold "
        "(`_build_chart_panel`, `_build_wash_in_section`, "
        "`_build_control_timeline_panel`), and the agent-accounting detail "
        "lines (`_agent_accounting_detail_text`, `_agent_amounts_text`). The "
        "gloss is judged at the same 4.5:1 as the name above it: at 12px it "
        "is normal text by WCAG's definition, nowhere near the 18.66px the "
        "large-text exception starts at, and it is the same MUTED colour on "
        "the same PANEL surface, so it adds no pair to this table (PL-8M05). "
        "Also the line of the new-case confirmation saying what carries over "
        "into the new case (`_build_new_case_dialog`, PL-R3KB), the "
        "playback rate drawn under the simulated-time readout "
        "(`_playback_rate_text`), which shares the surface and the size of the "
        "MAC multiples beside it (PL-SN2C), and the border of the chart's "
        "time-base dropdown (`_time_base_dropdown`), a user-interface component "
        "needing only SC 1.4.11's 3:1.",
    ),
    Requirement(
        "ACCENT_TEXT",
        "BACKGROUND",
        AA_TEXT,
        "1.4.3",
        "the run-status word while running (`_status_text`, set by `_refresh_view`)",
    ),
    Requirement(
        "ACCENT_TEXT",
        "PANEL",
        AA_TEXT,
        "1.4.3",
        "the agent-accounting status word when conservation holds "
        "(`_agent_accounting_status_text`, inside `_build_agent_accounting_panel`, "
        "written by `_refresh_view`). Rendered at 20px bold, which is large text, "
        "so SC 1.4.3's 3:1 would suffice - the stricter bar is applied "
        "deliberately",
    ),
    Requirement(
        "ACCENT",
        "PANEL",
        AA_NON_TEXT,
        "1.4.11",
        "the active track and thumb of all four parameter sliders, which is how "
        "each control shows its current value (`_fresh_gas_flow_slider`, "
        "`_delivered_concentration_slider`, `_alveolar_ventilation_slider`, "
        "`_cardiac_output_slider`, each drawn on the PANEL surface "
        "`_build_parameter_panel` sets)",
    ),
    Requirement(
        "WARNING",
        "BACKGROUND",
        AA_TEXT,
        "1.4.3",
        "the halted-run notice (`_notice_text`, written by `_refresh_notice`), "
        "the run-status word while stopped (`_status_text`), and the "
        "educational-use disclaimer, which `mount` builds inline at the foot of "
        "the page",
    ),
    Requirement(
        "WARNING",
        "PANEL",
        AA_TEXT,
        "1.4.3",
        "the agent-accounting status word when validation fails "
        "(`_agent_accounting_status_text`, in `_build_agent_accounting_panel`), "
        "the notice naming a compartment "
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
    EitherRequirement(
        ("sevoflurane.fill", "sevoflurane.foreground"),
        "BACKGROUND",
        AA_NON_TEXT,
        "1.4.11",
        "the identification swatch in the header, read as a shape - by its "
        "fill or by its border, whichever carries the edge. `AGENT_RENDER_STYLES` "
        "outlines the badge 1px in the agent's own text colour and "
        "`_agent_header_badge` is the container both are set on, so either "
        "channel locating the badge satisfies SC 1.4.11. This one is carried "
        "by its border: ISO 5360 yellow is far too light to hold an edge "
        "against the page, which is why the badge is outlined at all",
    ),
    EitherRequirement(
        ("isoflurane.fill", "isoflurane.foreground"),
        "BACKGROUND",
        AA_NON_TEXT,
        "1.4.11",
        "the identification swatch in the header, read as a shape - by its "
        "fill or by its border, whichever carries the edge. Carried by its "
        "fill: the border is white, which is near-invisible against the page, "
        "so the ISO 5360 purple is the channel a reader finds this badge by",
    ),
    EitherRequirement(
        ("desflurane.fill", "desflurane.foreground"),
        "BACKGROUND",
        AA_NON_TEXT,
        "1.4.11",
        "the identification swatch in the header, read as a shape - by its "
        "fill or by its border, whichever carries the edge. Carried by its "
        "fill, for the same reason as isoflurane above: the white border "
        "disappears into the page and the ISO 5360 blue is what remains",
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
KNOWN_SHORTFALLS: dict[tuple[str, str], str] = {
    ("ACCENT", "PANEL"): "PL-W8DQ",
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


def read_symbols(root: Path) -> frozenset[str]:
    """Every name the two color-defining modules define.

    Four kinds, because those are the four a description has cause to cite:
    module-level constants, classes, functions and methods, and the `self.X`
    attributes the view builds its controls into. Read with `ast` for the same
    reason the palette is - `app/simulation_view.py` imports Flet.

    Deliberately a flat set rather than a scope-aware resolution. It answers
    "does this name exist here", which is the whole of what a citation check
    can decide; it does not answer whether a method belongs to the class a
    reader would expect, and no message here implies that it does.

    Args:
        root: Repository root.

    Returns:
        Every defined name, unqualified.
    """
    names: set[str] = set()
    for relative in (THEME, VIEW):
        path = root / relative
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                names.add(node.name)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                names.add(node.id)
            elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
                names.add(node.attr)
    return frozenset(names)


def check_citations(root: Path) -> tuple[str, ...]:
    """Resolve every symbol the requirement descriptions cite.

    Two rules, both decidable by reading the tree, which is why they are here
    rather than in a session's head. A description may not cite a line number,
    and every symbol it does cite must exist. What the citation is *for* -
    whether that method is really where the pair is drawn, and whether every
    site is named - stays with the reader, the same division `tools/doc_check.py`
    draws between resolving a path and judging the sentence around it.

    Args:
        root: Repository root.

    Returns:
        One message per unresolved citation; empty when every one resolves.
    """
    symbols = read_symbols(root)
    errors: list[str] = []
    for requirement in REQUIREMENTS:
        pair = f"{requirement.label} on {requirement.background}"
        for match in LINE_CITATION_RE.finditer(requirement.why):
            errors.append(
                f"  {pair}: cites {match.group(0)}, a line number. Name the symbol the "
                "color is set on instead - a line number is stale by the next edit "
                "and says nothing when it is."
            )
        for name in SYMBOL_SPAN_RE.findall(requirement.why):
            if name not in symbols:
                errors.append(
                    f"  {pair}: cites `{name}`, which {THEME.name} and {VIEW.name} do "
                    "not define. A renamed symbol leaves the requirement pointing at "
                    "nothing."
                )
    return tuple(errors)


@dataclass(frozen=True)
class Result:
    """One evaluated requirement, at the ratio that decided it.

    For a single pair that is the pair's own ratio; for an `EitherRequirement`
    it is the best channel's, which is the one the verdict turns on.
    """

    requirement: AnyRequirement
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
    citations: tuple[str, ...]
    trace_pairs: tuple[tuple[str, str, float], ...]

    @property
    def errors(self) -> bool:
        return bool(self.missing or self.unexpected or self.repaired or self.citations)


def analyze(root: Path) -> Report:
    """Evaluate every declared requirement against the palette on disk."""
    palette = read_palette(root)
    results: list[Result] = []
    missing: list[str] = []

    for requirement in REQUIREMENTS:
        names = (*requirement.candidates, requirement.background)
        absent = [name for name in names if name not in palette]
        if absent:
            missing.extend(absent)
            continue
        background = palette[requirement.background]
        # The best channel decides. For a single pair there is only one, so
        # this is the pair's own ratio; for a disjunction it is the channel
        # the reader actually perceives the element by.
        results.append(
            Result(
                requirement,
                max(contrast_ratio(palette[name], background) for name in requirement.candidates),
            )
        )

    unexpected = tuple(
        result
        for result in results
        if not result.meets and result.requirement.key not in KNOWN_SHORTFALLS
    )
    repaired = tuple(
        result for result in results if result.meets and result.requirement.key in KNOWN_SHORTFALLS
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
        citations=check_citations(root),
        trace_pairs=trace_pairs,
    )


def format_report(report: Report, *, matrix: bool) -> str:
    """Render a report the way `bin/docket check` renders one: verdict first."""
    met = sum(1 for result in report.results if result.meets)
    error_count = (
        len(report.unexpected) + len(report.missing) + len(report.repaired) + len(report.citations)
    )
    lines = [
        f"contrast: {met} of {len(report.results)} declared requirements meet WCAG 2.2 AA, "
        f"{len(KNOWN_SHORTFALLS)} known shortfalls, "
        f"{error_count} errors"
    ]

    if report.citations:
        lines.append("")
        lines.append("Requirement descriptions citing code that cannot be resolved:")
        lines.extend(report.citations)

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
                f"  {requirement.label} on {requirement.background}: "
                f"{result.rounded:.2f} < {requirement.minimum} "
                f"(SC {requirement.criterion}) - {requirement.why}"
            )

    if report.repaired:
        lines.append("")
        lines.append("Listed as a known shortfall but now passing - remove the entry:")
        for result in report.repaired:
            requirement = result.requirement
            lines.append(
                f"  {requirement.label} on {requirement.background}: {result.rounded:.2f}, "
                f"tracked by {KNOWN_SHORTFALLS[requirement.key]}"
            )

    shortfalls = [result for result in report.results if not result.meets and not report.errors]
    if shortfalls:
        lines.append("")
        lines.append("Known shortfalls (tracked, not failing):")
        for result in shortfalls:
            requirement = result.requirement
            lines.append(
                f"  {requirement.label} on {requirement.background}: {result.rounded:.2f} < "
                f"{requirement.minimum} - {KNOWN_SHORTFALLS.get(requirement.key, '?')}"
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
