---
id: PL-0B22
title: ROADMAP.md's timeline row for v0.6.x - one source of truth still says 'Not yet scoped or sized' after PL-K88Z sized it on 2026-10-19, so the row and planned-milestone item 43 disagree
priority: P3
effort: S
status: done
classes: docs
feature: one-source-of-truth
touches: ROADMAP.md, tools/doc_check.py, tests/unit/test_doc_check.py, docs/apparatus.md
added: 2026-10-24
closed: 2026-10-24
pr: 1725
payoff: the roadmap's row and its milestone item agree that the one-source-of-truth work is sized, and no sentence under the timeline can state a status that the next step of the work makes false
verify: ! grep -qF 'Not yet scoped or sized' ROADMAP.md && ! grep -qF 'are not yet scoped' ROADMAP.md && grep -q 'def check_timeline_status' tools/doc_check.py && grep -q 'def test_a_timeline_row_that_says_not_yet_is_an_error' tests/unit/test_doc_check.py
---

**Problem.** ROADMAP.md's timeline row for v0.6.x - one source of truth still says 'Not yet scoped or sized' after PL-K88Z sized it on 2026-10-19, so the row and planned-milestone item 43 disagree

**Found 2026-10-24** on `main` at `345e8bb2`. Planned-milestone item 43 in `ROADMAP.md` records the size from `PL-K88Z` in a sentence that begins "Inventoried 2026-10-19". The row for the same work in § "The timeline" still ends "Not yet scoped or sized." The row is sized now. What is still missing is the scoping, meaning a decision about which of the feature's items the row needs before it counts as done. Fix the row so it says that, and do the scoping when the feature's 13 untriaged items are triaged.

**Why it matters.** The timeline row and planned-milestone item 43 describe the same work and now disagree about whether it has been sized. A session reading only the row would size it again, or would treat the work as further from ready than it is.

**Done when.** The `v0.6.x — one source of truth` row in § "The timeline" says the work is sized and points at item 43's "Inventoried 2026-10-19" sentence for the size, and says that scoping is still to come. Scoping itself, which decides which of the feature's items the row needs, is release work and is not part of this item.

**Checked 2026-10-24.** The row still ends "Not yet scoped or sized.", and item 43 carries the size.

**Worked 2026-10-24.** The row now ends "**Inventoried 2026-10-19** by `PL-K88Z`, and item 43 records the count." It does not say that scoping is still to come, as **Done when** asked. That sentence would have been the next stale copy: scoping makes it false, and nothing would tell the scoping session to edit it. The Size column's `—` already says that the row is not scoped, as it does for the other unscoped rows.

**The cause.** The `PL-2LB5` design round wrote one fact into two places on 2026-10-19. The row said "Not yet scoped or sized", and item 43 said that `PL-K88Z`'s inventory would size the work. `PL-K88Z`'s brief then named only item 43 as the place to record the size, and its worker did exactly that. So the row held a second copy of a status, and the work that changed the status was told about one copy only. The paragraph under the table had the same shape. "Rows 9 and 11 are the intended order and are not yet scoped" would have gone false when v0.7.0 is scoped, which is the next beat on the plan.

**The fix by shape.** Neither sentence states a current status now. `check_timeline_status` in `tools/doc_check.py` fails any "not yet" under § "The timeline", in the table or in the prose under it, and asks for a dated event such as "Scoped 2026-09-16" or a condition such as "Frozen when v0.6.0 ships" instead. Run against `main`'s `ROADMAP.md` at `b2ae9e4d`, it failed exactly the two sentences, at lines 430 and 453, and nothing else. It does not read § "The planning model: a rolling wave", where "not yet scoped" defines a horizon and stays true. "Not yet scoped" had been written onto the timeline or the catalogue four times before this, on 2026-08-26 (twice), 2026-09-02 and 2026-09-16. A session rewriting that row or entry removed each one later. This copy went stale through its "sized" half, because an inventory is not a scoping and nobody rewrote the row.
