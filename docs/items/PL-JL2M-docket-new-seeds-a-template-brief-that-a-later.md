---
id: PL-JL2M
title: docket new seeds a template brief that a later-written brief appends to rather than replaces, leaving empty required headings that block triage
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.4.8
touches: subprojects/docket/src/docket/store.py, subprojects/docket/src/docket/checks.py
added: 2026-09-02
closed: 2026-09-07
pr: 428
verify: uv run pytest subprojects/docket/tests/test_store.py && grep -rq 'def test_new_seed_is_not_double_written' subprojects/docket/tests
---

**Problem.** `bin/docket new "<title>"` seeds a body of `**Problem.** <title>`
followed by empty `**Why it matters.**`, `**Where.**` and `**Done when.**`
headings. Where a session then writes the real brief, it has twice appended
below that stub rather than replacing it, leaving the file carrying two
`**Problem.**` sections and three empty required headings above a complete
brief.

`checks.py:78` `brief_gaps()` reads the *first* occurrence of each required
marker, so the empty stub wins and the item cannot leave `untriaged` until a
session notices and deletes it by hand. Observed in `PL-G1MF` and `PL-K2YF`,
both captured 2026-09-01; both were repaired during the 2026-09-02 triage pass,
which is how the shape was found.

**Why it matters.** Two of the eight items in one triage batch carried it, so
it is not a one-off. The failure is silent at capture time and surfaces only at
triage, where the reader sees `brief has nothing under: **Why it matters.**,
**Done when.**` on an item whose brief plainly says both — a message that reads
as a checker bug rather than as a real gap, and costs a session the time to
work out which of the two it is.

It is cheap to prevent and the prevention is deterministic, which is
`CLAUDE.md`'s test for putting a rule in code: nothing here needs judgment.

**Where.** `subprojects/docket/src/docket/store.py` (or wherever `new` writes
the seed body) and `subprojects/docket/src/docket/checks.py`.

**Approach.** Two candidates; the implementing session should pick one rather
than both.

- Have `docket new` seed no headings at all beyond `**Problem.** <title>`, so
  there is nothing to append below and `brief_gaps` reports the honest gap.
  Cheapest, and it removes the failure rather than detecting it.
- Have `brief_gaps` treat a marker as satisfied when *any* occurrence carries
  text, and add a separate advisory for a duplicated `**Problem.**`. Keeps the
  template's prompting value at the cost of a second rule.

The first is preferred: the template's headings are a prompt a session already
has from the checker's own error message, and a seed that cannot be
double-written is better than one that is detected after it has been.

**Found.** 2026-09-02, during the triage pass that cleared the eight untriaged
items captured on 2026-09-01 and 2026-09-02. The two affected files were
repaired in that pass; this item is the cause, not the instances.

**Done when.** An item captured by `docket new` and given its brief afterwards
cannot end up with an empty required heading above a filled one, and a test
covers the shape.
