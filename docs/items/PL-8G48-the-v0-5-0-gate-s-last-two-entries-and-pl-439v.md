---
id: PL-8G48
title: The v0.5.0 gate's last two entries and PL-439V became promotable when PL-FG9D and PL-4DCG closed today, and all three still read as blocked
status: untriaged
added: 2026-09-20
---

**Problem.** The v0.5.0 gate's last two entries and PL-439V became promotable when PL-FG9D and PL-4DCG closed today, and all three still read as blocked

Found while closing `PL-NM7X` (the fresh gas flow default), 2026-09-20, from
`bin/docket check`'s own promotable advisory.

**What is true right now.** `bin/docket wave` reports the v0.5.0 gate at 173 of
175 cleared, with `PL-WZVZ` and `PL-8PS6` open — and both carry `status:
blocked`, so `bin/docket next` will not offer either. Their blockers are
`PL-FG9D` (the machine abstraction design) and `PL-4DCG` (the machine survey),
and both closed **today**. `PL-439V` is in the same state from the same cause.
`bin/docket check` already prints all three as "every blocker has closed; it is
ready to promote".

**Why the previous pass did not cover them.** `PL-JFQ3` groomed seven items
measured 2026-09-16 — `PL-5NR5`, `PL-LPLD`, `PL-MBP6`, `PL-QR6Q`, `PL-QRD1`,
`PL-W7H9`, `PL-Z3V5`. These three were still genuinely blocked on that date.
This is the same advisory firing on a new batch, not a missed one.

**Why it is worth an item rather than waiting for the advisory to be noticed
again.** These two *are* the remainder of the gate. While they read as blocked,
the beat says "clear the gate — 2 entries still open" and `bin/docket next`
offers neither, so the gate looks stuck when it is two promotions from clear.
`PL-6T44` is the standing tool defect behind the appearance (`next` and `wave`
read `status: blocked` literally where `check` computes it); this item is the
grooming that clears the instance, and does not depend on `PL-6T44` landing.

**Done when.** Each of `PL-WZVZ`, `PL-8PS6` and `PL-439V` has been read against
the tree as it now stands — `docs/machine-abstraction.md` and
`docs/machine-survey.md` both landed since they were written — and is either
promoted to `ready` with a `verify:` command that was run and seen to fail, or
re-blocked on a named live blocker, or dropped with a reason. Promoting is not
the assumed outcome: `PL-WZVZ` is `P3`/`M` and rests on a design decision that
only just settled, so its brief may need correcting before it is startable.
