---
id: PL-WK57
title: claims.holdings reads a branch named claude/fix-pl-html-export-abc123 as holding PL-HTML, an item no copy of the store holds, so flight lists it as filed there and claims_nothing exempts the branch's unclaimed work from the branch-id refusal
status: untriaged
touches: subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_claims.py, tools/branch_id_check.py
added: 2026-09-26
---

**Problem.** claims.holdings reads a branch named claude/fix-pl-html-export-abc123 as holding PL-HTML, an item no copy of the store holds, so flight lists it as filed there and claims_nothing exempts the branch's unclaimed work from the branch-id refusal

Reproduced 2026-09-26 against c2be4070, in a scratch repository whose `main` holds one item, `PL-K7QX`: a branch `claude/fix-pl-html-export-abc123` carrying one commit, `PL-K7QX: the work`, that writes `src/work.py` and records no claim. `claims.holdings` returns a live `NAMED` hold on `PL-HTML` for it; `claims.claims_nothing` answers `False` for it; and `bin/docket flight` prints `PL-HTML  claude/fix-pl-html-export-abc123  live  branch name  last commit 1 day ago  filed there`. No copy of the store holds `PL-HTML`, the branch's own included, so "filed there" is false, and the branch's unclaimed work passes the refusal `tools/branch_id_check.py` asks `claims_nothing` for. The cause is one reading: `BRANCH_ID_RE` applies the store's grammar and nothing else, and `HTML`, like `CTRL`, fits the alphabet. Three readers take the name's word for it: the named-hold loop in `holdings`, the name exemption in `claims_nothing`, and `unattributed`, which also takes a subject's leading id on its grammar alone. `branch_id_check.hint` mirrors the `claims_nothing` exemption so that the hint and the refusal agree, and moves with it.

**Why it matters.** Who holds an item is the one fact `flight`, `show`, `next` and the claims refusal all read, and a name that names no item makes each of them answer with confidence about an item that does not exist. The branch it misattributes is invisible under the real item it works on.

**Done when.** A branch name holds an item only where the base's copy or the branch's own copy of the store holds its id, the rule `PL-SN2T` gave `branch_id_check`'s attribution; `claims_nothing`'s name exemption and `unattributed` read the same answer; `branch_id_check.hint` moves with the exemption; and a test holds the reproduction above.

**Generator check.** The fact misread is who holds an item now, read from a branch name without asking the store: `PL-7TVT`'s and `PL-MB2W`'s `misread:`, two spent heads, which triage should weigh as this item's home. It is `PL-SN2T`'s rule one module over, found while building `PL-SN2T` as step 4 of `PL-GPJ7`, and not folded in there: `PL-SN2T`'s `touches` reach `tools/branch_id_check.py` alone, `PL-GPJ7`'s Split confines its step 4 to the two id gates, and this changes the one reading of who holds an item that every in-flight guard answers from, so it is reviewed on its own. Nor is it a member of `PL-GPJ7`: the refusal asks `claims_nothing` for the who-holds answer rather than recognising anything itself, so what is misread is the holding, not whether a sentence makes a gate's claim.
