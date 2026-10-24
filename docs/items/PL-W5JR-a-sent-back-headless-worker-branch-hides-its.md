---
id: PL-W5JR
title: A sent-back headless worker branch hides its item from bin/docket next, and the daily branch sweep keeps it, so only the owner's hand push can release the item: claude/pl-928v-worker after #1733 carried its two commits to main
status: untriaged
added: 2026-10-24
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
