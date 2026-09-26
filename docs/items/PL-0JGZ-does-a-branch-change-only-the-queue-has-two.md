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

**Changed by `PL-K6B2`, 2026-09-25.** Arming's side of the title no longer counts `docs/items` only: `arm` now arms a branch whose every path is under `docs/items/` or `subprojects/docket/`, `arming.py` excepted (`arming.TOOLING`, `arming.GATE`). The two definitions still disagree, now on `subprojects/docket/` as well as on `ROADMAP.md` and `docs/WORKING_NOTES.md`.

**Answered 2026-09-26: no, keep arming at its own scope** (project owner, 2026-09-26, ratified, over widening `arm` to treat `ROADMAP.md` and `docs/WORKING_NOTES.md` as queue records). The owner agreed with the recommendation above on a decision card in the Fix generators project. The done-when is therefore the recommendation's: two named predicates in `claims.py`, every caller importing one of them, and a test holding the `ROADMAP.md`-only branch for each. Recorded here by the `PL-PVW2` build thread so the answer does not live only on the card; the status moves when the item is taken.

**Reopened 2026-09-26, on where arming's predicate lives.** The done-when above puts both named predicates in `claims.py`, with `arming` importing its own from there. A ratified decision of the same day refuses that import: `PL-F6MM` (project owner, 2026-09-26, ratified, over `arming` importing `claims.RECORDS`) keeps arming's path set in `arming.py`, because the gate holds `arming.py` for a read so that it cannot loosen itself, while `claims.py` arms on green (`arming.TOOLING`, `PL-K6B2`). Moved into `claims.py`, a one-line widening of what arms would merge unread and then arm whatever it newly admitted. `test_the_gate_keeps_its_own_copy_of_the_body_records` in `subprojects/docket/tests/test_claims.py` pins that decision. The case ratified above was written before `PL-K6B2` and did not carry that cost, so this is a ratified decision reopened on ordinary evidence.

**Decision needed.** Should arming's named predicate live in `arming.py`, the held module, rather than in `claims.py` beside `in_queue`?

**Recommendation:** yes, `arming.py`. Name arming's inline test there as `arming.arms_on_green`, have `arm` call it, and make each docstring name the other and the question it answers: `in_queue` whether a change owes a claim, `arms_on_green` whether it merges on green CI without the owner's read. `test_a_roadmap_only_branch_is_queue_work_but_not_armable` stays in `test_claims.py`, where `PL-PVW2`'s `verify:` names it, and asks both. It costs the side-by-side placement: the two definitions sit in two modules, and the cross-referencing docstrings carry what placement would have shown. The alternative keeps the done-when as written and reverses `PL-F6MM`, putting the rule for what merges unread outside the one file whose every change waits on a read. Under the recommendation the done-when is: `claims.in_queue` and `arming.arms_on_green`, each docstring naming the other, `arm` calling the second, and that test asking both about a `ROADMAP.md`-only branch.
