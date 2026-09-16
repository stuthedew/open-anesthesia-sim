---
id: PL-XWH4
title: A decision the owner ratified and one they specified read identically in the record, so a later session cannot tell a design they authored from a recommendation they agreed to, and defends both at the same bar
status: done
added: 2026-09-16
priority: P2
effort: S
classes: planning, docs
touches: CLAUDE.md, ROADMAP.md, docs/MODEL.md
closed: 2026-09-16
verify: python3 tools/doc_check.py check && grep -qF 'are not the same' CLAUDE.md && grep -qF 'ratified' CLAUDE.md
---

**Problem.** A decision the owner ratified and one they specified read identically in the record, so a later session cannot tell a design they authored from a recommendation they agreed to, and defends both at the same bar

**Why it matters** (project owner, 2026-09-16, in their own words). "Agree with
recs" does not mean a hard decision: "It means you suggested it, and nothing
jumped out at me as obviously wrong (though I may have not read everything
carefully to be honest, or even if I did a nuance may not have been appreciated
by me)." Something they spelled out - specific desired user-facing behavior - is
firmer, "though would reconsider if very compelling argument against". Recorded
identically, the two get defended identically, and the weaker one gets defended
at the stronger one's bar: a later session reads "(project owner, DATE)" and
treats a recommendation it made itself as settled.

**What was asked for, and what was deliberately not.** The owner asked for
honest reconsideration down the road rather than "this is what it is because the
owner commanded it", and said making the trade-offs clearer would be a bonus -
but explicitly not at the price of "adding a bunch of context that will just
weaken everything else". So the trade-off half is one clause naming what a
decision was chosen over, not a section: the reply that put the case is gone
after the session, and one clause is the cheapest thing that keeps the
alternative recoverable.

**Done when.** `CLAUDE.md` § "Working with the project owner" states the two
kinds, the notation, the two bars to reopen, and that the safety-critical
standard overrides both; and the decisions taken in the session that asked for
it are marked in the form it defines.

**Landed 2026-09-16, in the session that asked for it**, per `CLAUDE.md`'s
behavior-change rule. The three decisions that scoped `ROADMAP.md` item 34 the
same day were all ratified recommendations rather than specified behavior, and
are marked so in `ROADMAP.md` and `docs/MODEL.md` with what each was chosen
over. `PL-QNMM` is the retrospective sweep of everything attributed before this
convention existed.
