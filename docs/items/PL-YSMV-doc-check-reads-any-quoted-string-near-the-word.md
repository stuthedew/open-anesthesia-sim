---
id: PL-YSMV
title: doc_check reads any quoted string near the word section as a section citation, so prose quoting a command's own output fails make check
priority: P3
effort: S
status: ready
classes: defect
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-21
payoff: prose quoting what a command printed passes make check, instead of being reworded to satisfy a check that misread it
verify: grep -q 'def test_a_quoted_command_output_is_not_a_section_citation' tests/unit/test_doc_check.py
recurrences: 2026-09-25 PL-L8VP
---

**Problem.** doc_check reads any quoted string near the word section as a section citation, so prose quoting a command's own output fails make check

**Mechanism, corrected 2026-09-21.** The title says the trigger is the word
`section`, and it is not. `CITATION_RE` in `tools/doc_check.py` matches on two
forms, neither of which mentions sections: a quoted phrase after `see` or
`under`, and a quoted phrase opening on a letter or a code span immediately
before `above` or `below`. Run against two sentences quoting a command's own
output, both matched and both would be looked up as section headings:

    The run printed "documentation: 0 errors, 0 advisories" above ...
      -> read as a citation of a heading named: documentation: 0 errors, 0 advisories

    See "docket check: 0 errors" for what a clean run prints.
      -> read as a citation of a heading named: docket check: 0 errors

**Why it matters.** The failure is a hard error on `make check` against prose
that is correct, and the remedy it implies is to reword the sentence. That has
already been paid once: `PL-KJ63` records prose being rewritten to satisfy this
check, and the `directed` branch was bounded afterwards to stop a quoted
measurement matching. Quoted command output is the same class of phrase and is
still unguarded, so the next session writing an item that shows what a tool
printed reaches the same wall and pays the same way. A check that refuses correct
content is one `CLAUDE.md` retires rather than teaches around.

**Done when.** A quoted phrase that names no heading in the documents this reads
is reported as an unresolvable citation rather than assumed to be one, or the
two forms are narrowed so that quoted tool output does not match; and a test in
`tests/unit/test_doc_check.py` holds a sentence quoting command output through a
clean run.

**Stress test, 2026-09-25 (PL-P0FP).** Two corrections and a number. `check_citations` reads the documents in `DOC_GLOBS` only - README, ROADMAP, `CLAUDE.md`, `AGENTS.md`, `docs/*.md`, `.claude/rules` and `.claude/skills` - not `docs/items/`, so an item quoting tool output does not reach this wall; a document does. And the false refusals reach past quoted output: UI labels, text in code spans and fences, an em dash against a hyphen, a heading carrying backticks (11 reproduced). The number: on all 1,647 item briefs, which this check has never filtered, the see and above/below forms matched 10 times and found 0 real stale citations. In the documents, going `§`-only costs 150 one-time rewrites and brings 264 bare `§` citations under checking, 2 of them stale today (PL-QQCD). **Recommendation:** close this under PL-GPJ7 by narrowing `CITATION_RE` to the explicit `§ "X"` form, with the rewrite scripted.
