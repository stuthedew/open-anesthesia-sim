---
id: PL-KBJT
title: PL-H46J's worked Code-column example cites AlveolarCompartment.partial_pressure_fraction, which does not resolve until PL-9SH6 lands
priority: P3
effort: S
status: done
classes: defect, docs
feature: core-domain-language
milestone: v0.4.1
touches: docs/items/PL-H46J-give-model-md-s-symbols-table-a-code-column.md
added: 2026-09-05
closed: 2026-09-05
pr: 356
verify: python3 tools/doc_check.py check && grep -qF 'Write the cells against the names in the tree today' docs/items/PL-H46J-give-model-md-s-symbols-table-a-code-column.md
---

**Problem.** `PL-H46J` adds a Code column to `docs/MODEL.md` § "Symbols" whose
cells name a resolvable expression, and offers
`AlveolarCompartment.partial_pressure_fraction` as its worked example.
`core/alveolar.py:47` defines `concentration_fraction`. The name in the example
is `PL-9SH6`'s target, and `PL-9SH6` lands later - behind `PL-GS5X`, where
`PL-H46J` is "the first item of the pass".

**Why it matters.** `PL-H46J`'s own Done when requires each cell to name a
resolvable expression, and `PL-FZ6T` rule 1 makes that a hard check. Written
first against the example as given, the column is wrong on the day it lands and
the check `PL-FZ6T` adds would fail against it.

**Two ways out, and the choice is the work.** Write the column against the
*current* accessor names and let `PL-9SH6` update it as part of the rename -
which is what `PL-H46J` already anticipates ("writing the column first and
updating it with them is one pass over the table"), and which makes the
example in the brief simply wrong rather than the plan wrong. Or move
`PL-H46J` behind `PL-9SH6`, which costs the "target vocabulary first" benefit
`PL-9SH6` depends on. The first looks right; the brief's example needs
correcting either way.

**Where.** `docs/items/PL-H46J-*.md` (the worked example);
`src/anesthesia_sim/core/alveolar.py:47`.

**Done when.** `PL-H46J`'s example names an expression that resolves in the
tree as it will stand when the item is worked, and says which names are
expected to move under `PL-9SH6`.
