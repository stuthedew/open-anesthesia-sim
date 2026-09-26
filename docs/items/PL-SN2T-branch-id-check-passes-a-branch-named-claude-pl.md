---
id: PL-SN2T
title: branch_id_check passes a branch named claude/pl-ctrl-hotkeys, reading pl-ctrl as an item id although no item PL-CTRL exists, and counts the subject 'PL-HTML export' as attribution
priority: P3
effort: S
status: done
classes: defect
feature: exact-gates
milestone: v0.5.12
touches: tools/branch_id_check.py, tests/unit/test_branch_id_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-25 triage pass
added: 2026-09-25
closed: 2026-09-26
pr: 1094
payoff: a branch or commit whose PL- token names no item stops passing the attribution check as though it named one
verify: grep -q 'def test_a_branch_named_for_an_id_the_store_does_not_hold_is_unattributed' tests/unit/test_branch_id_check.py && grep -q 'def test_a_subject_leading_with_an_id_the_store_does_not_hold_is_unattributed' tests/unit/test_branch_id_check.py
recurrences: 2026-09-26 PL-WK57
---

**Problem.** branch_id_check passes a branch named claude/pl-ctrl-hotkeys, reading pl-ctrl as an item id although no item PL-CTRL exists, and counts the subject 'PL-HTML export' as attribution

Reproduced: exit 0 on both. The check tests the id's position, never that the id names an item in the store.

Re-confirmed 2026-09-25 against 46954a81: `attribution('claude/pl-ctrl-hotkeys', ['PL-HTML export'])` returns `branch name carries PL-CTRL` and `a commit subject leads with PL-HTML`, and the store holds neither id. Both regexes, `vcs.BRANCH_ID_RE` and `vcs.LEADING_IDS_RE`, already apply the store's alphabet; `CTRL`, `HTML` and any other four-letter word without a vowel fit it, so the grammar alone is not an exact rule here and existence in the store is.

**Generator check.** The fact misread is whether a branch name or subject makes the attribution claim, recognised by an id-shaped token - `PL-GPJ7`'s `misread:`, and a member of it correctly, with one refinement for the head: the id grammar its done-when names is already what this check applies, and it passes English words, so the exact rule for attribution is an id the store holds.

**Why it matters.** A branch or commit attributed to an item that does not exist is unattributed work that reads as attributed.

**Done when.** An id in a branch name or leading a subject must resolve in the store (base or branch copy); a test holds both reproductions.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
