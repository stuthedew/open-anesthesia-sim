---
id: PL-JB3Z
title: Decide whether the workflow lane's capture or tagging criteria change, on the never-was-an-issue versus overtaken split the 2026-09-19 staleness sweep measured
priority: P2
effort: S
status: untriaged
classes: docs, infra
feature: apparatus-capture-criteria
touches: .claude/skills/docket/SKILL.md, docs/items
added: 2026-09-19
---

**Problem.** Decide whether the workflow lane's capture or tagging criteria change, on the never-was-an-issue versus overtaken split the 2026-09-19 staleness sweep measured

**The measurement.** `PL-6ZQY`'s sweep read all 166 open workflow-lane items
against the tree on 2026-09-19 and dropped 12 (7.2%): **7 overtaken** and **5
that were never an issue**. A further 3 of the 10 partly-overtaken items rest
partly on a premise that was false at filing, and 1 more was flagged and kept.
Nine of 166 (5.4%) therefore rest wholly or partly on a stale premise, and seven
of those nine were filed in the twelve days before the sweep, so the mechanism
is live rather than historical.

**The answer to "are we over-tagging" is no, and the distinction is the whole
finding.** Over-tagging would mean filing things that are true but not worth
fixing. That is not what is in the lane: 154 of 166 are real defects, each
carrying a file, a line and a command that still fails. The five bad items were
not over-tagged — they were **mis-observed**. Their premise about the tree was
already false on the day they were written.

- `PL-RZPX` asked for a no-`touches` report that had shipped in docket's first
  commit the day before.
- `PL-T86P` said `PL-SCB4` carried no `**Decision needed.**` section; it had one
  from the day it was created, and the checker has enforced that since docket's
  first commit.
- `PL-3GSZ` rested on two items being open; both had closed eight days earlier.
- `PL-77SV` rested on `PL-G8TR`'s `Done when` naming a block's shape; it was
  byte-identical on the filing date and names the guard's behaviour.
- `PL-YNYK` asserted a falsifying count that its own body records as zero.

**Why it matters.** The project owner's position, 2026-09-19: "We should fix
anything that is an actual issue or drop it. Otherwise what's the point of
having it in the queue." A false item costs more than its own line. It is
triaged by one session, ranked by `bin/docket next`, read past by every session
after that, counted into the debt gate, and finally found only by a sweep that
reads the whole lane. `PL-6ZQY`'s first attempt at that sweep died at its usage
limit; the second cost twelve agents and 145,000 tokens of briefs. That is the
recurring price of not checking a premise once, at the moment somebody already
has the item open.

**Two tightening proposals, both refuted by running the count first**, as
`.claude/rules/expert-review.md` requires.

*Raise the bar on a band or a class.* For this to be right, what it suppresses
would have to be mostly dead. Measured over the swept 166:

| Filter | dead killed | still-real killed | precision |
| --- | --- | --- | --- |
| drop the `P3` band | 8 | 73 | 10% |
| `P3` and effort `S` | 8 | 62 | 11% |
| `docs`-classed | 5 | 45 | 10% |
| touching `docs/items` | 8 | 23 | 26% |
| filed over 7 days ago | 2 | 49 | 4% |

Every one is worse than the 67%-still-real count that already refuted this
proposal on `PL-LKGL` and `PL-27S8`. It stays refuted.

*Make `docket check` flag a brief asserting another item is open when it is
closed.* Eight of the twelve drops turn on exactly that, so it looks decidable —
which is the shape `CLAUDE.md` says to prefer. It fails its own threshold test.
For it to earn a place it would have to fire rarely and mean something each
time. Counted over the open workflow and crossing items: **26 such assertions,
14 of them naming an item that is now closed** — and roughly twelve of those
fourteen are correct past-tense narration (`PL-BNYF audited 49 open items`,
`PL-D188 on 2026-09-05, both triaged to ready`). A check that fires fourteen
times to be right twice is `CLAUDE.md`'s own definition of a defect in the
check. Do not build it.

**Why the existing discipline cannot catch this class, which is the part worth
keeping.** Triage already runs the `verify:` command and watches it fail. Three
of the five — `PL-3GSZ`, `PL-77SV`, `PL-T86P` — carried a `verify:` that was run
and failed correctly, because no fix existed, while the premise was already
false. `PL-LKGL` named the mechanism from the other end: a `verify:` command
tests for the presence of the fix, never for the presence of the fault. So the
gap is exact and is not a bar: **triage proves the fix is absent; nothing ever
proves the fault is present.**

**Decision needed.** Whether triage gains one obligation: **reproduce the fault
once, and record the observation with its date**, beside the existing rule that
the `verify:` command is run and watched fail. Three candidates:

1. **Add it to the docket skill's triage mode.** One paragraph in a document
   that already loads at exactly that moment, so its resident cost is zero. It
   catches roughly one item in thirty-three triaged, at a cost of about one
   command each. **This is the recommendation.**
2. **Do nothing.** Five items in 166 is 3%, and a sweep can drain them. The
   honest case for this is that the sweep found the lane 87% real, so the
   problem is small; the case against is that the sweep cost twelve agents
   reading 145,000 tokens of briefs, which is not a cheap recurring remedy.
3. **Put it at capture instead.** Refused, and named here so it is not
   re-proposed: `CLAUDE.md`'s capture rule is unconditional by design because a
   thought lost to a rate limit is the worst available outcome, and adding a
   verification step to ideation-mode capture would break even only if it lost
   fewer than 3% of ideas.

Candidate 1 does not touch capture and does not change what reaches the project
owner's desk, so it is a change to how sessions triage rather than to what gets
filed.

**Done when.** One of the three candidates is recorded as decided, with what it
was chosen over; and if candidate 1, the paragraph is in
`.claude/skills/docket/SKILL.md`'s triage mode and a later sweep can tell whether
it fired.

**Related, and not duplicated here.** `PL-YVV4` is "run the suppression count
`expert-review.md` requires" for `PL-VV6N` (whether the queue needs an expiry
rule). The table above **is** that count for the workflow lane — 73 still-real
suppressed to catch 8 dead. It is not written onto `PL-YVV4` because that item's
scope is the whole store's 109 open `P3` items, not this lane's, and because
this sweep was commissioned not to work the items it keeps.

**Note for triage.** Left `untriaged` deliberately, on `PL-G424`'s precedent from
earlier the same day. `needs-decision` makes this debt under "The debt gate",
and v0.5.0's gate was frozen 2026-09-06 with two open entries left of 175 — so
an undispositioned entry fails
`test_this_repository_records_a_disposition_for_every_open_debt_item`, and
disposing of it means editing a frozen list in `ROADMAP.md` during a sweep
commissioned not to widen into the product lane. The disposition is genuinely
open rather than dodged: the *finding* is from 2026-09-19, which sends it to
the next gate, but the *problem* has instances back to 2026-08-25 (`PL-RZPX`),
which under "The gate is a snapshot" would put it on the list instead.
`check_gate_reentries` decides that, not this note. Whoever triages this seats
the band and the gate together.
