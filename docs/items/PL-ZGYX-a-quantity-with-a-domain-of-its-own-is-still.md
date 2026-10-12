---
id: PL-ZGYX
title: A quantity with a domain of its own is still checked by hand wherever no checked type holds it, so reviewers find its unchecked way in one quantity at a time: three on 2026-10-11 - a MAC divisor's positivity (PL-0FJ8), the fraction-percent crossings (PL-1DP1), a compartment's agent amount (PL-544D) - after parse-dont-validate typed the step, the flows, the case instant, the step count and the concentrations
priority: P1
effort: M
status: done
classes: defect, refactor
feature: parse-dont-validate
touches: docs/items, src/anesthesia_sim
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21); the head's own work is a sweep, and each safety find is filed and placed by its own triage, as PL-0FJ8 was; recorded as a generator head by PL-74T0, 2026-10-11
added: 2026-10-11
closed: 2026-10-11
pr: 1429
payoff: every quantity with a domain of its own is found at once and held by a checked type, so reviewers stop finding its unchecked way in one quantity at a time
verify: grep -qE '^\*\*Swept 2026-' docs/items/PL-ZGYX-*.md
root-cause-of: PL-YZ17, PL-5F76, PL-BPRK, PL-WP52, PL-HSFV, PL-BBMG, PL-LBQY, PL-5BD7, PL-RCYZ, PL-0FJ8, PL-1DP1, PL-544D, PL-19Y0, PL-9DF9, PL-7694
generator: spent - the 2026-10-11 sweep enumerated every remaining way in and filed each as a member; what still handed members was code written before the resident principle, which now holds new code
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

**Swept 2026-10-11.** Three new members, from 113 hand checks read at 52
parameter and field names under `src/anesthesia_sim/` on `main` at
`d9340516`. The scratch scans were AST reads. One read listed every
`require*`/`_check*` call or `if ...: raise` naming a parameter annotated
`float` or `int`. One listed the same on a parameter annotated with a checked
type, which catches an extra domain on one. One compared each non-frozen
dataclass's `__post_init__` checks against its `__setattr__` guards. The last
was a name search for instants, flows, fractions and percents still typed
`float`.

- **Filed:** `PL-19Y0`, where a direct write skips every compartment check
  but the three flows'. It covers the dial past its vaporizer maximum, the
  inspired fraction, the circuit volume and the venous agent amount, and
  `PL-544D` holds the alveolar and tissue amount. `PL-9DF9`, where the chart
  time base re-checks a case instant by hand. `PL-7694`, where the compared
  run count and index are checked by hand in seven functions and indexed
  unchecked in `off_scale_notice`.
- **Re-found, already members:** `PL-0FJ8`, the MAC divisor's positivity in
  five formatters, closed since by #1424. Its strictly positive percent also
  covers `percent_axis_ticks`' two checks on the axis top and interval derived
  from the MAC. Also `PL-WP52`, where a compartment's `advance` takes a
  `float` step. Also `PL-1DP1`, the crossings, with `wash_in.py`'s bare
  fraction among its call sites. Also `PL-RCYZ`, the control record's
  instants.
- **Not counted, each by a recorded rule:**
  - **The guards and constructors themselves.**
  - **A record's own sign and finiteness**, covering volumes, partition
    coefficients, blood flows, the accounting totals, the deliverable flow
    range and the playback multiplier. The reason is
    `.claude/rules/core-domain.md` § "Where it stops".
  - **Relations a record or query holds:** an instant within the run, a
    window's order, a clock against its opening, flow against machine, dial
    against maximum, amount against capacity, steps against run length and
    perfusion against output.
  - **A value checked once at its one way in:** the tick interval, column
    spacing, propagation interval, plot width, a duration's components, the
    window-geometry fraction, grid columns (two minimums for two
    quantities) and the schema versions.
  - **`perfusion_fraction`**, which stays a bare `float` by
    `core/parameters.py`'s "a type per parameter rather than a type per
    boundary".
  - **`MacMultiple`**, a `NewType` with no range to prove, by
    `core/concentration.py`'s rationale.
  - **The default flows**, each built into its checked type at its one use
    in `core/uptake_system.py`.
  - **The canonical state vector**, one shared guard at each sink and a
    structure rather than a quantity.

**No check for it.** Most of the `raise`s on a `float` parameter under
`core/` are correct code: guards, a record's own sign, relations. A check
keyed on that would fire every run without changing a decision. The exact
part, a mutable record's checked field with no write guard, is `PL-19Y0`'s.
Five records hold every such field, and new code is held by the resident
principle, so the members came from code that predates it, which this sweep
has now enumerated.
