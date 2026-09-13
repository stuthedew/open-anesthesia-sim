---
id: PL-TTMF
title: PL-6BDX's title names two expired refs and the live instance this item was filed on has cleared too, so the item now reproduces nothing while the defect it describes is unfixed
priority: P2
effort: S
status: ready
classes: defect, docs
feature: parallel-sessions
touches: docs/items/PL-6BDX-two-shipped-items-are-reported-in-flight-in.md
added: 2026-09-12
verify: python3 tools/doc_check.py check && ! grep -qF 'PL-GVXP (v0.4.7) and PL-S5LB (v0.4.6)' docs/items/PL-6BDX-two-shipped-items-are-reported-in-flight-in.md
---

**Problem.** PL-6BDX's title names two refs that no longer exist while the defect has a live instance today: the digest reports PL-3Z9X in flight under 'do not start these again' though it is done, closed and shipped in v0.4.14

**Confirmed at triage, 2026-09-12.** `bin/docket flight` after a fetch reports
two items, `PL-XLQ5` and `PL-Y31G`, both open and both on
`origin/claude/ready-vcs-batch-closure-xrvfya`, which is live work rather than an
instance of this defect. Neither `PL-GVXP` nor `PL-S5LB` appears - their branch
refs are gone - and `PL-3Z9X`, the live instance this item was filed on, no
longer appears either. So `PL-6BDX` currently has **no** instance at all: the
two in its title are dead and the one in this title has cleared since filing.

**Why it matters.** `PL-6BDX` is open at `ready` with a `verify:` command, and it
is the item a session picks up expecting to reproduce a defect by fetching and
running `flight`. It will reproduce nothing, and the brief gives it no way to
tell "fixed" from "no instance this week" - the store happens to be clean, which
is the same trap `PL-KBD0` fell into and `PL-PQQ2` records.

The defect itself has not been fixed. Nothing has changed in how the in-flight
mark reads branch refs; the refs that produced the false positives were deleted
by something else. So dropping the item would be wrong for the reason `PL-KBD0`
already states: the defect is that nothing notices, and an empty store this week
is not evidence.

**Done when.** `PL-6BDX`'s title and brief describe the defect rather than the
two expired instances, say explicitly that a clean `flight` is not evidence the
defect is gone, and carry a `verify:` that fails on the mechanism rather than on
whichever ref happened to be stale when it was written - or the item is dropped
with the reason recorded, if the mechanism turns out to have been fixed since.
