---
id: PL-Q7V1
title: ROADMAP.md's varying-perfusion note ('Also unsupported at rest, one layer down', under planned milestone item 35) reads the stored fat flow as 'that far out' against Heinonen alone, where PL-HBH2 records that Yasuda 1991's washout fits put it at or a little above the stored figure
priority: P1
effort: S
status: done
classes: science, docs
feature: late-washout-evidence
milestone: v0.5.20
touches: ROADMAP.md
added: 2026-09-27
closed: 2026-10-01
pr: 1251
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

**Closed 2026-10-01.** The note now gives both human comparisons as
`docs/MODEL.md` § "Known limitations" does - Heinonen et al.'s PET measurement
(PMID 22223450), close to half what the stored fraction implies, and both
Yasuda 1991 washout fits (PMID 1994760 and PMID 2001028), whose fat-group flow
per 100 mL of tissue sits at or a little above the stored figure - says why
neither settles it, and draws its conclusion from the unsettled direction of
the resting flow's error rather than from Heinonen alone: a varying fraction
on a resting one whose sign of error the two sources cannot agree on is the
second storey on the same foundation. The figures and citations are the ones
`PL-HBH2` recorded; no paper was re-read. `ROADMAP.md`'s v0.4.6 release row,
which records Heinonen alone, was checked and left: it describes what that
release found on 2026-09-06, before either Yasuda paper had been read for the
fat group.
