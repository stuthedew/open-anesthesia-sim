---
id: PL-W80S
title: The 150k handoff budget leaves ~35k of headroom over a ~115k session-start baseline, so read literally it refuses to start almost any M item
priority: P2
effort: M
status: needs-decision
classes: session-cost
feature: context-budget-reading
touches: CLAUDE.md
added: 2026-09-20
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
