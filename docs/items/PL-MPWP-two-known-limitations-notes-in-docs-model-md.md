---
id: PL-MPWP
title: Two Known-limitations notes in docs/MODEL.md name a per-compartment gas-phase model as the lift for the temperature and humidity simplifications, and ROADMAP.md's planned milestones track it nowhere
status: untriaged
added: 2026-09-19
---

**Problem.** Two Known-limitations notes in docs/MODEL.md name a per-compartment gas-phase model as the lift for the temperature and humidity simplifications, and ROADMAP.md's planned milestones track it nowhere

**Found 2026-09-19, while working `PL-7DMJ`** (the alveolar water-vapour
simplification). `docs/MODEL.md` now carries two notes under "Known
limitations" that end the same way: the temperature note at line 7362 says
lifting the single reference condition "means a gas-phase model carrying
explicit conditions per compartment", and the humidity note this session
added says correcting it means re-referencing the coefficients and the
inspired term together, "which is the same per-compartment gas-phase model".

**Why it matters.** Two recorded limitations name one change as their lift and
nothing tracks that change. `ROADMAP.md`'s planned milestones carry no line
for it - grepped 2026-09-19 for `gas-phase`, `condition`, `temperatur`,
`humid` and `BTPS` across the "Planned milestones" section, and the hits are
item 28's consumption figure and unrelated layout prose. So a reader who asks
"is this going to be fixed?" gets no answer, and the next session to meet
either note re-derives the same conclusion.

This is intent rather than a specific change, so `CLAUDE.md`'s routing rule
points at one unscoped line in `ROADMAP.md`'s "Planned milestones" rather than
at a queue item to be worked - which is why this item asks the project owner
whether they want that line, and does not write it.

**Done when** either `ROADMAP.md` carries a planned-milestone line for a
per-compartment gas-phase model, or this item is dropped with the project
owner's reason for leaving the two notes pointing at nothing.
