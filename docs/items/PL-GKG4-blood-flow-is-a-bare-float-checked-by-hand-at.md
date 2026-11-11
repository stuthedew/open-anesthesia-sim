---
id: PL-GKG4
title: Blood flow is a bare float checked by hand at three places in core (blood.py, tissue.py, governing_equations.py) and is not a checked type as cardiac output is, so the next function that takes one can skip the check
priority: P1
effort: M
status: done
classes: defect, safety
touches: src/anesthesia_sim/core, tests/unit, tests/integration, docs/MODEL.md, docs/ARCHITECTURE.md, .claude/rules/core-domain.md
deferred-from: v0.7.0 - present at the freeze and not on the frozen list; found by the 2026-11-10 audit; not live: checked 2026-11-10, all three places that take a blood flow refuse a negative or non-finite one, so no wrong value is computed now
added: 2026-11-10
closed: 2026-11-11
pr: 2114
payoff: a blood flow is checked once where it is built, so a new function that takes one cannot skip the check
verify: grep -rq 'class BloodFlow' src/anesthesia_sim/core
reenters: PL-ZGYX
recurrences: 2026-11-11 PL-LHCL
---

**Problem.** Blood flow is a bare float checked by hand at three places in core (blood.py, tissue.py, governing_equations.py) and is not a checked type as cardiac output is, so the next function that takes one can skip the check

**Checked 2026-11-10:** `require_nonnegative_finite` is called on a `blood_flow_l_min: float` at three places: `time_constant_s` in `src/anesthesia_sim/core/blood.py`, `src/anesthesia_sim/core/tissue.py`, and `src/anesthesia_sim/core/governing_equations.py`. Cardiac output is a checked type, `CardiacOutput`. Not checked: whether any caller can pass a blood flow that did not come from a `CardiacOutput` and a `Fraction`, and so whether an upper limit is missing in practice. The audit's reviewer reported that `tests/unit/test_numerical_envelope_sweep.py` passes a blood flow of `sys.float_info.max`.

**Why it matters.** `.claude/rules/expert-review.md` asks that a quantity with a check of its own is checked once, by building a type that only the check produces. A check repeated at each way in fails at the one nobody guarded, as `PL-HSFV`'s settings record did. `docs/MODEL.md` says "Every input to the model has a range that includes its ends"; for blood flow the code enforces only that it is finite and not negative.

**Done when.** Blood flow is a checked type built from a cardiac output and a share, or by one check that states its range. The three functions take the type and no longer check a float. `docs/MODEL.md` states the range the type enforces, or says that blood flow is derived and has none of its own.

**Generator check.** An instance of `PL-ZGYX`'s fact (which values a quantity may take, and whether a number in hand was already checked against them), filed after that head closed on 2026-10-11. Its fix was a sweep that filed each way in as a member; blood flow stayed a float.

**Built 2026-11-11, as step (b) of `PL-LHCL`'s build order.**
`src/anesthesia_sim/core/blood_flow.py` holds two checked types.
`PerfusionFraction` is checked as above 0 and at most 1 when it is built.
`BloodFlow` is built only as a `PerfusionFraction` of a `CardiacOutput`, and
has no check of its own. The three hand checks are gone:

- `TissueGroup.time_constant_s` and `advance` take a `BloodFlow`, and
  `blood_flow_l_min_at` returns one.
- `VenousBloodCompartment.time_constant_s` and `advance` take the
  `CardiacOutput`, which is the pool's flow. The parameter is renamed from
  `blood_flow_l_min` to `cardiac_output_l_min`.
- `TissueGroupEquationSettings.blood_flow_l_min` is a `BloodFlow`. Its
  `_hold_as_exact_floats` helper is deleted, because the field now has one
  type in every record.

`TissueGroup.perfusion_fraction` and `ReferenceAdultParameters`' three
fractions are `PerfusionFraction`s. The note in `core/parameters.py` that kept
the perfusion fraction a bare `float` on the public side (`PL-KL2Q`) is
rewritten, because `PL-LHCL` decided the other way.

**Failed first.** The first three tests in `tests/unit/test_blood_flow.py`
replay the report at the three places, with 5e-324, 3.75 and the largest
float. They use only what existed before the change. The rest of the file
imports `core/blood_flow.py`, which the change added, so the whole file cannot
be collected against the old code. The variant that can is the file up to
`def _muscle()`, with its two imports of `core.blood` and `core.blood_flow`
removed, saved as `tests/unit/test_blood_flow_replay.py` in a checkout of
`main` at `e084968ac`. There, `uv run pytest -q -p no:randomly
tests/unit/test_blood_flow_replay.py` gave `9 failed`, each with `Failed: DID
NOT RAISE TypeError`. Run again that way on 2026-11-11 after the review, with
the same result.

**Decided while building, each with one clearly better option.**

1. *A flow of 5e-324 L/min is still a flow.* It is the smallest perfusion
   fraction of 1 L/min. A smallest positive flow was refuted: zero flow is
   supported, the model is continuous down to it, and a gap between zero and
   a minimum would refuse values with nothing wrong in them. So
   `time_constant_s` returns `inf` where the quotient overflows, as at zero
   flow. A tissue stepped alone is then left unchanged, where the exact
   change over 24 hours is below 5e-296 L (largest envelope tissue: 1e4 L,
   tissue:gas 1e4, flow below about 3e-299 L/min). A test states this with
   the change worked out from the flow.
2. *A pickle or a copy rebuilds a flow as the whole of a cardiac output equal
   to it.* The flow stores neither factor. Storing them was refuted: it adds
   state that equality ignores and a write rule to guard it. The set of
   numbers the constructor can produce is exactly 0 to the largest cardiac
   output, so the rebuild proves what the original proved, and gives the same
   number bit for bit.
3. *The types live in their own module.* `core/supported_ranges.py` was
   refuted: `tests/unit/test_supported_range_edges.py` reads every `float`
   subclass there as built through a guard of the same parameter name, and
   `BloodFlow.__new__(cardiac_output_l_min, ...)` would have been read as the
   cardiac output's type.
4. *The perfusion fraction is its own type and not a `Fraction`.* A
   `Fraction` is a partial pressure and admits zero.

**What changed in behaviour.** A bare number where a blood flow or a
perfusion fraction belongs now raises `TypeError`, whatever its value. A
perfusion fraction outside its range is refused where it is built, with a
message that gives the value and cites `docs/MODEL.md` § "Tissue groups". The
earlier messages named only the field. No run changes: the matrix reads
`blood_flow_l_s`, a plain `float`, and the two sums of fractions add plain
`float`s as before (`float()` at three places, because CPython's `sum` adds a
`float` subclass without compensation, `PL-5BD7`).

**Still bare, and why.** `TissueGroupEquationSettings.blood_flow_l_s` and the
two `total_perfusion_fraction` returns are derived values, and are listed
under that reason in `tests/unit/test_bare_numbers.py`. The count there went
from 173 to 165.

**The range-edge test now draws the venous pool.** Its two methods take a
`CardiacOutput`, so `tests/unit/test_supported_range_edges.py` hands them
every cardiac-output edge. A tissue group's methods take a `BloodFlow`, which
no guard in that test's modules builds, so they are not drawn. That is step
(d) of `PL-LHCL`.

**The blind review of step (b), 2026-11-11, pass 2.** Two findings, both
`optional`, both real when run, both fixed.

1. A saved flow edited out of range was refused in the cardiac output's
   words, which sends a reader to a value the record still holds unchanged.
   `BloodFlow.__reduce__` now saves the flow's number, and
   `_restored_blood_flow` rebuilds it through the constructor and names the
   saved blood flow before the cardiac output's reason. The return of
   `__reduce__` is a plain number, so it is on the bare list as a checked
   type's plain number, and the count is 165.
2. A cardiac output handed to a tissue group as its flow was told to build
   the flow "from the value that it should hold, not from this one". A flow
   is built from that cardiac output and a fraction, so `require_blood_flow`
   now says how a flow is built.

Each fix has a test of the whole message. Before the fixes those tests fail
on the message text.

**The adversarial review of step (b), 2026-11-11.** Three passes, each for one
class of defect. The pass on save and restore stopped on the account's usage
limit before it reported, so the session ran its checks directly: 56 flows and
4 fractions through every pickle protocol, `copy` and `deepcopy`, the whole
uptake system and its settings record the same way, and edited saved values.
All held. The other two passes ran.

*Numbers and domain.* No value differed from `main` in about 580,000 compared
(whole-model runs at 9 cardiac outputs and 3 steps, a 24-hour replay,
hand-built settings, compartments stepped alone). Two findings, both wording,
both real, both fixed:

1. The module docstring of `core/blood_flow.py`, and the test file's, said
   that no cardiac output can give a flow of 5e-324 L/min. One can. Only the
   1.8e308 L/min flow became impossible.
2. The venous pool's time constant is also `inf` at a cardiac output above
   zero and below 60 V / 1.8e308, about 4e-307 L/min for the reference pool.
   Its docstring said so only for zero. The behaviour is the same on `main`.
   The docstring and `docs/MODEL.md` now say it, with the same bound as the
   tissue's (below 5e-296 L over 24 hours), and a test checks it.

*Tests and rules.* 48 mutants, 37 killed. Eight findings, all real when run,
all fixed:

1. Nothing tested the new check in `ReferenceAdultParameters`. A test now
   hands each of the three fields a bare 0.06.
2. `core/supported_ranges.py` still said, in two docstrings, that a tissue's
   blood flow is a plain `float`.
3. Nothing tested the `TypeError` half of the restore's refusal.
4. Nothing tested the `float()` in the three sums. A test now builds a patient
   at fractions of 0.7, 0.2 and 0.1, whose total is 1.0 as plain `float`s and
   0.9999999999999999 as the subclass. The other two conversions cannot be
   seen from outside: one sits behind the 1e-12 tolerance on the sum, the
   other inside a message rounded to 6 decimals. They stay, so that each sum
   is the arithmetic it was.
5. The "Failed first" record above named a command that no longer collects
   against the old code. It now names the variant.
6. `docs/MODEL.md` and `core/checked_number.py` each said something of every
   checked type that is false of `BloodFlow`.
7. The state-capture test's helper wrote a halved perfusion fraction as a
   plain `float`.
8. Nothing tested that a refusal of the wrong type gives the fraction's name.

It also asked for a test that the time constant stays finite at a flow just
large enough, which pins "infinite only where the quotient overflows". Two
tests now do that, one for the tissue and one for the pool. Each new test was
run against the mutant it was written for, and each failed there (8 of 8).
Two smaller wording slips went with them: a garbled phrase in
`docs/ARCHITECTURE.md`, and "an unperfused tissue" in the docstring of
`require_nonnegative_finite`, which no longer checks any flow.

Three surviving mutants are left as they are. One differs from the code only
for a saved minus zero edited by hand, one is unreachable because the payload
has already validated the value, and the third is the pair in finding 4.

**The copy edit of step (b), 2026-11-11, and where it stopped.** The copy
editor read the 94 passages the branch had changed before the adversarial
review, and offered 42 rewrites. Four of them equalled the original. Of the
other 38, 33 are applied. Five are not: four are passages that the review
fixes had since changed, so the rewrite no longer matched, and one, a
paragraph of `docs/ARCHITECTURE.md`, turned a sentence into list items that
name no code, which that document's own rule refuses. Four statements that a
rewrite dropped were put back by hand: "finite" in the description of the
sweep in `docs/MODEL.md`, the pointer to `core/run_definition.py`, and two
item ids in `core/governing_equations.py`. A rewrite of one `docs/MODEL.md`
paragraph that this change did not touch was left out.

The project owner then said "stop copy editor" and "skip copy editor"
(project owner, 2026-11-10 at about 22:50 CST). A second run, on the 21
passages that the review fixes added or changed, was stopped after its four
reads and before its meaning checks, and nothing from it is applied. Those 21
passages, and the pull request's title and body, are as the session wrote
them.

**The branch audit's mutation check, 2026-11-11.** Of 100 mutants of changed
lines, the unit tests caught 85 and missed 15, so the first audit refused the
branch. `make check` passed in the same run.

- Three were the last line of `require_perfusion_fraction`'s message. A test
  now compares the whole message.
- Twelve changed or removed the `name=` that `parse_reference_adult_parameters`
  gives each `PerfusionFraction`. No input reaches that name: the payload has
  already checked the fraction against the same range, above 0 and at most 1,
  so the constructor cannot refuse it there. The three lines were first
  marked `# pragma: no mutate`, and a second audit still counted the twelve:
  mutmut reads that marker only on a line of its own between statements, or
  at the end of a whole statement, and not after an argument inside a call.
  So the three names are removed, which leaves nothing there to mutate. A
  comment says why no name is given.
