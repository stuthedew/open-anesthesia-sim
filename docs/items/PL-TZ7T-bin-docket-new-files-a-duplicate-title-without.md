---
id: PL-TZ7T
title: bin/docket new files a duplicate title without noticing: PL-LBR6 sat ready for six days with the record rename diagnosed and a verify command written while PL-5QLP and PL-QMC0 were filed as fresh discoveries of the same mechanism
priority: P3
effort: S
status: ready
classes: infra
feature: slug-rename-on-write
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-19
verify: grep -q 'def test_new_names_an_existing_item_with_a_near_identical_title' subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket new files a duplicate title without noticing: PL-LBR6 sat ready for six days with the record rename diagnosed and a verify command written while PL-5QLP and PL-QMC0 were filed as fresh discoveries of the same mechanism

**What it cost, 2026-09-19.** `PL-LBR6` sat `ready` for six days with the
`docket record` rename diagnosed and a `verify:` command written against it,
while `PL-5QLP` and `PL-QMC0` were filed as fresh discoveries of the same
mechanism - one writer renaming an item file as a side effect of writing a
field. Three items, one cause, and the two later ones were each captured by a
session that had no way to know the first existed. All three have since closed
under `feature: slug-rename-on-write`, so the grouping was recoverable; what
was not recovered is the two diagnoses paid for twice.

**Why it matters.** `CLAUDE.md`'s capture rule is deliberately unconditional -
"Do not ask whether to record it" - and that is right, because the alternative
is losing findings. The cost it accepts is exactly this one, and it is paid at
the only moment the duplicate is cheap to catch: `bin/docket new` has the
title, the store, and a session's attention, and says nothing. Every later
mechanism that could catch it is more expensive - `feature:` grouping needs
somebody to already know the items are one problem, and the apparatus backlog
sweep that found this cluster read 145,000 tokens across twelve agents.

This is the last of `feature: slug-rename-on-write`'s three open items, so it
is also what closes a group at 5/8 rather than adding to a standing theme.

**Done when.** `bin/docket new` names the existing items whose titles are close
to the one being filed, prints them with their status, and files the item
anyway - a warning rather than a refusal, because the capture rule may not be
made conditional on a similarity score, and a near-duplicate that is genuinely
a second instance is a legitimate filing.
