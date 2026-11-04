---
id: PL-BZ21
title: docs/MODEL.md says a price per millilitre typed as the bottle price makes the shown price per millilitre 100 to 1000 times the true one, in the cost section and in its hazard row, but that mistake makes it 100 to 250 times too low
priority: P3
effort: S
status: ready
classes: defect
feature: model-claims-held-by-tests
touches: docs/MODEL.md
deferred-from: v0.7.0 - a documentation misstatement of an error's direction; the screen still shows the far-off price per millilitre that catches the mistake, so no learner is misled while it waits
added: 2026-11-04
payoff: the cost section and its hazard row state each entry mistake's effect on the price per millilitre with the right direction and size
verify: ! grep -qF 'Each of the first two mistakes makes that price 100' docs/MODEL.md
---

**Problem.** docs/MODEL.md says a price per millilitre typed as the bottle price makes the shown price per millilitre 100 to 1000 times the true one, in the cost section and in its hazard row, but that mistake makes it 100 to 250 times too low

**Checked 2026-11-04**, by the copy editor on `#2024`. `docs/MODEL.md` § "A cost at the reader's price" says a price per millilitre typed as the bottle price "gives a cost 100 to 250 times too low", and a bottle volume typed in litres or as one bottle "gives a cost 100 to 1000 times too high". Three sentences later it says "Each of the first two mistakes makes that price 100 to 1000 times the true one", and the hazard row on entry mistakes repeats that. For the first mistake the price per millilitre shown is a hundredth to a 250th of the true one.

**Why it matters.** The hazard row is the record of what the screen does to catch each mistake. The screen still catches this one, because the price per millilitre shown is far from any real price, but the row states the wrong direction and size.

**Done when.** The cost section and the hazard row say that the first mistake makes the price per millilitre 100 to 250 times too low and the second makes it 100 to 1000 times too high, or that each puts it wrong by a factor of 100 to 1000.

**Generator check.** Stock of `PL-B6YV`'s fact, whether a `docs/MODEL.md` sentence about what the model computes matches what it computes. The sentence dates from `PL-1P15`, before that head closed on 2026-11-02, so this is not a re-entry.
