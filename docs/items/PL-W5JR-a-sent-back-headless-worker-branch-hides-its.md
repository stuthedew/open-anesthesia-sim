---
id: PL-W5JR
title: A sent-back headless worker branch hides its item from bin/docket next, and the daily branch sweep keeps it, so only the owner's hand push can release the item: claude/pl-928v-worker after #1733 carried its two commits to main
priority: P2
effort: S
status: ready
classes: defect
feature: worker-runs
touches: tools/branch_sweep.py, tests/unit/test_branch_sweep.py
added: 2026-10-24
payoff: a sent-back worker branch is named for deletion, so its item returns to bin/docket next instead of hiding as in flight
verify: grep -q 'def test_a_sent_back_worker_branch_is_listed_for_deletion' tests/unit/test_branch_sweep.py
reenters: PL-BHVM
---

**Problem.** A sent-back headless worker branch hides its item from bin/docket next, and the daily branch sweep keeps it, so only the owner's hand push can release the item: claude/pl-928v-worker after #1733 carried its two commits to main

**Observed 2026-10-24.** `docs/maintainer.md` § "Spend the monthly API credit
on delegable items" says to carry a sent-back branch's two record commits to a
branch of their own. #1733 did that for `PL-928V`, and #1736 then set the item
back to `ready`. The worker branch `claude/pl-928v-worker` (tip
`3ed6a9e72e2d3b7cfbee66fcf25f9457cdb70c5c`) is still on the remote, and two
readers misread it:

- `python3 tools/branch_sweep.py` keeps it, giving "unfinished work on
  PL-928V; an edit to PL-928V, open on main, that main lacks". The carried
  commits have new shas, and the reviewing session edited the same item file
  after them, so the branch's copy never matches `main`'s.
- `bin/docket next` excludes `PL-928V` as already in flight once its open pull
  request merges, by the branch's name, as it does `PL-TBQS` ("live branch
  name").

So every sent-back run hides its item from `next` until the owner deletes the
branch with the hand push in `.claude/skills/docket/modes/capture.md`, because
a session's delete push is refused with HTTP 403. The procedure's last step
could say so, or the sweep could treat a worker branch whose run record is
reviewed `sent-back` on `main` as finished.

**Checked 2026-10-24.** `git ls-remote origin refs/heads/claude/pl-928v-worker` prints nothing, so the owner has since deleted the branch and `bin/docket flight` no longer lists `PL-928V`. This instance is resolved; the mechanism is not, and the next sent-back run will meet it.

**Why it matters.** Each sent-back worker run hides its item from `bin/docket next` until the owner happens to delete the branch by hand, and `tools/branch_sweep.py` never names the branch for deletion, so nothing prompts the owner to. An item can sit invisible indefinitely while it reads as in flight.

**Route decided 2026-10-24 at triage: teach the sweep, not the procedure.** A last step in `docs/maintainer.md` relies on the owner remembering it after every run. Instead, `tools/branch_sweep.py` treats a worker branch whose run record on `main` is reviewed `sent-back` as finished, so it lists the branch for deletion in the reply the owner already reads.

**Done when.** `tools/branch_sweep.py` lists a worker branch whose run record on `main` is reviewed `sent-back` as finished rather than as unfinished work, and `tests/unit/test_branch_sweep.py` has `test_a_sent_back_worker_branch_is_listed_for_deletion`.

**Generator check.** An instance of the fact "whether the base already holds or has superseded a branch commit's change, by whatever route", which `PL-BHVM`'s `misread:` states. The carried commits have new shas, so the sweep compares file content and finds `main`'s copy different. `PL-BHVM` closed on 2026-09-19. Recorded as `reenters: PL-BHVM`.
