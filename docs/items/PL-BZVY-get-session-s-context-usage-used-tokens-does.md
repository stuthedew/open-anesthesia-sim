---
id: PL-BZVY
title: get_session's context_usage.used_tokens does not refresh within a turn, so the prescribed budget check reads a start-of-turn value for the whole of an item worked in one turn
status: untriaged
feature: context-budget-reading
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
