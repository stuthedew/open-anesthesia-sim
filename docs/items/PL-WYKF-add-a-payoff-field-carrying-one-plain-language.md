---
id: PL-WYKF
title: Add a payoff: field carrying one plain-language line of what an item buys, required from a cutover date on the verify: pattern, and printed wherever docket names an item
priority: P2
effort: M
status: done
classes: infra
feature: recommendation-rationale
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_model.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_plan.py, subprojects/docket/README.md, .claude/skills/docket/SKILL.md, docket.toml, docs/items
added: 2026-09-19
closed: 2026-09-19
payoff: picking work stops needing a read of the brief - what an item buys is written once and printed wherever docket names it
verify: grep -q 'def test_payoff_is_required_from_its_cutover_date' subprojects/docket/tests/test_checks.py
---

**Problem.** Nothing in the store carries a plain-language statement of what
closing an item buys, so every recommendation reads in mechanism terms and a
session offering one has to compose the consequence from the brief at full
context, in every session that offers it. The decision to add `payoff:` is
taken and recorded below; what is left is building it.

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

**The cost, measured 2026-09-19, because it was asked and the first answer was
not counted.** The session that wrote this brief recommended **(c)** on the
strength of one number it had not checked - "halves the writing, ~163 items
instead of 324". The project owner asked what (a) would actually cost. Counting
it reversed the recommendation, which is `.claude/rules/expert-review.md`
§ "Name the number that would change your mind" firing on the session that had
just invoked it.

| | (a) every item | (c) workflow lane only |
| --- | --- | --- |
| Startable open items owing a sentence | 267 | 157 |
| Open items with no defined answer | 0 | **31** (crossing or no `touches`) |
| Extra items charged per day, at the 2026-09-04..19 closure rate | +23.6 | baseline |
| Rule to implement | "every item from date D" | the same, plus a lane condition |

Three things the count says that the estimate did not:

1. **(c) has 31 undefined cases and (a) has none.** An item whose `touches`
   spans both halves, or declares nothing, is in neither lane - 42 of 325 open
   items, 31 of them startable. A lane-scoped requirement has no answer for
   them, and they are disproportionately the large cross-cutting work where the
   sentence is worth most.
2. **(c) is more code than (a), not less.** "Every item from date D" is the
   whole of (a). (c) is that plus a condition on a computed lane, over a
   `touches` field 10 open items do not declare.
3. **The precedent is decisive and it is in this store.** `verify:` is the same
   shape - required at `ready` from a cutover date, advisory only for the items
   `bin/docket next` is about to offer. 913 of 1,278 items carry one today, and
   **12 of 218 open `ready` items still lack one**. A required field on every
   item, charged at the moment the item is started, drained to ~95% with no
   backfill campaign and no pass dedicated to it.

The marginal cost of (a) over (c) is therefore about 110 sentences across the
open backlog, each one line written by a session that already has the brief
open because it is about to work the item. That is not a campaign; it is the
same per-item charge `verify:` already carries, on an item a session is
spending an hour on.

**Decision: (a), a `payoff:` field on every item** (project owner, 2026-09-19),
on the `verify:` pattern above - required from a cutover date, advisory for the
items `next` is about to offer, no backfill of anything already closed. The
owner named (a) before the count; the count is why the session's own (c)
recommendation is withdrawn rather than defended.

**Done when.** `payoff:` is documented in `subprojects/docket/README.md`'s item
format with its cutover date; `docket set` writes it and `docket check` requires
it from that date and raises the offer-time advisory before it; `docket next`,
`docket show` and the digest print it beside the band and gate relation
`PL-Z27P` added. Nothing already closed is backfilled.

**Two things whoever implements this must not get wrong.** The cutover date is
tomorrow rather than today, as `verify_prerequisite_refused_from` was, so the
grandfathered set is closed at exactly what the store held when the rule began
working. And the field holds a *consequence*, not a restatement of the title -
`docket check` cannot judge that and must not try, so the checker's job is
presence only, and the shape to copy is the one in
`.claude/skills/docket/SKILL.md` § "Say what the work buys".
