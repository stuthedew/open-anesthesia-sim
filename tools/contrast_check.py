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

**Colors are read, not imported, from every module under `app/`.** The
interface imports PySide6, so a standard-library-only tool cannot import it. The constants
are extracted with `ast` from every `.py` under `APP` - the theme first, so an
alias of a theme name resolves, then the rest in path order - which also means
this runs in a bare checkout with no virtualenv, the promise every tool here
makes. Every module rather than two named paths since PL-BXB2: a colour
declared in a module this tool did not read was measured by nothing and missed
by nothing, and the decomposed Qt view is what would have created such modules.

**Descriptions cite code by symbol, and the citation is checked.** A `why`
below names where its pair is drawn by putting a symbol in backticks - from
`app/theme.py`, which holds every color since PL-2CS8, or from whichever
module under `app/` holds the method that draws them. It used to
give line numbers, and every one of them rotted: on 2026-09-05 fourteen cited
lines were read and not one landed on what its entry claimed - `:682`, cited as
the run-status word, was a list of chart control marks (PL-GJDW). A wrong
citation is worse than none, because it looks authoritative and quietly makes
the check's own coverage unauditable. `check_citations` now refuses a line
number outright and resolves every cited symbol against every module under
`app/`, so the form that rotted cannot come back.
Whether the named symbol is really where that color matters stays a
person's judgment, exactly as the pair itself does.

**Known shortfalls, and why they do not simply fail the build.** The
requirements listed in `KNOWN_SHORTFALLS` do not meet their minimum today. Listing them
there against the item that closes each one keeps `make check` green while making the
gap visible and owned, which is the opposite of the comment-that-nobody-checks
this file replaces. The list cannot rot: a shortfall that starts *passing* is
an error too, so fixing one forces its entry out.

**What a Qt port costs this check, measured rather than estimated (PL-JRS3).**
It survives, because its whole input is module-level `NAME = "#RRGGBB"`
constants and no toolkit owns those. Measured 2026-09-14 by rewriting
`app/theme.py` and `app/simulation_view.py` on the AST - every Flet property
assignment replaced by the PySide6 setter call that supplants it - and running
this tool against the result: it reported `0 errors` on the ported tree, which
is the correct answer. Every way of *removing* a declared color is loud:
renaming `FAT_COLOR` failed with the constant named in `missing`, and moving
`SimulationView` to its own module - which PL-B9PY records the port doing from
the start - failed with 68 unresolved citations. That last failure is gone
since PL-BXB2, correctly: a symbol is resolved against every module under
`app/`, so a class moving to its own module is a citation that still resolves
rather than one that has to be re-pointed.

**The one hole was additive, and PL-BXB2 closed it before the port could open
it.** A color declared in a module that was neither `app/theme.py` nor
`app/simulation_view.py` was measured by nothing and missed by nothing: PL-JRS3's
probe D1 put a selection color at 1.07:1 on the panel in a new chart-panel
module and this tool reported `0 errors`. Every module under `app/` is read
now, so that color is measured, and `check_colors_live_in_the_theme` refuses it
for being outside the theme - as a named constant, or as a hex literal written
inline in a call, which has no name a requirement could cite and so could never
be measured at all. The report says how many modules it read, so a decomposed
view being measured is visible rather than assumed. What remains unread, and is
stated rather than hidden: a color that is neither a module-level constant nor
a literal - one computed, or taken from a toolkit's own palette by name - is
not a value this tool can see, and `tools/agent_identity_check.py` exists for
the one such case that has bitten.

**Disabled states are out of scope, and that is a decision rather than an
oversight (PL-NGF7, decided 2026-09-16).** Every colour a control takes when it
is disabled comes from `QPalette`'s `Disabled` colour group, which the platform
style fills in - measured 2026-09-16 as `#BEBEBE` for every disabled text role
under Fusion, confirmed per widget on a disabled `QPushButton`, `QComboBox` and
`QLabel`. That value is declared nowhere in `app/theme.py`, so it is not merely
undeclared but unreachable to the `ast` extraction above; and `app/main.py`
never calls `setStyle`, so it is the *platform's* number rather than the
product's and differs on the machine a learner uses. There is nothing here for
this tool to measure, and a requirement written against `#BEBEBE` would assert
a value this project does not choose.

*What covers them instead, since "nothing covers them and nothing says so" is
what PL-NGF7 was filed for.* The safety-relevant half is covered by
`tools/agent_identity_check.py`: no control carrying agent identity may be
*rendered* disabled (project owner, 2026-09-08), enforced as the
`setDisabled`/`setHidden` pairing, so the ISO 5360 obligation to show the right
agent colour is never left to a style's grey. What remains is the splitter
handle and the start, pause and reset buttons - plain controls carrying no
identity, no value and no clinical meaning, whose labels are the only thing at
stake. W3C WCAG 2.2 SC 1.4.3 exempts "text ... that is part of an inactive user
interface component" from any contrast requirement
(https://www.w3.org/TR/WCAG22/#contrast-minimum), which is the same exemption
`agent_identity_check` declines to claim for identity controls and which applies
squarely here.

*What is deliberately not claimed.* SC 1.4.11's own exception wording for
inactive components was **not** read at the source for this decision: `w3.org`
returns `EGRESS_BLOCKED` from this container, as PL-JX0Z recorded across five
routes. So nothing here rests on it. The argument above stands on SC 1.4.3,
which this repository already quotes verbatim, and on the measurement that
there is no author-chosen colour to check.

*And the scope note cannot rot silently*, which is the half a docstring alone
would not buy. `check_disabled_states_are_the_style_s` fails the build the
moment a `:disabled` rule or a `setPalette` call appears under `app/`, because
at that moment the colour *is* author-controlled, *is* measurable, and the two
paragraphs above stop being true. The correct response to that error is to
declare the colour in the theme and add a requirement - not to delete the
check.
"""

from __future__ import annotations

import argparse
import ast
import re
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

#: Every module under this tree is read; nothing under it is named by path.
APP = Path("src/anesthesia_sim/app")
#: The one module colors belong in (PL-2CS8), read first so that a name another
#: module aliases from it resolves to a color.
THEME = APP / "theme.py"

#: A six-digit sRGB hex literal, the only form a color takes in this tree.
HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")

#: How a requirement description cites the code its pair is drawn in: a bare
#: symbol from a module under `APP`, in backticks. Bare, so `mount` and
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


#: Dichromacy simulation: the linear-sRGB transform for each of the three
#: dichromacies, from Brettel H, Vienot F, Mollon JD, "Computerized simulation
#: of color appearance for dichromats", J Opt Soc Am A 1997;14(10):2647-2655,
#: https://doi.org/10.1364/JOSAA.14.002647.
#:
#: **The algorithm.** Brettel projects a stimulus onto the reduced surface a
#: dichromat can see, which is two half-planes meeting at the neutral axis, so
#: each deficiency needs two matrices and a rule for which one applies. The
#: rule is the sign of the dot product with `plane_normal`; both matrices and
#: the normal are given here already composed into linear sRGB, so no explicit
#: trip through LMS is needed. The later Vienot F, Brettel H, Mollon JD,
#: "Digital video colourmaps for checking the legibility of displays by
#: dichromats", Color Res Appl 1999;24(4):243-252, collapses this to one matrix
#: per deficiency and is the more widely copied form; it is *not* used here,
#: because its simplification is inaccurate for tritanopia and this project
#: reports all three.
#:
#: **The coefficients** are the precomputed sRGB-space forms published by
#: libDaltonLens (public domain, https://github.com/DaltonLens/libDaltonLens),
#: which derives them from Brettel's construction over the Smith & Pokorny
#: (1975) cone fundamentals; the derivation is written out at
#: https://daltonlens.org/understanding-cvd-simulation/. They are a *composed*
#: form of the paper's algorithm rather than a second method, which is why they
#: can be cited to it - but they are also one implementation's arithmetic, so
#: `tests/unit/test_contrast_check.py` holds them to the properties the paper
#: itself states: a dichromat's confusion lines collapse, and the neutral axis
#: and the deficiency's own copunctal-free primaries are left alone.
#:
#: **What this is not.** A simulation of appearance for a normal observer, not
#: a measurement of what a dichromat perceives, and not a WCAG measure: SC
#: 1.4.11 is defined on the color the display actually emits. Ratios computed
#: on simulated output are this project's own bar, recorded as such in
#: `docs/MODEL.md`, and are used for exactly two things - the trace floor
#: below, and the pairwise matrix that shows why line style rather than color
#: has to separate these curves.
DICHROMACY_TRANSFORMS: dict[str, tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...]]] = {
    "protanopia": (
        (0.14980, 1.19548, -0.34528, 0.10764, 0.84864, 0.04372, 0.00384, -0.00540, 1.00156),
        (0.14570, 1.16172, -0.30742, 0.10816, 0.85291, 0.03892, 0.00386, -0.00524, 1.00139),
        (0.00048, 0.00393, -0.00441),
    ),
    "deuteranopia": (
        (0.36477, 0.86381, -0.22858, 0.26294, 0.64245, 0.09462, -0.02006, 0.02728, 0.99278),
        (0.37298, 0.88166, -0.25464, 0.25954, 0.63506, 0.10540, -0.01980, 0.02784, 0.99196),
        (-0.00281, -0.00611, 0.00892),
    ),
    "tritanopia": (
        (1.01277, 0.13548, -0.14826, -0.01243, 0.86812, 0.14431, 0.07589, 0.80500, 0.11911),
        (0.93678, 0.18979, -0.12657, 0.06154, 0.81526, 0.12320, -0.37562, 1.12767, 0.24796),
        (0.03901, -0.02788, -0.01113),
    ),
}

#: The four ways every trace is measured: as displayed, and as simulated for
#: each dichromacy. Normal vision is named rather than implied so a report
#: column and a `docs/MODEL.md` row cannot come to mean different things.
VISION_MODELS: tuple[str, ...] = ("normal", *DICHROMACY_TRANSFORMS)

#: What every chart trace must clear against the panel in *all four* models.
#:
#: The number is SC 1.4.11's; extending it past normal vision is this project's
#: judgment and not the criterion's. The reason is that the criterion's purpose
#: - that a graphical object be findable against its background - is not served
#: by a trace measured only as emitted: `ALVEOLAR_COLOR` was 2.93:1 as
#: displayed and 2.61:1 simulated for protanopia, and `MUSCLE_COLOR` cleared
#: the bar as displayed at 3.19:1 and missed it at 2.98:1 simulated for
#: deuteranopia. The second of those was invisible to a checker that measured
#: normal vision alone, which is the whole argument for measuring all four
#: (PL-GVXP).
TRACE_FLOOR = AA_NON_TEXT


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
    (`_apply_agent_color_scheme` writes the border, `_agent_header_badge` is
    the container it is set on), so a reader finds its shape by the fill or by
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
#: `SimulationView` paints its page `BACKGROUND` and places the transport row,
#: the notice banner and the disclaimer directly on it, so the run-status
#: word, the halted-run notice and the disclaimer all sit on `BACKGROUND`,
#: while the readouts, the setting controls, the sidebar panels and the
#: new-case confirmation set their own `PANEL` surface (`MetricPanel`,
#: `ParameterSlider`, `RunView`, `NewCaseDialog`). `BACKGROUND` is the darker
#: surface, so it is the binding one wherever a color appears on both - which
#: is what made `MUTED` a worse failure than the panel measurement showed
#: (PL-X0RG).
#:
#: `MUTED` is judged at the normal-text minimum rather than the large-text one
#: even where it is bold: WCAG's large-text exception starts at 18pt, or 14pt
#: bold (18.66px), and no size `app/theme.py` gives MUTED text reaches it. The
#: one genuinely large string, the 26px application title in `INK`, clears the
#: stricter bar anyway, so the exception is not claimed anywhere in this
#: interface.
REQUIREMENTS: tuple[AnyRequirement, ...] = (
    Requirement(
        "INK",
        "BACKGROUND",
        AA_TEXT,
        "1.4.3",
        "the application title in the page header, which `SimulationView` places "
        "on the page surface",
    ),
    Requirement(
        "INK",
        "PANEL",
        AA_TEXT,
        "1.4.3",
        "every numeric readout and its unit (`MetricPanel` for the compartment "
        "grid, `ParameterSlider` for the four settings beside their sliders), "
        "each panel heading (`ParameterSlider` for a setting's name, `RunView` "
        "for the accounting and control-change panels it builds for its run, "
        "`SimulationView` for the chart's and the wash-in section's), and every "
        "legend label beside a swatch (`TraceLegend` for the concentration "
        "chart's three rows, `WashInLegend` for the wash-in plot's). Also the "
        "six compartment checkboxes that show and hide the chart's traces "
        "(`TraceLegend`), whose label is INK text while that trace is drawn and "
        "MUTED while it is hidden - `_on_toggled` is the one writer of that. "
        "The box is a user-interface component, so SC 1.4.11's 3:1 would "
        "suffice for it - the text minimum is met anyway, and is what the label "
        "needs. Deliberately not one of the six trace colours nor ACCENT: the "
        "legend row has already spent its colour budget on six compartments "
        "(.claude/rules/ui-color.md, judgment 3), so the control is drawn as "
        "furniture rather than competing with the swatch beside it (PL-CG7J). "
        "Also the title and the opening statement of the new-case confirmation "
        "(`NewCaseDialog`), whose surface is set to PANEL explicitly rather "
        "than left to the platform style, so that these three text colours "
        "stand on a background this table measures them against (PL-R3KB), and "
        "its outlined discard button - INK text inside a 1px INK border on "
        "PANEL, the border being a user-interface component that needs only SC "
        "1.4.11's 3:1 (PL-25KS). Also both dropdowns whose "
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
        "(`_status_text`, whose colour `refresh` writes for every run "
        "state), the 'Playback' caption beside the rate selector in that row "
        "(`build_transport_row`), and the interpretation line beside the "
        "readout heading (`_interpretation_text`, PL-2K1R). Also the border of "
        "the playback-rate dropdown drawn beside them "
        "(`_playback_rate_dropdown`), which is a user-interface component "
        "and so needs only SC 1.4.11's 3:1 - met with room to spare by the text "
        "minimum this pair already carries (PL-SN2C)",
    ),
    Requirement(
        "MUTED",
        "PANEL",
        AA_TEXT,
        "1.4.3",
        "the compartment name and the smaller clinical gloss under it on each "
        "readout, and the MAC multiple under the value (`MetricPanel`), the "
        "chart's axis description (`_time_axis_caption`; the wash-in chart's "
        "own went with the prose `PL-F9TQ` removed, having restated that "
        "chart's axis titles), the sub-headings and status lines the chart and "
        "its neighbours hold (`SimulationView` for the chart column's, "
        "`RunView` for the control-change panel's), the legend rows' captions "
        "and the label of a compartment whose trace is hidden (`TraceLegend`), "
        "and the agent-accounting detail lines (`_agent_accounting_detail_text`, "
        "`_agent_amounts_text`). The "
        "gloss is judged at the same 4.5:1 as the name above it: at 12px it "
        "is normal text by WCAG's definition, nowhere near the 18.66px the "
        "large-text exception starts at, and it is the same MUTED colour on "
        "the same PANEL surface, so it adds no pair to this table (PL-8M05). "
        "Also the line of the new-case confirmation saying what carries over "
        "into the new case (`NewCaseDialog`, PL-R3KB), the "
        "playback rate drawn under the simulated-time readout "
        "(`_playback_rate_text`), which shares the surface and the size of the "
        "MAC multiples beside it (PL-SN2C), and the border of the chart's "
        "time-base dropdown (`_time_base_dropdown`), a user-interface component "
        "needing only SC 1.4.11's 3:1. Also the gloss under a setting's name "
        "in the controls row (`ParameterSlider`, PL-71CF), which is the "
        "readout gloss one panel row up: the same colour on the same surface "
        "at the same size, so it too adds no pair.",
    ),
    Requirement(
        "ACCENT_TEXT",
        "BACKGROUND",
        AA_TEXT,
        "1.4.3",
        "the run-status word while running (`_status_text`, set by `refresh`)",
    ),
    Requirement(
        "ACCENT_TEXT",
        "PANEL",
        AA_TEXT,
        "1.4.3",
        "the agent-accounting status word when conservation holds "
        "(`_agent_accounting_status_text`, in the accounting panel `RunView` "
        "builds, written by `refresh`). Rendered at 20px bold, which is large text, "
        "so SC 1.4.3's 3:1 would suffice - the stricter bar is applied "
        "deliberately",
    ),
    Requirement(
        "ACCENT",
        "PANEL",
        AA_NON_TEXT,
        "1.4.11",
        "the active track of all four parameter sliders, which is how each "
        "control shows its current value (`_fresh_gas_flow_slider`, "
        "`_delivered_concentration_slider`, `_alveolar_ventilation_slider`, "
        "`_cardiac_output_slider`, each a `ParameterSlider` whose stylesheet "
        "paints the filled track in ACCENT on the PANEL surface the control "
        "sets)",
    ),
    Requirement(
        "WARNING",
        "BACKGROUND",
        AA_TEXT,
        "1.4.3",
        "the halted-run notice (`_notice_text`, a `NoticeLabel` written by "
        "`refresh`), the run-status word while stopped (`_status_text`), and "
        "the educational-use disclaimer, which `SimulationView` places at the "
        "foot of the page",
    ),
    Requirement(
        "WARNING",
        "PANEL",
        AA_TEXT,
        "1.4.3",
        "the agent-accounting status word when validation fails "
        "(`_agent_accounting_status_text`, in the accounting panel `RunView` "
        "builds), the notice naming a compartment trace that is above the top "
        "of the chart (`_off_scale_text`), and the line of the new-case "
        "confirmation stating what a switch would discard (`NewCaseDialog`, "
        "PL-R3KB)",
    ),
    Requirement(
        "PANEL",
        "PRIMARY",
        AA_TEXT,
        "1.4.3",
        "the label of the new-case confirmation's keep button, PANEL text on a "
        "PRIMARY fill (`NewCaseDialog`): the one filled button in the "
        "interface, filled so that the safe action reads as the default and "
        "filled-versus-outlined is a second channel beside its trailing "
        "position. The text is at the application default size, so the "
        "normal-text minimum applies; 6.02:1 when declared (PL-25KS)",
    ),
    Requirement(
        "sevoflurane.foreground",
        "sevoflurane.fill",
        AA_TEXT,
        "1.4.3",
        "the agent name over its ISO 5360 identification color, in all three "
        "places it is drawn: the header badge's subtitle (`_subtitle_text`), "
        "the selector while the run is stopped or paused (`_agent_dropdown`), "
        "and the static chip that stands in the selector's place while it is "
        "going (`_running_agent_display`, whose name and lock caption are "
        "`_running_agent_text` and `_running_agent_lock_text`). All three are "
        "written by `_apply_agent_color_scheme`. The chip is why this entry "
        "still describes what is on screen during a run: the selector used to "
        "be merely disabled while running, and Flet/Material painted a disabled "
        "label in the theme's disabled-content grey - a colour app/theme.py "
        "never declares, so this tool could not reach it and reported a "
        "passing ratio for a pair that had stopped being rendered. Nothing "
        "carrying agent identity is disabled now, which is what makes the "
        "measured pair and the rendered pair the same again (PL-61WW)",
    ),
    Requirement(
        "isoflurane.foreground",
        "isoflurane.fill",
        AA_TEXT,
        "1.4.3",
        "the agent name over its ISO 5360 identification color, in all three "
        "places it is drawn: the header badge's subtitle (`_subtitle_text`), "
        "the selector while the run is stopped or paused (`_agent_dropdown`), "
        "and the static chip that stands in the selector's place while it is "
        "going (`_running_agent_display`, whose name and lock caption are "
        "`_running_agent_text` and `_running_agent_lock_text`). All three are "
        "written by `_apply_agent_color_scheme`. The chip is why this entry "
        "still describes what is on screen during a run: the selector used to "
        "be merely disabled while running, and Flet/Material painted a disabled "
        "label in the theme's disabled-content grey - a colour app/theme.py "
        "never declares, so this tool could not reach it and reported a "
        "passing ratio for a pair that had stopped being rendered. Nothing "
        "carrying agent identity is disabled now, which is what makes the "
        "measured pair and the rendered pair the same again (PL-61WW)",
    ),
    Requirement(
        "desflurane.foreground",
        "desflurane.fill",
        AA_TEXT,
        "1.4.3",
        "the agent name over its ISO 5360 identification color, in all three "
        "places it is drawn: the header badge's subtitle (`_subtitle_text`), "
        "the selector while the run is stopped or paused (`_agent_dropdown`), "
        "and the static chip that stands in the selector's place while it is "
        "going (`_running_agent_display`, whose name and lock caption are "
        "`_running_agent_text` and `_running_agent_lock_text`). All three are "
        "written by `_apply_agent_color_scheme`. The chip is why this entry "
        "still describes what is on screen during a run: the selector used to "
        "be merely disabled while running, and Flet/Material painted a disabled "
        "label in the theme's disabled-content grey - a colour app/theme.py "
        "never declares, so this tool could not reach it and reported a "
        "passing ratio for a pair that had stopped being rendered. Nothing "
        "carrying agent identity is disabled now, which is what makes the "
        "measured pair and the rendered pair the same again (PL-61WW)",
    ),
    EitherRequirement(
        ("sevoflurane.fill", "sevoflurane.foreground"),
        "BACKGROUND",
        AA_NON_TEXT,
        "1.4.11",
        "the identification swatch in the header, read as a shape - by its "
        "fill or by its border, whichever carries the edge. "
        "`_apply_agent_color_scheme` outlines the badge 1px in the agent's own "
        "text colour and `_agent_header_badge` is the container both are set "
        "on, so either "
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
#: `ACCENT` was listed twice with the same measured value and two different
#: owners - the alveolar trace and the slider track, two on-screen elements
#: sharing one constant, which was itself the defect each item described.
#: `PL-GVXP` ended the sharing by giving the trace `ALVEOLAR_COLOR` of its own
#: and clearing it, so one entry remains and it is the slider track's.
KNOWN_SHORTFALLS: dict[tuple[str, str], str] = {("ACCENT", "PANEL"): "PL-W8DQ"}

#: The six chart traces, in the order `chart_frame.COMPARTMENT_TRACES` lists them.
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


def simulate_dichromacy(hex_color: str, model: str) -> str:
    """The color a `model` dichromat's reduced gamut renders this one as.

    Brettel 1997's projection, applied in linear sRGB with the composed
    matrices in `DICHROMACY_TRANSFORMS`. Which of the deficiency's two
    half-planes a stimulus projects onto is decided by the sign of its dot
    product with that deficiency's separation-plane normal - the paper's own
    construction, since the reduced surface is two planes meeting at the
    neutral axis rather than one.

    Args:
        hex_color: Six-digit sRGB hex, with or without a leading `#`.
        model: A key of `DICHROMACY_TRANSFORMS`.

    Returns:
        Six-digit sRGB hex, upper case and `#`-prefixed. Out-of-gamut results
        are clamped per channel, which is what the projection can produce for
        saturated inputs and what every published implementation does.

    Raises:
        ValueError: If `hex_color` is not six hex digits, or `model` is not
            one of the three simulated dichromacies.
    """
    if model not in DICHROMACY_TRANSFORMS:
        raise ValueError(f"expected one of {sorted(DICHROMACY_TRANSFORMS)}, got {model!r}")
    digits = hex_color.lstrip("#")
    if len(digits) != 6:
        raise ValueError(f"expected a six-digit sRGB hex color, got {hex_color!r}")
    channels = [int(digits[index : index + 2], 16) / 255 for index in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]

    plane_one, plane_two, normal = DICHROMACY_TRANSFORMS[model]
    matrix = (
        plane_one if sum(v * n for v, n in zip(linear, normal, strict=True)) >= 0 else plane_two
    )
    projected = [
        sum(matrix[3 * row + column] * linear[column] for column in range(3)) for row in range(3)
    ]

    encoded = []
    for value in projected:
        clamped = min(1.0, max(0.0, value))
        srgb = clamped * 12.92 if clamped <= 0.0031308 else 1.055 * clamped ** (1 / 2.4) - 0.055
        encoded.append(round(srgb * 255))
    return "#" + "".join(f"{channel:02X}" for channel in encoded)


def as_seen(hex_color: str, model: str) -> str:
    """This color as `model` renders it, where `"normal"` renders it unchanged.

    The one place the four vision models are treated uniformly, so a caller
    iterating `VISION_MODELS` needs no special case for the model that is not
    a simulation.

    Args:
        hex_color: Six-digit sRGB hex, with or without a leading `#`.
        model: A member of `VISION_MODELS`.

    Returns:
        Six-digit sRGB hex.

    Raises:
        ValueError: If `model` is not one of `VISION_MODELS`.
    """
    if model == "normal":
        return hex_color
    return simulate_dichromacy(hex_color, model)


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


def separation_ceiling_above_floor(count: int, floor: float) -> float:
    """The same bound, once every trace must also clear `floor` on the panel.

    The bound above spends the whole black-to-white axis; a trace cannot. Being
    legible against a white panel at `floor`:1 caps its luminance, which
    shortens the axis the `count` traces have to spread along and lowers the
    bound with it. At six traces and SC 1.4.11's 3:1 the ceiling falls from
    1.84 to about 1.48 - so the gap between what luminance can deliver and the
    3:1 that would make color sufficient is wider than the unconstrained figure
    suggests, not narrower.

    Args:
        count: How many traces share the axis.
        floor: The contrast each must hold against the white panel.

    Returns:
        The largest ratio every adjacent pair can share.

    Raises:
        ValueError: If `count` is below two, or `floor` is below 1 - a
            contrast ratio's own minimum, and below it the cap is not a
            luminance any color has.
    """
    if count < 2:
        raise ValueError("a separation ceiling needs at least two traces")
    if floor < 1.0:
        raise ValueError(f"a contrast floor cannot be below 1:1, got {floor}")
    # The lightest admissible trace, from the panel's own luminance of 1.0.
    brightest = 1.05 / floor - 0.05
    return float(((brightest + 0.05) / 0.05) ** (1.0 / (count - 1)))


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


def app_modules(root: Path) -> tuple[Path, ...]:
    """Every module under `APP`, relative to `root`, the theme first.

    The theme first because `_string_value` resolves a name against what has
    already been read, so `STRAY = INK` in another module is a color only once
    `INK` is known; the rest in path order, so a report reads the same way
    twice. Recursive, so a subpackage the port adds is read rather than
    skipped. Two named paths until PL-BXB2, which is how a color in a third
    module was measured by nothing.

    Raises:
        FileNotFoundError: The theme is not in the tree. Every color lives
            there (PL-2CS8), so a tree without it has nothing to measure and
            saying so beats reporting every requirement as missing.
    """
    modules = sorted(path.relative_to(root) for path in (root / APP).rglob("*.py"))
    if THEME not in modules:
        raise FileNotFoundError(
            f"{THEME.as_posix()} is not in the tree; every color is declared there "
            "(PL-2CS8), so there is nothing to measure without it"
        )
    return (THEME, *(module for module in modules if module != THEME))


def read_palette(root: Path) -> dict[str, str]:
    """Extract every named color from every module under `app/`.

    PL-2CS8 moved every color into `app/theme.py`, and
    `check_colors_live_in_the_theme` below is what holds them there. This still
    reads every module, deliberately: narrowing it to the theme would make a
    color added anywhere else invisible here, which is the exact failure that
    item existed to fix - `"#D9E2EC"` sat unmeasured at five view sites while
    the file it was in reported as checked. Enforce the convention, and keep
    measuring what the convention is meant to prevent.

    Read with `ast` rather than imported: the interface imports PySide6, which
    a standard-library-only tool running in a bare checkout does not have.

    Args:
        root: Repository root.

    Returns:
        Color name to six-digit sRGB hex. Agent entries are keyed
        `<agent>.fill` and `<agent>.foreground`.
    """
    palette: dict[str, str] = {}
    for relative in app_modules(root):
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
    """Every name any module under `app/` defines, for resolving a citation.

    Four kinds, because those are the four a description has cause to cite:
    module-level constants, classes, functions and methods, and the `self.X`
    attributes the view builds its controls into. Read with `ast` for the same
    reason the palette is - the interface imports PySide6.

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
    for relative in app_modules(root):
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


def check_colors_live_in_the_theme(root: Path) -> tuple[str, ...]:
    """Refuse a color declared in any module under `app/` other than the theme.

    PL-2CS8 consolidated every display token into `app/theme.py`; this is what
    keeps them there. Without it the convention is a habit, and the failure it
    would allow is the one that item was filed for: `"#D9E2EC"` sat at five
    sites in `app/simulation_view.py`, named nowhere, so the tool that reports
    on colors could not see it while the file it sat in reported as checked.

    Two forms are refused. A module-level constant resolving to a color, which
    `read_palette` deliberately still reads so that it is *measured* rather than
    lost - the error is then the difference between a convention and a
    guarantee. And a hex literal written inline, in a call or anywhere else,
    which has no name a requirement could cite and so could never be measured
    at all: the only correct treatment is to send it to the theme, where it
    gains one. Every module rather than the view alone since PL-BXB2.

    Returns:
        One message per offending declaration, empty when only the theme
        declares a color.
    """
    theme = read_palette(root)
    offenders: list[str] = []
    for relative in app_modules(root):
        if relative == THEME:
            continue
        path = root / relative
        module = relative.as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        # Values already reported as a named constant, so the literal walk
        # below does not report the same line a second time.
        reported: set[int] = set()
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
                resolved = _string_value(value, theme)
                if resolved is not None and resolved.startswith("#"):
                    reported.add(id(value))
                    offenders.append(
                        f"  {target.id} is declared in {module}; every color belongs in "
                        f"{THEME.as_posix()} (PL-2CS8). Move the constant, and its comment "
                        "with it."
                    )
        for node in ast.walk(tree):
            if id(node) in reported:
                continue
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and HEX_COLOR_RE.match(node.value)
            ):
                offenders.append(
                    f"  {node.value} is written inline at {module}:{node.lineno}; a literal "
                    "has no name a requirement can cite, so it can never be measured. "
                    f"Declare it in {THEME.as_posix()} and cite the constant (PL-2CS8, "
                    "PL-BXB2)."
                )
    return tuple(offenders)


def check_disabled_states_are_the_style_s(root: Path) -> tuple[str, ...]:
    """Refuse author-controlled disabled styling, which this tool does not measure.

    The module docstring records the decision that disabled states are out of
    scope, and the whole of that decision rests on one fact: the colours belong
    to `QPalette`'s `Disabled` group, which the platform style fills in and no
    module here chooses. A `:disabled` rule in a stylesheet, or a `setPalette`
    call, takes that choice back - and at that moment the colour is a value
    this project picked, is measurable, and is covered by nothing.

    So this is the guard that stops the scope note becoming a false green. It
    is a hard error rather than an advisory because the rule is exact: either a
    module under `app/` writes one of these two forms or it does not. The fix
    is never to delete the check - it is to declare the colour in
    `app/theme.py` and give it a requirement, which is what the scope note says
    is owed the moment the premise changes (PL-NGF7).

    Returns:
        One message per offending site, empty while every disabled colour is
        still the style's.
    """
    offenders: list[str] = []
    for relative in app_modules(root):
        path = root / relative
        module = relative.as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if ":disabled" in node.value:
                    offenders.append(
                        f"  {module}:{node.lineno}: a ':disabled' rule makes a disabled "
                        "colour author-controlled, so it is measurable and owes a "
                        "constant in app/theme.py and a requirement here (PL-NGF7)"
                    )
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == "setPalette":
                    offenders.append(
                        f"  {module}:{node.lineno}: setPalette takes the disabled colours "
                        "from the platform style, so they are measurable and owe a "
                        "constant in app/theme.py and a requirement here (PL-NGF7)"
                    )
    return tuple(offenders)


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
                    f"  {pair}: cites `{name}`, which no module under {APP.as_posix()}/ "
                    "defines. A renamed symbol leaves the requirement pointing at "
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
    #: Colors declared anywhere under `app/` other than the theme (PL-2CS8).
    misplaced_colors: tuple[str, ...]
    #: Sites taking the disabled colours back from the platform style, which
    #: ends this tool's scope decision about them (PL-NGF7).
    author_styled_disabled: tuple[str, ...]
    #: `(trace, trace, vision model, ratio)`, every pair in every model.
    trace_pairs: tuple[tuple[str, str, str, float], ...]
    #: `(trace, vision model, ratio)` for each trace under `TRACE_FLOOR`.
    below_trace_floor: tuple[tuple[str, str, float], ...]
    #: How many modules under `APP` the palette and the symbols came from, so
    #: the report says what it read rather than leaving that to be assumed.
    modules_read: int

    @property
    def errors(self) -> bool:
        return bool(
            self.missing
            or self.unexpected
            or self.repaired
            or self.citations
            or self.misplaced_colors
            or self.author_styled_disabled
            or self.below_trace_floor
        )


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
    drawn = tuple(name for name in TRACES if name in palette)
    trace_pairs = tuple(
        (
            first,
            second,
            model,
            contrast_ratio(as_seen(palette[first], model), as_seen(palette[second], model)),
        )
        for model in VISION_MODELS
        for first, second in combinations(drawn, 2)
    )
    # The floor is judged at the printed precision, exactly as a declared
    # requirement is: a verdict disagreeing with the number beside it is the
    # defect `DISPLAY_DECIMALS` exists to prevent, and it would be no less one
    # here.
    below_trace_floor = tuple(
        (name, model, ratio)
        for model in VISION_MODELS
        for name in drawn
        if (ratio := contrast_ratio(as_seen(palette[name], model), palette["PANEL"]))
        and round(ratio, DISPLAY_DECIMALS) < TRACE_FLOOR
    )
    return Report(
        results=tuple(results),
        missing=tuple(sorted(set(missing))),
        unexpected=unexpected,
        repaired=repaired,
        citations=check_citations(root),
        misplaced_colors=check_colors_live_in_the_theme(root),
        author_styled_disabled=check_disabled_states_are_the_style_s(root),
        trace_pairs=trace_pairs,
        below_trace_floor=below_trace_floor,
        modules_read=len(app_modules(root)),
    )


def format_report(report: Report, *, matrix: bool) -> str:
    """Render a report the way `bin/docket check` renders one: verdict first."""
    met = sum(1 for result in report.results if result.meets)
    error_count = (
        len(report.unexpected)
        + len(report.missing)
        + len(report.repaired)
        + len(report.citations)
        + len(report.misplaced_colors)
        + len(report.author_styled_disabled)
    )
    lines = [
        f"contrast: {met} of {len(report.results)} declared requirements meet WCAG 2.2 AA, "
        f"{report.modules_read} modules read under {APP.as_posix()}/, "
        f"{len(KNOWN_SHORTFALLS)} known shortfalls, "
        f"{error_count} errors"
    ]

    if report.misplaced_colors:
        lines.append("")
        lines.append("Colors declared outside the theme:")
        lines.extend(report.misplaced_colors)

    if report.author_styled_disabled:
        lines.append("")
        lines.append("Disabled colours taken back from the platform style:")
        lines.extend(report.author_styled_disabled)
        lines.append(
            "  This tool treats disabled states as out of scope because the style "
            "chooses them. These sites choose them here, so declare each colour in "
            "app/theme.py and add a requirement - do not delete the check."
        )

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

    if report.below_trace_floor:
        lines.append("")
        lines.append(f"Chart traces below {TRACE_FLOOR}:1 against PANEL:")
        for name, model, ratio in report.below_trace_floor:
            lines.append(f"  {name:<20} {model:<13} {ratio:.2f}")
        lines.append(
            "  Every trace clears this as displayed and as simulated for each "
            "dichromacy - see TRACE_FLOOR for why all four."
        )

    if matrix and report.trace_pairs:
        lines.append("")
        lines.append(
            f"Chart-trace pairwise separation (not decided here; PL-GVXP sets the bar). "
            f"No arrangement of six traces gives every pair more than "
            f"{separation_ceiling(len(TRACES)):.2f} on luminance alone, and no more than "
            f"{separation_ceiling_above_floor(len(TRACES), TRACE_FLOOR):.2f} once each "
            f"also clears {TRACE_FLOOR}:1 on the panel. Both are under SC 1.4.11's 3:1, "
            f"so a non-color channel is required, not optional."
        )
        for first, second, model, ratio in sorted(report.trace_pairs, key=lambda pair: pair[3]):
            lines.append(f"  {first:<20} {second:<20} {model:<13} {ratio:.2f}")

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
