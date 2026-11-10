---
id: PL-N3SK
title: docs/MODEL.md § 'Known limitations' says nothing on screen shows the liquid-agent figure, but the hazard rows, § 'Agent amounts in millilitres, and the cost' and § 'A cost at the reader's price' describe a cost View that shows delivered agent in mL of liquid (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: ready
classes: defect, docs
feature: model-md-structure
touches: docs/MODEL.md
deferred-from: v0.7.0 - not present at the freeze (817a4d88): the sentence became false with 26eb4e39 (#1932), the milestone's own agent cost View
added: 2026-11-05
payoff: the reference-condition limitation says which liquid figures are on screen and why none carries its 5.8% error, so a change that would show a converted store meets the reason it is refused
verify: ! grep -qF 'invisible in everything the simulator shows today' docs/MODEL.md
reenters: PL-4FBP
---

**Problem.** docs/MODEL.md § 'Known limitations' says nothing on screen shows the liquid-agent figure, but the hazard rows, § 'Agent amounts in millilitres, and the cost' and § 'A cost at the reader's price' describe a cost View that shows delivered agent in mL of liquid (copy editor structure read, 2026-11-05)

**Checked 2026-11-09:** On cfd4a4b6, § "Known limitations", in the note "One reference condition, where the model physically has two", still says "**It is invisible in everything the simulator shows today.**" It also says the liquid-equivalent figure is "planned under § "Planned milestones" item 28", and that "nothing on screen shows its result yet". § "Agent amounts in millilitres, and the cost" says the agent cost display shows the delivered and exhausted totals in millilitres of liquid, and refuses the stored total. § "A cost at the reader's price" prices the delivered liquid. `PL-SP6H` (#2024) shipped that display.

**Why it matters.** Known limitations is where a clinician looks to learn which displayed values a limitation reaches. This note says the 5.8% reference-condition error reaches nothing on screen, but the liquid figures are on screen. The delivered and exhausted totals are exact and the stored total is refused, so no displayed value carries the error today. The note should say that, because it is the reason the display is safe. A later change that shows a converted store would otherwise meet a note that says the question cannot arise.

**Done when.** The note says that the cost display shows delivered and exhausted agent in millilitres of liquid, which convert exactly, and that it refuses the stored total, which would read 5.8% high. It points to § "Agent amounts in millilitres, and the cost". No sentence in `docs/MODEL.md` describes the liquid figure as planned or unshown.

**Generator check.** `PL-4FBP`'s fact: the link between a document sentence and the tree fact it restates, here a limitation note that `PL-SP6H`'s display change left behind. `PL-4FBP` closed on 2026-09-19, so this is an instance filed after its head closed, recorded as `reenters: PL-4FBP`.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Not present. At 817a4d88 the sentence "It is invisible in everything the simulator shows today" was true, because no liquid figure was on screen. It became false with `26eb4e39` (#1932, `PL-B396`), which added the agent cost View as v0.7.0's own milestone work. The deferral stays with that reason.

**Disposition under PL-BLN0 (2026-11-09).** PL-BLN0 is the head over the
sentences that went stale when the code they restated changed. It binds every
paragraph of `docs/ARCHITECTURE.md` and of the last chapter of
`docs/interface-provenance.md` to the code it describes, and leaves the free
prose of `docs/MODEL.md` outside that binding, for the reason its brief gives.
This item's sentence is in that free prose, so it stays its own documentation
fix.
