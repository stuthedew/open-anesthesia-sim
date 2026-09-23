---
id: PL-GHHW
title: bin/docket stranded lists a commit whose change already reached main through another pull request as work that never landed, and its recover line would overwrite the newer file: #938's test port f1bf1528 arrived on main via #934, and the printed git checkout of test_cli.py would drop 97 lines main added since
status: untriaged
feature: landed-elsewhere
added: 2026-09-23
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

**Done when.** `stranded` recognises a commit whose change the base already
holds, by patch identity or by content, and does not offer a checkout that
would overwrite newer content on the base.
