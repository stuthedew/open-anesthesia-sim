---
id: PL-CZXN
title: verify's 'no existing assertion removed' check REJECTs intended test rewrites: about 15 of the 17 verify --self REJECTs in main's commit messages since 2026-10-01 were waived, so decide whether diff mutation on the changed lines replaces it
status: untriaged
feature: defect-review-2026-10
added: 2026-10-19
---

**Problem.** verify's 'no existing assertion removed' check REJECTs intended test rewrites: about 15 of the 17 verify --self REJECTs in main's commit messages since 2026-10-01 were waived, so decide whether diff mutation on the changed lines replaces it

**How it was measured.** A defect review on 2026-10-19 read `docs/items` with `docket.store.read_items` and placed each item with `Item.lane(workflow_paths)`. A defect is an item whose `classes` include `defect` or `safety`. An organic defect is one filed before any head's `root-cause-of:` named it and carrying no `reenters:`. The scripts lived in the session's scratchpad and are gone, so this paragraph is the method.

**Evidence.** `git log origin/main --since=2026-10-01` bodies name `verify --self` 228 times. They record about 17 `REJECT`s, and about 15 of those come from the one check "no existing assertion removed", each explained away as an intended rewrite. Examples: #1650, #1606, #1585, #1583, #1572, #1537, #1475, #1453 and #1451. The check's heads, `PL-G21K` and `PL-4W2L` (detecting weakened tests from diff text), recorded 12 members and 3 re-entries. A hard `REJECT` that is routinely waived teaches sessions to read past `REJECT`, which `CLAUDE.md` § "Prefer deterministic tooling over repeated model work" counts as a defect in the check. The protection still matters, because a weakened simulator test is a safety risk.

**Decided** (project owner, 2026-10-19, ratified, over demoting the check to an advisory and over keeping it): replace it with `tools/diff_mutation.py`, added 2026-10-17, run on the branch's changed lines. That measures directly whether the tests still fail when the changed code is altered.

**Done when.** `verify --self` no longer runs the assertion-removed check, and a branch whose tests stop catching a mutation of its changed lines fails instead, with tests for both.
