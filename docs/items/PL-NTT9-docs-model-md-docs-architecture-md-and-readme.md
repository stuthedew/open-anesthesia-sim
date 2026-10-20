---
id: PL-NTT9
title: docs/MODEL.md, docs/ARCHITECTURE.md and README.md still describe the area system as planned and the page as about to stop scrolling: the page still scrolls, and no shipped Workspace shows the accounting the README lists
priority: P2
effort: S
status: done
classes: docs
feature: v0.6.0-done-check
touches: docs/MODEL.md, docs/ARCHITECTURE.md, README.md
added: 2026-10-20
closed: 2026-10-20
pr: 1700
payoff: the specification and README say where the use disclaimer and the required values actually sit, so a reader trusting them is not wrong about what is on screen
verify: ! grep -q "1571 px" docs/MODEL.md && ! grep -q "planned area and" docs/ARCHITECTURE.md && ! grep -q "becoming closeable when the" docs/MODEL.md
---

**Problem.** docs/MODEL.md, docs/ARCHITECTURE.md and README.md still describe the area system as planned and the page as about to stop scrolling: the page still scrolls, and no shipped Workspace shows the accounting the README lists

**Why it matters.** `/mnt/project-files/v0.6.0/dod-check.md` holds the whole check of v0.6.0's Definition of done, run on 2026-10-20 before the cut. Its last bullet asks that the documents describe the interface that exists. Four passages do not:

- `docs/MODEL.md` § "Where the educational-use disclaimer lives", the paragraph "Present, and not yet always in view", says the page is 1571 px tall and that the gap closes when v0.6.0's tiled layout stops the page scrolling. Measured offscreen on 2026-10-20 at 1366 px wide, the page is 1087 px tall in the Default Workspace and 1505 px in Induction and Maintenance, and it still scrolls at a 700 or 900 px window, and in those two Workspaces at 1100 px too.
- `docs/MODEL.md` § "What this list requires once the layout is the reader's" opens by calling the reader's layout a planned milestone, and the paragraph on the setting sections speaks of "when the area system's docking operations arrive".
- `docs/ARCHITECTURE.md`'s opening paragraph calls it "the interface's planned area and workspace model".
- `README.md`'s list "While a case runs, the interface shows" names the agent accounting and the wash-in curve. No shipped Workspace holds the accounting View, and the Default Workspace has no wash-in plot. Both are reachable through each Area's View chooser.

A reader who trusts the specification about where the use disclaimer and the unconditional values sit would be wrong about what is on screen.

**Done when.** Each passage describes the shipped interface, the scrolling gap is stated with the 2026-10-20 measurement and the item that closes it, and `make check` is green.
