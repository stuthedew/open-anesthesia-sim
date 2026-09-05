---
id: PL-KBD0
title: A blocked-by edge with no status blocked is invisible to the ranking, which is the same silent wrong answer one step along
status: untriaged
added: 2026-09-05
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

**Done when.** An item that declares an open blocker cannot sit at `ready`
without something saying so, `PL-SN2C` and `PL-LKRP` are resolved either way,
and `PL-ZBRB`'s advisory message no longer has to name a field its own check
does not read.
