---
id: PL-Z4WL
title: Planned-milestone item 1 does not name PL-4DCG or PL-FG9D, the survey and design round that scope it, and ROADMAP.md twice says PL-FG9D has no planned-milestone line of its own when item 1 is that line
priority: P3
effort: S
status: done
classes: docs
milestone: v0.4.26
touches: ROADMAP.md, docs/items
added: 2026-09-16
closed: 2026-09-16
pr: 604
verify: grep -q 'PL-4DCG' ROADMAP.md && ! grep -q 'has no planned-milestone line of its' ROADMAP.md
---

**Problem.** Planned-milestone item 1 does not name PL-4DCG or PL-FG9D, the survey and design round that scope it, and ROADMAP.md twice says PL-FG9D has no planned-milestone line of its own when item 1 is that line

**Why it matters.** `PL-4DCG` and `PL-FG9D` are the root of a chain that carves
two `safety`-classed entries out of Gate 1 - `PL-8PS6` and `PL-WZVZ` - and
`bin/docket wave` correctly reports them as blocked on work outside the gate.
The project owner asked, reasonably, whether such blockers should be pulled
into the gate automatically; the answer is no (it would import an unbounded
transitive closure and make a frozen list a moving one), but the question only
arises because the blockers look unplanned. They are not: § "Planned
milestones" item 1 has been the intent since the catalogue was written. It
simply never said which queue items would do it.

**The false statement, and how the two documents disagreed.** § "Deferred to
the Qt port" said `PL-FG9D` "has no planned-milestone line of its own", while
`PL-FG9D`'s own **Problem.** opens: *"`ROADMAP.md` planned-milestone item 1
says 'a modular anesthesia-machine abstraction' and stops there."* The item
cites the line the roadmap says does not exist. Nothing caught it -
`tools/doc_check.py` resolves a cited *path*, and this is a claim about the
document's own contents.

The narrower claim underneath it is true and is what the paragraph now says:
no milestone *section* places `PL-FG9D`, because § "Planned milestones" is
deliberately unspecified intent and `Scope` reads only a section's frozen list
and its `Required scope`. Intent is not scope. That is why nothing schedules
it, and the deferral of `PL-8PS6` and `PL-WZVZ` stands unchanged.

**What was done.** Item 1 now names `PL-4DCG` (the survey) and `PL-FG9D` (the
design round), says they are sequential and why - the extension points are the
axes of variation that reach a number, so designing before surveying is
guessing - and names the two gate entries waiting behind them. This is the
same shape item 1 already used for `PL-8DJ7`. No new numbered item was added:
item 1 *is* the line, and a second one would have split one improvement in
two, which the section's own preamble forbids.

**Deliberately not done.** Promoting item 1 into a scoped milestone, which is
what would actually schedule `PL-4DCG` and let `PL-8PS6` and `PL-WZVZ` back
into a gate. That is a milestone decision for the project owner and a design
round of its own, and the roadmap's development rules put it after the current
step rather than beside it.

