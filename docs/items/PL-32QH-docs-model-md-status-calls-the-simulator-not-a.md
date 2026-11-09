---
id: PL-32QH
title: docs/MODEL.md § 'Status' calls the simulator not a medical device, while § 'Intended use' says the safety class settles no device status and the section claims no regulatory status; decide which claim stands (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: untriaged
feature: model-md-structure
touches: docs/MODEL.md
added: 2026-11-05
payoff: the specification makes one claim about regulatory status, so no reader meets the project asserting a device status it says it does not claim
verify: ! grep -qF 'not a clinical prediction, dosing tool, patient monitor, or medical device' docs/MODEL.md
---

**Problem.** docs/MODEL.md § 'Status' calls the simulator not a medical device, while § 'Intended use' says the safety class settles no device status and the section claims no regulatory status; decide which claim stands (copy editor structure read, 2026-11-05)

**Checked 2026-11-09:** The restructure moved the first claim. § "Status" no
longer mentions device status. § "Intended use" now says "It is not a clinical
prediction, dosing tool, patient monitor, or medical device" (line 78). Two
subsections later, § "This is an engineering bar, not a regulatory status" says
the project claims "no regulatory status" (line 157) and that the safety class
"does not settle whether the simulator is a medical device" (line 160). It then
cites FDA's examples of educational software that is not a medical device.

**Why it matters.** "It is not a medical device" is itself a claim of
regulatory status, which the next subsection says the project does not make.
A reader, or a regulator, meets two positions in one chapter. The FDA passage
already supports an intended-use statement, so the fix is one sentence.

**Done when.** § "Intended use" states what the simulator is not intended for
(clinical prediction, dosing, monitoring a patient, or any other use as a
medical device) rather than stating its device status. The chapter then makes
one claim about regulatory status: none. The FDA passage stays as the reason
that the intended-use boundary is drawn at a specific patient's data.

**Generator check.** One-off: a finding from the `docs/MODEL.md`
structure-read sweep of 2026-11-05.

**Present at the Gate 3 freeze (checked 2026-11-09).** The passage this item
fixes was already in its file at `817a4d88`, the commit that froze Gate 3, so
under ROADMAP.md § "The gate is a snapshot, not a moving target" the item
joins v0.7.0's frozen list rather than being deferred by its capture date.
