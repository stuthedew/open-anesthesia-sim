---
id: PL-NGLV
title: PL-4YY1 is classed defect+docs but its subject is two unsourced clinical constants in core/circuit.py, so docket check's safety pin never seats it at P1 where every other safety item sits
priority: P2
effort: S
status: done
classes: defect
touches: docs/items
added: 2026-09-12
closed: 2026-09-12
pr: 500
verify: python3 tools/doc_check.py check && grep -qE '^classes: .*science' docs/items/PL-4YY1-record-provenance-for-the-circuit-volume-and.md
---

**Problem.** PL-4YY1 is classed defect+docs but its subject is two unsourced clinical constants in core/circuit.py, so docket check's safety pin never seats it at P1 where every other safety item sits

**Verified 2026-09-12** against the tree, by the `PL-6ZQY` consolidation pass.

`src/anesthesia_sim/core/circuit.py:85-86`:

```python
circuit_volume_l: float = 6.0
fresh_gas_flow_l_min: float = 4.0
```

`grep -rn 'circuit_volume_l|fresh_gas_flow_l_min' src/anesthesia_sim/data/`
returns nothing: neither value is in a data file, neither carries a `tier` or
an `adopted` field, and neither has a provenance row.

**Why the classification is the defect rather than a labelling nit.** Both are
scientific parameters by `CLAUDE.md`'s own list - it requires provenance for
"scientific models, equations, constants, parameter sets", and the architecture
rules require agent/model parameters to live "in validated, versioned data
files". A breathing-circuit volume and a fresh gas flow are not incidental:
together they set the circuit time constant, so they determine wash-in and
washout kinetics and therefore every displayed concentration during induction.

`PL-4YY1` is classed `defect, docs` at P2. `subprojects/docket/src/docket/checks.py`
pins `safety`- and `science`-classed items to P1, so the class it carries is
exactly what keeps the pin from seating it beside the eleven other P1 items,
all of which are product-lane safety or science work. The band is not being
overridden; it is never being consulted.

**Recommended:** re-class `PL-4YY1` as `science` (keeping `defect`), which pins
it to P1, and source both constants into a data file with tier and adopted
fields like every other stored parameter.

**What the reclassification costs, since this item is itself a tightening
argument.** It adds a twelfth item to the P1 band. It displaces nothing:
`docket next` ranks within a band rather than across it, and the eleven
existing P1 items keep their order. The objection worth taking seriously is
`CLAUDE.md`'s own warning that the P1 band stops meaning "a clinician could be
misled" if it also means "the release script is annoying" - but this is the
first case rather than the second, which is the whole point.

**Decided by the project owner 2026-09-12: yes.** `PL-4YY1` is now
`classes: defect, science, docs` at P1, and the item records why the class was
the defect underneath the defect. The provenance work itself - moving both
constants into a versioned, cited data file and adding their `docs/MODEL.md`
rows - remains `PL-4YY1`'s own, unstarted and now correctly banded.

