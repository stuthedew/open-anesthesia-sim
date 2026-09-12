---
id: PL-VJ1X
title: docket check requires the literal '**Decision needed.**' where the README says a heading is matched by the words it opens with and may continue past them, so a heading that elaborates is an error
priority: P2
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-08
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
