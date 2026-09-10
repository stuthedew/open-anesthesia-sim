---
id: PL-ZD67
title: Three stored values - alveolar_gas_volume_l 2.5, default_alveolar_ventilation_l_min 4.0 and muscle volume 33.0 - appear in Smith 1972 and Zwart 1972, two links up the chain, and the first two are the ones Lowe and Ernst demonstrably cannot supply
status: untriaged
added: 2026-09-10
---

**Problem.** Three stored values - alveolar_gas_volume_l 2.5, default_alveolar_ventilation_l_min 4.0 and muscle volume 33.0 - appear in Smith 1972 and Zwart 1972, two links up the chain, and the first two are the ones Lowe and Ernst demonstrably cannot supply

**Why it matters.** `alveolar_gas_volume_l` has no identified upstream at all.
`PL-7HDS` established that Lowe and Ernst do not supply it — page 58 lumps the
circuit and the patient's functional residual capacity into one ventilatory
volume of "about 100 dl" and states no alveolar gas volume — and the Gas Man
Workbook's own table is the only place it has ever been traced to.
`default_alveolar_ventilation_l_min` is in the same state: an interface default
the Workbook states no number for. Both now turn up in documents Lowe and Ernst
cite for the reference patient's volumes and flows.

**What was found, 2026-09-10 (`PL-LT51`).** Reading references 19 and 20 —
Smith, Zwart and Beneken, *Anesthesiology* 1972;37(1):47-58, and Zwart, Smith
and Beneken, *Comput Biomed Res* 1972;5(3):228-38, which share one parameter
set:

| Stored | Value | Where it also appears |
| --- | --- | --- |
| `default_alveolar_ventilation_l_min` | 4.0 | Table 1 of both papers, "Alveolar ventilation 4 l/min" |
| `alveolar_gas_volume_l` | 2.5 | Zwart's Table 1, "Functional residual capacity 2.5 l". Smith's Table 1 does not carry the row. |
| `tissue_groups.muscle.volume_l` | 33.0 | Smith's Table 2, "Skeletal muscle 33" tissue litres, for a **75 kg** man |

**The case against reading anything into it, which is strong and should be
stated first.** 2.5 L for functional residual capacity and 4 L/min for alveolar
ventilation are textbook round numbers for an anaesthetised adult and would be
unremarkable in any model of the period. The muscle figure is at 75 kg where
this file stores 70. There is no evidence Gas Man read either paper — its
stated upstream is Lowe and Ernst, and Lowe and Ernst reach these two papers
only as three of four references named in one sentence on page 56. And this
project has already recorded a 33.0 coincidence once, against Janssen et al.'s
measured skeletal muscle mass, with `reference_adult.json` saying in capitals
that the numeric match must not be read as a source. A third 33 is better
evidence that 33 is a convention than that it is a lineage.

**The case for looking again anyway.** Two of the three are precisely the
parameters this file cannot source at all, and they appear together, in one
table, in a document two links up its own citation chain. That is not proof and
it is not nothing.

**What would settle it, and it is cheap.** Reference 19's Table 2 volumes are
*assumed* — the paper says so in that word and cites nothing for them — so the
question is not "did Smith measure 33" but "did the number travel". Two things
would move it:

1. **Read Mapleson 1963** (`PL-LT51`'s last outstanding reference). If the same
   figures are there, the numbers are the period's shared furniture and the
   coincidence reading is settled in the negative.
2. **Look for a Gas Man statement of alveolar volume's origin** outside
   Appendix B. `PL-XTMB` already covers the Workbook citation.

**Decision needed.** Whether anything about this reaches
`reference_adult.json`. Three candidates, and the middle one is the
recommendation: say nothing until `PL-LT51` closes, since a coincidence
recorded is a coincidence a reader has to evaluate; **record the observation on
the `alveolar_gas_volume_l` provenance note in the terms above, coincidence
case first**, so the next session that finds it does not re-derive it; or treat
it as a lead worth chasing and open the reading of Gas Man's own provenance.
Nothing is adopted under any of the three.
