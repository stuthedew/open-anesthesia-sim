---
id: PL-VJ1X
title: docket check requires the literal '**Decision needed.**' where the README says a heading is matched by the words it opens with and may continue past them, so a heading that elaborates is an error
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-08
closed: 2026-09-12
pr: 496
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_an_elaborated_decision_needed_heading_is_accepted' subprojects/docket/tests/test_checks.py
---

**Problem.** docket check requires the literal '**Decision needed.**' where the README says a heading is matched by the words it opens with and may continue past them, so a heading that elaborates is an error

**Why it matters.** The checker and the document disagree about the same rule,
and the checker is the one that stops a commit. `_section_text`
(`subprojects/docket/src/docket/checks.py`) matches `**Problem.**`,
`**Why it matters.**` and `**Done when.**` by the words the heading opens with,
so `**Why it matters, and why it is not new.**` is the same section - the
docstring says so and `subprojects/docket/README.md` states the rule. The
`needs-decision` requirement is a bare substring test for the literal
`**Decision needed.**`, so a heading that elaborates - `**Decision needed, and
by whom.**` - is an error.

The cost is that the one heading a reader most wants to qualify is the one
heading that may not be. A session meeting the error either reverts to the bare
form, losing the qualification, or spends a pass finding out that the README it
read is not what runs.

**Done when.** A `needs-decision` item whose heading opens with `**Decision
needed` and continues past it passes `bin/docket check`, matched the same way
the other three required headings are, with a test holding an elaborated
heading.

**Observed again while this item was being triaged, 2026-09-12.** `PL-RFLN`'s
brief was written with the heading `**Decision needed, and it is the project
owner's.**` - the elaboration carrying the one fact a later session most needs,
that the item waits on the owner supplying a paper rather than on anybody's
analysis. `bin/docket check` rejected it:

```text
PL-RFLN-...: marked needs-decision but states no decision to make; add a
**Decision needed.** line so a later session can answer it
```

The error is also wrong about what it found: the item states its decision in the
sentence directly under that heading. The message sends a reader looking for a
missing section when what is missing is four characters of punctuation, which is
the cost on top of the refusal.

Resolved there by demoting the qualification into the sentence, which is the
workaround this item predicts and the reason the defect is invisible in the
store - every item that met it now reads as though it never wanted to elaborate.
