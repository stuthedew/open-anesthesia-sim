---
id: PL-LPH9
title: ROADMAP.md's cadence says no interim release is cut partway through clearing a gate, but 159 of Gate 1's 175 frozen entries already shipped in v0.4.x patches, so the sentence a later session would cite to refuse a cut describes nothing this project has done since v0.4.5
priority: P2
effort: S
status: needs-decision
classes: docs, planning
touches: ROADMAP.md
added: 2026-09-19
payoff: stops a later session declining a release the project has cut twenty-seven times, on a cadence rule ROADMAP.md still states
---

**Problem.** ROADMAP.md's cadence says no interim release is cut partway through clearing a gate, but 159 of Gate 1's 175 frozen entries already shipped in v0.4.x patches, so the sentence a later session would cite to refuse a cut describes nothing this project has done since v0.4.5

**The two sentences, read against the tree 2026-09-20.** `ROADMAP.md`
§ "The cadence" states the rule twice:

> **A gate does not get a version.** Cleared gate work ships inside the
> milestone it gates: it lands between that milestone's predecessor and its own
> release, so the milestone's release notes carry it, and no interim release is
> cut partway through clearing. `docket release` will offer one as soon as a
> few gate items are finished — decline it, or the gate work scatters across
> patch releases and the milestone ships carrying only its feature work.

and again where the Qt port reads it as the one open question about its own
number. `bin/docket wave` that day: Gate 1 holds 175 entries, **172 cleared,
3 open**, and the version is 0.4.32. Those 172 cleared across the v0.4.x patch
track - twenty-seven patch releases between v0.4.5 and v0.4.32 - which is
precisely "the gate work scatters across patch releases", done deliberately,
release after release, by sessions following the offer the sentence says to
decline.

**Why it matters.** This is a rule a later session would cite to refuse work,
and it is the only kind of sentence `.claude/rules/expert-review.md` singles
out for that reason - `ROADMAP.md` and `docs/MODEL.md` are the two documents
whose prose closes questions. A session reading it correctly declines a release
the project has cut twenty-seven times, and one reading the practice correctly
is contradicting the roadmap. Neither is wrong about what they read, which is
what makes it worth an item rather than an edit: whichever way it is
reconciled, the reconciliation is what stops the next session re-deriving it.

It also reaches `bin/docket release`, which offers the cut. The tool does what
the sentence says it will do; what the sentence says to do about the offer is
what no longer matches.

**Decision needed.** Which of the two is the record - and this is a release
train question rather than a wording one, which is why it is not being answered
at triage:

1. **The prose is stale.** Cutting patch releases while a gate drains is the
   working practice, the gated milestone still takes its own number, and the
   sentence is rewritten to say so. **Recommended**: 172 of 175 entries shipped
   this way with no observed harm, and the stated cost - "the milestone ships
   carrying only its feature work" - is what a milestone release *should*
   carry once its debt has been paid down continuously. It also matches
   § "Versioning decision", where the number marks the capability boundary
   crossed, and a gate crosses none.
2. **The practice is wrong.** The rule stands, and clearing the remaining gate
   entries happens without further patch cuts. Costs: work sits unreleased for
   the length of a gate, which at Gate 1's size was months, and the ephemeral
   container makes an unreleased finished item indistinguishable from an
   unfinished one to every session that follows.

Whichever is chosen, § "The cadence" and the Qt port's open-question paragraph
both change, and Gate 0's exemption paragraph should be re-read in the same
pass - it exists to explain why v0.3.0 was allowed a version, which option 1
would make unremarkable.

**Done when.** `ROADMAP.md` § "The cadence" states one rule about interim
releases during a gate that the last twenty-seven cuts satisfy, and the Qt
port's paragraph citing the old reading is brought into line with it.
