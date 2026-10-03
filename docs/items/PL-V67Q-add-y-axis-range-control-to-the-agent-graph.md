---
id: PL-V67Q
title: Add y-axis range control to the agent graph: optional auto-scale, and a settable MAC / volume-percent scale
priority: P2
effort: M
status: needs-decision
classes: feature, ux
feature: chart-readout
touches: src/anesthesia_sim/app
added: 2026-09-08
---

**Problem.** Add y-axis range control to the agent graph: optional auto-scale, and a settable MAC / volume-percent scale

Raised by the project owner, 2026-09-08, as a passing want rather than a
scoped request: the agent graph's y-axis should either auto-scale to the
data or be set explicitly, for MAC and for volume-percent values.

**Two mechanisms, and they are not alternatives.** A plotting surface that
offers "auto" normally also offers "fixed", because each fails where the
other works: a fixed axis wastes most of its height on a low-dose case, and
an auto axis makes a 0.05 % drift fill the plot. The item is one feature
with a mode, not a choice between two features.

**Open questions for the design round, not answered here.**

- Do MAC and volume-percent share one axis, or does each get its own range?
  They are different units, and a single control governing both would have
  to say which one it is setting.
- What are the fixed defaults, and are they per-agent? Sevoflurane at 2 %
  and desflurane at 6 % are the same MAC-ish depth on very different
  volume-percent scales, so one fixed volume-percent range across agents is
  either too tall for one or clips the other.
- Does the range persist across a run, or reset with it?

**Auto-scale is the half with a safety-critical edge, and it is why this is
not a pure convenience item.** An axis that rescales itself changes what the
same physiology looks like: a trace that is visually flat under a 0-3 MAC
axis becomes a dramatic climb the moment the axis shrinks to the data, and
nothing about the patient changed. Two consequences follow, both to be
settled when the item is worked rather than assumed now — whether auto is
off by default and visibly marked when on, and whether the axis limits are
readable on the plot itself rather than only in a settings panel. This sits
squarely under `CLAUDE.md`'s clinical-output standard ("a visually
attractive but misleading graph is a defect") and under
`.claude/rules/expert-review.md`'s data-visualization domain. The design
round owes a look at the actual human-factors literature on autoscaling
trend displays; nothing here has consulted it.
**Why it matters.** An axis that rescales itself changes what the same
physiology looks like: a trace that reads as flat against a 0-3 MAC axis becomes
a dramatic climb the moment the axis shrinks to the data, with nothing about the
patient changed. `CLAUDE.md`'s clinical-output standard names that class of
defect directly - "a visually attractive but misleading graph is a defect" - and
requires that presentation not imply more certainty than the model supports. So
the mode this introduces is one a reader can be inside without knowing, which is
the hidden-mode failure `.claude/rules/expert-review.md` lists under human
factors, and it is why this is not filed as a convenience control.

**Done when.** The open questions above are answered in a design round and items
are written from it. That round owes at least: whether MAC and volume-percent
take one axis or two; whether fixed defaults are per-agent; whether the range
survives a run; whether auto-scale is off by default and visibly marked when on;
and whether the axis limits are readable on the plot itself rather than only in
a settings panel. It also owes a look at the human-factors literature on
autoscaling trend displays before any default is chosen - nothing here has
consulted it, and `.claude/rules/expert-review.md` requires the source be
consulted before the recommendation is formed rather than after.

**Not startable as filed**, which is what `status: needs-decision` says here.
Half the decision is the project owner's: what the graph should offer a reader
is direction rather than implementation.

**Decision needed.** The design round's five open questions, of which two are the project owner's: what the y-axis control offers a reader, and whether auto-scale may be on by default.

## Design round 2026-10-03: the five questions, answered against the tree and the literature

**What the chart does today** (`src/anesthesia_sim/app/qt_chart.py:644-656`, `app/formatting.py:200-220`, `PL-CC23`). One vertical axis, 0 to 3 MAC, chosen in MAC so it is the same ruler for every agent: the left labels read volume percent, the right labels read MAC multiples, both against the same range, ruled every half MAC. Three is desflurane's dial maximum (18 % at a 6 % MAC), so the most limited agent has no dead band and 1 MAC sits at a third of the height. It is fixed for the whole session, not only within a run, so consecutive runs are comparable, and a trace that leaves the top is reported by `OFF_SCALE_NOTICE_TEMPLATE` (in MAC only, `dashboard_frame.py:1923-1925`) rather than left to read as a plateau. `docs/MODEL.md` § "Why the axis is fixed rather than fitted" settled the same question for the wash-in plot. The time base is the precedent for a reader-chosen chart mode: it is displayed in words beside the plot because "a span nobody can see is one a reader supplies their own assumption for" (`docs/MODEL.md:6746-6758`). `PL-CC23` closed 2026-09-04 with "growth beyond it was not built" (project owner, 2026-09-04 - dated before the kind was recorded, so reopened here on ordinary evidence, which this item is).

**What the literature says about an axis that follows the data.** Consulted before the recommendation was formed, as `.claude/rules/expert-review.md` requires; the quotations are from the abstracts read on 2026-10-03, not from memory.

- Correll M, Bertini E, Franconeri S. *Truncating the Y-Axis: Threat or Menace?* CHI 2020, https://doi.org/10.1145/3313831.3376222 (abstract read at https://arxiv.org/abs/1907.02035). Crowd-sourced experiments across chart types: "the subjective impact of axis truncation is persistent across visualization designs, even for designs with explicit visual cues that indicate truncation has taken place", and the authors "suggest that designers consider the scale of the meaningful effect sizes and variation they intend to communicate, regardless of the visual encoding." An auto-scaled axis is truncation that moves, and this says marking it does not undo the bias - which answers the brief's "visibly marked when on" directly: marking is necessary and not sufficient.
- Witt JK. *Graph Construction: An Empirical Investigation on Setting the Range of the Y-Axis.* Meta-Psychology 2019;3, https://doi.org/10.15626/MP.2018.895 (abstract via Crossref). "A range set just beyond the data will bias readers to see all effects as big. Conversely, a range set to the full range of options will bias readers to see all effects as small"; sensitivity and bias were both best at a range of about 1.5 standard deviations of the quantity - a range chosen from what the quantity means, not from the data on screen.
- Huber C, Huber J. *Scale matters: risk perception, return expectations, and investment propensity under different scalings.* Exp Econ 2018;22(1):76-100, https://doi.org/10.1007/s10683-018-09598-4 (PubMed). "A narrower scale of the vertical axis leads to significantly higher perceived riskiness of an asset even if the underlying volatility is the same", and adapting the scale "makes it easier to recognize yearly return variations [within] a single security, but at the same time makes it harder to identify differences [between] dissimilar securities" - the comparison cost, which is this chart's two-run case.
- Görges M, Staggers N. *Evaluations of physiological monitoring displays: a systematic review.* J Clin Monit Comput 2008;22(1):45-66, https://doi.org/10.1007/s10877-007-9106-8 (PubMed); Drews FA, Westenskow DR. *The right picture is worth a thousand numbers: data displays in anesthesia.* Hum Factors 2006;48(1):59-71, https://doi.org/10.1518/001872006776412270 (PubMed). The clinical display literature evaluates integrated graphical displays against numerical ones (31 studies, mostly with anesthesiologists) and says of itself that "we know little about which graphical displays are optimal and why". Neither review, nor two PubMed searches on trend-display scaling (59 and 32 hits, read by title on 2026-10-03), tests axis autoscaling in a clinical trend display. So the evidence on autoscaling is the general graph-perception evidence above, and it points one way.

**The five questions.**

1. *One axis or two for MAC and volume percent?* **One, as now**: one range, chosen in MAC, labelled in both units. Two ranges would let the two labels disagree about where a point sits. The single control then says plainly which unit it sets - MAC, the per-agent-invariant one - with the percent equivalent for the running agent shown beside it.
2. *Fixed defaults, and per-agent?* **The default stays 0-3 MAC for every agent**, on `PL-CC23`'s reasoning, and "per-agent" is answered by the unit: a ceiling fixed in MAC is already per-agent in percent (6 % sevoflurane, 3.6 % isoflurane, 18 % desflurane at 3 MAC, from the stored `mac_percent` values).
3. *Does the range survive a run?* **Yes.** A chosen range is a reader setting that holds until the reader changes it, across runs and across the two runs of a comparison, which is what keeps consecutive runs comparable. It resets with the application until the chart's modes get persistence, and then rides with the time base, whatever that gets.
4. *Auto-scale off by default and marked when on?* **Not built.** A continuous auto-scale is the one mechanism every source above argues against and the one `PL-CC23` refused for this chart: it redraws the same physiology at a different height mid-lesson, the bias survives an explicit marker, and it breaks the two-run comparison. The want behind it - a low-dose case using a tenth of the plot - is met by a reader-chosen fixed range, below.
5. *Are the limits readable on the plot?* **Yes, in three places**: the axis labels (the ceiling is the top tick in both units, as now); a statement beside the plot in words, as the time base is stated ("0-3 MAC, the default" or "0-1.5 MAC, chosen"); and the off-scale notice, which names the top and should name it in both units.

**Recommendation: build a reader-chosen fixed range from a short ladder of MAC ceilings, with the default unchanged, no continuous auto-scale, and the chosen range displayed as a mode.** The ladder is three ceilings: 1.5 MAC (maintenance detail, 1 MAC at two thirds of the height), 3 MAC (the default, desflurane's dial maximum) and 4.5 MAC (above every shipped agent's dial maximum - sevoflurane 8 % is 4.0 MAC and isoflurane 5 % is 4.17 MAC on the stored values - so nothing is ever off scale). A ladder rather than a typed range because a preset cannot be set to a nonsense span and keeps the ruling ladder `MAC_AXIS_STEP_LADDER_MAC` meaningful (1.5 rules every quarter MAC, 4.5 every half); the exact rungs are the build thread's to measure, with the ruling and the MAC-awake band checked at each. One optional convenience, if the owner wants the "auto" affordance at all: a *fit to run* action that picks the lowest rung above the drawn maximum, once, on request, after which the axis stays fixed - the tighter view without an axis that moves on its own. Where the control lives follows the time-base selector's home; this is a chart control, not an Area or Workspace behaviour, so no Blender reading applies.

**If the owner wants continuous auto-scale anyway**, the terms the evidence allows: off by default; on only while one run is drawn, and off again the moment a branch is taken; the plot marked in words beside the axis ("axis follows the data") and the ceiling labelled in both units; never while two runs share the axis. Recorded so the build thread does not re-derive them, and marked as the weaker route.

**Items to write from this round once answered**, under `feature: chart-readout`: the range control, its ladder and its mode display (one `M`); the `docs/MODEL.md` paragraph recording the ladder, the mode display and the refusal of continuous auto-scale beside § "Why the axis is fixed rather than fitted" (rides the same item); and the off-scale notice carrying both units (one `S`).
