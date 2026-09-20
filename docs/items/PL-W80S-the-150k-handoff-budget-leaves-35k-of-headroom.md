---
id: PL-W80S
title: The 150k handoff budget leaves ~35k of headroom over a ~115k session-start baseline, so read literally it refuses to start almost any M item
status: untriaged
feature: context-budget-reading
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
