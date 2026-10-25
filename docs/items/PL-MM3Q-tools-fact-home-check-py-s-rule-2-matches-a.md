---
id: PL-MM3Q
title: tools/fact_home_check.py's rule 2 matches a second copy only by its name, so a fact copied under a new name passes; PL-LGDV's drain found five such copies by reading the code
priority: P3
effort: M
status: done
classes: defect
feature: one-source-of-truth
touches: tools/fact_home_check.py, tests/unit/test_fact_home_check.py
added: 2026-10-24
closed: 2026-10-25
pr: 1762
payoff: a second copy of an apparatus fact fails make check even under a new name
verify: grep -q 'def test_a_fact_copied_under_another_name_is_reported' tests/unit/test_fact_home_check.py
---

**Problem.** Rule 2 of `tools/fact_home_check.py` reports an upper-case module-level name that two apparatus files define. A copy of the same value under another name passes. `PL-H5T9` lists five such copies that `PL-LGDV` found by reading the code, for example `roadmap.SECTION_ID_RE` and `store.CITED_ID_RE`, which are the same `re.compile(ID_PATTERN)`.

**Why it matters.** `CLAUDE.md` asks that a second copy be fixed by its shape, so that the next one fails a check. The baseline is now empty, so rule 2 refuses every new same-named copy, but a renamed copy is still invisible to it.

**Done when.** A decidable form of "the same fact under another name" is chosen and checked, or the item records why none is decidable. One candidate is two module-level bindings whose values are the same call with the same constant arguments, such as two `re.compile(ID_PATTERN)`. Any such rule must not report two different facts that happen to share a value, such as `trend.UNPLACED_PATH` and `roadmap.UNPLACED`, which are both `"unplaced"` and mean different things.

**Generator check.** A one-off. This is the check's own matching rule, not a reader misreading a fact. The copies it misses are `PL-H5T9`'s, which records the misread fact.

**Closed 2026-10-25.** Rule 2 now also groups module-level bindings by the call they make, compared as the `ast.dump` of a call with arguments. One call bound under different names in more than one module is reported, unless every file in the group reads one shared name. On its first run it found `checks._ANY_ID` and `duplicates._TITLE_ID`, two more copies of `store.CITED_ID_RE`, which `PL-H5T9` removed in the same pull request.
