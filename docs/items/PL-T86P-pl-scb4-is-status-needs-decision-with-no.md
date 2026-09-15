---
id: PL-T86P
title: PL-SCB4 is status needs-decision with no Decision needed section, which the checker requires and does not catch
priority: P3
effort: S
status: ready
classes: defect, infra
feature: queue-hygiene
touches: docs/items, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-14
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_a_needs_decision_item_without_a_decision_section_is_an_error' subprojects/docket/tests/test_checks.py
---

**Problem.** PL-SCB4 is status needs-decision with no Decision needed section, which the checker requires and does not catch

**Why it matters.** Two failures, and the second is the one worth fixing.
`PL-SCB4` sits at `needs-decision` with nothing saying what has to be decided,
so the question it was supposed to carry to the owner is lost - the status ranks
it in `bin/docket next` and counts it as debt in `bin/docket gate` while holding
no answerable question. That is the queue asserting a decision is pending
without recording which.

The general failure is that `docket check` states this requirement in the triage
rules it prints and does not enforce it, so every `needs-decision` item written
without the section is silently the same. A rule a session is told and a tool
does not check is `CLAUDE.md`'s "find the decidable part and put it in code"
going the other way: whether a heading is present is exactly the yes/no half a
script should decide, leaving only the sentence under it to a person.

**Done when.** `docket check` errors on any `needs-decision` item carrying no
`**Decision needed.**` section, with a test that plants one; and `PL-SCB4` names
its decision, or moves to the status that fits it.
