---
id: PL-R7XK
title: v0.5.0's gate defers PL-MN4J in the declined subsection, but 'Debt inside the milestone's own scope' already places it in Required scope
priority: P2
effort: S
status: done
classes: docs, planning
feature: debt-gate
milestone: v0.4.26
touches: ROADMAP.md
added: 2026-09-16
closed: 2026-09-16
pr: 640
verify: python3 tools/doc_check.py check && grep -qF 'cannot be cleared before the compare mode it is about' ROADMAP.md
---

**Problem.** v0.5.0's `### Declined to Gate 2 ...` subsection defers `PL-MN4J`
(the chart hover names the agent and the instant but not which run) on the
ground that "the display it concerns does not exist outside the feature this
milestone builds". `PL-MN4J` is `safety`-classed, and § "The gate is a snapshot,
not a moving target" closes by saying `safety` and `science` "are not deferrable
by this project's own standard". So the disposition written for it is not one
the rule offers.

**Why it matters.** The ground given is sound and the rule already has a
mechanism for it - it is just not deferral. § "Debt inside the milestone's own
scope" answers this exact case in advance: "Debt that the milestone itself
exists to clear is cleared *by* it, not before it ... The test is whether the
item appears in the milestone's `Required scope`." And it names the safety
interaction explicitly: "This does not weaken the `safety`/`science` re-entry
rule above. Such an item inside the scope is still not deferrable — it just
cannot be finished earlier than the work it is part of, and the milestone's
definition of done is what holds it." A hover that does not say which run is
ambiguous only while two runs are drawn, which *is* v0.5.0's compare mode, so
the item is milestone work by that test rather than deferred work.

The cost of the current record is not cosmetic: a deferral says the gate has
released the item, while Required scope says the milestone's definition of done
holds it. Only the second is true, and only the second stops it being closed out
of v0.5.0 unnoticed.

**Found 2026-09-16** while fixing `PL-R0Q0`, which made `doc_check`'s
safety-class advisory name only the two remedies the rule accepts. That advisory
now names `PL-MN4J` with a reachable clean state; this item is that state.

**Where.** `ROADMAP.md` § "v0.5.0 - the case you can branch": the
`### Declined to Gate 2 ...` paragraph beginning "One more from 2026-09-16", and
`### Required scope`. The frozen-list and Required-scope counts
`tools/doc_check.py` holds to the document move with it.

**Note.** The other four items the advisory names - `PL-7Z84`, `PL-9LNF`,
`PL-NWTM`, `PL-W54S` - are *not* this case: their hazard belongs to
planned-milestone item 34, which is past v0.5.0 and unscoped, so Required scope
here cannot hold them. `PL-83LS` carries that question, and this item is
independent of it.

**Done when.** `PL-MN4J` is recorded under a disposition the gate rule offers -
Required scope, or the frozen list with the date and reason as `PL-GS3R`,
`PL-BXB2`, `PL-V53R` and `PL-0PJG` were - with the reasoning that is currently in
the declined subsection carried across rather than dropped, and every count
`doc_check` holds to the document updated with it. `make check` reports
`PL-MN4J` no longer.

## Decided (project owner, 2026-09-16, ratified)

**`PL-MN4J` moves into v0.5.0's `Required scope`**, chosen over leaving it
deferred in the `### Declined to Gate 2 ...` subsection where it sits today.

Ratified on this session's recommendation, so it reopens on ordinary evidence
per `CLAUDE.md`. The ground is not new judgment: § "Debt inside the milestone's
own scope" already answers this exact case, and says so about the safety
interaction in terms - such an item "is still not deferrable - it just cannot be
finished earlier than the work it is part of, and the milestone's definition of
done is what holds it."

Carry the reasoning currently in the declined subsection across rather than
dropping it, and move every count `doc_check` holds to those two structures.
