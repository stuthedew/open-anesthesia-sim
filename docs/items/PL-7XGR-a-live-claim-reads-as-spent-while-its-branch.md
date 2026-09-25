---
id: PL-7XGR
title: A live claim reads as spent while its branch holds nothing the base lacks: a branch that took another pull request's captures-only head and then claimed was not offered by vcs._unlanded_refs once that pull request squash-merged, so show dropped its IN FLIGHT line and the first-edit hook said 'this branch claims nothing' until the branch merged main
status: untriaged
feature: claim-integrity
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/claims.py
added: 2026-09-25
---

**Problem.** A live claim reads as spent while its branch holds nothing the base lacks: a branch that took another pull request's captures-only head and then claimed was not offered by vcs._unlanded_refs once that pull request squash-merged, so show dropped its IN FLIGHT line and the first-edit hook said 'this branch claims nothing' until the branch merged main

**What happened, 2026-09-25.** `PL-DR3G`'s capture was only on `claude/awesome-cray-gglruu`, whose captures-only pull request `#1019` was armed. `PL-DR3G`'s session fast-forwarded `claude/trusting-fermi-19wadt` onto that head (`589ada8a`), ran `bin/docket claim PL-DR3G` (the empty claim commit `baaa64b3`, trailer `Claim: PL-DR3G claude/trusting-fermi-19wadt cse_0116b1Y6PdQDjAwffXLEQnVM`) and pushed it by hand at 21:55Z (`PL-WX87`). `#1019` then squash-merged as `cd524cc6`. From then until the session ran `git merge origin/main` at about 22:00Z, the claim read as held by nobody. `bin/docket show PL-DR3G` printed neither `IN FLIGHT` nor "already edited", and `.claude/hooks/docket-branch-guard.sh` added "this branch claims nothing: `bin/docket claim <id>`" before the first edit outside the queue, through `tools/branch_id_check.py --hint`. After the merge, `show` printed "IN FLIGHT on this branch ... live claim, made 2026-09-25 21:55 UTC" and `--hint` printed nothing.

**Why, as far as read.** `subprojects/docket/src/docket/claims.py`'s module docstring: "A branch the base contains, or whose content it holds, is never offered by `vcs._unlanded_refs`." A branch whose only content is a capture that another pull request landed, plus an empty claim commit, is by that rule a landed branch, so every claim on it is spent. Why merging the base revived it is not established: the merge brought no content of the branch's own either. That wants reading in `_unlanded_refs` before any fix is chosen.

**Why it matters.** `.claude/skills/docket/modes/start.md` says `show`, `flight` and `next` answer from one read, so `next` would have offered `PL-DR3G` as startable in that window. That is inferred, since `next` was not run then. The shape arises whenever a session is asked to work an item whose capture is still riding another session's captures-only pull request. Captures arm at their first push and merge within minutes (`PL-WNCT`), so the item lands under a claim that was written moments before. The window lasts until the claiming session commits work of its own. The claim record exists so that a holder is never read as nobody (`PL-MB2W`), and this is a holder read as nobody.

**Done when.** A claim on a branch whose content the base holds stays live until one of the five ends in the module docstring actually happens, and a test holds the shape: branch at another branch's head, claim, that head squash-landed on the base.
