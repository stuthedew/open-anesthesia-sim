---
id: PL-CBYS
title: The page still scrolls at every common screen size, though PL-JG82's brief says v0.6.0 removes the page scroll: the Areas and the marks and branch section sit in one scrolling page, which measured offscreen on 2026-11-11 scrolls 414 px (Default) and 832 px (Induction) at 1366 by 768, and 102 px and 520 px at 1920 by 1080, so the Induction Workspace's wash-in chart opens below the fold; decide whether the Areas fill exactly the space between the unconditional region and the disclaimer, as a Blender window's Areas fill the window
priority: P2
effort: M
status: ready
classes: feature, ux
feature: window-is-the-frame
touches: src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/views.py, docs/MODEL.md
deferred-from: v0.7.0 - the gate's frozen list does not name it, and it is built after PL-9YPR's pull request merges
added: 2026-11-11
payoff: every shipped Workspace fits the window on a laptop, so the Induction wash-in chart opens on screen and not below the fold
verify: grep -q 'def test_no_shipped_workspace_scrolls_the_page' tests/integration/test_simulation_view.py
---

**Problem.** The page still scrolls at every common screen size, though PL-JG82's brief says v0.6.0 removes the page scroll: the Areas and the marks and branch section sit in one scrolling page, which measured offscreen on 2026-11-11 scrolls 414 px (Default) and 832 px (Induction) at 1366 by 768, and 102 px and 520 px at 1920 by 1080, so the Induction Workspace's wash-in chart opens below the fold; decide whether the Areas fill exactly the space between the unconditional region and the disclaimer, as a Blender window's Areas fill the window

**Measured, offscreen font, 2026-11-11** (`main.open_dashboard`, one run at
5 minutes). "Room" is the height between the unconditional region and the
disclaimer. "Scroll" is the page scroll bar's range.

| Window | Workspace | Room | Areas drawn | Areas' minimum | Scroll |
| --- | --- | --- | --- | --- | --- |
| 1366 by 768 | Default | 515 px | 665 px | 591 px | 414 px |
| 1366 by 768 | Induction | 515 px | 1083 px | 999 px | 832 px |
| 1920 by 1080 | Default | 827 px | 665 px | 591 px | 102 px |
| 1920 by 1080 | Induction | 827 px | 1083 px | 999 px | 520 px |
| 2560 by 1440 | Default | 1187 px | 923 px | 591 px | 0 px |
| 2560 by 1440 | Induction | 1187 px | 1083 px | 999 px | 160 px |

Maintenance measured the same as Default at each size. No Area showed its
too-small notice at any size, because the page grows instead (`PL-K285` Q2:
"the dashboard's page is a `QScrollArea`, so it grows to that and scrolls").

**Why it is a departure from Blender.** In Blender the window's rectangle is
the layout: the Areas divide it exactly, and nothing scrolls at the window
level. Here the Areas' minimum heights add up to more than the window, the page
grows to hold them, and the marks and branch section (`PL-9YPR`) adds its
height under them. A Workspace is then a page a learner scrolls, and a border
drag changes the page's length as well as the Areas' shares.

**Decided: make the window the frame** (project owner, 2026-11-11, ratified,
over keeping the page that grows and scrolls, which `PL-K285` Q2 built). The
owner agreed to the session's recommendation, in three steps that each stand
alone:

1. Make the marks panel and the branch control Views (`PL-9YPR`), so nothing
   but Areas sits between the region and the disclaimer.
2. Give the Areas exactly the room between the region and the disclaimer. A
   View whose content needs more height than its Area scrolls inside its own
   Area, as a Blender editor scrolls its own regions.
3. Lower the concentration chart View's minimum height, 558 px with one run,
   by moving its legend and reference rows beside the plot or behind a
   disclosure. That is the visual pass's work (planned-milestone item 33).

What it costs: step 2 changes `PL-K285` Q2's ratified answer and what a
learner sees on a laptop, so it is the owner's decision. The Induction
Workspace's two stacked charts cannot both hold their present minimum in
515 px, so one of them scrolls inside its Area or the Workspace is recomposed.

**What the decision leaves to the building session.** No mock-up was shown
before the owner agreed, so the first build step renders the result beside
today's screen at 1366 by 768 and 1920 by 1080. How the Induction Workspace's
two charts share 515 px is still open: one chart scrolls inside its Area, or
the Workspace is recomposed. This item needs triage and a split into build
items for steps 1 and 2 before work starts.

**Triaged, 2026-11-11: this item is now step 2, the build.** Step 1 is
`PL-9YPR`, built on pull request `#2103`. Step 3 stays with the visual pass
(planned-milestone item 33).

**Why it matters.** On a 1366 by 768 laptop the Induction Workspace's wash-in
chart opens below the fold, and a border drag changes the page's length as
well as the Areas' shares. A learner arranges a page, where the design they
were promised is a window.

**Done when.** The session first renders a mock-up at 1366 by 768 and 1920 by
1080, Induction Workspace in both, and the owner has seen it. Then the Areas
take exactly the room between the unconditional region and the disclaimer,
the page scroll bar has no range at either size in any shipped Workspace, and
a View that needs more height than its Area scrolls inside the Area. The
scroll that `PL-9YPR` put inside `_CasePanelView` moves into the container.
`docs/MODEL.md` and `PL-K285`'s recorded answer are updated to match.

**Generator check.** A one-off. It reopens a ratified answer (`PL-K285` Q2)
on a measurement, and no reader misread a fact.

**The mock-up, 2026-11-11, and the question it raised.** Rendered from the
branch with a patch in the render script (scratch only, nothing built): the
Areas take exactly the room, a plot may shrink to 160 px (concentrations) or
120 px (wash-in), and a View taller than its Area scrolls inside it. Same run
in every picture, 2% sevoflurane at 5 minutes. Measured:

- At 1366 by 768 the Areas get 1334 by 488 px. The band of readouts, the tab
  strip and the disclaimer take the other 280 px of height.
- The concentration chart's heading, reference lines and legend take about
  250 px above its plot. The wash-in chart's take about 170 px.
- Induction as shipped, at 1366 by 768: the chart's Area has 261 px and the
  wash-in's has 173 px. Each chart scrolls inside its Area (151 px and
  128 px), and neither plot is on screen until the learner scrolls. Stacked,
  the two charts cannot both show a plot in 488 px whatever the plot's floor:
  the text above the two plots and the two Area headers take about 300 px.
- Induction with the charts side by side (shares 0.34, 0.25, 0.41), and the
  rule that a chart keeps its plot in view while the block above it scrolls
  on its own: both plots are on screen at 1366 by 768 (218 px and 164 px
  tall), and the legend blocks scroll 114 px and 41 px.
- At 1920 by 1080 nothing scrolls in either arrangement. Stacked gives plots
  about 1280 px wide; side by side gives plots about 540 px and 390 px wide
  and 380 px and 480 px tall.
- The Parameters View needs 590 px of width for its four controls in one row.
  In a quarter-width column at 1366 px it scrolls 50 px sideways. That is
  `PL-4JCC`'s to fix by letting the controls wrap.
- Maintenance at 1366 by 768: the schematic needs 358 px and its Area has
  137 px. It needs a taller Area, a placeholder choice for the building
  session.

**The question put to the owner, answered below.** Which Induction ships? A learner on a laptop sees one
of these when they open Induction.

- A. Charts side by side at every window size. Both curves are on screen at
  1366 by 768. On a large monitor each plot is narrower than today.
- B. Charts stacked, as shipped. On a large monitor the plots are wide. At
  1366 by 768 neither curve is on screen until the learner scrolls inside
  each Area.

**Recommendation:** A. Induction exists to show the wash-in beside the
concentrations, and B hides both curves on the commonest laptop size. A
learner with a large monitor can drag the charts into a stack and save that
layout; a learner on a laptop cannot make room that is not there. Either
answer gets the plot-stays-in-view rule for both charts, which the session
decides as a placeholder.

**Decided: the charts stay stacked and the concentration chart keeps its
long time axis** (project owner, 2026-11-11: "I like the long graph of the
main anesthetic. Not side by side"). The owner chose this after seeing both
mock-ups, against the session's recommendation of A. It is specified, so it
reopens only on a compelling argument.

**What the session decides inside that answer, as placeholders.** A second
mock-up, sent to the owner the same day, shows these on Induction:

- The concentration chart keeps its plot on screen. Its legend block
  scrolls in its own box above the plot.
- At 1366 by 768 the two stacked charts need about 520 px and the Areas have
  488 px. The concentration chart gets the room its plot needs (300 px in the
  mock-up, plot 160 px). The wash-in Area gets the rest (126 px) and scrolls
  122 px inside itself. A learner who wants the wash-in curve scrolls that
  Area, drags the border between the two, or uses Maximize Area once
  `PL-VJD2` builds it.
- At 1920 by 1080 nothing scrolls. The wash-in plot is short there (about
  70 px in the first mock-up), so the build gives it a larger share of the
  column's height.
- The Areas report only their floors, so the page never scrolls.

**From the review of `PL-9YPR`, 2026-11-11.** The branch View declares a
minimum width of 220 px in `view_registry.py`, and its row of selector and
button needs about 308 px. At the narrowest Area a border drag reaches, the
Branch button is behind a sideways scroll. Set the declared minimum from what
the row needs when this item decides the room each Area gets.
