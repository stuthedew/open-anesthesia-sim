---
id: PL-JG82
title: Compare mode leaves the concentration chart about 200 px on the 1366 by 700 laptop reference, 159 px under PL-84QX's 360 px minimum, after PL-F2YS paired the readouts
priority: P1
effort: S
status: done
classes: safety
feature: interface-areas
touches: src/anesthesia_sim/app/, ROADMAP.md, docs/MODEL.md
added: 2026-10-18
closed: 2026-10-18
pr: 1604
payoff: compare mode on the commonest laptop shows the chart at a size the owner chose, rather than a refusal or a scroll nobody decided
verify: grep -q 'Compare mode accepts that' ROADMAP.md
---

**Problem.** With two runs compared, the unconditional region leaves the
concentration chart about 200 px on the 1366 by 700 laptop reference. `PL-84QX`
(project owner, 2026-10-11, ratified) set 360 px as the chart's minimum there
for one run and handed compare mode on, and `PL-F2YS` measured it after pairing
the readouts. Measured on 2026-10-18 on the offscreen font, at `PL-F2YS`'s
branch, with `SimulationView` shown at 1366 by 700:

| Consumer, 1366 by 700 | One run (px) | Two runs (px) |
| --- | ---: | ---: |
| page padding, top and bottom | 32 | 32 |
| unconditional region (its size hint) | 175 | 366 |
| spacing under the region | 12 | 12 |
| disclaimer line and the spacing above it | 27 | 27 |
| furniture above the first Area (`PL-84QX`: tab strip, header, handle) | 62 | 62 |
| **left for the concentration chart** | **392** | **201** |

One run clears 360 px with 32 px to spare. Two runs fall 159 px short.

Where the 191 px a second run adds go, from the same measurement:

- **Transport rows, 29 px to 96 px.** Each run has its own row, and in compare
  mode each carries its run name and a lock sentence ("Locked while
  comparing"), so at a 1074 px column each wraps onto a second line (48 px).
- **Readout block, 122 px to 218 px.** The paired panels are 176 px tall
  against one run's 103 px, because each panel now carries the second run's
  value, its second unit and both run names. The second run's heading line
  (its substance, delivered concentration and 1 MAC) adds 15 px and spacing.
- **Spacing between the added rows** makes up the rest.

Every one of those lines carries a value `docs/MODEL.md` § "Minimum displayed
outputs" requires for each run, so none can simply be removed.

**Why it matters.** v0.6.0 removes the page scroll: an Area that cannot be
given its View's minimum shows that it is too small rather than scrolling
(`PL-K285`). So on the commonest laptop a learner comparing two runs would see
a refusal where the chart belongs, unless the chart's minimum, the region, or
the reference changes. Compare mode is what branching exists to teach.

**Decision needed.** What compare mode does on the 1366 by 700 reference.

- **Recommendation: accept a shorter chart in compare mode only, then win
  back what layout can.** Keep 360 px as the one-run rule. In compare mode the
  chart takes what the reference leaves, about 200 px today. A build item then
  folds each run's transport row and readout heading into one line in compare
  mode, which by the rows above is worth roughly 70 to 80 px (inferred, not
  measured), so about 280 px. Why: every remaining line is a required value;
  a refused chart is the worst of the outcomes for the reading compare mode
  exists for; and scrolling is what v0.6.0 removes.
- *Keep 360 px and scroll.* Compare mode keeps the chart at 360 px and the
  page scrolls on a laptop. That reverses v0.6.0's removal of the page scroll
  for this one mode, and the region scrolls out of view as it does today
  (`docs/MODEL.md` § "Displayed precision", `PL-562Z`).
- *Keep 360 px and refuse.* The chart's Area shows its too-small state in
  compare mode until the window is about 860 px tall or an Area is closed.

The chart's legibility at 200 to 280 px with two runs' traces has not been
measured. `PL-84QX` refused lowering the minimum for one run on exactly that
ground, so the recommendation is limited to compare mode.

**Done when.** The owner's answer is recorded here with its kind and date,
`ROADMAP.md` Required scope entry 20's budget sentence says what compare mode
does on the reference, and any build item the answer calls for is filed.

## Answered 2026-10-18

**Accept a shorter chart in compare mode, then compact** (project owner,
2026-10-18, ratified, over keeping 360 px and scrolling the page and over
keeping 360 px and refusing the chart's Area), given by tapping "Accept,
compact" on the thread's decision card. One run keeps the 360 px minimum on the
1366 by 700 reference. In compare mode the chart takes what that reference
leaves, about 201 px at `PL-F2YS`. `PL-QLZ5` folds each run's transport row and
readout heading into one line in compare mode, to win back what layout can.
`ROADMAP.md` Required scope entry 20 records the answer, and this item closes
on it.
