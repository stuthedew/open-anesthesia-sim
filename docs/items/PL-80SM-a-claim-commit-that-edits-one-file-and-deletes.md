---
id: PL-80SM
title: A claim commit that edits one file and deletes another reads as merged once the base holds the edit, though the base never took the deletion: _Landings.taken_whole asks only the content split, so claims and _unlanded_refs disagree about one branch (found working PL-2CL5)
priority: P2
effort: S
status: done
classes: defect
feature: landing-deletions
milestone: v0.6.17
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.7.0 - found 2026-11-11 after the freeze; apparatus, and it changes no displayed value, so the release does not wait on it
added: 2026-11-11
closed: 2026-11-11
pr: 2091
payoff: a claim is not released while its branch still holds a deletion main never took, so the item is not offered to a second session
verify: grep -q 'def test_a_ref_whose_deletion_the_base_never_took_is_not_taken_whole' subprojects/docket/tests/test_vcs.py
---

**Problem.** A claim commit that edits one file and deletes another reads as merged once the base holds the edit, though the base never took the deletion: _Landings.taken_whole asks only the content split, so claims and _unlanded_refs disagree about one branch (found working PL-2CL5)

**Reproduced 2026-11-11** in a scratch repository. A branch adds `a.txt` and deletes `old.txt`. The base then writes the same `a.txt` by another route and keeps `old.txt`. `_Landings.taken_whole` returned `True` for the branch, and `_unlanded_refs` listed the same branch as unlanded.

**Why it matters.** `claims._landed_through` asks `taken_whole` whether a squash took a claim's commits. A `True` there releases the claim, so the item is offered to a second session while the branch still holds a deletion the base never took.

**Done when.** `taken_whole` is false for that branch, and `test_a_ref_whose_deletion_the_base_never_took_is_not_taken_whole` in `subprojects/docket/tests/test_vcs.py` pins it.

**Generator check.** A member of `PL-2CL5`, the head for what `PL-927J`'s single landing test left unread: a deletion. Found by that head's own work.

**Built, 2026-11-11.** `taken_whole` reads `_LandingSplit.whole`, which counts a deletion the base kept as work outstanding. `PL-2CL5` has the design.
