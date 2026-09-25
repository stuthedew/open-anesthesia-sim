---
id: PL-0JGZ
title: 'Does a branch change only the queue' has two definitions - claims.in_queue counts ROADMAP.md and WORKING_NOTES.md, arming counts docs/items only - so a ROADMAP.md-only branch passes branch_id_check and shows no unclaimed row while arm holds it
priority: P3
effort: S
status: needs-decision
classes: refactor
feature: one-answer
touches: subprojects/docket/src/docket/claims.py, subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_claims.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-25 with the one-answer batch
added: 2026-09-25
---

**Problem.** 'Does a branch change only the queue' has two definitions - claims.in_queue counts ROADMAP.md and WORKING_NOTES.md, arming counts docs/items only - so a ROADMAP.md-only branch passes branch_id_check and shows no unclaimed row while arm holds it

Reproduced: `in_queue` True, `work_under_record` False; `arm` says `hold - ... changes 1 path outside docs/items`. PL-FFR0 moved one predicate into claims.py; this is the next one.

**Why it matters.** Two answers to whether a branch is captures-only decide auto-merge and the CI refusal differently.

**Re-confirmed 2026-09-25 against 46954a81**, importing `claims.in_queue` with the repository's config. `ROADMAP.md` and `docs/WORKING_NOTES.md` answer `True` to it and `False` to arming's inline test (`arm`, `path.startswith(prefix)` over `items_dir`); an item file answers `True` to both. #1015 changed how arming reads the diff and not what it counts.

**The two tests answer different questions, and each has a recorded reason.** `in_queue` decides whether a change owes a claim. It was widened to the roadmap and the notes because read as the items directory it refused 12 queue passes in a week (`PL-3CTW`, in its docstring). Arming decides whether a branch merges on green CI without review, and `arming.py`'s docstring keeps it to "item files", the words of `PL-WNCT`'s ratified decision (project owner, 2026-09-23, ratified). Neither answer is false today: `arm` names the path that holds it. The cost of the split is real, though. A triage pass that also puts an item on a roadmap gate list is held for a manual merge, and until that merge lands its item edits are invisible to other sessions' `next`. That is the shape `PL-N1JK` recorded.

**Generator check.** It is an instance of PL-PVW2's fact, which spelling of a repeated predicate is the answer. The predicate is captures-only, with a third spelling in `vcs._annotates_only` (items only), which is how `PL-GJPD`'s triage pass recorded the wrong pull request. Whether arming's spelling should become `in_queue`'s is the open question below, because it is the only one of the three whose widening changes what merges unreviewed.

**Decision needed.** Should `arm` treat a branch whose only changes are queue records (item files, `ROADMAP.md`, `docs/WORKING_NOTES.md`) as it treats an items-only branch, arming auto-merge on green CI? A yes widens what merges without the owner's review, so it reopens `PL-WNCT`'s ratified "item files". That makes it the owner's question on ordinary evidence, and the evidence is the held-triage-pass cost above.

**Recommendation:** no. Keep arming at item files and re-scope this item to what a session can do alone. Move arming's inline test into `claims.py` as a named predicate beside `in_queue`, and make each docstring say which question it answers and why the other differs. `vcs._annotates_only`, the third spelling, is left to PL-GJPD under PL-HMZZ. `ROADMAP.md` is the authoritative milestone map the owner sets direction in, so an unreviewed merge of it is a different risk from an item file. The held-pass cost is one manual merge, on the rarer shape of triage pass. Under that answer the done-when becomes: two named predicates in `claims.py`, every caller importing one of them, and a test holding the `ROADMAP.md`-only branch for each.

**Done when.** It depends on the decision above. As filed, it is one definition in claims.py that arming imports. Under the recommendation, it is the two named predicates described there.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
