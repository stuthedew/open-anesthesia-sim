---
id: PL-ZD67
title: Three stored values - alveolar_gas_volume_l 2.5, default_alveolar_ventilation_l_min 4.0 and muscle volume 33.0 - appear in Smith 1972 and Zwart 1972, two links up the chain, and the first two are the ones Lowe and Ernst demonstrably cannot supply
priority: P1
effort: S
status: done
classes: science, docs
feature: model-spec-accuracy
touches: src/anesthesia_sim/data/patients/reference_adult.json, docs/MODEL.md
added: 2026-09-10
closed: 2026-09-10
verify: uv run pytest tests/unit/test_parameters.py && python3 -c "import json; d=json.load(open('src/anesthesia_sim/data/patients/reference_adult.json')); assert any('Dittmer and Grebe' in s['note'] for s in d['sources'])"
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

## Outcome, 2026-09-10: two of the three are lineage, not coincidence

**The project owner approved the recommendation** — record the observation on
the provenance notes with the case against reading anything into it stated
first. **What is recorded is stronger than that, and the reason is that this
item's own test came back the same afternoon.** The brief said reading Mapleson
1963 would settle it: "If the same figures are there, the numbers are the
period's shared furniture and the coincidence reading is settled in the
negative." Mapleson arrived, and the answer is neither of the two the brief
anticipated. Two of the three are not coincidence and not shared furniture:
they are a traceable lineage, and one of them has a named measurement behind
it.

**`alveolar_gas_volume_l` = 2.5.** Mapleson's Appendix 1, on the "air in lungs"
row of his Table 1: "Average of all measurements in **Dittmer and Grebe** in
which the average age was over 20 gives a **functional residual capacity of 2.5
liters**." His reference 31 is *Dittmer DS, Grebe RM. Handbook of Respiration.
Philadelphia: Saunders, 1958, p. 38*. So 2.5 L is a mean of published human
measurements with a citation behind it, in a document Lowe and Ernst name — not
a round number somebody chose. **It is still not this file's source**, and the
distinction has to survive the excitement: Mapleson's row is *air in the lungs*
= FRC + half the tidal volume, and this file stores an *alveolar gas volume*;
the value reaches here through Gas Man, whose stated upstream is Lowe and
Ernst, and Lowe and Ernst lump the quantity away at page 58. Nothing is
promoted or adopted, and the `provenance_gap` still says no upstream is
identified.

**`tissue_groups.muscle.volume_l` = 33.0.** Not a coincidence either, and its
path is exact. Mapleson's Table 1 gives muscle 30 litres and skin nutritive 3
litres. Smith 1972's Table 2 lumps them — its own footnote reads "Muscle =
muscle and skin nutritive" — and prints **33**. That table reproduces
Mapleson's in nine rows of nine, and the nine sum to 58.04 litres against
Mapleson's own 58.04. So the 33 is Mapleson's 30 + 3, travelling one link. What
it is *not* is this file's 33.0: `PL-7HDS` established that Lowe's muscle row is
42.6% of body weight, 29.8 L at 70 kg, and does not reproduce the stored value
under any grouping. **Two unrelated 33s in one chain, and the file already
records a third against Janssen et al.'s measured skeletal muscle mass.** That
is now a documented fact about the number rather than a suspicion.

**`default_alveolar_ventilation_l_min` = 4.0** is the one that stays a
coincidence. Mapleson gives no alveolar ventilation figure; he gives a formula,
"the alveolar ventilation for the anesthetized patient may be estimated from
V̇A = 0.7V̇ − fVD′". The 4 l/min in Smith's and Zwart's Table 1 is theirs, with
no source, and 4 l/min is the textbook value. Recorded as a coincidence, in
those terms.

**Where it is recorded.** `src/anesthesia_sim/data/patients/reference_adult.json`
— the Mapleson entry carries the Dittmer and Grebe derivation and the 30 + 3
arithmetic, and the Smith entry records that its "assumed" table is Mapleson's.
`docs/MODEL.md`'s "Parameter provenance" carries the same in prose.

**The decision this item asked for is answered by the facts rather than by the
option list.** The three candidates were: say nothing until `PL-LT51` closes;
record the observation with the coincidence case first; or chase Gas Man's own
provenance. `PL-LT51` closed first, which retires the first option, and what is
recorded is no longer an observation about coincidences. The third stays open
as `PL-XTMB`'s territory and nothing here needs it.
