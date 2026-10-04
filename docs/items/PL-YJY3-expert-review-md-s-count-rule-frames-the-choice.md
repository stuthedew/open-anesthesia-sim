---
id: PL-YJY3
title: expert-review.md's count rule frames the choice as two routes to one end state, so a recommendation to take the durable route only if another instance turns up reads as a third option the rule does not name: PL-51B7's first recommendation, 2026-10-04, deferred checked types for the supported-range quantities that way, without taking the count, after the step's range had been captured eight times before PL-0GJC typed it, and the project owner refused it
priority: P2
effort: S
status: ready
classes: defect
touches: .claude/rules/expert-review.md, docs/resident-instructions.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: a recommendation to build the durable route only once another instance turns up has to carry the count first, so a deferral like PL-51B7's is priced before it reaches the owner instead of being refused by them
verify: grep -qF 'another instance' .claude/rules/expert-review.md
---

**Problem.** expert-review.md's count rule frames the choice as two routes to one end state, so a recommendation to take the durable route only if another instance turns up reads as a third option the rule does not name: PL-51B7's first recommendation, 2026-10-04, deferred checked types for the supported-range quantities that way, without taking the count, after the step's range had been captured eight times before PL-0GJC typed it, and the project owner refused it

**Reproduced 2026-10-04** on `main` at `8f24fe78`: `grep -c 'another
instance' .claude/rules/expert-review.md` prints 0, and § "Count what undoing
it would cost" frames the trade as "two routes to one end state, the durable
one slower, the cheap one destined to be redone", naming no deferral.
`PL-51B7`'s brief on `main` records what that let through: build the checked
types only "if another unchecked way in turned up", refused by the owner the
same day.

**Why it matters.** A deferral conditioned on a further instance is the cheap
route with its repayment made conditional: nothing is built now, and the
principal grows with every instance added while waiting, which is exactly what
the count exists to price. Read as a third option, it escapes the count, and it
arrives under a respectable name, the rule of three, whose purpose (not
extracting an abstraction before enough cases show its shape) is spent once the
abstraction is chosen and built, as `PL-0GJC`'s `SimulationStep` was. The owner
caught this one; the section exists so that the owner need not (`PL-0GMC`).

**Done when.** § "Count what undoing it would cost" in
`.claude/rules/expert-review.md` names waiting for another instance as the
cheap route rather than a third option, so the count applies to it, and says
when the rule of three applies (the abstraction not yet known) and when it does
not (the abstraction already chosen). The edit names what it replaces in the
resident set, or says why nothing can be cut, as `CLAUDE.md` requires of every
resident edit.

**Generator check.** A re-entry of `PL-0GMC` (closed 2026-09-21, 13 days
before this capture), whose rule should have covered it. The fact misread is
what counts as the cheap route in the durable-versus-cheap trade: a deferral
read as a third route escaped the count that rule added. No head's `misread:`
states it, and no other open item misreads it.
