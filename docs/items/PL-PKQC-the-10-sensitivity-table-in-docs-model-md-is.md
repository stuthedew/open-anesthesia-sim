---
id: PL-PKQC
title: The 10% sensitivity table in docs/MODEL.md is dated the day before the venous pool changed, and two of its rows no longer reproduce to the last digit
status: untriaged
feature: model-spec-accuracy
added: 2026-11-21
---

**Problem.** The 10% sensitivity table in docs/MODEL.md is dated the day before the venous pool changed, and two of its rows no longer reproduce to the last digit

**Found by.** `PL-RMNP`, the check of `docs/MODEL.md` against the code, on 2026-11-21.

**What the document says.** § "Published wash-in and elimination validation test" gives a table of "how far each ratio moves when one coefficient is raised by 10%, in units of that ratio's own published SD (from model runs on 2026-09-06)". Two rows read "| Blood:gas | −0.57 to −0.64 | +0.09 to +0.17 |" and "| Vessel-rich tissue:gas | −0.02 to −0.06 | +0.45 to +0.55 |".

**What the tree gives today.** With `StoredParameterChange(parameter, 1.10)` and the test module's own `_wash_in_ratio()` and `_eliminate()`, against each agent's first cohort: blood:gas elimination +0.11 to +0.18, and vessel-rich elimination +0.44 to +0.54, wash-in −0.02 to −0.07. The muscle and fat rows reproduce as printed. The venous pool volume changed on 2026-09-07, the day after the table's date. With the second isoflurane cohort's own SD, which the table's wording does not exclude, blood:gas wash-in reaches −0.52 and vessel-rich elimination +0.65. The conclusions drawn from the table still hold.

The docstring of `tests/reference/test_published_wash_in_and_elimination.py` carries the same table, and its line "+0.45 to +0.55" repeats one figure. A change under `tests/reference/` waits for the project owner's read.

**Done when.** The table and the test module's copy give the figures of the tree that ships, with the date and the words "against each agent's first cohort".
