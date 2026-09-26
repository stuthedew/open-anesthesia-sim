---
id: PL-7XGR
title: A live claim reads as spent while its branch holds nothing the base lacks: a branch that took another pull request's captures-only head and then claimed was not offered by vcs._unlanded_refs once that pull request squash-merged, so show dropped its IN FLIGHT line and the first-edit hook said 'this branch claims nothing' until the branch merged main
priority: P2
effort: M
status: ready
classes: defect
feature: claim-integrity
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_claims.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-26 triage pass
added: 2026-09-25
payoff: a claim on a branch whose only content another pull request has landed keeps its item held, so next, show and the first-edit hook never read a claimed item as free once a captures-only pull request merges
verify: grep -q 'def test_a_claim_on_a_branch_whose_only_content_another_pull_request_landed_stays_live' subprojects/docket/tests/test_claims.py
---

**Problem.** A live claim reads as spent while its branch holds nothing the base lacks: a branch that took another pull request's captures-only head and then claimed was not offered by vcs._unlanded_refs once that pull request squash-merged, so show dropped its IN FLIGHT line and the first-edit hook said 'this branch claims nothing' until the branch merged main

**What happened, 2026-09-25.** `PL-DR3G`'s capture was only on `claude/awesome-cray-gglruu`, whose captures-only pull request `#1019` was armed. `PL-DR3G`'s session fast-forwarded `claude/trusting-fermi-19wadt` onto that head (`589ada8a`), ran `bin/docket claim PL-DR3G` (the empty claim commit `baaa64b3`, trailer `Claim: PL-DR3G claude/trusting-fermi-19wadt cse_0116b1Y6PdQDjAwffXLEQnVM`) and pushed it by hand at 21:55Z (`PL-WX87`). `#1019` then squash-merged as `cd524cc6`. From then until the session ran `git merge origin/main` at about 22:00Z, the claim read as held by nobody. `bin/docket show PL-DR3G` printed neither `IN FLIGHT` nor "already edited", and `.claude/hooks/docket-branch-guard.sh` added "this branch claims nothing: `bin/docket claim <id>`" before the first edit outside the queue, through `tools/branch_id_check.py --hint`. After the merge, `show` printed "IN FLIGHT on this branch ... live claim, made 2026-09-25 21:55 UTC" and `--hint` printed nothing.

**Why, as far as read.** `subprojects/docket/src/docket/claims.py`'s module docstring: "A branch the base contains, or whose content it holds, is never offered by `vcs._unlanded_refs`." A branch whose only content is a capture that another pull request landed, plus an empty claim commit, is by that rule a landed branch, so every claim on it is spent. Why merging the base revived it is not established: the merge brought no content of the branch's own either. That wants reading in `_unlanded_refs` before any fix is chosen.

**Premise confirmed by reading, 2026-09-26, against `78b1a02b`.** The module
docstring still says a branch "whose content it holds, is never offered", and
`vcs._work_already_on_base` still reads a ref as landed when every blob it adds
is one the base has held. The same reading also explains the revival.
`vcs._work_already_on_base` says "A ref introducing nothing has an empty landed
side and reads as not landed", and `vcs._landing_split` compares the ref's tree
with the tree it forked from. Once the branch had merged `main`, it forked at
the base's tip and added no blob beyond it, so it read as unlanded again and
its claim was read. Not yet reproduced against a scratch repository.

**Why it matters.** `.claude/skills/docket/modes/start.md` says `show`, `flight` and `next` answer from one read, so `next` would have offered `PL-DR3G` as startable in that window. That is inferred, since `next` was not run then. The shape arises whenever a session is asked to work an item whose capture is still riding another session's captures-only pull request. Captures arm at their first push and merge within minutes (`PL-WNCT`), so the item lands under a claim that was written moments before. The window lasts until the claiming session commits work of its own. The claim record exists so that a holder is never read as nobody (`PL-MB2W`), and this is a holder read as nobody.

**Done when.** A claim on a branch whose content the base holds stays live until one of the five ends in the module docstring actually happens, and a test holds the shape: branch at another branch's head, claim, that head squash-landed on the base.

[superseded 2026-09-26: PL-MB2W closed in #1041 before this was placed] **Where it goes, open for the project owner.** `PL-NZC0`'s Order list sequences `PL-KX73`, `PL-1X56` and `PL-ZLJ9` before the `PL-MB2W` close-out, which "should not close while the record it built carries them". This is another defect in that record: `vcs._unlanded_refs` and `claims.holdings` read a live claim as spent. The brief lists those three under Stream B, but at 22:08Z on 2026-09-25 the trial's coordinator reported "PL-KX73 running in Stream A". So the streams have been rebalanced since the brief was written, and this names no stream. **Recommendation:** add it to the Order list after `PL-ZLJ9` and before the `PL-MB2W` close-out, in whichever stream carries the claim fixes, for the reason the trial already gives for the other three. It changes `claims.py`, which those fixes change in sequence. Whether its `vcs.py` change meets another stream's build is for the coordinator to check against the list. The cost is one more thread before the close-out. Leaving it out lets `PL-MB2W` close with a known way for its record to read a holder as nobody.

**Generator check.** A misreading of `PL-MB2W`'s fact, "Who holds an item now,
and whether that holder is still live". It was filed 2026-09-25, before
`PL-MB2W` closed on 2026-09-26 (#1041), and that close-out did not take it into
its `root-cause-of:`, so it is not a post-close instance. It is triaged as an
ordinary defect in the record `PL-MB2W` built.
