---
id: PL-RFHH
title: plan.gate()'s feature test and roadmap.GateStatus.self_cleared's Required-scope test both answer 'cleared by the milestone itself' and disagree, so bin/docket gate and bin/docket wave can report different membership for the same milestone with nothing saying which is authoritative
priority: P2
effort: S
status: done
classes: defect, infra
feature: gate-list-integrity
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/, subprojects/docket/README.md, .claude/skills/docket/modes/release.md, ROADMAP.md
added: 2026-09-21
closed: 2026-09-23
verify: bin/docket gate --no-git --feature interface-areas 2>/dev/null | grep -q 'in the store, split by whether each carries' && bin/docket wave --no-git 2>/dev/null | grep -q 'named in its Required scope, so cleared by the milestone itself:'
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

## Resolved 2026-09-23: reworded, not unified

**Decided by this session, on the project owner's delegation** - chosen over
making `plan.gate()` read the frozen list, and over making it split by
`Required scope`.

**Not the frozen list.** `bin/docket gate` is what a freeze is computed with,
so it cannot read the list it exists to produce; and after a freeze it is the
only view of debt filed since - 12 of the 163 open debt items were on no frozen
list on 2026-09-23. Two questions, both wanted.

**Not the `Required scope` test either, costed.** `cmd_gate` would have to read
`ROADMAP.md` and name a milestone section, which `--feature` cannot do - a new
flag, under the generator pause. The two would still disagree: `wave` carves
out blocked entries first, and 12 of the 14 `gate` listed read as blocked
outside the gate. It also reads deferrals - `PL-Y04W` is deferred to Gate 3 -
and a store-wide split knows neither. So the rewording is needed under either
route. Nothing is stored downstream of it, so it is cheap to redo when
`PL-J6HP` settles how gate facts are read.

**Measured, v0.6.0, 2026-09-23.** `gate --feature interface-areas` listed 14
carrying the feature against `wave`'s 3 cleared by the milestone itself. On the
test alone they differed on four entries, both ways: `PL-NDKC` and `PL-Y04W`
carry the feature unnamed, and `PL-CNCF` and `PL-PGZF` are named without it.
`ROADMAP.md` said "two entries". `#850` wrote that six hours before `#862`
named the second pair. The sentence now gives the dated ids instead of a count.

**What changed.** `format_gate` says it reads the whole store, headed
`Not carrying` / `Carrying` the feature, and its footer names `bin/docket wave`
and `Required scope` as the rule. Its empty-store message no longer implies
debt without the feature. `format_wave` says `frozen list recorded under` and
`named in its Required scope, so cleared by the milestone itself:`, which keeps
`PL-YVP7`'s `verify:` matching. The same correction went into the `plan.Gate`
docstrings, the `gate` help text, the docket README, the release mode's freeze
pass (which had equated the milestone's own debt with the items carrying its
feature) and `ROADMAP.md`'s v0.6.0 gate paragraph.

**The generator moved to `PL-J6HP`.** This item carried `generator: live` for
gate facts in `ROADMAP.md` prose, a mechanism the rewording does not touch. A
closed head is never asked for a verdict, so closing with the claim here would
have dropped a live generator from the tier with nothing saying so. `PL-J6HP`
holds it now, `PL-RFHH` among its members.
