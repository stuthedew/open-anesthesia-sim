---
id: PL-VFJ3
title: The triage mode never says that a capture classed as debt while a gate is frozen owes a Declined entry in ROADMAP.md, which tools/doc_check.py enforces, nor that the pass should lead that commit with its own housekeeping id: #953 followed the mode, went red in checks, and its fix commit then marked the items it led with as in flight
status: done
milestone: v0.5.9
added: 2026-09-23
closed: 2026-09-23
pr: 970
reason: Closed through PL-WD5Z's route 1, which removed what set off this instance. A debt capture during a freeze now owes a deferred-from: field on the item, which bin/docket check requires and whose error names the command, not a ROADMAP.md entry the triage mode never mentioned. A triage pass recording one writes only under docs/items/, which vcs._annotates_only reads as annotation, so its leading ids claim nothing in flight. The general mechanism, a claim read from a commit's shape, stays with PL-MB2W.
verify: grep -q 'def test_an_open_debt_item_the_gate_neither_places_nor_defers_is_an_error' subprojects/docket/tests/test_checks.py
---

**Problem.** The triage mode never says that a capture classed as debt while a gate is frozen owes a Declined entry in ROADMAP.md, which tools/doc_check.py enforces, nor that the pass should lead that commit with its own housekeeping id: #953 followed the mode, went red in checks, and its fix commit then marked the items it led with as in flight

**Found 2026-09-23 on `#953`.** `.claude/skills/docket/modes/triage.md` covers
fields, briefs, `verify:` and the generator check, and says nothing about the
gate. The first `checks` run failed on `tools/doc_check.py`: eleven open debt
items had no v0.6.0 disposition. The fix commit was led by three of the triaged
ids, so `bin/docket flight` then showed `PL-JD4L` - the top of `bin/docket
next` - in flight on the triage branch with no work on it. The three passes
before it filed an item for the pass (`PL-2JRC`, `PL-14QR`) and led with that,
which is the convention the mode would need to state.

**Generator check.** Two mechanisms. The first half, a debt capture made
during a freeze owing a `ROADMAP.md` entry the triage mode never mentions, is a
member of `PL-WD5Z`: the entry is owed only because the disposition lives in a
second store. The second half, the fix commit's leading ids marking the triaged
items in flight, belongs to the claim-from-commit-shape candidate that
`PL-MB2W` records unverified.
