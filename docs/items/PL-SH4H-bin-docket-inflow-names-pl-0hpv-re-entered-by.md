---
id: PL-SH4H
title: bin/docket inflow names PL-0HPV re-entered by three filings since the 2026-10-12 triage pass (#1455) - PL-RW3T, PL-ZXM1, PL-HSB3, none of them a head - so it reads as a generator whose fix did not hold until a session records a successor head or says why not, as PL-4097 did for the nine before it
priority: P2
effort: S
status: done
classes: housekeeping
feature: generator-heads
milestone: v0.5.28
touches: docs/items
added: 2026-10-12
closed: 2026-10-18
pr: 1571
payoff: the last unanswered line in bin/docket inflow's 'fix did not hold' list gets its answer, so a generator still producing there is either recorded and ranked or shown settled
verify: grep -qE '^\*\*Answered 2026-' docs/items/PL-SH4H-*.md
---

**Problem.** bin/docket inflow names PL-0HPV re-entered by three filings since the 2026-10-12 triage pass (#1455) - PL-RW3T, PL-ZXM1, PL-HSB3, none of them a head - so it reads as a generator whose fix did not hold until a session records a successor head or says why not, as PL-4097 did for the nine before it

**Reproduced 2026-10-17.** `bin/docket inflow --no-fetch` still prints
`PL-0HPV  by PL-RW3T, PL-ZXM1, PL-HSB3` under "a generator whose fix did not
hold", with no successor named. No item's `root-cause-of:` names any of the
three (`grep -lE '^root-cause-of:.*(RW3T|ZXM1|HSB3)' docs/items/*.md` prints
nothing). `PL-RW3T` is done (#1133, 2026-09-27); `PL-ZXM1` and `PL-HSB3` are
open at `P3`. A lead for the session that answers it, not the answer: all
three sit in `tools/doc_check.py`'s gate-parity reading (`check_gate_parity`
and the Makefile readers it counts from), which is the function `PL-0HPV`'s
`generator: spent` verdict names as what keeps the two gates from drifting.

**Why it matters.** Until a successor head is recorded or the reason none is
owed is written, the line reads as a generator nobody is pulling, on every run
of the command `CLAUDE.md` § "What this project is" expects such a thing to be
found by. If the answer is a live successor, it also ranks above every band
but `P0` and holds `CLAUDE.md`'s pause on new workflow mechanisms, so leaving
it unasked changes what the queue offers.

**Done when.** This brief carries a dated answer for `PL-0HPV`'s line, as
`PL-4097` did for nine: either a successor head is recorded (an item whose
`root-cause-of:` names the members, with `generator:`, `misread:` and
`reenters: PL-0HPV`, so `inflow` lists it as the line's successor), or the
reason none is owed is written here - and, once `PL-C4F0` (inflow cannot see a
"no successor" answer) has landed, written in the record that item adds, so
`inflow` lists the line apart rather than re-asking it.

**How `PL-C4F0` bears on it.** Only on the second ending. A successor head is
already a record `inflow` reads (`PL-0WT0`); a "none owed" answer today is
prose `inflow` cannot see, exactly `PL-61FT`'s state. So this item is not
blocked on `PL-C4F0`: the analysis and either answer can be written now, and
`PL-C4F0`'s backfill picks up a prose answer here if it lands first.

**Generator check.** Bookkeeping: the answer `inflow`'s re-entered list asks
for, as `PL-4097` was, not an instance of a head's fact. It was filed in
`PL-4097`'s closing commit as the one line that pass left open, so it is not
a re-entry of it either.

**Answered 2026-10-18.** A successor head is owed, and `PL-ZQ3R` carries it,
recorded live with `reenters: PL-0HPV`. `PL-RW3T`, `PL-ZXM1` and `PL-HSB3`
each misread `PL-0HPV`'s own fact: the checks each gate runs, and where the
two sets differ. `PL-RW3T` missed a script's mode. `PL-ZXM1` missed a workflow
step's `if:`. `PL-HSB3` missed a Makefile conditional. `PL-5M36`'s first
bullet is a fourth instance, filed 2026-10-10, and it now carries `reenters:
PL-0HPV` too. No other head states a narrower fact that covers them.
`PL-848V` reads only a workflow's `on:` triggers, and `PL-R417` reads only
lines that continue a statement. `PL-0HPV`'s spent verdict held the gates
together only at the script level. Gate parity still counts a command as run
without reading the mode or condition it runs under, and two members are
still open, so the mechanism is still producing.
