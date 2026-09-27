---
id: PL-RH88
title: docs/ARCHITECTURE.md's routing bullet still says Editor contract and editor, where PL-GPYV renamed both to View on 2026-09-16 (#654), so a reader searching ROADMAP.md for the contract it names finds nothing
priority: P3
effort: S
status: done
classes: docs
touches: docs/ARCHITECTURE.md
added: 2026-09-26
closed: 2026-09-26
pr: 1131
verify: ! grep -qE 'Editor contract|holds one editor|bind an editor' docs/ARCHITECTURE.md && grep -q 'the View contract that replaces it' docs/ARCHITECTURE.md
---

**Problem.** docs/ARCHITECTURE.md's routing bullet still says Editor contract and editor, where PL-GPYV renamed both to View on 2026-09-16 (#654), so a reader searching ROADMAP.md for the contract it names finds nothing

**Evidence, 2026-09-26.** The bullet in `docs/ARCHITECTURE.md` that opens
"**The *whose is it* question describes the fixed layout shipped today" says an
area "holds one editor with any editor able to occupy any area", that
"`PL-TH35` is where the Editor contract that replaces it is written", that two
properties "bind an editor exactly as they bind a panel today", and, in its
dated note "*The supersession has a release, as of 2026-09-16*", that v0.6.0
"builds the Areas, the Editor contract, the Workspaces and the persistence".
`grep -c 'View contract'` finds 10 in `ROADMAP.md` and 0 in
`docs/ARCHITECTURE.md`; `grep -c 'Editor contract' ROADMAP.md` finds none.
`PL-GPYV` (done) chose View because Blender's editors predominantly edit and
this project's Areas predominantly display modelled values; the rename reached
`ROADMAP.md` in #654 and stopped there.

**Why it matters.** The bullet is the routing rule a session reads before
putting interface code somewhere, and it sends the reader to a contract by a
name nothing else in the tree uses. The dated note is not a licence to keep
the word: the rename landed the same day, and the note's claim is about what
v0.6.0 builds, which is a View contract.

**Fix.** Replace the four mentions with View and View contract, and nothing
else in the bullet. Found while working `PL-LJVD`, which surveyed the standing
documents for restatements of the release order.
