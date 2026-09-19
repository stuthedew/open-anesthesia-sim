---
id: PL-QMC0
title: bin/docket release re-derives an item file's slug while stamping milestone:, so PL-5QLP's rename is not confined to bin/docket record: cutting v0.4.28 moved PL-XQRK's file and the fix has to cover every writer
priority: P2
effort: M
status: blocked
classes: defect
feature: slug-rename-on-write
touches: subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/store.py, docs/items
blocked-by: PL-JF5Z
added: 2026-09-19
---

**Problem.** bin/docket release re-derives an item file's slug while stamping milestone:, so PL-5QLP's rename is not confined to bin/docket record: cutting v0.4.28 moved PL-XQRK's file and the fix has to cover every writer

**Found while cutting v0.4.28** (`PL-T2LH`). `bin/docket release` writes
`milestone:` into every item it stamps, and for `PL-XQRK` the write moved the
file: `PL-XQRK-a-session-cannot-delete-a-remote-branch-git.md` became
`PL-XQRK-a-session-cannot-delete-a-remote-branch-so.md`, because the slug is
re-derived from a title that had been edited on `main` without the file being
renamed. Confirmed byte-identical apart from the stamp, so the rename is the
whole of it; `git status` reported a delete plus an untracked add, which is the
shape `PL-5QLP` records for `bin/docket record`.

**Why it is not just an instance of `PL-5QLP`.** That item names `record` and
the `pr:` write. This is a second writer, reached by a different command, on a
different field — and `release` stamps *every* finished item at once, so where
`record` moves one file a cut can move many. A fix scoped to `record` leaves
the larger case standing. Whether the answer is to stop re-deriving the slug on
write, or to rename deliberately and stage both sides, is `PL-5QLP`'s question
to settle; this item is the scope that answer has to cover.

**Blocked on reading `PL-5QLP`, which is not in this checkout.** It exists only
on `origin/claude/tender-keller-omy3ec` — `PL-JF5Z` is the recovery.

**Why it matters.** The delete-plus-add is invisible until two sessions write
the same item and git is expected to merge them: `PL-5QLP` records that the
merge the tooling promises is not the merge git performs, and that reverting
with `git checkout` leaves a duplicate-id error. A release cut is the write
most likely to hit many items at once and the one least likely to be reviewed
file by file, so it is where a silent rename does the most damage.
