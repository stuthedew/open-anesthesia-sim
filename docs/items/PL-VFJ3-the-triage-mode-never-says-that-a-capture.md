---
id: PL-VFJ3
title: The triage mode never says that a capture classed as debt while a gate is frozen owes a Declined entry in ROADMAP.md, which tools/doc_check.py enforces, nor that the pass should lead that commit with its own housekeeping id: #953 followed the mode, went red in checks, and its fix commit then marked the items it led with as in flight
status: untriaged
added: 2026-09-23
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
