---
id: PL-CBYS
title: The page still scrolls at every common screen size, though PL-JG82's brief says v0.6.0 removes the page scroll: the Areas and the marks and branch section sit in one scrolling page, which measured offscreen on 2026-11-11 scrolls 414 px (Default) and 832 px (Induction) at 1366 by 768, and 102 px and 520 px at 1920 by 1080, so the Induction Workspace's wash-in chart opens below the fold; decide whether the Areas fill exactly the space between the unconditional region and the disclaimer, as a Blender window's Areas fill the window
status: untriaged
feature: window-is-the-frame
added: 2026-11-11
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
