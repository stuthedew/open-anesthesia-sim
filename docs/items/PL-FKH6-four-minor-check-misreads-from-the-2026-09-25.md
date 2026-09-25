---
id: PL-FKH6
title: Four minor check misreads from the 2026-09-25 stress test: dead_ends reads a > quote line after an entry as a continuation, the recommendation marker counts 'lacks a recommendation:' as marked, possessive_section_check refuses quoting a bold lead sentence, and doc_check's line-citation check fires on an item describing a bad citation inline
priority: P3
effort: S
status: ready
classes: defect
feature: exact-gates
touches: tools/dead_ends.py, tools/possessive_section_check.py, subprojects/docket/src/docket/checks.py, tools/doc_check.py, tests/unit/test_dead_ends.py, tests/unit/test_possessive_section_check.py, subprojects/docket/tests/test_checks.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-09-25
payoff: a needs-decision brief that says it lacks a recommendation stops counting as one that marks it, and the other three misreads end fixed or recorded as the rule working
verify: grep -q 'def test_lacks_a_recommendation_does_not_mark_one' subprojects/docket/tests/test_checks.py
not-delegable: four independent parts, each closing by a fix with a test or by a recorded drop, and two look like drops; the command proves part (b) alone, the one certain to need a test, so a session closes the other three by reading them
---

**Problem.** Four minor check misreads from the 2026-09-25 stress test: dead_ends reads a > quote line after an entry as a continuation, the recommendation marker counts 'lacks a recommendation:' as marked, possessive_section_check refuses quoting a bold lead sentence, and doc_check's line-citation check fires on an item describing a bad citation inline

Each reproduced once in the fuzz harness. None has cost a session yet that the store records.

Re-confirmed 2026-09-25 against 46954a81, each in a scratch root: (a) `dead_ends.check` reports a `>` line under an entry as a continuation; (b) `_marks_recommendation` returns true for a brief saying it lacks a recommendation; (c) `possessive_section_check.sites` tells a possessive quotation of a bold lead sentence to use the section mark; (d) `check_line_citations` errors on a document describing an out-of-range line citation as an example.

Two of the four look like drops rather than fixes. (a) is the rule working: `docs/dead-ends.md` is one line per entry, and a quote line under one is emitted nowhere, which is what the check refuses. (d) already has a documented escape - `.claude/rules/citation-drift.md` says an item whose subject is a broken citation can fence it, and `_without_fences` blanks fences. (b) is a plain false pass of an advisory, and (c) a hard gate refusing a quotation that is also correct. So the `verify:` proves (b) alone, and `not-delegable:` says why.

**Generator check.** PL-GPJ7's fact, for (b), (c) and (d): each recognises its claim by wording - the word recommendation followed by a colon, a quotation matching a bold marker, a line citation inside a sentence describing one - where the sentence does not make that claim. (a) is not an instance.

**Why it matters.** Low; recorded so the class count is honest.

**Done when.** Each either fixed with a test or dropped with its reason.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
