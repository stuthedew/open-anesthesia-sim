---
id: PL-XP6W
title: MODEL.md's Symbols table has no row for f_i, the stored per-group perfusion fraction its own Tissue groups section uses in Q_i = f_i Q
priority: P2
effort: S
status: done
classes: docs
feature: core-domain-language
milestone: v0.4.24
touches: docs/MODEL.md, tests/unit/test_core_vocabulary_check.py
added: 2026-09-13
closed: 2026-09-14
pr: 561
verify: python3 tools/doc_check.py check && grep -qF 'TissueGroup.perfusion_fraction' docs/MODEL.md
---

**Problem.** MODEL.md's Symbols table has no row for f_i, the stored per-group perfusion fraction its own Tissue groups section uses in Q_i = f_i Q

§ "Tissue groups" lists what each group has, and one of the six entries is "a
fraction of cardiac output $`f_i`$". It is used immediately afterwards, in
$`Q_i = f_iQ`$ and in $`\sum_i f_i = 1`$, and it is a stored parameter: the
reference-adult data file holds `vessel_rich_perfusion_fraction`,
`muscle_perfusion_fraction` and `fat_perfusion_fraction`, and `TissueGroup`
carries it as `perfusion_fraction`. Every other stored parameter that appears
in an equation has a row in § "Symbols"; this one is defined only at the point
of use.

**Why it matters.** `PL-H46J` gave the Symbols table a Code column so the map
from specification to `core/` is enumerable, and `PL-FZ6T` will check that
every Code cell resolves. Neither can see a symbol that has no row, so a
missing row is the one failure mode that survives the mechanism. $`f_i`$ is
the only instance found while writing the column: $`C_i`$, $`\tau_i`$,
$`\tau_v`$, $`\dot M_{\mathrm{delivered}}`$ and
$`\dot M_{\mathrm{exhausted}}`$ are all derived quantities defined where they
are used, and none of them is stored.

**Where.** `docs/MODEL.md` § "Symbols" — one row, `TissueGroup.perfusion_fraction`
in the Code column, dimensionless, and the same "for group $`i`$" phrasing the
other indexed rows use.

**Found.** Writing the Code column for `PL-H46J`, 2026-09-13.

**Done when.** § "Symbols" carries a row for $`f_i`$ - dimensionless, with
`TissueGroup.perfusion_fraction` in the Code column and the same "for group
$`i`$" phrasing the other indexed rows use - and `make doc-check` passes.

**Done 2026-09-14.** § "Symbols" carries a row for $`f_i`$ — "Fraction of
cardiac output reaching tissue group $`i`$, so that $`Q_i = f_iQ`$",
dimensionless, `TissueGroup.perfusion_fraction` in the Code column — placed
directly under $`Q_i`$, the quantity it defines. The row count
`tests/unit/test_core_vocabulary_check.py` pins moved from 24 to 25, which is
what stops the table being parsed halfway and passing on what it read.
