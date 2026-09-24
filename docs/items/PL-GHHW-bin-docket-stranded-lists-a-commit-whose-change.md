---
id: PL-GHHW
title: bin/docket stranded lists a commit whose change already reached main through another pull request as work that never landed, and its recover line would overwrite the newer file: #938's test port f1bf1528 arrived on main via #934, and the printed git checkout of test_cli.py would drop 97 lines main added since
priority: P2
effort: M
status: done
classes: defect
feature: landed-elsewhere
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_vcs_silence.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, tools/left_behind_check.py, tests/unit/test_left_behind_check.py, .claude/hooks/docket-digest.sh, docs/ARCHITECTURE.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-23 triage pass
added: 2026-09-23
closed: 2026-09-23
payoff: stranded stops handing out a recovery command that would silently revert newer work on main whenever a ported fix also landed through another pull request
verify: grep -q 'def test_a_change_the_base_took_inside_a_larger_commit_is_not_left_behind' subprojects/docket/tests/test_vcs.py
root-cause-of: PL-XLQ5, PL-MBTZ, PL-PXZ3
generator: spent - the readers that report a change as unlanded work - vcs.orphaned, which stranded and the digest print, and tools/left_behind_check.py - now read one change-level test, vcs.change_landed, instead of commits, blobs or whole files; its open remainder PL-SLCC is one fixed shape, an adjacent-line edit git merges as a conflict, read in the safe direction
---

**Problem.** bin/docket stranded lists a commit whose change already reached main through another pull request as work that never landed, and its recover line would overwrite the newer file: #938's test port f1bf1528 arrived on main via #934, and the printed git checkout of test_cli.py would drop 97 lines main added since

**Found 2026-09-23, straight after #938 merged.** `bin/docket stranded` printed
this under "work its own pull request left behind":

```
claude/laughing-clarke-m1u08s  (9 files of its work already landed)
  f1bf15282  PL-1PBV: port PL-XYQW's fix for main's red replay test (795ebbf6), so this branch's CI can go green
    subprojects/docket/tests/test_cli.py
  recover: git checkout claude/laughing-clarke-m1u08s -- subprojects/docket/tests/test_cli.py
```

The change had landed. `main` held the same line through #934 before #938
merged, so the squash had nothing to carry for that file. `git show
origin/main:subprojects/docket/tests/test_cli.py` contains the ported line, and
`main`'s copy of the file is 97 lines ahead of the branch's. So the answer is
wrong, and following the printed command would silently revert other work.
That is worse than a false alarm, because the command looks like the fix.

**The same mechanism as `PL-PXZ3`**, which holds it for
`tools/left_behind_check.py` and is itself only on a branch
(`claude/affectionate-fermat-dp9uu8`). Its remedy, matching a commit to one
already on the base by `git patch-id`, is the likely answer here too. Group the
two under this item's feature when that item is recovered.

**Why it matters.** Porting a fix that is also landing elsewhere is what the
drive-to-green rules prescribe for a red base, and four branches did it on
2026-09-23 for this one test. So the shape is routine rather than rare. Every
such branch will read as having unlanded work once it merges, with a recovery
line that clobbers the file.

**The owner's direction, 2026-09-23.** In their words: "I'd rather fix it right once, then fix it twice" (project owner, 2026-09-23). Read against
this item: one test of whether the base already holds a change, called by both
`vcs.orphaned` and `tools/left_behind_check.py`, rather than one more heuristic
in each. `PL-PXZ3` is the same question in the second tool. A lead, not a
finding: test the change hunk by hunk against the base. That holds where the
base carries the change plus more, which is the case the reproduction below
shows both whole-patch and plain comparisons missing.

**Done when.** `stranded` recognises a commit whose change the base already
holds, by patch identity or by content, and does not offer a checkout that
would overwrite newer content on the base.

**Reproduced at triage, 2026-09-23, in a scratch repository, because the
original cannot be replayed:** `claude/laughing-clarke-m1u08s` has since been
restarted from `main`, and `f1bf1528` is on no ref here. Branch `port` changes
one line; `main` takes the same change plus an edit to another line in one
commit. `vcs._superseded("port", "main", ("f.txt",), ...)` returns an empty set,
so the path is outstanding, and the printed `git checkout port -- f.txt` reverts
`main`'s newer line. Neither remedy tried recognises it: `git patch-id` against
the base's commits (the squash carries more than the port), or a plain `git
apply --reverse --check` of the port's patch (its context moved). The
reverse-apply succeeds only at reduced context (`-C1`), so patch identity has to
be matched against the other pull request's own head commits, as `PL-PXZ3`'s
finding was, or content compared at line level.

[superseded 2026-09-23: recorded as the head below] **Generator check.** Shares its mechanism with `PL-PXZ3` - a change that merged
through another pull request, read as unmerged because the check compares
commits or whole files rather than the change - and the two are grouped under
`landed-elsewhere`. Two items in two tools with no shared function, so not a
generator; the drive-to-green rules make the shape routine, so a third would
make it one.

**Recorded as the head, 2026-09-23, under `PL-TH9K`.** `PL-T7Y1`'s audit
verified that landed-elsewhere is a generator by count: `PL-XLQ5`, `PL-MBTZ`,
this item and `PL-PXZ3`. `PL-R808` and `PL-BHVM` each recorded it, and both
are closed. `PL-R808` closed `spent`, and this item and `PL-PXZ3` were filed
after it, so the mechanism is live and nothing ranked it. This item states the
mechanism at the right altitude, so it carries the record.

**Recommended.** Fix the mechanism rather than the one reader. Build one
landing test that works at the level of the change, such as a patch-id
compared against the base, and have three readers use it: `stranded`,
`tools/left_behind_check.py` and the orphaned report. `PL-PXZ3` then closes
with this item. If the working session keeps this item to `stranded` alone, it
should say so here, and move the record to an item that does fix the
mechanism.

**Done 2026-09-23, as recommended: the mechanism, not one reader.** The
project owner asked for one change-level landing test read by all three
readers, with patch-id against the base as the example mechanism, and for
`PL-PXZ3` to close with it (project owner, 2026-09-23). The mechanism is a
three-way replay rather than patch-id, because this brief's own reproduction
shows patch-id cannot answer the case: the landing squash carries the port and
more, so no base commit's patch-id matches, and matching the other pull
request's own commits needs `refs/pull/*`, which a checkout does not fetch and
`orphaned` must answer without.

- **The test.** `vcs.change_landed(commit, base)` replays the commit onto a
  base commit with `git merge-tree --write-tree --merge-base=<commit>^` and
  calls it landed where the result is that base commit's own tree - the
  condition `git cherry-pick` reports as "now empty". Hunk by hunk by
  construction, so a base that edited other lines of the file does not
  confound it. It walks the base's first-parent commits since the fork that
  touch the commit's paths, oldest first, and returns the first that holds the
  change ("ever held", `_landing_split`'s rule), whose squash subject names the
  pull request. Every failure reads as not landed: a conflict, a git older
  than 2.40 (no `--merge-base`, confirmed in git's 2.40.0 release notes), a
  root or merge commit. Measured: 48 candidates, 1.1 s, for a commit forked 300
  commits back touching `vcs.py` and `test_cli.py`; paid only for a commit a
  reader would otherwise report.
- **The readers.** `vcs.orphaned` drops a commit the test clears, which is
  both `bin/docket stranded`'s "left behind" section and the digest's "Left on
  a branch after its pull request merged" line. `tools/left_behind_check.py`
  asks it of every commit past the merged head, and a branch whose only such
  commits landed elsewhere reads as clear, naming the pull request (`--all`
  lists each). The two checks now share the answer for a port, so the
  disagreement their docstrings called benign is gone.
- **The recovery line.** `format_orphaned` printed `git checkout <branch> --
  <first path>`, which overwrites whatever the base changed in that file since.
  It now prints `git cherry-pick` of the reported commits, oldest first, which
  applies only the change and stops on a conflict. This is the second half of
  the Done-when above.
- **Tests.** Real repositories in `test_vcs.py` for the test itself (this
  brief's reproduction, landed-then-rewritten, never taken, a conflict, a git
  without `--merge-base`) and for `orphaned` end to end on `#938`'s shape;
  both `orphaned` tests fail with the filter removed. A replay git does not
  answer ends the walk with `None` rather than falling through to a later
  candidate and naming the wrong pull request, pinned by its own test and by
  `change_landed`'s entry in `test_vcs_silence.py`'s sweep, which every public
  read taking a runner must join. `test_cli.py`'s stranded test pins the
  cherry-pick line in place of the checkout it pinned.

**The residue** is `PL-SLCC`: git merges adjacent-line changes as one hunk, so
a port whose landing squash also edited the neighbouring line still conflicts
and still reads as left behind - the safe direction, and recall only.

**Readers deliberately not converted.** `_work_already_on_base` (in-flight and
stranded refs) and `landed_whole` (`docket branch`'s verdict) still read blobs.
Neither reports work as lost: the first keeps a ref in the report, where an id
the base took or closed already drops it, and the second decides
`MERGE`/`LANDED`. Converting them would put a replay per commit on every
in-flight ref at every `docket next`; a member arriving through either is the
evidence that it should be.
