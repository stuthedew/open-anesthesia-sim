---
id: PL-HKTB
title: The chart gridline and divider grey measures 1.31:1 on the panel and carries no contrast requirement; decide whether it should be darkened or recorded as exempt furniture
priority: P2
effort: S
status: needs-decision
classes: ux
feature: presentation-safety
touches: tools/contrast_check.py, src/anesthesia_sim/app/theme.py
added: 2026-09-08
---

**Problem.** The chart gridline and divider grey measures 1.31:1 on the panel and carries no contrast requirement; decide whether it should be darkened or recorded as exempt furniture

**Why it matters.** Every other colour pair in this interface carries a declared
contrast requirement that `tools/contrast_check.py` enforces, and this one
carries none - so the question of whether it is legible has never been asked,
rather than having been asked and answered "exempt". WCAG 2.2 does not require
a minimum for purely decorative furniture, and a chart gridline plausibly is
that; a divider separating two regions of content plausibly is not, since it
carries structure a reader uses. At 1.31:1 it is far below the 3:1 that would
make it a non-text contrast pass, so if it is ever load-bearing it is failing.

The value of settling it is that the answer gets written down either way. A
recorded exemption is as good an outcome as a darker grey, and better than a
colour nobody has a requirement for - which is how this one has survived.

**Decision needed.** Whether the gridline and divider grey is darkened to meet
3:1 as a non-text contrast requirement, or recorded in `tools/contrast_check.py`
as exempt furniture with the reason. Note the two may separate: a gridline is a
stronger candidate for exemption than a divider, and there is no need to give
them one answer.

**Sequencing.** `PL-L9RD` re-expresses `app/theme.py` for Qt and makes the
interface pass's visual decisions once. This is one of those decisions, so it
lands there unless it is answered sooner - deciding it twice is the thing that
item exists to prevent.

**Done when.** The grey either meets a declared requirement in
`tools/contrast_check.py` or is recorded there as exempt with the reasoning, and
`make check` reports it under whichever it is.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation). Still real, and it has lost the
pass that was going to pick it up.** The measurement reproduces: `GRIDLINE` is
still `#D9E2EC` at `src/anesthesia_sim/app/theme.py:519`, serving both the chart
gridlines (`qt_chart.py:316`, `:346`) and the panel divider
(`simulation_view.py:365`), and `contrast_ratio("#D9E2EC", "#FFFFFF")` returns
1.3092 - 1.31:1 as recorded, and 1.22:1 against `BACKGROUND`.
`tools/contrast_check.py` still names it nowhere: no `GRIDLINE` requirement,
`KNOWN_SHORTFALLS` empty at `:724`, and the report line reads 24 of 24.

Two corrections. The question has in fact been *argued* once -
`theme.py:505-513` carries "**It carries no `REQUIREMENTS` entry, and that is a
judgment rather than an omission.** Measured 1.31:1 on `PANEL` …" since
`PL-2CS8` on 2026-09-08 - so the item is about recording that judgment where
`make check` reports it, not about asking an unasked question; `theme.py:518`
says "`PL-HKTB` carries it" in the same breath. And the sequencing this brief
rests on has lapsed: `PL-L9RD` closed 2026-09-16 without redeciding the
visuals, pushing that pass to `v0.7.x`, so no scheduled work will absorb this
decision and it now has to be taken on its own.

## Design round 2026-09-27: recommendations

Recommendations, not decisions: the thread that records the project owner's
answer marks each `(project owner, DATE, ratified)` or replaces it. Measured
against the tree at `aeb00392` on 2026-09-27; every ratio below is
`tools/contrast_check.py`'s own arithmetic.

**The constant serves four things, not the two the title names.** `GRIDLINE`
is drawn as the chart's rulings at the labelled ticks (`_GridLines`, under the
traces at `_Z_GRIDLINE`) and the three axis lines (`_plot`); as the rule
between sections of the chart column (`_section_divider`, three call sites:
above the wash-in section, above the bookmarks panel, above the fork panel);
and as the slider's unfilled groove (`_slider_stylesheet`). A record that
covers the two named leaves the other two where they were, so the record has
to name all four - and it is one constant, so the four share the colour
whatever is decided.

**Q1. Is the ruling "required to understand the content", so that SC 1.4.11's
3:1 binds it?** The judgment `theme.py` carries says WCAG's line-graph example
"treats the graduated lines as furniture the traces need not contrast
against". Read at source on 2026-09-27 (w3c/wcag,
`understanding/21/non-text-contrast.html`, via raw.githubusercontent.com;
www.w3.org was not probed), the example says the opposite about the rulings
themselves: *"To perceive the values of each line along the chart you need to
discern the grey lines marking the graduated 100 value increments. The
graphical objects are the lines in the graph, including the background lines
for the values, and the colored lines with shapes. The lines should have 3:1
contrast against their background, but as there is little overlap with other
lines they do not need to contrast with each other or the graduated lines."*
The example counts gridlines as graphical objects and asks 3:1 of them
against the background; the clause the comment leans on is about traces
against gridlines, a different pair. `docs/MODEL.md` § "Color contrast" quotes
the same sentence for the pairwise argument and reads it correctly. The
`theme.py` comment does not, and the build rewrites it whichever way this is
decided - a misquoted standard in a safety file is a defect on its own.

What the criterion does exempt is stated three paragraphs on, under "Required
for understanding": the requirement does not apply when *"a graphic with text
embedded or overlaid conveys the same information, such as labels and values
on a chart"* or *"the information is available in another form"*. This chart
has both and the example's chart had neither: every ruling stands at a tick
the axis labels in `MUTED` at 5.00:1 (`PL-Q4VH` made the ruling and the
labelling one scale), the seven readouts state every compartment's current
value as text, and the hover states the exact value at any drawn point,
running or paused (`PL-YVHK`). WCAG's own test for an object under 3:1 -
*"assume that area is invisible, is the graphical object still
understandable?"* - is passed: with the rulings gone the chart is six labelled
traces against two labelled axes, which is where a reader takes a value from;
the rulings only speed the carry across.

**Recommendation: record the ruling as exempt on that ground, and do not
darken it.** Darkening is refused on the chart's own hierarchy rather than on
the criterion. The lightest trace, `MUSCLE_COLOR`, stands at 3.43:1 on `PANEL`
and `FAT_COLOR` is a slate grey at 4.76:1, so a ruling at 3:1 would be 87% as
dark as the lightest data line and a hue step from the fat trace: furniture
weighing as much as data, and the ordering the chart rests on - `GRIDLINE`
1.31:1 under the `MUTED` reference lines at 5.00:1 under traces at 3.43-6.02:1,
with widths 1 / 1.5 / 2-3 px carrying the same order - would collapse at its
bottom rung. 1.31:1 is where charting practice puts a ruling deliberately, read
at source the same day: ggplot2's `theme_bw` rules its panel at
`col_mix(ink, paper, 0.92)`, grey92, 1.19:1 on white, and `theme_light` at
0.871, 1.35:1 (`R/theme-defaults.R`); Matplotlib's `grid.color` default is
`#b0b0b0`, 2.17:1 (`lib/matplotlib/mpl-data/matplotlibrc`), the darkest of
the three and still under 3:1. *Alternative:* a grey at 3:1 (`#7F8C99` reaches
3.43:1 on `PANEL` and 3.19:1 on `BACKGROUND`), refused above. A second
alternative - darken a little without claiming 3:1 - is refused because it is
a change with no bar behind it, which is the state this item exists to end.

**Q2. The divider.** Each of the three rules sits directly above a heading or
a titled panel (`WASH_IN_HEADING` in bold `INK`; the bookmarks and fork panels
carry their own titles), so the boundary it marks is already carried by text,
and SC 1.4.11's own words for a boundary apply: *"a border or other
indication of the overall boundary ... is not required"* where visible content
identifies the thing. **Recommendation: exempt, in the same table, with its
own reason** - it is not the gridline's reason, and the brief was right that
the two may separate.

**Q3. The two uses the title omits.** The axis lines are the plot's frame; the
tick labels carry the scale, so the ruling's ground covers them. The groove is
the boundary of the slider's hit area; the handle and the `ACCENT` filled
track (3.21:1, measured) identify the control and its state, which is the
boundary case the criterion excuses in the sentence quoted under Q2.
**Recommendation: exempt, each named with its own reason** rather than folded
into the gridline's.

**Q4. Where the record lives, so `make check` reports it.** **Recommendation:
an `EXEMPT` table in `tools/contrast_check.py` beside `KNOWN_SHORTFALLS`**,
keyed by constant name, each entry naming the surface it is drawn on, the
criterion's ground in a few words and the drawing symbols in backticks
(resolved by `check_citations` exactly as a `why` is). The report line gains
"N exempt", and two errors keep the table honest: an exempt constant absent
from the palette, and an exempt constant that is also a `REQUIREMENTS`
foreground on the same surface, since a colour cannot be required and exempt
at once. Not a `KNOWN_SHORTFALLS` entry: `.claude/rules/ui-color.md` forbids
that list being used to make a colour go green, and a shortfall is a pair that
*should* meet a minimum and does not, which is the opposite claim. Alongside:
`docs/MODEL.md` § "Color contrast, and the standard this interface is held to"
lists the exemption among its deliberate decisions, beside the deferred
criteria, and the `theme.py` comment quotes the example as it reads. *Cheaper
alternative:* the prose record alone, in `theme.py` and `docs/MODEL.md`, with
the report line unchanged - honest but invisible to `make check`, which the
brief's done-when refuses; it is the fallback only if the build thread finds
`bin/docket generators` naming a live head, since the table is a new field in
a check and `CLAUDE.md`'s pause would then hold it (no head was live on
2026-09-27).

**For the build.** Add `docs/MODEL.md` to `touches`. Done-when as written,
plus: `theme.py`'s comment no longer says the example treats graduated lines
as furniture, and the table names all four uses.
