---
id: PL-5748
title: docs/WORKING_NOTES.md's PL-009 playback-speed thread still states the pre-PL-010 frame cost (~17 ms, of which ~15 ms chart-point construction) as current, and describes PL-010's point reuse as headroom still to spend, though it landed 2026-09-02 and the frame now costs 2.6 ms
priority: P3
effort: S
status: ready
classes: docs
feature: dev-tooling
touches: docs/WORKING_NOTES.md
added: 2026-09-07
verify: python3 tools/doc_check.py check && ! grep -qF 'frame currently costs ~17 ms' docs/WORKING_NOTES.md
---

**Problem.** docs/WORKING_NOTES.md's PL-009 playback-speed thread still states the pre-PL-010 frame cost (~17 ms, of which ~15 ms chart-point construction) as current, and describes PL-010's point reuse as headroom still to spend, though it landed 2026-09-02 and the frame now costs 2.6 ms

**Why it matters.** `docs/WORKING_NOTES.md`'s own preamble asks that an entry be
written so a reader with no memory of the originating conversation can act on
it. This entry now tells that reader the frame costs ~17 ms and that `PL-010`'s
point reuse is headroom still to spend, when `PL-010` landed 2026-09-02 and the
frame costs 2.6 ms. Both halves mislead in the same direction: they describe
optimization work as available that has already been taken, so a session reading
it would go looking for a win that is spent.

Low consequence - nothing clinical, and no check reads it - but it is the second
`WORKING_NOTES` entry found stale in the same sweep (`PL-60CQ` is the other),
which is the argument for closing resolved threads rather than amending them.

**Done when.** The `PL-009` thread either carries the current frame cost or, if
the thread is resolved, is deleted per `CLAUDE.md`'s rule for a resolved thread
with its outcome recorded wherever it belongs.
