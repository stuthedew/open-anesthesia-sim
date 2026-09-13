---
id: PL-FX0K
title: docket silently parses a YAML-list touches: field as empty, so an item using the list form is offered to no lane and is unanalysed for concurrency
priority: P2
effort: S
status: ready
classes: defect
feature: docket-store
touches: subprojects/docket
added: 2026-09-13
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_a_block_list_field_is_refused' subprojects/docket/tests/test_checks.py
---

**Problem.** docket silently parses a YAML-list touches: field as empty, so an item using the list form is offered to no lane and is unanalysed for concurrency
**Why it matters.** Verified 2026-09-13: every list field goes through
`_split_list` in `subprojects/docket/src/docket/model.py`, which splits on
commas and nothing else, so a `touches:` with an empty value followed by
indented `- path` lines parses to an empty tuple with no complaint. No item in
the store uses that form today, so the defect is latent - but it reaches further
than `touches`. `classes` and `blocked-by` go through the same function, and an
empty `classes` is what defeats the safety pin: `checks.py` seats a `safety`- or
`science`-classed item at P0 or P1 only when it can see the class, so a
`classes:` written as a YAML block list would leave work a clinician could be
misled by sitting in the bottom band with `bin/docket check` reporting zero
errors. That is `PL-MVC2` exactly, arriving through the parser instead of
through a misspelling - and `known_classes` cannot catch it, because there is no
class there to reject.

`parse_item`'s own docstring already states the principle a fix should follow:
"Missing fields come back empty rather than defaulted ... Guessing would turn a
validation failure into a silently wrong queue position." An unreadable field is
not a missing one, and the store should say so.

**Done when.** `bin/docket check` fails with a named error on a front-matter
list field written as a YAML block list, for `classes`, `touches` and
`blocked-by` alike; a test in `subprojects/docket/tests/test_checks.py` pins it;
and the parser is *not* taught the block form. Refusing an ambiguous field is
the store's stated stance, and two spellings of one field is a second thing
every reader of the format has to know.
