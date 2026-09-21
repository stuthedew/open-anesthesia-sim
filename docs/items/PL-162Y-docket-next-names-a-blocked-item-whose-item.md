---
id: PL-162Y
title: docket next names a blocked item whose item blockers have all closed, but not one whose blocked-by milestone is now scoped, which docket check reports as equally promotable
priority: P3
effort: S
status: needs-decision
classes: defect, infra
feature: stale-blocked-routing
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
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

**Decision needed.** Whether `bin/docket next` should name an item whose
`blocked-by` milestone has since been scoped, alongside the item-blocker case
`plan.promotable` already reports - or whether the two shapes are different
enough work that naming them together misleads more than the reach buys.

**Recommended:** report it, under wording of its own. `PL-B9PY`'s lesson is
about *status*, not about reach: what it cost was a milestone-blocked item
parked at `needs-decision` and then hidden from `next` for two days, and the
repair for that is exactly the reader being told. The two are different work -
an item blocker clears when an item closes, a milestone blocker when a scoping
round happens - so the line should say so rather than folding them into one
count: "`PL-XXXX` - v0.5.0 is scoped and every other blocker has closed" reads
differently from "every blocker has closed" and cannot be mistaken for it. On
shape, prefer the caller composing the two readings over `plan.promotable`
growing a roadmap argument: the helper is deliberately store-only, `cmd_next`
already holds a plan, and `checks.py` already narrows the milestone case
correctly for an item the milestone's own `Required scope` names (`PL-L09X`).

**What would change the answer.** A count of how many open items are in the
milestone-blocked-and-now-scoped state at any one time. If it is routinely
zero or one, the reach is not worth a second sentence in `next`'s output and
dropping this with that reason is the better answer.
