---
id: PL-G1MF
title: docket next says 'Finishes <feature>' for any item in an underway feature, and contradicts itself in the same sentence with the count still open
status: untriaged
feature: dev-tooling
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/tests/test_plan.py
added: 2026-09-01
---

**Problem.** docket next says 'Finishes <feature>' for any item in an underway feature, and contradicts itself in the same sentence with the count still open

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `plan.py:194-197` builds `underway` from *every* open item in a
feature that is underway, and `plan.py:229-233` prints
`Finishes '<feature>', which is N% done (K item(s) left)` for any item in that
set. So `bin/docket next` today says "Finishes 'dev-tooling', which is 51% done
(27 item(s) left)" - a sentence that asserts and then withdraws the same claim.

**Why it matters.** This is the rationale line of the command every session
leads with, and the ranking it explains is sound: the tie-break really is
"prefer the feature nearer completion", which is the reason worth giving. The
wording overstates it into something the parenthetical immediately disproves,
which teaches a reader to discount the whole line - including the cases where
the item genuinely is the last one open.

**Where.** `subprojects/docket/src/docket/plan.py` - the `elif item.identifier
in underway:` branch at 229-233, and `test_plan.py` beside it.

**Approach.** Two wordings, chosen by `len(feature.open_items)`: at one item
left the current sentence is true and should stay; above one, say what the rank
actually is - advances a feature already underway, N% done, K left, and a
shipped feature beats progress on several.

**Done when.** An item that is the last open one in its feature is still
described as finishing it; an item with others open is not; and a test covers
both.
