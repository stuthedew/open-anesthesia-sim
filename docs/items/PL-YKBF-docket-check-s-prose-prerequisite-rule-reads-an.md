---
id: PL-YKBF
title: docket check's prose-prerequisite rule reads an item id after a negated 'not blocked by' as a prerequisite and refuses the brief with an error - this item's own first draft was refused by it
status: untriaged
feature: exact-gates
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-25
---

**Problem.** docket check's prose-prerequisite rule reads an item id after a negated 'not blocked by' as a prerequisite and refuses the brief with an error - this item's own first draft was refused by it

Reproduced by the fuzz harness, and again by filing this item: its first draft quoted the sentence "This is not blocked by" followed by a real id, and `bin/docket check` refused the store with an error ("names ... as a prerequisite in prose and does not list it in `blocked-by`"), so the example had to be reworded to satisfy the check it reports - PL-KJ63's pattern. The rule reads any cue word within 40 characters of an id.

**Why it matters.** An advisory that fires on the opposite claim trains sessions to skim advisories.

**Done when.** A negation cue before the id suppresses it; a test holds the reproduction.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` on `claude/upbeat-heisenberg-27vafn` (PL-P0FP).
