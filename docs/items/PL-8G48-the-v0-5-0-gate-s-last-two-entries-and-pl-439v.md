---
id: PL-8G48
title: The v0.5.0 gate's last two entries and PL-439V became promotable when PL-FG9D and PL-4DCG closed today, and all three still read as blocked
priority: P2
effort: S
status: done
classes: planning, docs
feature: debt-gate
touches: docs/items, ROADMAP.md
added: 2026-09-20
closed: 2026-09-20
payoff: gets three blocked-but-promotable items back in front of bin/docket next, including two of v0.5.0's five open gate entries that no session is currently offered
verify: ! grep -lE '^blocked-by:.*(PL-FG9D|PL-4DCG)' docs/items/PL-WZVZ-*.md docs/items/PL-8PS6-*.md docs/items/PL-439V-*.md
not-delegable: The deliverable is a per-item judgment recorded in three item files - whether each is genuinely startable now that PL-FG9D and PL-4DCG have closed, and for PL-WZVZ whether an anticipated safety concern keeps its P3 band once its hazard is live. No command can tell a promotion that was reasoned from one that was typed, and the verify: only proves no closed blocker is still named.
---

**Problem.** The v0.5.0 gate's last two entries and PL-439V became promotable when PL-FG9D and PL-4DCG closed today, and all three still read as blocked

Found while closing `PL-NM7X` (the fresh gas flow default), 2026-09-20, from
`bin/docket check`'s own promotable advisory.

**What was true when this was captured, 2026-09-20.** `bin/docket wave` reported
the v0.5.0 gate at 173 of 175 cleared, with `PL-WZVZ` and `PL-8PS6` open — and both carry `status:
blocked`, so `bin/docket next` will not offer either. Their blockers are
`PL-FG9D` (the machine abstraction design) and `PL-4DCG` (the machine survey),
and both closed **today**. `PL-439V` is in the same state from the same cause.
`bin/docket check` already prints all three as "every blocker has closed; it is
ready to promote".

**Why the previous pass did not cover them.** `PL-JFQ3` groomed seven items
measured 2026-09-16 — `PL-5NR5`, `PL-LPLD`, `PL-MBP6`, `PL-QR6Q`, `PL-QRD1`,
`PL-W7H9`, `PL-Z3V5`. These three were still genuinely blocked on that date.
This is the same advisory firing on a new batch, not a missed one.

**Why it matters, and why waiting for the advisory to be noticed again is not
enough.** These two were the whole remainder of the gate until #757 merged (see
the dated note at the end). While they read as blocked,
the beat says "clear the gate — 2 entries still open" and `bin/docket next`
offers neither, so the gate looks stuck when it is two promotions from clear.
`PL-6T44` is the standing tool defect behind the appearance: `bin/docket next`
and `bin/docket wave` read `status: blocked` literally where `bin/docket check`
computes it. The two are independent work and can land in either order — fixing
the tool stops the *next* batch reading as stuck, while this grooming clears the
batch standing today.

**Done when.** Each of `PL-WZVZ`, `PL-8PS6` and `PL-439V` has been read against
the tree as it now stands — `docs/machine-abstraction.md` and
`docs/machine-survey.md` both landed since they were written — and is either
promoted to `ready` with a `verify:` command that was run and seen to fail, or
re-blocked on a named live blocker, or dropped with a reason. Promoting is not
the assumed outcome: `PL-WZVZ` is `P3`/`M` and rests on a design decision that
only just settled, so its brief may need correcting before it is startable.

**What triage checked, 2026-09-20** (`PL-028T`). The fault reproduces:
`bin/docket check` prints all three as "every blocker has closed; it is ready to
promote", and `bin/docket wave` reports the gate at 175 entries with `PL-WZVZ`
and `PL-8PS6` its two open ones. Two facts the brief does not carry, both read
off the item files rather than inferred:

- **`PL-WZVZ` is `P3` and carries `classes: safety, anticipated`.** It sits
  below the P1 floor `bin/docket check` enforces for `safety` only because
  `anticipated` exempts a concern whose feature does not exist yet, letting it
  wait at its blocker's band. Promoting it is therefore a band decision as well
  as a status one, and it is the decision `PL-ZF2G` and `PL-JFQ3` already
  settled - promoting an anticipated safety item is what returns it to the debt
  gate. Apply that precedent rather than re-deriving it.
- **All three carry `feature: anesthesia-machine`**, which stands at 3/8 done -
  the same triage pass that wrote this note put `PL-KZ60` into that feature, so
  it was 3/7 when the note was first drafted. They are three of its five open
  items, so this pass decides how much of that feature is startable, not merely
  how three files read.

`PL-JFQ3` is the worked precedent for the pass itself: seven items, `P2`/`M`,
`classes: planning, docs`, `touches: docs/items`, and non-delegable because no
command can tell a promotion that was reasoned from one that was typed. The
same holds here, which is why this item records `not-delegable:` beside a
`verify:` that only proves no closed blocker is still named.

**#757 merged, so the gate moved under this item** (`PL-028T`, 2026-09-20,
verified against `origin/main` at `9ade366` rather than against the pull
request). The frozen list went from 175 entries to **178**: `PL-0RZ0`
(`safety`), `PL-D126` and `PL-WJNS` (`science`) were added under the
unconditional safety/science exception. So v0.5.0's gate now has **five** open
entries, not two - `PL-WZVZ` and `PL-8PS6` plus those three - and promoting the
two this item covers no longer clears it.

Three consequences, all of them corrections to text above rather than new work:

- The **Why it matters** heading no longer says these two *are* the remainder.
- The `payoff:` was rewritten. It said the pass takes the gate off "two
  promotions from clear", which was true when written and is not now.
- **What is true right now** said 173 of 175 cleared; read `bin/docket wave`
  for the live split rather than any number written here.

**The pass itself is unchanged.** The three items needing a disposition are the
same three, for the same reason, and the `verify:` command does not read the
gate. What changed is only what closing this item buys.

## The pass, 2026-09-20

**Four items, not three.** `bin/docket check` named `PL-CTD7` (detect a bookmark
crossing inside the advance loop) as a fourth promotable item after `PL-LPLD`
merged as `#758`, which this brief predates. It is worked here on the same
reasoning and by the same test.

**One of the four was promotable.** Each was read against the tree as it now
stands, and the reasoning lives in the item rather than here:

| item | disposition | why |
| --- | --- | --- |
| `PL-8PS6` | `ready`, `P1` | the machine profile carrier exists and the abstraction slots the field; the split is buildable over one profile |
| `PL-439V` | `done` | `docs/machine-abstraction.md` § "Dial mapping" already answers all three clauses of its `Done when.` |
| `PL-WZVZ` | stays `blocked`, now `PL-TH35, PL-R1WQ` | one machine profile, no selection surface; and its table is a new display surface, deferred by item 34's standing rule |
| `PL-CTD7` | `needs-decision`, `P1` | two user-facing questions were written into it on 2026-09-20, after its last triage |

**Both band moves are the `anticipated` exemption lapsing, not a re-rating.**
`check_gate_reentries` exempts a `safety` item from the `P1` floor only while
`anticipated` and `status: blocked` hold together, so leaving `blocked` is the
event that returns the finding to the debt gate. `docket set` refused both moves
at `P2` in those words. Neither hazard is live; `anticipated` stays on both.

**`ROADMAP.md` was edited, which widened this item's `touches`.** Re-pointing
`PL-WZVZ` at two v0.6.0-placed items is a gate deferral, and § "The gate is a
snapshot, not a moving target" permits one only where the deferral section "says
so and says why" - a `blocked-by:` field alone is the `PL-9S30` defect. Two
paragraphs in § "Declined to Gate 2 on the refilling-queue ground" said the two
entries both wait on `PL-FG9D`; both now say what is true.

**`PL-CHQY` closes with this.** It was filed the same day from the same
advisory over the same three items - two sessions, one finding - and its
`Done when.` is satisfied in full by this pass.

**The measurement went to `PL-6T44`**, the recorded generator behind the
appearance, which is at `needs-decision` and weighing exactly this: across this
pass and `PL-JFQ3`'s, 13 items the advisory called promotable, 6 genuinely
startable. The decision is not answered there; the count it rests on is.
