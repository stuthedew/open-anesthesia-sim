---
id: PL-1J0P
title: docket next labels every Gate 0 entry 'in scope for v0.4.0 - the step the project is on' while wave says the step is v0.3.0
priority: P2
effort: S
status: ready
classes: defect, infra
feature: planning-cadence
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/render.py
added: 2026-09-02
verify: uv run pytest subprojects/docket/tests/test_plan.py && grep -q 'def test_a_gate_placed_item_names_the_release_that_clears_it' subprojects/docket/tests/test_plan.py
---

**Problem.** `bin/docket next` prints, for each of the three items it offers
today, "In scope for v0.4.0 — the teachable case, the step the project is on".
`bin/docket wave`, run in the same checkout minutes apart, prints "Step: step 2
of 10: v0.3.0 — the foundation". The two commands a session reads at its start
disagree about which release the project is working on.

**Why it happens.** Placement is read from the milestone section that names an
id, and Gate 0's frozen list is recorded under `ROADMAP.md`'s "Milestone after
next: v0.4.0 - the teachable case" — deliberately, because the gate belongs to
the milestone it gates. v0.3.0 has no list of its own; its content *is* that
list. So every v0.3.0 entry is correctly found under a v0.4.0 heading, and the
render then describes the section it was found in as "the step the project is
on", which it is not.

**Why it matters.** The ranking is right and only the label is wrong, which is
what makes it worth fixing rather than tolerating: a session that trusts the
label reads the project as being on v0.4.0 and can reasonably start
teachable-case work — the one thing v0.3.0's scope excludes. It will say this
about every entry for the whole of v0.3.0, since all nine are placed the same
way, so the exposure is the entire release rather than an edge case.

It also lands badly against `PL-SZ56`, which makes v0.3.0 a pre-registered
trial of whether the loop is reliable enough for two milestones. A digest that
names the wrong release in every session of the release under test is evidence
for that trial, not background noise.

**Where.** `subprojects/docket/src/docket/plan.py` (placement) and
`subprojects/docket/src/docket/render.py` (the reason string). The fix is in
the wording rather than the ranking: an entry placed by a gate recorded under a
later milestone should say so — "Gate 0, cleared by v0.3.0 and recorded under
v0.4.0" — rather than claiming the section it was found in is the current step.
`wave` already computes the true step and the gate split, so the fact needed is
available and only has to reach the other renderer.

**Related, not the same.** `PL-BZCM` (docket status shows no plan placement)
concerns a different command showing no placement at all; this is a command
showing the wrong one.

**Found.** 2026-09-02, while confirming that admitting `PL-0MLQ` to Gate 0 had
reached the tool. Captured rather than fixed: that session was a planning round
on what v0.3.0 needs, and this is docket source.

**Done when.** `docket next` and `docket wave` cannot disagree about which
release the project is on, and an item placed by a gate says which gate places
it and which release clears it.
