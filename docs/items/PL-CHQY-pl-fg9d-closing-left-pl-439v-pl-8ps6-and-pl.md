---
id: PL-CHQY
title: PL-FG9D closing left PL-439V, PL-8PS6 and PL-WZVZ blocked on a closed blocker, two of them safety and anticipated, which is PL-JFQ3 recurring within the hour of PL-JFQ3 closing
priority: P2
effort: S
status: done
classes: docs
touches: docs/items
added: 2026-09-20
closed: 2026-09-20
pr: 765
payoff: returns two safety findings to the debt gate built to catch them, or records why their hazards are not live yet, instead of leaving them held outside it by a stale blocked status
not-delegable: the deliverable is a per-item judgment recorded in three item files - whether each was blocked on something nobody wrote into blocked-by, and for the two safety/anticipated ones whether the design document landing made the hazard live - and no command can tell a promotion that was reasoned from one that was typed
---

**Problem.** PL-FG9D closing left PL-439V, PL-8PS6 and PL-WZVZ blocked on a closed blocker, two of them safety and anticipated, which is PL-JFQ3 recurring within the hour of PL-JFQ3 closing

**What was found, 2026-09-20.** `PL-JFQ3` closed a grooming pass over nine items
whose blockers had closed. Within the hour, `PL-FG9D` (design the base
anesthesia-machine abstraction) merged as `#748`, and `bin/docket check`
immediately reported three more:

| item | classes | `blocked-by` |
| --- | --- | --- |
| `PL-439V` | `docs, anticipated` | `PL-FG9D` |
| `PL-8PS6` | `safety, anticipated, refactor` | `PL-FG9D` |
| `PL-WZVZ` | `safety, anticipated, ux` | `PL-FG9D, PL-4DCG` |

Both blockers are closed - `PL-FG9D` 2026-09-20 (`pr: 748`), `PL-4DCG`
2026-09-19 (`pr: 742`).

**Why it is not simply "run `PL-JFQ3` again".** Two of the three are
`safety, anticipated`, so this is the `PL-ZF2G` mechanism a second time:
`check_gate_reentries` exempts an item from the `safety`/`science` gate
advisory only while `anticipated` and `status: blocked` hold *together*, so
promoting either is the event that returns a safety finding to the debt gate.
Each needs the same judgment `PL-JFQ3` applied - whether `PL-FG9D` closing made
the hazard live or merely removed one prerequisite - and on `PL-JFQ3`'s own
evidence that question does not have a uniform answer: of its nine, five were
genuinely startable, three were blocked on something nobody had written down,
and one was already done by another item.

The relevant precedent for these three is `PL-JFQ3`'s `PL-KZ99` case rather
than its promotions: the machine abstraction is a *design document*
(`docs/machine-abstraction.md`), and a design landing is not the same event as
the code it specifies existing. Read each against the tree before promoting.

**The pattern, which is the part worth more than the three items.** The
advisory fires whenever a blocker closes, and nothing routes it to anybody: it
is a standing line in `bin/docket check` that only a session running a
deliberate grooming pass acts on. `PL-JFQ3` was filed as a one-off and it
recurred the same day. The obvious cheaper route - make "what does this
unblock?" part of the `docket` skill's close-out, where the session closing an
item is the one that knows what it means - is **recommended and deliberately
not implemented here**, because `CLAUDE.md` reserves a change to how sessions
work for the session the project owner asks for it in. It is put to them in the
reply that filed this item.

**Why it matters.** `bin/docket next` reads `status`, so a blocked item whose
blockers have all closed is startable work nobody is ever offered - and on two
of these three it is also a `safety` finding held outside the gate built to
catch it, which is the mechanism `PL-ZF2G` installed working exactly as
designed and reaching nobody.

**Done when.** Each of `PL-439V`, `PL-8PS6` and `PL-WZVZ` has been read against
the tree and either promoted out of `blocked`, or left blocked with the real
blocker written into `blocked-by`; and for the two `safety, anticipated` ones,
whether `PL-FG9D` closing made the hazard live or merely removed one
prerequisite is recorded in the item.

## Closed by the `PL-8G48` pass, 2026-09-20

`PL-8G48` was filed the same day, from the same `bin/docket check` advisory,
over the same three items - two sessions reaching one finding. This item's
`Done when.` is satisfied in full by that pass rather than separately, so it
closes with it rather than being dropped as a duplicate: the work was wanted and
was done.

Each disposition, and where the reasoning is recorded:

| item | disposition | in the item under |
| --- | --- | --- |
| `PL-439V` | `done` - `PL-FG9D`'s specification already satisfied it | "Satisfied by `PL-FG9D`'s specification" |
| `PL-8PS6` | `ready`, band to `P1` | "Promoted, 2026-09-20, and what the tree now supplies" |
| `PL-WZVZ` | stays `blocked`, re-pointed to `PL-TH35`, `PL-R1WQ` | "Re-pointed, 2026-09-20" |

**And the `safety, anticipated` question this item asked is answered for both:
`PL-FG9D` closing removed a prerequisite and did not make either hazard live.**
There is still one machine profile and no selection surface, so nothing is
currently misattributing anything and nothing displayed is wrong. What separates
the two is startability, not liveness - `PL-8PS6`'s split is buildable over one
profile and `PL-WZVZ`'s comparison is not buildable at all - which is why one
returns to the debt gate and the other does not.

**The pattern section above is still live and is carried in the reply**, not
here: nothing yet routes the promotable advisory to anybody, and `PL-6T44` now
holds the measurement this pass produced against its own open decision.
