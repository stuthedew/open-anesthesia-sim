---
id: PL-6Q9L
title: Pause new workflow mechanisms and re-specifications of the generator rule while any open item carries generator: live, so the live generators are worked before more apparatus is added (project owner, 2026-09-22, ratified)
priority: P2
effort: S
status: done
classes: planning, docs
feature: generator-identification
touches: CLAUDE.md
added: 2026-09-22
closed: 2026-09-22
pr: 916
payoff: additions pause while live generators drain, so the convergence expectation can finally be tested
verify: grep -qF 'no new workflow mechanism is' CLAUDE.md
---

**Problem.** The first pass over the 161 non-product items filed 2026-09-20 to
09-22 (`PL-KVDK`) found that apparatus inflow stayed flat mainly because
mechanisms kept arriving. At least nine were requested or ratified on 09-20 and
09-21, and the generator rule was re-specified four times in five days, with a
24-item tail. Meanwhile six closed generator heads were still producing items.
`PL-04KR`'s convergence prediction assumed no new functionality was being added,
so it could not be tested while that held.

**Decision.** The project owner agreed with the recommendation on 2026-09-22
(ratified, chosen over continuing to add mechanisms under standing approval).
While any open item carries `generator: live`, no new workflow mechanism is
built. `CLAUDE.md` § "What this project is" states the rule, and the
standing-approval sentence in § "Prefer deterministic tooling over repeated
model work" now points at it.

**Why it matters.** Each new mechanism brings its own tail of items. Pausing
additions is what lets the live generators drain, and it makes `PL-04KR`'s
expectation testable.

**Done when.** `CLAUDE.md` states the pause, and the licence it suspends names
it.
