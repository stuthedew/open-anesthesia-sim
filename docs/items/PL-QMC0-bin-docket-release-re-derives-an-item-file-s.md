---
id: PL-QMC0
title: bin/docket release re-derives an item file's slug while stamping milestone:, so PL-5QLP's rename is not confined to bin/docket record: cutting v0.4.28 moved PL-XQRK's file and the fix has to cover every writer
priority: P2
effort: S
status: done
classes: defect, infra
feature: slug-rename-on-write
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-19
closed: 2026-09-19
pr: 708
verify: grep -q 'def test_a_cut_does_not_rename_the_files_it_stamps' subprojects/docket/tests/test_cli.py
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

**Fixed 2026-09-19, with `PL-LBR6`.** The stamp loop in `cmd_release` now
calls `store.rewrite_item` rather than `store.write_item(replace=...)`, so a
cut stamps `milestone:` without moving any file. This was the worse of the two
cases as the brief says: `record` moves one file and a cut moves as many as it
stamps, into the commit a release tag points at - `PL-XQRK` in the v0.4.28 cut
is the observed instance.

`test_a_cut_does_not_rename_the_files_it_stamps` pins it. It failed before the
change; `_interrupt_after`, which stops the stamp loop part way to stand for a
lost container, was retargeted to the same writer so the interrupted-cut tests
still interrupt what the loop now calls.

**The decision this item deferred to `PL-5QLP` was already taken.** Stop
re-deriving the slug on write, rather than rename deliberately and stage both
sides: `store.rewrite_item`'s docstring records it against `PL-LBR6` and
`PL-YTDN`, and bringing a drifted name back into line stays its own pass
(`PL-YTDN`, still open, 7 files). Nothing new was settled here - two callers
were brought to a decision the store had already encoded.
