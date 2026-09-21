---
id: PL-W80S
title: The 150k handoff budget leaves ~35k of headroom over a ~115k session-start baseline, so read literally it refuses to start almost any M item
priority: P2
effort: M
status: done
classes: session-cost
feature: context-budget-reading
touches: CLAUDE.md, tools/context_reading.py, tests/unit/test_context_reading.py, docs/ARCHITECTURE.md, docs/maintainer.md, docket.toml, docs/items/PL-BZVY-get-session-s-context-usage-used-tokens-does.md
added: 2026-09-20
closed: 2026-09-21
pr: 835
verify: grep -q 'def test_a_missing_reading_exits_non_zero_rather_than_reporting_zero' tests/unit/test_context_reading.py && grep -q context_reading.py docs/ARCHITECTURE.md
---

**Problem.** The 150k handoff budget leaves ~35k of headroom over a ~115k session-start baseline, so read literally it refuses to start almost any M item

**Measured 2026-09-20**, in the session that worked `PL-CTD7`.
`get_session` reported `external_metadata.context_usage.used_tokens` at
**115,320** before the session had read a single project file: the resident
set (62,458 characters), the session-start digest, and the `docket` skill body
(91,770 characters, loaded because `CLAUDE.md` requires it for any queue
workflow) are all in that number.

`CLAUDE.md` § "Session and tool-use efficiency" says to hand off at about
150,000 and to check *before* starting an item, handing off rather than
starting if it will not fit. Applied literally that leaves about 35,000 tokens
of headroom, which no `M` item fits - this one used roughly ten times it - so
a session obeying the rule would hand off having done nothing, and the next
session would start from the same baseline and do the same. What actually
happens is that the rule is read as advisory and the number is ignored, which
is worse than either: `CLAUDE.md` calls this "the largest adherence lever the
project has", and a lever nobody can pull is not one.

**The same file already records the counter-evidence** without drawing this
conclusion: seven concurrent sessions on 2026-09-16 were carrying 263k-519k,
and the session that wrote the stopping rule read 176,689 before it looked.
Those are the observed working range; 150,000 is below all of them.

**What is not being proposed here is raising the number**, which would be
`PL-LKGL`'s error - tightening or loosening a threshold without counting what
the change suppresses. What needs deciding is what the budget is *for*: it was
written as a stopping rule about a 1,000,000-token window, and the quantity
that matters may be the spend since the baseline rather than the absolute
reading. Name the number that would change the answer, then count it.

Sibling: `PL-BZVY`, which is why the reading a session takes is stale anyway.

**Why it matters.** `CLAUDE.md` calls the handoff budget "the largest adherence
lever the project has", and the number it states cannot be pulled: 115,320
tokens are spent before a session has read a project file, so 150,000 leaves
about 35,000 of headroom and no `M` item fits. A session obeying the rule
literally hands off having done nothing and the next starts from the same
baseline; what happens instead is that the rule is read as advisory and the
number ignored, which is the worse of the two - an advisory being routed
around, the second of `CLAUDE.md`'s own compounding-friction tests, sitting on
the mechanism that decides when every session stops.

**Done when.** The budget names an observable a session can read and act on -
with what it is measuring stated, not only its value - and `CLAUDE.md`'s
§ "Session and tool-use efficiency" carries it, so a session reading the rule
can follow it rather than discount it.

**Decision needed.** What the handoff budget measures: the absolute
`used_tokens` reading it names today, or the spend since the session's own
baseline. This is the project owner's, because the 150,000 figure is a ratified
owner decision (2026-09-16) about how every session stops, and `CLAUDE.md`'s
own rule is that a ratified decision reopens on ordinary evidence and is put
back to them rather than replaced.

**Recommended:** measure the spend since the baseline, not the absolute
reading, and set the number only after counting. The baseline is a fixed cost
the session did not choose - the resident set, the digest, the `docket` skill -
so a budget stated against the absolute reading is mostly a budget on the
apparatus rather than on the work, and it moves every time the resident set
grows. Spend-since-baseline is the quantity the rule is actually about: how
much this session has added. What the number should be is a separate question
and must not be answered in the same breath - `PL-LKGL` is the standing refusal
to move a threshold without counting what the move suppresses, and the count
here is the distribution of per-session spend over recent sessions, which the
session listing carries.

**Its sibling is why the reading is stale anyway.** `PL-BZVY` measured that
`used_tokens` does not refresh within a turn, so whichever observable is chosen
has to be one a session can read mid-item. That item is `blocked` on this one.

## Measured and counted 2026-09-21, and the decision is now the only thing left

**The count the brief above asked for, run.** Final `context_usage.used_tokens`
across the 24 most recent archived sessions: minimum **173,021**, median
**313,293**, maximum **495,290**, on a 1,000,000-token window. **None of the 24
finished at or below 150,000** - the smallest overshoot is 15% and the median
is more than double the budget. Subtracting the baseline gives per-session
spend of roughly 60,000-390,000 with a median near 200,000, against headroom of
35,000-69,000 under the current rule. The brief's claim that no `M` item fits
is not an estimate; the budget is below the observed minimum.

**Naming the number that would make the recommendation wrong, per
`PL-LKGL`.** Spend-since-baseline is the wrong quantity if the binding
constraint is the *window* rather than the per-turn cost, because a window
constraint cares about absolute occupancy and not about who chose it. Counted:
the maximum occupancy in 24 sessions is 495,290 of 1,000,000, so nothing has
reached half the window. The window is not binding and a budget defending it
would defend against something that has never happened. `CLAUDE.md` states the
constraint that *is* binding in its own first line - "Session cost is turns
times context" - which is a cost constraint, and under it what a handoff buys
back is exactly the distance above the floor it restarts at.

**The baseline is variable, which the brief above did not know.** This session
read **81,048** at its first request with no skill loaded; `PL-CTD7`'s read
115,320 with the `docket` skill body in context. So the same absolute budget
grants 35,000 or 69,000 of headroom depending on whether the session did a
queue workflow - a 42% swing in the thing being budgeted, driven by something
`CLAUDE.md` requires. An absolute number cannot hold still.

**The gauge reads zero, not stale, which is worse than `PL-BZVY` found.**
`get_session` returned `used_tokens: 0` for this session while its transcript
showed 112,857, and the same listing showed **all six** concurrently RUNNING
sessions at 0. The field is written at turn boundaries, so before the first
boundary it reads 0 and after it reads late. The prescribed check happens
inside a turn, which is where it reads 0.

**A mid-turn observable exists, and is now built.** `tools/context_reading.py`
reads this session's own transcript - `$CLAUDE_CONFIG_DIR/projects/*/`
`$CLAUDE_CODE_SESSION_ID.jsonl`, appended as each request happens rather than
at turn boundaries - and reports `baseline`, `context` and `spend`. Verified
live: the series moved 81,048 -> 112,857 across 15 requests inside one turn
while `get_session` held at 0. It prints all three and decides nothing, so it
is correct under either answer below. This unblocks `PL-BZVY`, whose open
question was whether such an observable exists from inside a session.

**Recommendation, unchanged in direction and now carrying its count:** state
the budget against **spend since baseline**, read with
`tools/context_reading.py`, and set it at **150,000 of spend** - which is the
owner's own ratified figure, re-anchored to the quantity it was always about
rather than a new number chosen to fit. Against the counted distribution that
still stops roughly the top third of sessions before they start another item,
where the present rule stops 100% of them from starting anything and is
therefore ignored instead.

**Both parts are the project owner's**, per `CLAUDE.md`'s rule that a ratified
decision (2026-09-16) reopens on ordinary evidence and goes back to them: the
quantity, and whether 150,000 carries over to it.

## Decided and landed 2026-09-21

**Both recommendations ratified** (project owner, 2026-09-21, ratified, over
keeping the budget on the absolute reading and accepting one that is mostly a
budget on the apparatus and moves whenever the resident set does). The budget
measures **spend since the session's own baseline**, and **150,000** carries
over to it - the same figure ratified on 2026-09-16, re-anchored to the
quantity it was always about rather than a new number chosen to fit.

`CLAUDE.md` § "Session and tool-use efficiency" now states it, names
`python3 tools/context_reading.py` as the instrument, and says in one clause
why not `get_session`. The resident set grew 442 characters; nothing was cut
to offset it, because `tools/doc_check.py`'s own advisory forbids trimming
other resident text for that purpose, and the addition is text the decision
required - the new quantity, the new instrument, and the attribution clause
the ratified-decision rule mandates.
