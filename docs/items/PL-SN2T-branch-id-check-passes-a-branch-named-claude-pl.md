---
id: PL-SN2T
title: branch_id_check passes a branch named claude/pl-ctrl-hotkeys, reading pl-ctrl as an item id although no item PL-CTRL exists, and counts the subject 'PL-HTML export' as attribution
status: untriaged
feature: exact-gates
touches: tools/branch_id_check.py, tests/unit/test_branch_id_check.py
added: 2026-09-25
---

**Problem.** branch_id_check passes a branch named claude/pl-ctrl-hotkeys, reading pl-ctrl as an item id although no item PL-CTRL exists, and counts the subject 'PL-HTML export' as attribution

Reproduced: exit 0 on both. The check tests the id's position, never that the id names an item in the store.

**Why it matters.** A branch or commit attributed to an item that does not exist is unattributed work that reads as attributed.

**Done when.** An id in a branch name or leading a subject must resolve in the store (base or branch copy); a test holds both reproductions.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
