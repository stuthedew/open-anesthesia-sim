---
id: PL-WYKF
title: Decide whether an item carries a one-line plain-language statement of what the work buys, so a recommendation can be read in consequence terms rather than mechanism terms
priority: P2
effort: M
status: needs-decision
classes: infra
feature: recommendation-rationale
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/checks.py, subprojects/docket/README.md, docs/items
added: 2026-09-19
---

**Problem.** Decide whether an item carries a one-line plain-language statement of what the work buys, so a recommendation can be read in consequence terms rather than mechanism terms

**Why it matters.** `PL-MN0F` and `PL-Z27P` fix the half of "why this item"
that is decidable - the band, and where the item stands against the debt gate.
Neither answers the half the project owner actually asked for: *"why it is
recommended in terms of user relevant language (e.g. improves speed, reduces
future bugs, makes xyz more reliable etc.)"* (2026-09-19).

Nothing in the store carries that sentence. A title names the mechanism; a
`**Why it matters.**` section argues the case at paragraph length, in the same
mechanism vocabulary, and is far too long for a recommendation line. So a
session reporting a recommendation has to compose the consequence from the
brief every time, at full context, in every session that offers the item - the
re-derivation `CLAUDE.md` § "Prefer deterministic tooling over repeated model
work" exists to move out of the model.

**Decision needed.** Whether an item carries a short plain-language statement
of what closing it changes - provisionally `payoff:`, one line, consequence
rather than mechanism - which `docket next`, `docket show` and the digest
would print beside the ranking.

The cost is what makes this the owner's call rather than a session's. It is a
new required field over a store of 1,275 items, so it needs a cutover date and
a grandfathering rule, and this project has twice refused to backfill a field
across a store it could not verify one entry at a time (`PL-5YK8` for
`verify:`, and `verify_required_at_close_from` for the other end of the same
field). The precedent that works is `verify:`: required from a date forward,
and raised as an advisory only for the items `docket next` is about to offer,
so it is written by the session that meets the item and reaches zero on a
normal day rather than in a campaign.

Three candidate answers. **(a)** The field, on the `verify:` pattern above.
**(b)** No field - the skill rule added in this session stands as the whole
remedy, and each session composes the consequence from the brief when it
reports. **(c)** A field on workflow-lane items only, which is where the owner
cannot judge the offer from the title; a simulator item's title describes
something they already have an opinion about.

Decide it on whether the sentence is worth writing 163 times, once per open
workflow item, at the moment each is next offered - not on how good the output
would look.

**Done when.** The decision is recorded here and, if a field is adopted, in
`subprojects/docket/README.md`'s item format with its cutover date, with items
filed for the checker and the renderers.
