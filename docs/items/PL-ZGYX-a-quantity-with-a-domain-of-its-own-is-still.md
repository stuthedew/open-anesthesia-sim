---
id: PL-ZGYX
title: A quantity with a domain of its own is still checked by hand wherever no checked type holds it, so reviewers find its unchecked way in one quantity at a time: three on 2026-10-11 - a MAC divisor's positivity (PL-0FJ8), the fraction-percent crossings (PL-1DP1), a compartment's agent amount (PL-544D) - after parse-dont-validate typed the step, the flows, the case instant, the step count and the concentrations
priority: P1
effort: M
status: ready
classes: defect, refactor
feature: parse-dont-validate
touches: docs/items, src/anesthesia_sim
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21); the head's own work is a sweep, and each safety find is filed and placed by its own triage, as PL-0FJ8 was; recorded as a generator head by PL-74T0, 2026-10-11
added: 2026-10-11
payoff: every quantity with a domain of its own is found at once and held by a checked type, so reviewers stop finding its unchecked way in one quantity at a time
verify: grep -qE '^\*\*Swept 2026-' docs/items/PL-ZGYX-*.md
root-cause-of: PL-YZ17, PL-5F76, PL-BPRK, PL-WP52, PL-HSFV, PL-BBMG, PL-LBQY, PL-5BD7, PL-RCYZ, PL-0FJ8, PL-1DP1, PL-544D
generator: live - three members filed on 2026-10-11 alone, each a quantity no checked type holds yet, found by a reviewer at the one way in that skips its hand check
misread: Which values a quantity may take, and whether a number in hand was already checked against them
---

**Problem.** A quantity with a domain of its own is still checked by hand wherever no checked type holds it, so reviewers find its unchecked way in one quantity at a time: three on 2026-10-11 - a MAC divisor's positivity (PL-0FJ8), the fraction-percent crossings (PL-1DP1), a compartment's agent amount (PL-544D) - after parse-dont-validate typed the step, the flows, the case instant, the step count and the concentrations

The `parse-dont-validate` feature (`.claude/rules/core-domain.md` § "Parse,
don't validate", `PL-M7QH`) gave a checked type to each quantity a capture had
found unchecked: the step (`PL-0GJC`), the flows (`PL-0YYV`), the case instant
and step count (`PL-CN5S`), the concentrations (`PL-4R3W`). It worked quantity
by quantity, and so does whatever finds the rest: a reviewer reaching the one
way in that skips a hand check. Members:

- the step: `PL-YZ17`, `PL-5F76`, `PL-BPRK`, and `PL-WP52` (each compartment's
  own `advance`, open);
- the flows and the dial past the settings record: `PL-HSFV`, `PL-BBMG`, and
  `PL-LBQY` (a direct field write);
- since the feature's types landed: `PL-5BD7` (the settings record keeps
  whatever numeric types it is handed, open), `PL-RCYZ` (the control record's
  case instants, open), and on 2026-10-11 alone `PL-0FJ8` (a MAC divisor's
  positivity, checked in five formatting functions), `PL-1DP1` (the
  fraction-percent crossings) and `PL-544D` (a compartment's agent amount
  written past its capacity).

**Why it matters.** Every member is a clinically read quantity - a dose, a
flow, a MAC multiple, a concentration - whose wrong value would display as a
plausible number, and each was found by a reviewer rather than by anything that
looks for it. The principle is resident for new code; what still hands members
is code written before it.

**Done when.** A sweep of `src/anesthesia_sim/` for every quantity with a check
of its own that a signature or record field still takes as a bare `float` or
`int` - a hand-written range, sign or capacity check on a parameter, a
`NewType` standing in for a range - is recorded in this brief under a
`**Swept <date>.**` heading at the start of a line, with its count. Each find is
typed here or filed in `parse-dont-validate` as a member, then `generator:`
says spent and the head closes. Whether part of the sweep is decidable in a
check - a `raise` guarding a parameter annotated `float` in `core/` - is this
item's to judge.

**Not counted.** Holes in a checked type's own construction (`PL-3800`,
`PL-7N8P`, `PL-979Z`, `PL-LLMN`, `PL-5D1Z`) are what a type admits, a different
fact and mostly drained. The interface's handling of a refusal (`PL-M4M0`,
`PL-V2HC`) is not a quantity's domain.

**Generator check.** This is the head, recorded 2026-10-11 by `PL-74T0` as its
cluster 3: one fact misread by twelve items, and no head's `misread:` states it.
