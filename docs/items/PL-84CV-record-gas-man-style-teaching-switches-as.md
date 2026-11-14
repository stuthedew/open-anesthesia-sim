---
id: PL-84CV
title: Record Gas Man-style teaching switches as planned-milestone item 44 in ROADMAP.md, beside filing PL-64NJ and PL-LBVN
priority: P3
effort: S
status: ready
classes: housekeeping
touches: ROADMAP.md
added: 2026-11-14
payoff: The teaching-switch idea from the Gas Man comparison is kept where milestone scoping reads it
verify: grep -q '^#### 44\. ' ROADMAP.md
---

**Problem.** Record Gas Man-style teaching switches as planned-milestone item 44 in ROADMAP.md, beside filing PL-64NJ and PL-LBVN

**Generator check.** None. This records new intent from the 2026-11-13 Gas Man
comparison thread, which the project owner agreed to file on 2026-11-14. No
existing mechanism produced it.

**What is recorded.** Gas Man's desktop control panel has "Disable Uptake" and
"Disable Return" switches (`src/gasman_main/gascontrol.ui:111-125` and
`src/gasman_main/gasdoc.cpp:652-668` in <https://github.com/rasman/gasmanonline>
at `d3a2dd3`, read 2026-11-13). They let a learner turn a mechanism off and see
what it was doing. The roadmap gains planned item 44 for the idea (project
owner, 2026-11-14, ratified, over leaving it unrecorded).
