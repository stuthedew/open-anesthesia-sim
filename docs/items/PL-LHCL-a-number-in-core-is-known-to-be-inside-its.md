---
id: PL-LHCL
title: A number in core/ is known to be inside its valid range only where a checked type holds it, and 151 parameters and fields are still bare float or int, so each sweep (PL-ZGYX) finds the ones someone listed and the next arrives after it closes: a blood flow of 5e-324 L/min is accepted (PL-GKG4) and a restored Keyframe holds instant_s = -50.0 (PL-8W1Q)
priority: P1
effort: L
status: ready
classes: safety
feature: numbers-outside-their-valid-range
touches: src/anesthesia_sim/core, tests/unit, docs/MODEL.md
deferred-from: v0.7.0 - filed 2026-11-11, after the gate froze; a large structural change whose design waits on the owner's answer
added: 2026-11-11
payoff: every number that crosses a function boundary in core/ is either a checked type or on one short list that says why it is bare, so a new unchecked way in fails a test the day it is written
not-delegable: a root cause built in several pull requests that change core/ signatures or comparison allowances, each read by the project owner, and run at extra-high effort
root-cause-of: PL-GKG4, PL-8W1Q, PL-8JV2, PL-8LQZ
generator: live - PL-ZGYX closed on a sweep that filed each bare number someone listed, and four items re-entered it afterwards; 86 bare float or int parameters and fields remain at public boundaries in core/ outside the guard modules, and nothing refuses the next one
misread: Which values a quantity may take, and whether a number in hand was already checked against them
reenters: PL-ZGYX
---

**Problem.** A number in core/ is known to be inside its valid range only where a checked type holds it, and 151 parameters and fields are still bare float or int, so each sweep (PL-ZGYX) finds the ones someone listed and the next arrives after it closes: a blood flow of 5e-324 L/min is accepted (PL-GKG4) and a restored Keyframe holds instant_s = -50.0 (PL-8W1Q)

**What each earlier fix built, and what got past it** (verified against the
tree on 2026-11-11, on `main` at the commit this branch starts from).

- `PL-ZGYX` (closed 2026-10-11) read 113 hand checks in a one-time sweep and
  filed each bare number it listed. It built no standing check, and its brief
  says so under "No check for it". Four items re-entered it afterwards:
  `PL-8JV2`, `PL-8LQZ`, `PL-GKG4` and, through `PL-S11T`, `PL-8W1Q`.
- `PL-GKG4` still reproduces. `TissueGroup.time_constant_s` and
  `VenousBloodCompartment.time_constant_s` take `blood_flow_l_min: float` and
  check only that it is finite and not negative. A flow of 5e-324 L/min is
  accepted and returns a time constant of `inf`, and the largest float is
  accepted and returns 3.4e-306 s. `TissueGroup.blood_flow_l_min_at` takes a
  `CardiacOutput` and returns a bare `float`, so the range that the cardiac
  output proved is lost at that return.
- `PL-8W1Q` still reproduces. `Keyframe.__new__` followed by
  `__setstate__([-50.0, state])`, which is what a pickle load does, gives a
  `Keyframe` whose `instant_s` is a bare `-50.0`. The constructor refuses that
  value. The `__setstate__` there is the one `dataclass(slots=True)` writes,
  and it runs no check. Only `UptakeEquationSettings` and
  `TissueGroupEquationSettings` restore through `_restore_through_checks`.
- `PL-N7MM` (closed 2026-10-25) built `tests/unit/test_record_writes.py`, which
  walks every class in `core/` and fails on a mutable field with no write
  rule. That is the one earlier fix with a standing check, and no later item
  re-enters it. It covers a write to a field. It does not cover a restore, or
  a parameter of a function.

**Counted 2026-11-11.** An AST read of `src/anesthesia_sim/core/` found 151
parameters and dataclass fields annotated `float` or `int` (or either with
`None`). 86 of them are on a public function or class outside the six modules
that define the checks themselves (`validation.py`, `supported_ranges.py`,
`checked_number.py`, `numerical_envelope.py`, `concentration.py`,
`simulation_step.py`). By quantity: an agent amount in litres, 25 (the
compartments, the circuit and the accounting validator); a blood flow, 5; a
compartment's own step, 4; an instant, interval or window bound in
`run_definition.py` and `matrix_exponential.py`, 10; the parameter payloads
and liquid-agent values, about 25; the rest are the closed form's arguments
and accounting results.

**The cause.** Whether a number was checked is a fact about its history. A
checked type carries that fact with the number. A bare `float` does not, so
the fact lives in whoever reads the call chain. `tests/unit/test_supported_range_edges.py`
already finds its functions by type: it draws every function that takes a
checked type, and so it draws nothing for a function that takes a bare
`float`. A bare number therefore escapes the type and the generated test
together. A sweep finds the bare numbers someone thought to list, and the
store has shown that twice.

**Why it matters.** A flow, a dose, an instant or an amount outside the range
its formula is valid for gives a number that looks right. The safety-critical
standard in `CLAUDE.md` asks for a refusal there. Each of these was found by a
reviewer, after the code shipped.

**Decided 2026-11-11: build the design below** (project owner, 2026-11-11,
ratified, over building the range part alone and over building neither).
It was the owner's because it changes most function signatures in `core/`, which is safety-critical code they read.

1. Every `float` or `int` on a public parameter, field or return in `core/` is
   a checked type, or is named on one list in a test with the reason it is
   bare. A test that walks `core/`, as `tests/unit/test_record_writes.py`
   does, fails on a bare number that is not on the list. The list starts at
   the 86 above and only shrinks.
2. A derived quantity gets a type that only its derivation builds. A blood
   flow is built from a `CardiacOutput` and a perfusion fraction and from
   nothing else, so `PL-GKG4`'s three hand checks go.
3. A record has one way to be built. Every checked record in `core/` restores
   through its constructor's checks from one shared helper, and the same
   walking test fails on a checked record that does not (`PL-8W1Q`'s triaged
   route).
4. The hand-written list of 16 edges in
   `tests/unit/test_numerical_envelope_sweep.py` is replaced by edges read
   from the types, as `tests/unit/test_supported_range_edges.py` already
   reads them.

**Established practice, read 2026-11-11.** A range cannot be made
unrepresentable in a type system of this kind, and the stated remedy is the
one this repository already uses for the flows and concentrations: "use an
abstract newtype with a smart constructor" (King A. Parse, don't validate.
2019. https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/).
The same essay names what a hand check costs: validation makes it "extremely
difficult or impossible to determine if everything was actually validated up
front". Types that state a relation between values restrict what they can say
so that checking stays decidable (Jhala R, Vazou N. Refinement Types: A
Tutorial. arXiv:2010.07763, section 2.3), so a relation stays with the record
that holds both values. Meyer's 1992 paper on design by contract was not
reachable from this session and nothing here rests on it.

**What it costs.** Signature changes across `core/` and the tests that call
it, in several pull requests, each read by the owner. A checked type on a
value computed at every step (an agent amount) costs a construction per step,
which has to be measured against the 61 µs step before it is taken.

**What could still get past it.** A relation between two values, which a type
of one value cannot state and which stays with the record that holds both. A
number on the bare list. A range that is itself wrong, which is validation
and not this item.

**Build order, one pull request each.** (a) The walking test and the bare
list, with nothing else changed, so the count is fixed before it shrinks. (b)
The blood-flow type, which closes `PL-GKG4`. (c) Restores through the
constructor's checks, which closes `PL-8W1Q`. (d) The edges read from the
types, replacing the hand-written 16. (e) The remaining bare numbers by
quantity, agent amounts last, after the cost of a checked type per step is
measured against the 61 µs step. Each replays its escape as a test that fails
first.

**Done when.** The walking test exists and fails on a new bare number and on
a checked record that restores without its checks. `PL-GKG4` and `PL-8W1Q` are
closed by it. Each past escape in this brief is replayed as a test that failed
before the change. The bare list is in the test with a reason per entry.

**Generator check.** This is a head. Its fact is `PL-ZGYX`'s, and this item
re-enters that head: four items were filed against the fact after it closed.

**Built 2026-11-11, step (a): the walking test and the list.**
`tests/unit/test_bare_numbers.py` reads the source of every module in `core/`
and collects each public parameter, dataclass field and return whose
annotation names `float` or `int`. Each must be in the test's `LISTED` table,
under the reason it is bare. `MOST_BARE_NUMBERS` is 164, and a longer list
fails. Nothing under `src/` changed.

The count is 164 and not the 151 or 86 counted above, for three reasons. The
design's point 1 includes returns, which the earlier count left out. The walk
also counts a `float` inside another type, such as `Keyframe.state:
tuple[float, ...]`, so that a container cannot hide one. And no module is
exempt: the six guard modules are listed too, under the reason `THE_CHECK`, so
a new function there that takes a bare number also fails. By reason: the check
itself 35, a checked type's plain number 2, a count shown in a refusal 1 (these
38 stay bare); blood flow 7, perfusion fraction 6, compartment step 4, instant
or window 11, state vector 8, stored parameter 25, closed form 9, agent amount
38, derived value 18 (these 126 are steps (b) and (e)).

**Failed first.** With `LISTED` empty, `uv run pytest -q -p no:randomly
tests/unit/test_bare_numbers.py` gave `1 failed, 12 passed`:
`test_every_bare_number_in_core_is_listed_with_its_reason` failed with
`AssertionError: these public parameters, fields or returns in core/ are a
bare float or int`, naming all 164.
`test_the_walk_names_each_bare_number_that_a_past_item_reported` replays the
signatures that `PL-GKG4` and `PL-HSFV` reported, and `Keyframe`'s bare state,
as text, and requires the walk to name each one. `PL-8JV2`'s number was in
`layout/`, which this walk does not read, and `PL-8LQZ` was a relation between
two values, which the brief says a type of one value cannot state. Their own
regression records are in their items.

**Next, for the session that picks this up.** Steps (b) to (e) of the build
order above, one pull request each. For (b), `BloodFlow` belongs beside
`CardiacOutput` in `core/supported_ranges.py`. `TissueGroup.blood_flow_l_min_at`
is the one place the product is formed, and the venous pool's flow is the whole
cardiac output. `TissueGroup.perfusion_fraction` is a bare `float` checked in
`__setattr__`, so (b) decides whether it becomes a `Fraction`. Note that a
perfusion fraction of 5e-324 times a cardiac output still gives a flow of
5e-324 L/min, so building the type from its two factors does not by itself
keep `time_constant_s` finite. (b) has to say whether `inf` is the right
result there, as it is at zero flow, or whether the flow has a smallest
positive value. Each of (b) and (c) removes its entries from `LISTED` and
lowers `MOST_BARE_NUMBERS`.

**Where step (a) stands, 2026-11-11 00:40 UTC.** The test is committed on
`claude/festive-cori-it7vs1` and its draft pull request is `#2099`. The
session stopped for length before close-out, at 143,000 tokens of spend. Still
owed before `#2099` is marked ready, as `bin/docket arm` lists them: the prose
review of the test file's 11 docstrings and comments; one blind review pass;
an `Owner-read:` record (the change adds a test and no behaviour, so the
judgment to record is whether the owner reads the list's reasons); the copy
edit of the title and body; and `bin/docket yield PL-LHCL`, because the item
stays open for steps (b) to (e). `main` was brought in after `#2095` merged, so the
branch differs from `main` only by the test and this record. `docs/MODEL.md` was left unchanged for (a):
its paragraph on `tests/unit/test_record_writes.py` under the mass-balance
identity is where (b) or (c) adds one on this test.
