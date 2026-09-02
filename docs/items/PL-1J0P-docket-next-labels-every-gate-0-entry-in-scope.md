---
id: PL-1J0P
title: docket next labels every Gate 0 entry 'in scope for v0.4.0 - the step the project is on' while wave says the step is v0.3.0
priority: P2
effort: S
status: done
classes: defect, infra
closed: 2026-09-02
pr: 179
verify: uv run pytest subprojects/docket/tests -k "current_step or gate_shipping or own_gate or outside_a_gate or whole_scope"
feature: planning-cadence
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/render.py
added: 2026-09-02
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

**Why it matters — and the diagnosis above was wrong.** This brief was
captured saying "the ranking is right and only the label is wrong". It is not.
Measuring it before fixing it found a second, worse half.

v0.4.0's section places **29 ids: 22 on the gate and 7 in `Required scope`
only** — `PL-011`, `PL-DHV7`, `PL-F52R`, `PL-R3KB`, `PL-SSBP`, `PL-VM40`,
`PL-ZRSP`. `Scope.current` was the section's whole `scope_ids`, so all seven
ranked as work the current step includes while the beat was `clear the gate`.
`ROADMAP.md` has the gate clear *before* the milestone it gates is
implemented, so every one of them is work the step has not reached.
`docket next` was really offering one: `PL-F52R` sat third at the time of
writing, and `PL-DHV7` and `PL-VM40` are `P1`.

So a session following `next` could start v0.4.0 implementation believing it
was v0.3.0's — which is what `CLAUDE.md`'s "do not implement beyond the current
milestone" forbids and what the gate mechanism exists to prevent. That is a
ranking defect, not a presentation one.

The two halves are also one fix rather than two. Labelling `PL-F52R` "on
Gate 0's frozen list" would have been a *new* false statement, so the label
cannot be corrected without first telling the gate's entries apart from the
milestone's own scope — and once that distinction is computed, ranking on it is
the same expression.

The label half still matters on its own terms: it will misname every entry for
the whole of v0.3.0, since all nine are placed the same way.

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

**Closed 2026-09-02.** Both halves, in one change, because they are one fix.

**The narrowing.** `milestone_scope` takes an optional `clearing_gate`. Given
one, `Scope.current` becomes the gate's entry ids alone and the anchor's other
`scope_ids` move into `later` under the anchor's own version — so they read as
work a milestone names that the step has not reached, which is exactly what
they are. `wave` passes the gate only on the `CLEAR` beat, so the moment the
gate is clear the milestone's `Required scope` is current work again. It is
opt-in rather than inferred inside `milestone_scope`, because that function is
given no beat: a caller reading a section directly means the section.

**The label.** `Scope` gained `step_label` (the timeline row, set only when it
differs from the anchor) and `clearing` (whether `current` is a gate's entries
or a milestone's whole section). Two fields rather than one: they answer
different questions — "which row?" and "on a gate?" — and the beat can move off
the gate while the labels still differ, which is the release arrangement that a
single field would have mislabelled. `plan.py` now writes three accurate
messages instead of one claim that was false in two of the three:

- gate recorded elsewhere: "On the debt gate recorded under v0.4.0 — the
  teachable case; v0.3.0 — the foundation clears it."
- a milestone clearing its own gate: "On v0.2.8's frozen list, the step the
  project is on."
- ordinary in-scope work: unchanged.

**Verified.** `docket next` no longer offers `PL-F52R`; the top three are now
`PL-9Y42`, `PL-0MLQ` and `PL-NV9W`, all Gate 0 entries. All seven
`Required scope`-only ids report `out-of-scope` attributed to `v0.4.0`, and all
22 gate ids report `in-scope`. Seven tests added: four in `test_roadmap.py`
covering the narrowing, the step label, the return of the milestone's scope
once its gate clears, and that reading a section directly is unaffected; three
in `test_plan.py` pinning each of the three messages, the first of them
asserting the old false claim is absent. `make check` green at 914 tests.

**One existing test changed rather than added to.**
`test_cli.py::test_next_leads_with_what_the_current_step_names` asserted the
old string verbatim. Its ranking assertion was left alone and still passes; the
string assertion now names the arrangement the fixture actually has, with the
retired claim pinned negatively so it cannot come back.

**Found by measuring rather than by reading.** The brief's wrong half would
have survived a careful re-read — it is a plausible description of the symptom.
It fell to counting what the section places against what the gate records,
which took one short script. Worth remembering for the next brief that
describes a display defect: check whether the value being displayed wrongly is
also being *used*.
