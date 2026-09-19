---
id: PL-Z27P
title: docket next's lane line and the session-start digest name the other lane's pick with a bare id and mechanism-language title and no reason at all, so workflow work is put in front of the owner every session with nothing saying why it was selected
priority: P2
effort: S
status: done
classes: defect
feature: recommendation-rationale
milestone: v0.4.31
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_plan.py, subprojects/docket/tests/test_cli.py
added: 2026-09-19
closed: 2026-09-19
pr: 729
verify: grep -qF 'def test_the_clause_names_the_gate_while_a_gate_is_open' subprojects/docket/tests/test_plan.py
---

**Problem.** docket next's lane line and the session-start digest name the other lane's pick with a bare id and mechanism-language title and no reason at all, so workflow work is put in front of the owner every session with nothing saying why it was selected

**Why it matters.** Two lines name an item to the project owner without room
for a reason, and both printed a bare id: `docket next`'s closing `Lane of this
answer:` line, once per invocation, and the session-start digest's `By lane,
for a second session:` line, resident in every session's context. Between them
they are the only places the workflow lane is ever surfaced to the owner.

A title is written for the session that will implement the item, so it names a
mechanism and not a consequence - "Nothing reconciles the jobs that report a
status check on pull_request against the branch-protection required list". The
owner's words for what that is like to read from outside: *"specific action
without any context where I don't know why it's selected - 'links predicate xyz
predicate to runner 267' or whatever"* (2026-09-19).

The missing information is not the title. It is that the id alone cannot
distinguish a `P1` sitting on the debt gate from a `P3` the roadmap places
nowhere, so an offer the owner should wave through and one they should question
look identical. Measured on 2026-09-19, the workflow lane's pick was `P2` and
off-gate while both `P1`s in the store were product-lane gate entries - the
single most useful fact about that offer, and nothing printed it.

Band and gate relation are facts in the store rather than readings of it, so
printing them scripts nothing. What the work *buys* is judgment and stays prose
a session writes; `PL-WYKF` is where that half is decided.

**Done when.** Both lines carry the pick's band and its relation to the gate,
drawn from a `placement_clause` helper that agrees with `placement_line` and
`placement_mark` about the same relation, with tests pinning the agreement and
the no-roadmap case.
