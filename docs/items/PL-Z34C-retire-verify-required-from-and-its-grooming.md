---
id: PL-Z34C
title: Retire verify_required_from and its grooming advisory once the grandfathered set reaches zero
status: needs-decision
priority: P3
effort: S
classes: infra, session-cost
touches: docket.toml, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/config.py
added: 2026-09-03
---

**Problem.** `verify_required_from` grandfathers 22 `ready` items from the
`verify:` requirement, and `checks.py` raises a grooming advisory naming the
one or two `docket next` is about to offer. When the set reaches zero the
advisory can never fire again, and the date it is anchored to stops
distinguishing anything: every item would be held to the rule.

**Why it matters.** `CLAUDE.md`: "A check earns its place every run, or it is
retired... an advisory nobody acts on is a candidate for retirement rather
than promotion." An advisory that *cannot* fire is the limiting case, and
leaving it costs a config key, a branch in `checks.py`, a paragraph in
`.claude/skills/docket/SKILL.md` and a reader's time working out which of two
dates applies to them.

**What must not be retired with it.** `verify_required_at_close_from` and
`_verify_required_at_close` are not transitional, and the distinction is the
whole reason this item exists rather than "delete the verify dates". Measured
2026-09-03 against an item captured *after* `verify_required_from`, so
grandfathered by nothing:

| status | opening gate demands a command |
| --- | --- |
| `needs-decision` | no |
| `blocked` | no |
| `done` | yes, and only via the closing gate |

The opening gate fires on `status == "ready"`, so an item reaching `done`
without ever passing through `ready` is never asked. That is not a corner
case: `PL-VYXP` and `PL-BNPY` both went `needs-decision` to `done` in one
commit on 2026-09-03 and never held `ready` at any moment a check ran. The
closing gate is what covers that path, for every item, forever.

Its *date* is permanent too, for a different reason: 182 items are `done` and
54 carry no command, items are never deleted, and backfilling a command onto
merged work means writing one with nothing to run it against. The date is the
boundary between history and policy rather than a transitional flag.

**Where.** `verify_required_from` in `docket.toml`; `_verify_required` and the
advisory block in `subprojects/docket/src/docket/checks.py`;
`config.py`'s field; the "Items older than the rule" paragraph in
`.claude/skills/docket/SKILL.md`.

**Decision needed.** Whether to retire it when the condition arrives, or to
keep the advisory as a standing record that the grandfathering existed. The
recommendation is to retire: an advisory that cannot fire changes no
decision, and this item plus `PL-5YK8` are the durable record.

It is held here rather than at `ready` because it cannot be worked yet, and
`blocked` was refused by `docket check` - that status names a blocking
*item*, and this waits on a condition. The workaround is adequate; the gap
is noted rather than filed, since nothing else in the store has wanted it.

**The trigger.** The set must reach zero -
`bin/docket check` reports the remaining count inside the advisory, so the
trigger is visible on every run without anything tracking it. 39 on
2026-08-31, 22 on 2026-09-03. `PL-J49T` should accelerate it: a grandfathered
item can no longer be closed without gaining a command.

**Done when.** The advisory, `_verify_required`, the config field and the
skill paragraph are gone; the closing gate and its date remain; and
`docket check` still refuses an item closed without a command.

## Worked 2026-09-13: retire is the right answer, the trigger is measurably close, and one question is left that is not this item's to answer

**Decided: retire, on this project's own retirement test.** `CLAUDE.md`: "A
check earns its place every run, or it is retired… an advisory nobody acts on is
a candidate for retirement rather than promotion." An advisory that *cannot*
fire is the limiting case of one nobody acts on, and the two costs it would keep
charging are both real: a second date in `docket.toml` that a reader has to
distinguish from the permanent one, and a paragraph in
`.claude/skills/docket/SKILL.md` explaining a grandfathering that no longer
grandfathers anything. `PL-5YK8` (done) and this item are the durable record
that it existed.

**The counter-argument, and why it loses.** Keeping it as a standing record puts
the record in the place least able to carry it: a config key and a branch in
`checks.py` say *that* a cutover happened and nothing about why, whereas an item
says both and costs no run time. Nothing reads a retired advisory to learn
history.

**The trigger is measurably close, and the trajectory is the evidence.**
Recounted today by the same rule the advisory uses — `status: ready`, `added`
before `verify_required_from` (2026-08-30), carrying neither `verify:` nor
`not-delegable:`:

| date | grandfathered `ready` items |
| --- | --- |
| 2026-08-31 | 39 |
| 2026-09-03 | 22 |
| **2026-09-13** | **15** |

PL-005, PL-024, PL-027, PL-029, PL-036, PL-038, PL-043, PL-41YP, PL-8LDF,
PL-LJVD, PL-NC2P, PL-RZPX, PL-YMY7, PL-Z7LY, PL-ZBR6 — every one added
2026-08-23 to 2026-08-26, so the set is closed and can only shrink. `PL-J49T`
(done) is what drains it: a grandfathered item can no longer be closed without
gaining a command.

**Two of the fifteen will not drain by being worked.** `PL-NC2P` and `PL-YMY7`
are coverage items over `app/main.py` and `app/simulation_view.py`'s
Flet-construction paths, which `ROADMAP.md` § "Items this port moots or
transforms" names as files `v0.5.1` replaces. They will most likely close as
`dropped`, which still removes them from the set — noted because it means the
count reaching zero does not require all fifteen to be *done*.

**What must not be retired with it is unchanged and was re-checked**, not
assumed: `verify_required_at_close_from` and `_verify_required_at_close` stay,
for both reasons this brief records. The opening gate fires on `status ==
"ready"`, so an item going `needs-decision` to `done` in one commit is never
asked by it — and this batch produced exactly that case again today, in
`PL-H1JD`, which was `needs-decision` at the start of the session and `done` at
the end of it without ever holding `ready`. The closing gate is what asked it
for a command.

## Still open, and it is a store-design question rather than this item's

The decision above is made, and this item **still cannot be worked**, because
the set is 15 rather than 0. That leaves it in a state the store has no name
for: *decided, waiting on a measurable condition*.

The three available statuses each say something false about it. `needs-decision`
says the next step is a decision, which it no longer is — and `bin/docket gate`
counts it as Gate 1 debt on that basis, so a gate that must clear before v0.5.0
is held open by an item whose question is answered. `ready` says a session may
pick it up, and a session that does will find the count is 15 and put it back
down. `blocked` was refused by `docket check`, correctly: that status names a
blocking *item*, and `PL-J49T` — the item that drains the set — is already done,
so there is nothing for `blocked-by` to point at.

This brief already noted the gap and declined to file it, "since nothing else in
the store has wanted it". Something else now does, which is what changes the
answer: `PL-GLBF` in this same batch is decided on its cheap half and gated on a
question, and the general shape — a decision recorded against a trigger nobody
is tracking — is what `bin/docket` has no representation for.

It is left `needs-decision` rather than moved, deliberately: choosing what the
store should represent is a store-design call, and picking `ready` to clear the
gate count would put unworkable work in front of `bin/docket next`, which is the
failure `.claude/skills/docket/SKILL.md` names for `L` items arriving in the
queue.
