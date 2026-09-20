---
id: PL-162Y
title: docket next names a blocked item whose item blockers have all closed, but not one whose blocked-by milestone is now scoped, which docket check reports as equally promotable
status: untriaged
feature: stale-blocked-routing
added: 2026-09-20
---

**Problem.** docket next names a blocked item whose item blockers have all closed, but not one whose blocked-by milestone is now scoped, which docket check reports as equally promotable

**Why it matters.** `PL-6T44` landed `plan.promotable`, which reports a blocked
item whose every *item* blocker has closed, and `bin/docket next` now names
those ids at the moment a session is choosing. `bin/docket check` reports a
second, equally promotable shape that `next` still says nothing about: an item
whose `blocked-by` names a milestone that has since been *scoped*. The advisory
for it reads "vX.Y.Z is scoped and every other blocker has closed; it is ready
to promote", and it is already narrowed correctly - `checks.py` suppresses it
for an item the milestone's own `Required scope` names, since such an item
ships *with* the milestone and scoping could never have unblocked it
(`PL-L09X`).

So the gap is one of reach rather than of correctness: the same reader, at the
same moment, is told about one half and not the other.

**Why it was left out.** An item blocker closes when an item closes, which the
store answers on its own. A milestone blocker clears when a scoping round
happens, which takes the roadmap - `milestones.is_cleared` and
`milestones.ships_with`. `plan.promotable` is deliberately store-only and has no
roadmap argument, and `cmd_next` does already hold a plan, so the question is
whether the helper grows a second optional reading or the caller composes the
two. Weigh that against `PL-B9PY`'s lesson: a milestone-blocked item is
genuinely different work - only a scoping round resolves it - so naming it in
the same breath as "every blocker has closed" may mislead more than it helps.

**Done when.** `bin/docket next` either names the items whose milestone blocker
is now scoped, in wording that distinguishes them from the item-blocker case, or
this item is dropped with the reason why the two should not be reported
together - and a test under `subprojects/docket/tests/` drives whichever way it
settles.
