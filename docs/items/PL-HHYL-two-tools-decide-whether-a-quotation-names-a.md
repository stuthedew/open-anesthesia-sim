---
id: PL-HHYL
title: Two tools decide whether a quotation names a heading - doc_check._cites_heading strips a trailing period and compares case-sensitively, possessive_section_check keeps the period and casefolds - so "Known limitations." cites the heading in one and not the other
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
milestone: v0.5.26
touches: tools/doc_check.py, tools/possessive_section_check.py, tests/unit/test_possessive_section_check.py, ROADMAP.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
closed: 2026-10-18
pr: 1527
payoff: a section citation resolves to the same heading in both checks that read one
verify: grep -q 'def test_a_trailing_period_cites_the_heading_as_doc_check_reads_it' tests/unit/test_possessive_section_check.py
---

**Problem.** Two tools decide whether a quotation names a heading - doc_check._cites_heading strips a trailing period and compares case-sensitively, possessive_section_check keeps the period and casefolds - so "Known limitations." cites the heading in one and not the other

- `doc_check._cites_heading` beside `possessive_section_check.sites`. On the quotation "Known limitations." against the heading "Known limitations", doc_check strips the period and matches, and possessive_section_check does not. It also casefolds where doc_check does not, and accepts no `:` or `-` prefix boundary.

**Why it matters.** Each copy is held to the others by nothing, so the first input they part on is answered one way by docket and another by the hook or check a session trusts at that moment; every pair below was read at both sites by the sweep, and the parting input is the sweep's reading, to re-confirm at start.

**Done when.** One function decides a heading citation for both checks, and a test pins the trailing period.

**Generator check.** A member of `PL-5DZ8`, filed by that head's closing sweep on 2026-10-12 and named in its `root-cause-of:`. The fact is the head's: which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it. It is neither a post-close instance nor a new generator.
