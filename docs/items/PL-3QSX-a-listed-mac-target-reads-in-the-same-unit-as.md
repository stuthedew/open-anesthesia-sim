---
id: PL-3QSX
title: A listed MAC target reads in the same unit as the readout beside it, and no hazard-table row covers mistaking one for a current reading
priority: P2
effort: S
status: untriaged
classes: docs, ux
feature: scenario-branching
touches: docs/MODEL.md, tests/unit
added: 2026-09-20
payoff: keeps a height the learner asked for from being read as a height the model computed, which is the same compartment in the same unit two panels apart
---

**Problem.** A listed MAC target reads in the same unit as the readout beside it, and no hazard-table row covers mistaking one for a current reading

**Why it matters.** `docs/MODEL.md`'s hazard table carries a row for every way
a reader can take a correct number to mean something it does not, and
`PL-LPLD` put a new class of MAC multiple on screen: one the learner *asked
for* rather than one the model computed. "Alveolar 0.34 ×MAC falling" in the
bookmark panel and "Alveolar 0.42 ×MAC" in the readout row are the same unit,
the same compartment name and the same resolution, several inches apart.

Two channels already separate them - the "MAC targets" heading above the rows,
and the direction word, which no reading ever carries - so this is a gap in the
*record* rather than a defect on screen today. The table's own rule is that
every row names the test that holds it; there is no row, so there is no test,
so nothing would catch a later change that dropped either channel.

**It sharpens when `PL-CTD7` lands.** A target a run halts at becomes a value a
learner acts on, which is the threshold `CLAUDE.md`'s safety-critical standard
turns on, and the halt will want to say which target was reached - a sentence
naming a compartment and a height, at which point the two readings are on the
same line rather than in two panels.

**Done when.** `docs/MODEL.md`'s hazard table carries a row for reading a
requested value as a modelled one, naming the channels that separate them, and
a test holds it in the shape the table's other rows are held.
