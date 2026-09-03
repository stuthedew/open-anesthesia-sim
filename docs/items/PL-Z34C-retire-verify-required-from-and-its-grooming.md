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
