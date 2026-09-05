---
id: PL-KJ63
title: doc_check reads any double-quoted phrase in a doc as a section citation, so quoting a measured figure hard-fails the check
priority: P3
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-05
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_a_quoted_measurement_before_above_is_not_a_citation' tests/unit/test_doc_check.py
---

**Problem.** `tools/doc_check.py`'s dangling-citation check treats a
double-quoted phrase in a documentation file as a citation of a section
heading in that file. Quoting anything else in prose therefore hard-fails the
check. Observed 2026-09-05 writing a measurement into
`docs/WORKING_NOTES.md`: the sentence contrasted a new figure with the old one
it replaced, quoting the old one as it appears in the note, and `make
doc-check` failed with

    docs/WORKING_NOTES.md:504: cites section "~88-256 B each" in this file,
    which has no such heading

**Why it matters.** It is a hard error rather than an advisory, so it stops a
commit, and the fix is to reword prose that was not wrong - here, to swap the
quotes for backticks. `CLAUDE.md`'s standard for a check is that it "earns its
place every run, or it is retired", and that hard failure is reserved for exact
rules; "a quoted phrase is a section citation" is a heuristic wearing a hard
rule's clothes. The cost is not the one-line fix but the incentive: a session
that meets this twice starts avoiding quotation marks in documentation, which
is a prose change made to satisfy a checker.

**Same family as `PL-WTQ1`** (doc_check's math-rendering check reads a regex in
an item's `verify:` command as LaTeX and hard-fails), which is the same shape -
a syntactic heuristic applied to text that is not making the claim the checker
assumes. Worth deciding together.

**Narrower than the title says, measured at triage 2026-09-05.**
`CITATION_RE` (`tools/doc_check.py:246`) already restricts the reading to the
two forms this repository writes - a phrase after `see` or `under`, and a phrase
immediately before `above` or `below` - and its own comment says a bare quoted
phrase is left alone. The observed failure was the second form:
`docs/WORKING_NOTES.md:504` read the figure in quotes followed by `above`, and
now reads it in backticks. So the defect is real and smaller than the title
claims - a quoted *value* followed by a direction word, which is ordinary prose,
is read as a citation - and the fix is that case, not every quoted phrase.

**Where.** `tools/doc_check.py`, the citation check.

**Done when.** A quoted phrase that is plainly not a section citation does not
fail the check - by narrowing what counts as a citation, by exempting a
recognisable non-citation, or by demoting this case to an advisory - and a test
covers the observed line.

**Found.** Recording the `PL-8GLL` measurement, 2026-09-05.
