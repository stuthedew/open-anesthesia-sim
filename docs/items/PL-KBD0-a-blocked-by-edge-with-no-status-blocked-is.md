---
id: PL-KBD0
title: A blocked-by edge with no status blocked is invisible to the ranking, which is the same silent wrong answer one step along
priority: P2
effort: S
status: done
classes: defect, infra
feature: planning-cadence
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-05
closed: 2026-09-13
pr: 515
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_a_ready_item_waiting_on_open_work_is_an_error' subprojects/docket/tests/test_checks.py
---

**Problem.** `docket next` filters on `status != "blocked"` (`plan.py:242`) and
never reads `blocked_by` — the field is consumed only by `concurrency.py`, which
uses it to refuse two items running together. So an item may declare
`blocked-by: PL-XXXX`, satisfy every check in the store, and still be offered
ahead of the work it says it waits on. Three items are in that state today:
`PL-SN2C` (`ready`, declares `PL-VM40`), `PL-LKRP` (`needs-decision`, declares
`PL-GS5X`), and `PL-S4M2` (`done`, which is the harmless case — a closed item
keeps the record).

**Why it matters.** This is `PL-ZBRB`'s defect displaced by one step rather
than fixed. That item made an undeclared prose prerequisite visible; this is
the state an author reaches *after* acting on that advisory and stopping one
field early. The wrong answer stays silent and stays in the ranking, which is
the property `CLAUDE.md` names as earning attention. `PL-SN2C` is the live
proof: the project owner declared the edge on 2026-09-04 while deciding
`PL-5WFS`, and the item is still `ready` and still offerable ahead of
`PL-VM40`.

`PL-ZBRB`'s advisory works around it by naming both fields in its message, and
its docstring says so. That is a message doing a checker's job.

**Where.** `subprojects/docket/src/docket/checks.py`; tests in
`subprojects/docket/tests/test_checks.py`. The README's "`blocked` means 'not
first'" section states the pairing in prose already.

**The decision, which is why this is not just a patch.** Two readings, and
they are not equally safe:

1. **An open blocker demands `status: blocked`.** Decidable and strict, and it
   would fire on `PL-SN2C` and `PL-LKRP` today. The risk is `needs-decision`:
   that status carries its own meaning, and forcing it to `blocked` would hide
   a pending decision from `docket gate`, which counts it.
2. **Advisory only, naming the pair.** Cannot go wrong, and can be ignored.

Prefer (1) restricted to `status: ready` — a `ready` item with an open declared
blocker is a plain contradiction, since `ready` asserts it can be started now —
and leave `needs-decision` alone. Confirm against `gate` before building it.

**State on 2026-09-05, at triage.** `PL-SN2C` closed that day, so the live
proof above is gone; `PL-LKRP` remains, at `needs-decision` with `PL-GS5X`
still open. Under the reading this brief prefers - the pairing enforced at
`status: ready` only - neither of today's two instances would fire, so the
check would land with no current instance to catch. That is a point for
whoever decides it, not against: the defect is that nothing notices, and the
store happens to be clean this week.

**Decision needed.** Which reading the check takes, and how far it reaches.
Refusing a `status: ready` item that declares an open blocker is decidable and
strict; an advisory naming the pair cannot go wrong and can be ignored. The
brief prefers the first, restricted to `ready`. What is left to settle is
whether `needs-decision` is reached too: `docket gate` counts that status, so
forcing it to `blocked` would hide a pending decision from the gate, and
leaving it alone accepts that `PL-LKRP`'s declared edge stays invisible to the
ranking.

**Done when.** An item that declares an open blocker cannot sit at `ready`
without something saying so, `PL-SN2C` and `PL-LKRP` are resolved either way,
and `PL-ZBRB`'s advisory message no longer has to name a field its own check
does not read.

**Decided 2026-09-13: reading 1, restricted to `status: ready`, as an error.**
`needs-decision` is not reached. This is the reading the brief itself
prefers, and the part it left open - "whether `needs-decision` is reached
too" - is settled against reaching it.

The reason is the one the brief identifies and is worth stating as the
decision rather than as a risk: `bin/docket gate` counts `needs-decision` as
debt somebody can go and resolve. An item forced from `needs-decision` to
`blocked` would leave the gate **by being renamed rather than by being
answered**, and a pending decision would go quiet - which is the same class of
silent wrong answer this item exists to close, pointed at a different reader.
Between an invisible edge in the ranking and a decision that disappears from
the gate, the first is the smaller harm. It is accepted explicitly, in the
check's own docstring, rather than left to be rediscovered.

At `ready` there is no such tension: `ready` asserts the work can be started
now and an open `blocked-by` asserts it cannot, so the two cannot both be
true and the fix is unambiguous.

**It lands with nothing to catch, and that was already the argument for it.**
Confirmed 2026-09-13: every open item carrying `blocked-by` is at `status:
blocked` - sixteen of them - so the store is clean and `bin/docket check`
still reports 0 errors with the check in place. The brief anticipated this
exactly ("the defect is that nothing notices, and the store happens to be
clean this week") and called it a point for the decider rather than against.
A guard is worth having before the instance, not after.

Two deliberate narrowings, both in the docstring so the next reader does not
have to re-derive them: milestones are not reached, because `blocking_items`
is the fail-closed half of the field and a milestone clears by a scoping
round rather than by an item closing; and an unknown blocker is left alone,
because `_check_references` already errors on it by name and a second error
would say the fix is a status change when it is a typo.

Six tests, and only two of them assert the error. The other four pin what the
check must *not* reach - `needs-decision`, a closed blocker, the `blocked`
state the check exists to push authors into, and a milestone edge - because
on a check whose whole content is where it stops, the negative cases are the
specification.

`PL-ZBRB`'s advisory message still names both fields. Narrowing it now that a
checker reads one of them is a separate change and was not made here.
