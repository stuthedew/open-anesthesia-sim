---
id: PL-Q7V1
title: ROADMAP.md's varying-perfusion note ('Also unsupported at rest, one layer down', under planned milestone item 35) reads the stored fat flow as 'that far out' against Heinonen alone, where PL-HBH2 records that Yasuda 1991's washout fits put it at or a little above the stored figure
priority: P1
effort: S
status: ready
classes: science, docs
feature: late-washout-evidence
touches: ROADMAP.md
added: 2026-09-27
payoff: the roadmap's case against varying perfusion rests on both human fat-flow sources, not the one that makes the stored value look furthest out
verify: ! grep -qF 'resting one that far out' ROADMAP.md
---

**Problem.** ROADMAP.md's varying-perfusion note ('Also unsupported at rest, one layer down', under planned milestone item 35) reads the stored fat flow as 'that far out' against Heinonen alone, where PL-HBH2 records that Yasuda 1991's washout fits put it at or a little above the stored figure

**Why it matters.** `ROADMAP.md` is what a scoping round reads to decide
planned item 35, and the note argues the resting fat flow is too far from human
data to build on, weighing it against Heinonen alone. `docs/MODEL.md` records,
since `PL-HBH2`, that Yasuda 1991's washout fits put it at or a little above the
stored figure, so the two human sources disagree about which way it errs and the
note overstates the case.

**Done when.** The note gives both sources as `docs/MODEL.md` § "Known
limitations" does, and draws its conclusion from their disagreement rather than
from Heinonen alone.
