---
id: PL-5J1X
title: At 1366 by 768 with a branch open, the page scrolls in every shipped Workspace (150 px in Default, 206 in Induction, 223 in Maintenance, measured 2026-11-22), because the Parameters View then needs two rows of dials; the Default right column falls short by about 40 px, yet the page grows by 150, so check whether the sizing grows the page by more than the Areas' shortfall, and whether a two-run arrangement can avoid page scrolling (found in review of PL-D5J4)
status: untriaged
feature: interface-design-review
added: 2026-11-22
---

**Problem.** At 1366 by 768 with a branch open, the page scrolls in every shipped Workspace (150 px in Default, 206 in Induction, 223 in Maintenance, measured 2026-11-22), because the Parameters View then needs two rows of dials; the Default right column falls short by about 40 px, yet the page grows by 150, so check whether the sizing grows the page by more than the Areas' shortfall, and whether a two-run arrangement can avoid page scrolling (found in review of PL-D5J4)

**A related case, measured 2026-11-22 by `PL-S6CP`.** With one run, an advisory above the concentration plot (all traces hidden) grows the chart's Area to keep the plot whole, and the page then scrolls 47 px in Induction and in Maintenance at 1366 by 768. Default does not scroll. The chart's Area is in a column whose other Area, Parameters, is already at its least height, so the page takes the height.
