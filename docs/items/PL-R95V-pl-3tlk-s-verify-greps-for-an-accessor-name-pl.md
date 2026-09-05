---
id: PL-R95V
title: PL-3TLK's verify greps for an accessor name PL-9SH6 introduces, and its ahead-of-PL-GS5X sequencing contradicts PL-9SH6's land-in-one-commit
priority: P2
effort: S
status: done
classes: defect, docs
feature: core-domain-language
touches: docs/items/PL-3TLK-core-and-model-md-call-the-middle-gas-phase.md
added: 2026-09-05
closed: 2026-09-05
pr: 356
verify: python3 tools/doc_check.py check && grep -qF 'The `core/` rename is *not* this item' docs/items/PL-3TLK-core-and-model-md-call-the-middle-gas-phase.md
---

**Problem.** Two contradictions in the same pair of items.

**One - the `verify:` command cannot pass without a different item.**
`PL-3TLK`'s command is:

```
uv run pytest -q tests/unit/test_circuit.py tests/reference/test_circuit_wash_in.py \
  && grep -q 'inspired_partial_pressure_fraction' src/anesthesia_sim/core/circuit.py
```

`inspired_partial_pressure_fraction` is not a name `PL-3TLK` derives. It is
`PL-9SH6`'s target form - `_partial_pressure_fraction` as the universal suffix,
prefixed where one object holds two such quantities - from that item's "After"
table. `core/circuit.py` today has `circuit_concentration_fraction`
(`:53`, `:79`, `:96`, `:120`). So `PL-3TLK` cannot satisfy its own command
without doing `PL-9SH6`'s rename.

**Two - the two items are ordered on opposite sides of a third.** `PL-3TLK`:
"This one goes *ahead* of `PL-GS5X` ... unlike the rest of the naming work."
`PL-9SH6`: "Sequencing changed 2026-09-03. Now behind `PL-GS5X`", and
"`PL-3TLK` supplies the $F_C \rightarrow F_I$ half of the table above ... the
two land in one commit." One commit cannot be both ahead of and behind
`PL-GS5X`.

**What is actually intended, from `PL-3TLK`'s own Sequencing.** The *decision*
goes ahead of `PL-GS5X`, so the new matrix assembly carries the domain's name
for the middle gas-phase state from its first line; "the full rename across the
existing call sites can follow with `PL-9SH6`". That is two pieces of work, and
the item is written as one.

**Where.** `docs/items/PL-3TLK-*.md` (`verify:`, Done when, Sequencing);
`docs/items/PL-9SH6-*.md` (Sequencing).

**Done when.** The decision half and the rename half are separable - either as
two items or as one item whose `verify:` proves only the half that lands ahead
of `PL-GS5X` - and the two briefs state one order.
