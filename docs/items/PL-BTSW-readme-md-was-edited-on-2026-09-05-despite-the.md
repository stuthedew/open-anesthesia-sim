---
id: PL-BTSW
title: README.md was edited on 2026-09-05 despite the freeze, and the edit left an unwrapped line
status: untriaged
feature: project-introduction
touches: README.md
added: 2026-09-05
---

**Problem.** `.claude/rules/readme-hold.md` froze `README.md` on 2026-09-05.
`#336` (`PL-ZK9R`, confine `secrets` and `uuid` out of `core/` too) edited it
the same day, extending the list of modules `core/` may not import. The change
is factually right — the guarantee did widen — but the freeze's own instruction
for exactly this case is to file it, not fix it: "A wrong or stale statement in
`README.md` is still worth recording — file it (`bin/docket new "..."`) and say
in your reply that you did. Do not fix it in passing, and do not fix it as part
of a doc sweep." So this item is what should have been filed then.

It also left the defect the freeze exists to prevent. Rewrapping the paragraph
around the longer module list pushed one line well past the width the rest of
the file keeps:

    `docs/MODEL.md` — and nothing measured either. Like `ignore_check.py` it needs the project interpreter, though

An isolated improvement that made the document slightly worse, which is the
pattern `PL-QTN6` recorded when it froze the file.

**Why it matters.** Small on its own. It matters as the first measured instance
of the freeze not holding, one day old — see `PL-3V4N` (the freeze is a
path-scoped rule, so it cannot fire before a write no read precedes) for why it
did not hold, which is the half worth fixing.

**Where.** `README.md`, the paragraph on `tools/import_boundary_check.py`.

**Do not fix this now.** The freeze still stands and this item is subject to it.
The content is correct and only the wrapping is wrong, so there is nothing
urgent here: it is a line for `PL-N092` (rewrite README as a human-readable
introduction) to absorb, and that rewrite is parked behind `PL-XYRN` (decide
when the repository goes public). Recorded so the rewrite does not have to
rediscover it.

**Done when.** The paragraph reads correctly and wraps like the rest of the
file, as part of the README rewrite rather than as a separate edit.
