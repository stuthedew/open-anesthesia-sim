---
id: PL-RFHH
title: plan.gate()'s feature test and roadmap.GateStatus.self_cleared's Required-scope test both answer 'cleared by the milestone itself' and disagree, so bin/docket gate and bin/docket wave can report different membership for the same milestone with nothing saying which is authoritative
priority: P2
effort: S
status: needs-decision
classes: defect, infra
feature: gate-list-integrity
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests/
added: 2026-09-21
root-cause-of: PL-H6VQ, PL-Z891, PL-YVP7, PL-B60Q, PL-JN3F
generator: live - gate membership, deferrals, marks and counts live in ROADMAP.md prose read by several functions; seven instances after PL-HWW1 closed, v0.6.0 gained 14 deferrals in 1.5 days (PL-KVDK)
---

**Problem.** plan.gate()'s feature test and roadmap.GateStatus.self_cleared's Required-scope test both answer 'cleared by the milestone itself' and disagree, so bin/docket gate and bin/docket wave can report different membership for the same milestone with nothing saying which is authoritative

**Why it matters.** `ROADMAP.md`'s v0.6.0 gate section already records the
symptom - "the test is whether `Required scope` below names the id, rather than
whether the item carries the `interface-areas` feature, and the two disagree on
two entries" - but nothing in the tooling says so, and a session reading either
command takes its answer as the answer. `PL-YVP7` was filed on the wrong one of
the two and its design was ratified before the error was caught; the only
reason it was caught is that a completeness critic went and ran both commands.
The next session has no such guarantee.

`bin/docket gate` partitions **every** open debt item in the store by `feature`
(178 items today, against a frozen Gate 2 list of 183). `bin/docket wave` reads
the frozen list and computes `self_cleared` from `milestone.own_scope_ids`,
which is the `Required scope` subsection. Neither is wrong; they answer
different questions under one phrase.

**Decision needed.** Whether the two tests are reworded to say which
question each answers, or `plan.gate()` is changed to read the frozen list so
there is one answer. Cost the second before choosing the first: they may
deserve to stay separate, in which case the wording is the whole fix.

**Recommended: reword, and do not unify.** The two commands answer different
questions and both answers are wanted. `bin/docket gate` has to partition the
whole store by `feature` to say what debt exists, including items filed after
the freeze; `bin/docket wave` has to read the frozen list, because a frozen list
is what a gate *is*. Making `plan.gate()` read the frozen list would leave
`bin/docket gate` unable to see debt filed after the freeze, which is the thing
it is for. So the expected fix is `format_gate` saying it partitions the store
by `feature` and `format_wave` saying it reads the frozen list and `Required
scope`. Cost unification before discarding it, as **Done when.** asks - but the
answer this brief expects is that the two stay separate and the wording is the
whole fix.

**Done when.** A reader of either command can tell which question it answered.
The cheapest form is wording rather than unification - `format_gate` saying it
partitions the store by feature, and `format_wave` saying it reads the frozen
list and Required scope - and that should be costed against actually making
`plan.gate()` read the frozen list before either is chosen. Do not assume
unification is right: the two may deserve to stay separate.
