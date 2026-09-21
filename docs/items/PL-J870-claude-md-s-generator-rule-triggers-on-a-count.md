---
id: PL-J870
title: CLAUDE.md's generator rule triggers on a count of three items, but promotion is being declined on severity: two sessions read PL-9HD1's FIELD_RE cluster oppositely on 2026-09-21 and nothing records which test governs
priority: P2
effort: S
status: done
classes: planning, docs
feature: generator-identification
milestone: v0.5.0
touches: CLAUDE.md
added: 2026-09-21
closed: 2026-09-21
pr: 827
payoff: what enters the one tier that outranks a safety-classed P1 stops depending on which session reads the cluster
verify: grep -q 'The count decides the record; expected recurrence decides the rank' CLAUDE.md
---

**Problem.** CLAUDE.md's generator rule triggers on a count of three items, but promotion is being declined on severity: two sessions read PL-9HD1's FIELD_RE cluster oppositely on 2026-09-21 and nothing records which test governs

**The two readings, both from 2026-09-21.** `PL-9HD1` names `model.py:33`'s
`FIELD_RE` - a line-at-a-time front-matter read - as the one mechanism behind
`PL-5B39`, `PL-FX0K` and `PL-V6CR`.

- **Read as a count.** `CLAUDE.md` says "a mechanism a session identifies as the
  cause of three or more items is a *generator*", and the recording instruction
  is `root-cause-of:` naming "three or more, or it is an ordinary item". Three
  items, one mechanism, so it is a generator and ranks above every band but
  `P0`.
- **Read with a severity test.** A parallel session measured the blast radius
  and declined promotion as "short of the bar for ranking above every band",
  while agreeing the three are one change.

Both sessions agreed on the mechanism and on the fix. They disagreed only on
rank, and the resident text names no severity test to settle it.

**Verified here against the tree, 2026-09-21**, so the next session need not
re-derive it:

| Claim | Result |
| --- | --- |
| Item files carrying a multi-line front-matter value | 12, of which **0 are open** |
| `cmd_record`'s writer | `insert_field` (`cli.py:2739`), safe |
| The exposed path | `cmd_set` via `rewrite_item` (`cli.py:1128`) |
| Measured loss | `PL-9HDH` 27 lines to 18, 9 of 10 `reason:` lines gone, exit 0 |

So the severity reading has real numbers behind it. That is the point: the
numbers are what decided it, and the rule as written never asks for them.

**Why it matters.** The generator tier is the one rank that outranks every band
including a `safety`-classed `P1`, so what enters it cannot be a judgment two
sessions make oppositely from the same text. Left as is, promotion depends on
which session reads the cluster, and `PL-XF5V`'s cluster-drain reporting would
be counting a population whose membership rule is unstated.

**Done when.** `CLAUDE.md`'s generator rule says which test governs - the count
alone, or the count plus a stated severity condition - in one sentence, and the
sentence names what it replaces per the resident-set rule. If severity governs,
the condition is written concretely enough that two sessions reach the same
answer on `PL-9HD1`'s own numbers.

**Not a re-litigation of `PL-9HD1`.** Its disposition was settled by the session
that measured it and relayed on the project owner's instruction; this item is
about the rule that produced two answers, not about that cluster's rank.

**Decision needed.** Which test governs entry to the generator tier - the count
of three or more items that `CLAUDE.md` states, or that count plus a severity or
recurrence condition - and if the latter, what the condition is in words two
sessions would apply the same way.

**Recommendation, for the project owner to accept or replace.** Neither reading
is right as stated, and the rule's own sentence says why: a generator ranks
where it does because "every session it stands through pays it again". That is a
claim about **future inflow**, not about the damage any one instance does. So:

- **The count governs recording.** Three or more items over one mechanism means
  `root-cause-of:` gets written. It is an auditable fact and nothing about
  severity changes it.
- **Expected recurrence governs the rank.** A recorded generator outranks every
  band but `P0` when the mechanism is still generating items - the store keeps
  handing it new members - and ranks on its own band when it is not.

`PL-9HD1` comes out consistent under this: recorded as a generator on the count,
ranked on its band because the form that triggers the truncation appears in
**0 open items** and the routine writer does not use the unsafe path. The
parallel session reached the right rank by a test the text does not carry; this
gives that test a name the next session can apply without measuring from
scratch.

The alternative worth stating: keep the count for both, and accept that a
three-item cluster of any severity outranks a `safety`-classed `P1` until
worked. That is what the text says today, and it is defensible - it is simply
not what either session did.

## Decided and shipped, 2026-09-21

**The recommendation above was ratified as written** (project owner,
2026-09-21, ratified, over keeping the count for both tests and accepting that
any three-item cluster outranks a `safety`-classed `P1`). `CLAUDE.md`'s
generator bullet now carries it: the count decides the record, expected
recurrence decides the rank, and a spent generator is recorded for the audit
and ranks on its own band.

**What the edit replaced**, per the resident-set rule: the bullet's closing
flourish - "This is the shape of the behavior-change rule below and holds for
the same reason - an item alone changes nothing, and a weed left standing
seeds" - collapses to the clause that carried the argument. It still nets +601
characters, and `tools/doc_check.py`'s growth advisory names that disposition
itself: "Text the project owner asked for is the second answer, already given.
Never trim other resident text to offset the number."

**One clause the approval did not state, answered here.** The two endings -
fix it now, or end the reply with a prompt - followed from the tier, so they
now bind a *ranking* generator and a spent one is ordinary work under the
capture rule. Stating it the other way would have left a session owing fix-now
treatment to a cluster the same rule had just told it not to rank.

**The code half is `PL-T7QR`.** `plan.recommend` still ranks on the field
alone, so until it carries the distinction a spent generator is demoted by the
session rather than by the tool. `CLAUDE.md` says so in the same bullet rather
than leaving prose and tool silently disagreeing.
