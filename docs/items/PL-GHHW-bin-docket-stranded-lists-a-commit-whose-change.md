---
id: PL-GHHW
title: bin/docket stranded lists a commit whose change already reached main through another pull request as work that never landed, and its recover line would overwrite the newer file: #938's test port f1bf1528 arrived on main via #934, and the printed git checkout of test_cli.py would drop 97 lines main added since
priority: P2
effort: M
status: ready
classes: defect
feature: landed-elsewhere
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-23 triage pass
added: 2026-09-23
payoff: stranded stops handing out a recovery command that would silently revert newer work on main whenever a ported fix also landed through another pull request
verify: grep -q 'def test_a_change_the_base_took_inside_a_larger_commit_is_not_left_behind' subprojects/docket/tests/test_vcs.py
root-cause-of: PL-XLQ5, PL-MBTZ, PL-PXZ3
generator: live - a change that merged through another pull request is read as unmerged because each check compares commits or whole files rather than the change; PL-PXZ3 and this item were filed after PL-R808 closed spent, in two tools with no shared function, after PL-XLQ5 and PL-MBTZ in a third
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
