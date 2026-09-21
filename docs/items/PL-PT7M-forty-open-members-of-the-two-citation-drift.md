---
id: PL-PT7M
title: Forty open members of the two citation-drift heads have no drain plan: PL-4FBP and PL-G424 both closed their mechanism, and the 40 repairs they named sit in the flat P2 band as forty independent items with no batch, no check and no disposition
priority: P2
effort: M
status: ready
classes: planning, docs, housekeeping
feature: citation-drift-drain
touches: docs/items, docs/WORKING_NOTES.md
added: 2026-09-21
payoff: 40 items the project has already decided about stop being offered as work, and the open count stops carrying non-findings
verify: test "$(grep -cE '^\| PL-[A-Z0-9]{4} \|' docs/items/PL-PT7M-forty-open-members-of-the-two-citation-drift.md)" -eq 40
---

**Problem.** Forty open members of the two citation-drift heads have no drain plan: PL-4FBP and PL-G424 both closed their mechanism, and the 40 repairs they named sit in the flat P2 band as forty independent items with no batch, no check and no disposition

**Measured 2026-09-21, over the whole store.** Eleven `root-cause-of:` heads
and one `impairs-generators:` head are recorded; all twelve are closed. Their
99 distinct members are not: 60 are still open, and the count is *unchanged*
from `PL-XF5V`'s measurement of 2026-09-20 - same 60, same per-head split, no
drain in a day. Two heads carry two thirds of it:

| Head | What its close fixed | Members | Still open |
| --- | --- | ---: | ---: |
| `PL-4FBP` | a live assertion must name what it asserts | 24 | 21 |
| `PL-G424` | `.claude/rules/citation-drift.md`, apparatus side | 21 | 19 |

The other five undrained heads - `PL-BHVM` (6), `PL-4Q9B` (6), `PL-6TP8` (4),
`PL-G21K` (3), `PL-L4YG` (1) - total 20 and are ordinary tails. Four heads
(`PL-2T03`, `PL-6T44`, `PL-HWW1`, `PL-TZ7T`) are genuinely drained.

**The 40 are not one kind of work, which is the finding.** Read individually
rather than counted, they split three ways:

- **9 are check-building**, all under `PL-4FBP`: `PL-036`, `PL-2M9N`,
  `PL-5N7T`, `PL-9LXK`, `PL-4RHP`, `PL-DHJ7`, `PL-8LDF`, `PL-41YP`, `PL-GQWP`
  each propose binding one class of prose claim to the tree in
  `tools/doc_check.py`. These are the leverage - a check retires its repair
  class forever - and they are ordinary engineering items that happen to sit
  under a drift head.
- **27 are single live-document repairs**: 7 in `docs/WORKING_NOTES.md`, 6 in
  open item briefs, 3 in `CLAUDE.md` or the docket skill, the rest in
  `ROADMAP.md`, `docs/ARCHITECTURE.md` and `README.md`.
- **4 are not startable**: `PL-NWTM` carries a `blocked-by` edge of its own,
  and `PL-Z5FG`, `PL-6QZP`, `PL-QV5Y` sit at `needs-decision`.

**37 of the 40 were filed before `.claude/rules/citation-drift.md` existed**
(project owner, 2026-09-19, ratified), and that rule disposes of some of them
outright: drift in a closed brief is not a finding, and re-pointing a line
number is banned rather than asked for more carefully. `PL-38PN` and `PL-JXVD`
are that exact shape - two generations of line-number repair - and `PL-RFSL`
already records that `PL-38PN`'s remaining deliverable is refused by the rule.
Nobody has re-judged the rest against it.

**What is not the answer.** Dropping the tail wholesale is the move `PL-LKGL`
refuted: the count nobody ran came back 67% still-real findings. The re-judging
below is a per-item test against a ratified rule, not a bar being raised.

**Recommendation (a session's, not the project owner's), in order:**

1. **Re-judge all 40 against `.claude/rules/citation-drift.md`.** Drop what the
   closed-brief clause and the line-anchor ban refuse, with `reason:` naming
   the clause. This is a reading pass over 40 briefs, not an editing pass, and
   it is the only step that needs no decision.
2. **Sweep the 27 live-document repairs in one pass per file**, not as 27
   items. The rule already says a drift repair rides the commit a session is
   already making; what is missing is one pass that clears the standing
   backlog, and the members cluster in four files.
3. **Rank the 9 check-building members on their own merits**, outside any
   drift sweep. `tools/doc_check.py` is where the class ends.

**Decided (project owner, 2026-09-21, ratified)**, over working the whole
three-step recommendation now and over deferring all of it behind `v0.5.0`:
**step 1 only.** Re-judge the 40 against `.claude/rules/citation-drift.md` and
drop what it refuses. The 27-repair editing sweep is **deferred** behind
`v0.5.0`'s product beat - none of the 27 blocks a learner-visible behavior - and
the 9 check-building members are **out of this item**, to be ranked on their own
merits like any other `tools/doc_check.py` work.

**Why it matters.** 37 of the 40 were filed against a convention that did not
exist yet, and the rule that now governs them refuses some outright. Until they
are re-judged, `bin/docket next` offers work the project has already decided not
to do, and every count of the open queue - including `PL-04KR`'s convergence
baseline - carries items that are not findings. It is also the cheapest 40-item
movement available: a reading pass against a written rule, with no editing and
no decision left in it.

**Done when.** Every one of the 40 open members of `PL-4FBP` and `PL-G424` has
been read against `.claude/rules/citation-drift.md` and either

- dropped, with `reason:` naming the clause that refuses it - the closed-brief
  clause, or the line-anchor ban; or
- kept, with the kind it is (check-building, live-document repair, or not
  startable).

Either way it gets one row in a disposition table in this brief, of the shape
`| PL-XXXX | kept/dropped | clause or kind |`, so the next session reads the
outcome instead of re-deriving it. That table is what this item's `verify:`
counts - 40 rows, one per member, whatever each row says. `PL-38PN` and `PL-JXVD` are the two known
candidates for the line-anchor ban and `PL-RFSL` already holds the finding for
one of them, so neither is a fresh judgment.

**Not a bar being raised.** Each drop cites a clause of a ratified rule against
one item's own brief. Nothing here changes what may be captured in future, which
is the move `PL-LKGL` refuted.

**Where it came from.** The project owner asked on 2026-09-21 whether the
generators and their clusters were dealt with. Answering it took a script over
the whole store - the read `PL-XF5V` exists to replace - and the answer was
"the heads yes, the clusters no", with these two heads accounting for 40 of the
60 open members.
