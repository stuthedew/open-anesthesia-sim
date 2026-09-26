---
id: PL-WK57
title: claims.holdings reads a branch named claude/fix-pl-html-export-abc123 as holding PL-HTML, an item no copy of the store holds, so flight lists it as filed there and claims_nothing exempts the branch's unclaimed work from the branch-id refusal
priority: P2
effort: S
status: done
classes: defect
feature: parallel-sessions
milestone: v0.5.12
touches: subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_claims.py, tools/branch_id_check.py, tests/unit/test_branch_id_check.py, subprojects/docket/README.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
closed: 2026-09-26
pr: 1100
payoff: flight, the claims refusal and the first-edit hint read a branch name as holding an item only where a copy of the store holds its id, so a branch named for a word is asked for its claim like any other
verify: grep -q 'def named_id' subprojects/docket/src/docket/claims.py
---

**Problem.** claims.holdings reads a branch named claude/fix-pl-html-export-abc123 as holding PL-HTML, an item no copy of the store holds, so flight lists it as filed there and claims_nothing exempts the branch's unclaimed work from the branch-id refusal

Reproduced 2026-09-26 against c2be4070, in a scratch repository whose `main` holds one item, `PL-K7QX`: a branch `claude/fix-pl-html-export-abc123` carrying one commit, `PL-K7QX: the work`, that writes `src/work.py` and records no claim. `claims.holdings` returns a live `NAMED` hold on `PL-HTML` for it; `claims.claims_nothing` answers `False` for it; and `bin/docket flight` prints `PL-HTML  claude/fix-pl-html-export-abc123  live  branch name  last commit 1 day ago  filed there`. No copy of the store holds `PL-HTML`, the branch's own included, so "filed there" is false, and the branch's unclaimed work passes the refusal `tools/branch_id_check.py` asks `claims_nothing` for. The cause is one reading: `BRANCH_ID_RE` applies the store's grammar and nothing else, and `HTML`, like `CTRL`, fits the alphabet. Three readers take the name's word for it: the named-hold loop in `holdings`, the name exemption in `claims_nothing`, and `unattributed`, which also takes a subject's leading id on its grammar alone. `branch_id_check.hint` mirrors the `claims_nothing` exemption so that the hint and the refusal agree, and moves with it.

**Why it matters.** Who holds an item is the one fact `flight`, `show`, `next` and the claims refusal all read, and a name that names no item makes each of them answer with confidence about an item that does not exist. The branch it misattributes is invisible under the real item it works on.

**Done when.** A branch name holds an item only where the base's copy or the branch's own copy of the store holds its id, the rule `PL-SN2T` gave `branch_id_check`'s attribution; `claims_nothing`'s name exemption and `unattributed` read the same answer; `branch_id_check.hint` moves with the exemption; and a test holds the reproduction above.

**Generator check.** The fact misread is who holds an item now, read from a branch name without asking the store: `PL-7TVT`'s and `PL-MB2W`'s `misread:`, two spent heads, which triage should weigh as this item's home. It is `PL-SN2T`'s rule one module over, found while building `PL-SN2T` as step 4 of `PL-GPJ7`, and not folded in there: `PL-SN2T`'s `touches` reach `tools/branch_id_check.py` alone, `PL-GPJ7`'s Split confines its step 4 to the two id gates, and this changes the one reading of who holds an item that every in-flight guard answers from, so it is reviewed on its own. Nor is it a member of `PL-GPJ7`: the refusal asks `claims_nothing` for the who-holds answer rather than recognising anything itself, so what is misread is the holding, not whether a sentence makes a gate's claim.

Triage, 2026-09-26: an instance of `PL-MB2W`'s fact, "Who holds an item now,
and whether that holder is still live", filed after that head closed (`#1041`,
2026-09-26 01:22 UTC). `PL-MB2W` is the family head that takes later
instances, as `PL-7TVT`'s `generator:` line records. It is the first one filed
after the close, since `PL-7XGR` and `PL-0JDP` were filed on 2026-09-25, so the
head stays spent; a third post-close instance would count it as a generator
whose fix did not hold. What misreads the fact is a defect in the one reader
`PL-MB2W` built, not a second reader re-deriving it.

**Priority.** `P2`: the branch-id refusal is a hard gate, and this passes
unclaimed work through it silently, which is `CLAUDE.md`'s first test for
friction that compounds. `PL-SN2T`'s `P3` was the same misreading in that
tool's own attribution, where the branch was still refused by its subjects.

**Reproduced again 2026-09-26 against `db20183a`.** Four tests written ahead
of the fix fail on that `main`: `holdings` returns a live `NAMED` hold on
`PL-HTML` for the reproduction's branch, `flight` leaves out of `unattributed`
a branch whose one subject reads `PL-HTML export`,
`tools/branch_id_check.py` exits 0 on the reproduction's branch, and its
`--hint` is silent on a fresh branch of that name.

**Approach.** The rule is spelled once, as `claims.named_id`: a name's first
id, read by `BRANCH_ID_RE` as every reader reads it, where a copy of the store
holds it. `holdings` asks it of each name against the base's copy and the
branch's own tip, whose listings the loop already reads for the item's
status, and asks the same of each subject's leading ids for `unattributed`.
`claims_nothing` then exempts a branch only where `holdings` recorded a name
hold for it, so the exemption and the flight row are one answer. The hint
cannot take that answer, because a branch with no commits yet is not read by
`holdings` at all, so it asks `named_id` against the ids
`branch_id_check.held` reads from the base's copy and `HEAD`'s.

**Joined the Fix generators project's list 2026-09-26** (project owner,
2026-09-26). Asked in the project timeline whether anything else was left for
generators, the coordinator named the seven items filed overnight, this one
among them, as staying out of scope unless he added them, and the owner
answered "Add them". Recorded here by the thread that took it.
