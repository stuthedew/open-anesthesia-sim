---
id: PL-75R0
title: docs/WORKING_NOTES.md still carries a thread headed "Open: the repository has no README" though PL-N092 shipped one a week ago and all four items it cites are done
priority: P3
effort: S
status: done
classes: docs
feature: project-introduction
milestone: v0.5.2
touches: docs/WORKING_NOTES.md
added: 2026-09-13
closed: 2026-09-21
pr: 867
verify: python3 tools/doc_check.py check && ! grep -q 'the repository has no README' docs/WORKING_NOTES.md
---

**Problem.** docs/WORKING_NOTES.md still carries a thread headed "Open: the repository has no README" though PL-N092 shipped one a week ago and all four items it cites are done

**Why it matters.** The thread states the opposite of the truth about a shipped,
reader-facing file. `PL-N092` (rewrite README as a human-readable introduction)
closed 2026-09-06, `README.md` is 10 KB with three commits since, and all four
ids the thread cites - `PL-WB5K`, `PL-N092`, `PL-XYRN`, `PL-4MHK` - are `done`.
The entry still reads "The root `README.md` was deleted on 2026-09-05 by the
project owner's direction... It is not a gap to be patched; it is the state the
repository holds until `PL-N092` writes a deliberate one."

That file's stated purpose is "so that a new conversation can pick up context
without re-deriving it", and this is the one shape of staleness that does not
merely go unread: a session cold-starting on it concludes the repository has no
README and can act on that - declining to update the one that exists, or
proposing to write it again.

**Where.** `docs/WORKING_NOTES.md`, the `## Open:` thread at line 821.

**Done when.** `docs/WORKING_NOTES.md` no longer states that the repository has
no README. Its own header asks for a fully resolved thread's entry to be deleted
rather than left stale, and every id this one cites is closed, so deletion is the
default; a rewrite is only right if something in it is still open.

**Found.** 2026-09-13, reviewing an outside article on long AI projects against
this repository. `PL-DG84` is the systemic form - this file's deletion policy has
no reader - and this is one of its five filed instances.
