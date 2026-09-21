---
id: PL-BZVY
title: get_session's context_usage.used_tokens does not refresh within a turn, so the prescribed budget check reads a start-of-turn value for the whole of an item worked in one turn
priority: P3
effort: S
status: blocked
classes: session-cost, infra
feature: context-budget-reading
touches: CLAUDE.md
blocked-by: PL-W80S
added: 2026-09-20
---

**Problem.** get_session's context_usage.used_tokens does not refresh within a turn, so the prescribed budget check reads a start-of-turn value for the whole of an item worked in one turn

**Measured 2026-09-20**, in the session that worked `PL-CTD7`. Two
`get_session` calls, one at the start of the item and one after the whole item
had been implemented, tested, documented, committed, pushed and opened as a
pull request, both returned `used_tokens: 115320` - byte-identical, including
`permission_mode_seq`. The field is written at turn boundaries, and that whole
item ran inside one turn.

So the check `CLAUDE.md` prescribes - "read it as you pick up the next item"
- cannot see the spend it is meant to bound whenever an item is worked in a
single turn, which is the normal shape here. A session that calls it twice
gets the same answer and reasonably concludes it has spent nothing.

Whether this is fixable from inside a session is the open question and is what
this item is for: if the field cannot refresh mid-turn, then a budget stated
in `used_tokens` is measuring the wrong thing and the rule wants a different
observable, which is `PL-W80S`.

**Why it matters.** The budget check `CLAUDE.md` prescribes is the project's
stated stopping rule, and a session that calls `get_session` twice - once
picking up an item and once after implementing it - gets a byte-identical
answer and reasonably concludes it has spent nothing. So the rule's own
instrument reads zero for exactly the shape of work this project does most: a
whole item inside one turn. A stopping rule whose gauge does not move is not a
loose rule, it is a rule that reports the wrong answer with the same confidence
as the right one.

**Measured twice on 2026-09-20**, in the session that worked `PL-CTD7`:
`used_tokens: 115320` at the start of the item and again after it had been
implemented, tested, documented, committed, pushed and opened as a pull
request, with `permission_mode_seq` identical too.

**Why this is `blocked` rather than open work.** What is left here is not a
measurement - the measurement is above and it is conclusive - but a choice of
observable, and that choice belongs to `PL-W80S`, which is deciding what the
budget measures at all. Whichever answer that item takes decides this one:
spend-since-baseline needs an observable that moves within a turn, and the
absolute reading does not need one. Working this first would be choosing a
gauge before knowing what is being weighed.
