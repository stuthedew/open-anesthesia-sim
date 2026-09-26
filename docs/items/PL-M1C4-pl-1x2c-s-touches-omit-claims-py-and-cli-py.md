---
id: PL-M1C4
title: PL-1X2C's touches omit claims.py and cli.py, where the carrier line is chosen: claims._editing keeps the first branch per item and never excludes the reader's own, and cmd_show takes one QueueEdit with next(), so the fix cannot be made inside its declared files
status: done
added: 2026-09-26
closed: 2026-09-26
pr: 1039
verify: grep -Eq '^touches: .*claims\.py.*cli\.py' docs/items/PL-1X2C-bin-docket-show-names-the-reader-s-own-branch.md
---

**Problem.** PL-1X2C's touches omit claims.py and cli.py, where the carrier line is chosen: claims._editing keeps the first branch per item and never excludes the reader's own, and cmd_show takes one QueueEdit with next(), so the fix cannot be made inside its declared files

**Found 2026-09-25** choosing slam-dunk batch 2, which passed `PL-1X2C` over
for this reason. `PL-1X2C` declares `render.py`, `vcs.py` and `test_cli.py`.
`subprojects/docket/src/docket/claims.py` `_editing` builds one `QueueEdit`
per item with `edited.setdefault`, the first branch in ref order, and reads
nothing about the current branch there; `subprojects/docket/src/docket/cli.py`
`cmd_show` then takes one edit with `next(...)`. Naming every other carrier and
dropping the reader's own branch needs both files, so the item's `touches`
wants widening at triage before a worker held to them can take it.

**Worked.** 2026-09-26, on `claude/pl-batch-03-viadw6`. The project owner chose
to widen `PL-1X2C`'s `touches` on slam-dunk batch 3's decision card, and the
commit closing this item makes that edit: `claims.py` and `cli.py` in, `vcs.py`
out, with the decision recorded in `PL-1X2C`'s brief. That was all this item
asked, so it closes with it.
