---
id: PL-J9S0
title: branch_id_check fails a work branch that holds no claim and a claim that orders behind another live claim, and the first-edit hook says to claim
priority: P2
effort: S
status: ready
classes: defect
feature: claim-record
touches: tools/branch_id_check.py, tests/unit/test_branch_id_check.py, .claude/hooks/docket-branch-guard.sh, tests/unit/test_docket_branch_guard.py, docs/items/PL-MB2W-who-holds-an-item-is-derived-by-every-reader.md, docs/items/PL-WX87-bin-docket-claim-reads-the-clone-s-remote.md
blocked-by: PL-0TD9
deferred-from: v0.6.0 - filed after the freeze by PL-MB2W's design round (2026-09-24), and not safety or science; generator work, which the pause on new mechanisms exists for
added: 2026-09-24
payoff: part of the claim record that ends PL-MB2W's generator: one recorded fact decides who holds an item
verify: grep -qF 'this branch claims nothing' .claude/hooks/docket-branch-guard.sh && grep -q 'def test_a_work_branch_holding_no_claim_is_refused' tests/unit/test_branch_id_check.py && grep -q 'def test_a_claim_ordering_behind_another_live_claim_is_refused' tests/unit/test_branch_id_check.py && grep -q 'def test_a_legacy_commit_owes_no_claim' tests/unit/test_branch_id_check.py
---

**Problem.** branch_id_check fails a work branch that holds no claim and a claim that orders behind another live claim, and the first-edit hook says to claim

**Part of `PL-MB2W`'s design** (who holds an item is recorded as a claim; design round of 2026-09-24, in `PL-MB2W` under "Design round, 2026-09-24"). Read that section's spec before starting: this brief names only this item's slice of it.

First verify that CI's fetch-depth 0 holds every head. Fail a non-legacy branch that does work outside the queue and holds no live claim. Fail a claim that orders behind another live claim. Skip legacy commits. The check is per branch, not per id, so captured or triaged ids are never pushed into claims (`PL-3CTW`, `PL-VFJ3`). The first-edit hook adds "this branch claims nothing: `bin/docket claim <id>`" to an edit outside `items_dir`.

**Why it matters.** `PL-MB2W` is a live generator: twenty items were each a new shape of work that some reader misread, because who holds an item is inferred from commit subjects, touched paths and ref age. This item is one slice of replacing that inference with a recorded claim, and the generator stops producing members only once the slices through `PL-DDYD` land.

**Done when.**

- `tools/branch_id_check.py` fails the two cases in the brief and skips legacy commits, with tests.

**Build order.** After `PL-3FYK`.

**The fault, reproduced 2026-09-24 on `b1d1b665`.** `tools/branch_id_check.py` never mentions a claim - it reads a branch's name and its leading subject ids alone - and `.claude/hooks/docket-branch-guard.sh` does not say `this branch claims nothing`.

**Premise checked first, 2026-09-24: CI's checkout holds every head.** The `checks` job of `quality` run 35969686133 (job 107536224669, `pull_request` for `claude/epic-faraday-f4yl2h`) ran `git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules origin +refs/heads/*:refs/remotes/origin/* +refs/tags/*:refs/tags/* +<sha>:refs/remotes/pull/989/merge` into a fresh `git init`, and fetched all nine heads then on the remote, `main` included, as `origin/<name>`. So the fence can see every pushed claim; its answer is stale only by a push landing after the job's fetch. HEAD there is the detached merge commit, so the branch is named by `GITHUB_HEAD_REF` as before.

**Decided while building, and why** (this session's calls inside the ratified design, recorded so `PL-N162`'s `unclaimed:` row can read the same way):

- **"Holds no claim" is no claim in any state, not "no live claim".** A branch releases its claim by closing its item in its own copy (`RELEASING_STATUSES`), so the spec's "no live claim", read literally, fails every finished pull request. What the clause exists for is the forgetful session, which has claimed nothing at all. A claim that lapsed, was yielded or was taken over is not refused here: `flight` reports lapsed claims, `claim` refuses behind a live one, and failing CI on a lapse would block the owner's merge of a pull request that waited more than the term.
- **A branch named for its item holds it by the name** (the spec's third "other hold", `PL-TZ3R`), so it owes no claim trailer.
- **Work is a non-merge commit in `base..HEAD` whose own tree carries `CUTOVER_MARKER` and which changes a path outside `items_dir`.** A branch the reader does not offer, because its work is already on the base, owes nothing.
- **Legacy is skipped on both sides of the fence.** Only this branch's live, non-legacy claims are judged, and only non-legacy claims order against them: an old-rule hold is an inference from a subject, which is what the record replaces. `claim`'s own refusal still reads them.
- **The hook asks the check** (`tools/branch_id_check.py --hint PATH`), once per session, at the first edit of a path inside the repository and outside `items_dir`, so the hook and CI share one definition.
