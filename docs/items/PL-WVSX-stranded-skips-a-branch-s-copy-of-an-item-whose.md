---
id: PL-WVSX
title: stranded skips a branch's copy of an item whose blob the default branch's history ever held, because its item filter reads _base_blobs' ever-held set: a branch that restores an item file to an earlier version, reopening a closed item for one, reads as behind the base, so its change is never reported if the branch is abandoned (reasoned from the code 2026-09-27, not yet run)
priority: P3
effort: S
status: ready
classes: defect
feature: pre-fork-content
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-27
payoff: an abandoned branch whose only change restores an item to an earlier version is reported by stranded instead of being lost with the branch
verify: grep -q 'def test_stranded_reports_a_branch_restoring_an_item_to_an_earlier_version' subprojects/docket/tests/test_vcs.py
---

**Problem.** stranded skips a branch's copy of an item whose blob the default branch's history ever held, because its item filter reads _base_blobs' ever-held set: a branch that restores an item file to an earlier version, reopening a closed item for one, reads as behind the base, so its change is never reported if the branch is abandoned (reasoned from the code 2026-09-27, not yet run)

**A member for `PL-927J`'s head.** `PL-927J`, filed on
`claude/vibrant-heisenberg-vhf99e` and not yet on main, records PL-GHHW's
misread producing again through `PL-8BR0`, `PL-RLTK` and `PL-P64J`; this is the
same misread in `stranded`. It bears on whether that head is recorded live or
spent: after `PL-RLTK`'s fix `_base_blobs` has two readers left,
`claims._landed_through` (`PL-P64J`) and this filter, and each now holds an
item. `PL-P813`, a head filed for it in the session that fixed `PL-RLTK`, was
dropped as a duplicate once `PL-927J` was found.

**Reproduced 2026-09-27**, by a scratch test built on the docket suite's
fixtures and not committed: a branch that restores an item file's prose to an
earlier version `main` held is not reported by `stranded`, though `_standing`
reads the copy as `ahead`; with `_base_blobs` patched to return nothing, it is
reported, so the ever-held filter is the only cause. Controls that pass: a
branch writing new content is reported, and a stale branch forked before `main`
changed the item is not. It lives in `stranded` in
`subprojects/docket/src/docket/vcs.py`: `held = _base_blobs(...)`, and the skip
on `blob in held`.

**Two corrections to the brief.** The title's own example, a restore that
reopens a closed item, is hidden twice: `_standing` reads it as `behind` by its
closure rule, which its docstring accepts as a known miss at two reopenings in
1,377 items, so dropping the blob filter alone does not report it. And the
filter cannot simply go: the stale branch in the control holds the same blob as
the restoring branch, and without the filter it is reported, wrongly. Only
history tells them apart - whether the branch itself wrote that blob after its
fork.

**Why it matters.** `stranded` is the safety net for work a session left on a
branch: whatever it skips is lost with the branch when that branch is abandoned
or swept. A restore is a real change to an item, and one nothing else reports.

**Done when.** `stranded` reports a branch's copy of an item that restores an
earlier version of the file, where the branch wrote that blob after its fork,
and still leaves out the stale branch the control pins; for a restore that
reopens a closed item, the fix either reports it or says in `_standing`'s
docstring why it stays unreported; and a test pins each case.

**Generator check.** A member of `PL-927J`, as `PL-P64J` is: the same family
fact in `stranded`'s item filter.
