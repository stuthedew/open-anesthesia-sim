---
id: PL-9GP1
title: Appendix C of the Gas Man Workbook carries three values the provenance notes say it does not
priority: P1
effort: S
status: done
classes: science, docs
feature: model-spec-accuracy
milestone: v0.4.26
touches: src/anesthesia_sim/data/patients/reference_adult.json, src/anesthesia_sim/data/machines/reference_circle_system.json, docs/MODEL.md, docs/references/README.md, .claude/rules/citing-sources.md
added: 2026-09-15
closed: 2026-09-15
pr: 602
verify: python3 tools/doc_check.py check && uv run pytest tests/unit/test_parameters.py -q && python3 -c "import json; d=json.load(open('src/anesthesia_sim/data/patients/reference_adult.json')); s=d['sources']; assert any('Appendix C' in x['citation'] for x in s); assert any('VEN=1.0' in x['note'] for x in s); assert d['venous_pool_volume_l']==1.222; assert not any('Laboratory Manual' in x['citation'] for x in s)"
---

**Problem.** The whole Gas Man Workbook reached the private reference corpus on
2026-09-15, where the project had previously held only its front matter,
Appendix B and Appendix E. **Appendix C, "Gas Man System Defaults", pages
171-172, prints the program's `GASMAN.INI` verbatim, and three provenance
statements in this repository are wrong against it.**

- `src/anesthesia_sim/data/patients/reference_adult.json` says
  `default_alveolar_ventilation_l_min` is an interface default "the chapters
  supplied state no numeric default for". Appendix C's `[Defaults]` block reads
  `VA=4`.
- The same file says `default_cardiac_output_l_min` 5.0 is present "only as the
  sum of the Flow column". `[Defaults]` reads `CO=5`.
- The same file and `docs/MODEL.md` say the venous pool's 1.0 L - the value
  carried until `PL-8ZJQ` adopted Davis and Mapleson's 1222 ml on 2026-09-07 -
  "is not in the table at all" and that **none of the four sources ever cited
  for it contains it**. `[Volumes]` reads `VEN=1.0`.

**Why it matters.** The third is the one that counts. `PL-3YZW` closed on the
finding that 1.0 L was this project's own number wearing a citation its
neighbours had earned, and `docs/MODEL.md` § "Parameter provenance" states that
as settled fact. It is not: the v0.1.0 note's sentence - "alveolar volume 2.5 L,
venous volume 1.0 L, alveolar ventilation 4 L/min, cardiac output 5 L/min,
tissue volumes 6/33/14.5 L, and flow percentages 76/18/6" - is Appendix C's
three blocks item for item, **including the flow fractions as the percentages
`76`/`18`/`6` the INI writes rather than the 0.76/0.18/0.06 of Appendix B's
table**. The original citation named the wrong section; it did not invent the
numbers. A provenance record that says a value came from nowhere, when it came
from the reference implementation's own defaults file, is the failure mode this
project's source hierarchy exists to prevent, pointed the other way.

**Why it was not found earlier.** `PL-XTMB` and `PL-3YZW` quote Appendix B and
Appendix E and never Appendix C. Whether that page was among those supplied on
2026-09-06 and went unread is not recorded, and this item does not claim to
know.

**Where.** `src/anesthesia_sim/data/patients/reference_adult.json` (the Workbook
entry and the Davis and Mapleson entry), `docs/MODEL.md` § "Parameter
provenance", `src/anesthesia_sim/data/machines/reference_circle_system.json`
(the same Workbook citation, and its statement that no source gives a fresh gas
flow).

**Done when.** Every statement above reads true against Appendix C, no stored
value changes, and the corpus's catalogue says which page a later session should
open instead of re-reading the book.

**Closed 2026-09-15. No stored value changed, and none should.**

*What Appendix C actually carries.* `[Volumes]` `CKT=8.0`, `ALV=2.5`,
`VRG=6.0`, `MUS=33.0`, `FAT=14.5`, `VEN=1.0`; `[Ratio]` `VRG=76`, `MUS=18`,
`FAT=6`; `[Defaults]` `VA=4`, `CO=5`, a default agent and a default circuit
mode; and per agent `Lambda`, `VRG`, `MUS`, `FAT` - blood/gas and the three
tissue/gas coefficients - for nine agents, matching all twelve coefficients
stored under `src/anesthesia_sim/data/agents/`. **It is a second statement of
the same parameter set, not a second source**, and everything in it stays tier 3.

*The venous pool is unaffected as a value and changed as a history.* Davis and
Mapleson's 1222 ml is tier 2, is the same object this model has, and was adopted
on the project owner's decision. What this item changes is that the stored value
is a considered replacement for Gas Man's own default rather than the correction
of an orphan. The one round number in the reference patient with no counterpart
anywhere is now `weight_kg`, which no equation reads.

*The circuit file gains a confirmation and keeps its gap.* `CKT=8.0` is the
published circuit volume this file deliberately departs from, now confirmed from
the program's own defaults rather than only from De Wolf et al.'s Methods. The
`[Defaults]` block carries **no** fresh gas flow, so
`default_fresh_gas_flow_l_min` remains a project convention with no published
counterpart - the same conclusion as before, reached against better evidence.

*The title was wrong, and is corrected.* Every `sources` entry naming this
document called it "Gas Man(R) Workbook and Laboratory Manual", which `PL-XTMB`
took from the cover and from the original PDF's `/Title` and `/Author`. That
string occurs **zero times in the document's 209 pages**; the title page reads
*Workbook for Gas Man(R): a simulation and teaching tool*. The corpus's section
PDFs were rewritten by `pypdf` and carry no `/Title`, so the two cannot be
reconciled from anything this project holds, and a citation follows the title
page.

*One caution recorded for whoever reads the Workbook next, not acted on here.*
Appendix B's second table is captioned "Tissue/Gas partition coefficients
(calculated)" and lists `Blood/Gas`, `Brain/Blood`, `Muscle/Blood` and
`Fat/Blood` rows, which are tissue/**blood** ratios. Every column reproduces as
the first table's tissue/gas divided by that agent's blood/gas except
isoflurane's, which is divided by 1.90 - enflurane's blood/gas, not isoflurane's
1.30. Appendix C agrees with the first table, and so do this project's stored
coefficients, so nothing here rests on the wrong column. It is recorded because
a later reader taking an isoflurane tissue/blood ratio off that table would be
taking a number the same document contradicts.

**Docs swept:** `src/anesthesia_sim/data/patients/reference_adult.json` (the
Workbook entry's citation, route and three-values passage; the Davis and
Mapleson entry's "no source ever contained it"), `docs/MODEL.md` § "Parameter
provenance" (a new paragraph on Appendix C, and the 1.0 L passage rewritten),
`src/anesthesia_sim/data/machines/reference_circle_system.json` (citation,
route, and the fresh-gas-flow absence), `docs/references/README.md` and
`.claude/rules/citing-sources.md` (the corpus's two new textbook holdings). The
provenance table's rows are unchanged: no value and no key changed, and
`make doc-check` confirms it.
