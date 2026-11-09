---
id: PL-6KNM
title: core/ names the quantity partial_pressure_fraction but still validates it with require_concentration_fraction, from a module called concentration.py
priority: P2
effort: M
status: done
classes: refactor
feature: core-domain-language
milestone: v0.4.24
touches: src/anesthesia_sim/core, src/anesthesia_sim/app, tests, docs/MODEL.md, docs/ARCHITECTURE.md, tools/core_vocabulary_check.py
added: 2026-09-13
closed: 2026-09-14
pr: 561
verify: uv run pytest tests/unit/test_validation.py && grep -q 'def require_fraction' src/anesthesia_sim/core/validation.py
---

**Problem.** core/ names the quantity partial_pressure_fraction but still validates it with require_concentration_fraction, from a module called concentration.py

`PL-9SH6` gave every compartment accessor the one name `docs/MODEL.md`
§ "Concentrations" implies — `partial_pressure_fraction`, prefixed only where
one object holds two of them. It deliberately stopped at the accessors, and
left three things behind that still call the same quantity a concentration:

| Still says concentration | What it is | Uses in `core/` |
| --- | --- | --- |
| `require_concentration_fraction` | `core/validation.py`, the [0, 1] guard every one of those accessors' setters calls | 19 |
| `Fraction` in `core/concentration.py` | the `NewType` the quantity is carried as, and the module holding it | whole tree |
| `percent_from_fraction` / `fraction_from_percent` | the conversion pair in that module | whole tree |

So `AlveolarCompartment.set_partial_pressure_fraction` validates its argument
with `require_concentration_fraction`, imported from `concentration.py`. That
is the same two-names-for-one-kind defect `PL-9SH6` was written to remove,
displaced one layer down rather than fixed.

**Why it was left, and why it is a decision rather than a rename.** The three
are one question, not three: renaming the validator without the module it is
imported beside trades one inconsistency for another, and the module's name,
the `NewType`'s name and `docs/MODEL.md` § "Concentrations" itself all move
together or none of them do. `PL-WVSK` made `Fraction` and `Percent` `NewType`s
in v0.4.17 for a reason unrelated to this, so the naming question was never put.

**What the answer has to weigh.** These name a *representation* — a
dimensionless number in [0, 1] — where the accessors name a *quantity*. That is
a real distinction and it may be the answer: a guard that checks a range does
not need to know which $`F`$ it is guarding, and `require_fraction` would say
so without taking a side. Against that, the module is the one place the kind is
defined, and `docs/MODEL.md` § "Concentrations" is the sentence both are
supposed to be implementing.

**Explicitly out of scope:** `max_delivered_concentration_percent`, the agent
data-file field under `src/anesthesia_sim/data/`. It is a versioned schema key
rather than an accessor, a vaporizer dial *is* read as a percent concentration
clinically, and renaming it is a data-file migration with nothing to gain.

**Where.** `core/validation.py`, `core/concentration.py`, and every importer of
either; `docs/MODEL.md` § "Concentrations" if the answer moves the term.
**Why it matters.** Two names for one kind is the defect `PL-9SH6` was written
to remove, and `.claude/rules/core-domain.md` asks that `core/` read like the
domain rather than like a translation of it. A reader of
`AlveolarCompartment.set_partial_pressure_fraction` meets
`require_concentration_fraction` on the next line and has to decide whether the
two name the same quantity - nineteen times across `core/`. The cost is
indirect but not cosmetic: `docs/MODEL.md` § "Concentrations" is the sentence
both are supposed to implement, and a reader who concludes they implement
different things has been misled about what the model holds.

**Done when.** A decision is recorded on whether these three name a
*representation* - a dimensionless number in [0, 1], which need not know which
fraction it is guarding, and which `require_fraction` would say without taking a
side - or the *quantity*, in which case the validator, `core/concentration.py`,
the `Fraction` `NewType` and `docs/MODEL.md` § "Concentrations" move together in
one change rather than three. Whichever is chosen,
`max_delivered_concentration_percent` in `src/anesthesia_sim/data/` is untouched,
for the reasons the brief already gives.

**Decision needed.** Do `require_concentration_fraction`, `core/concentration.py` and the `Fraction` `NewType` name a representation - a number in [0, 1] that need not know which fraction it guards - or the quantity, in which case all three move with `docs/MODEL.md` § "Concentrations"?

**Decided 2026-09-14: the guard names a representation, the module and the
`NewType`s name the quantity.** The three parts turned out to answer
differently, which is why one answer for all three would have been wrong
either way.

**`require_concentration_fraction` is now `require_fraction`.** Three pieces of
evidence, none of them a preference:

1. **Every caller already disagrees with the old name.** All eleven call sites
   in `core/` pass a `..._partial_pressure_fraction` string; not one passes a
   concentration. A reader of `alveolar.py` met
   `require_concentration_fraction("partial_pressure_fraction", ...)` — two
   names for one kind, on one line, which is exactly the defect `PL-9SH6`
   removed from the accessors.
2. **`core/validation.py`'s own convention is representation-naming**, and this
   function was the only exception to it. `require_positive_finite` and
   `require_nonnegative_finite` each name a property of the number. The guard
   checks a range and nothing else; it cannot tell which $`F`$ it holds and
   does not need to.
3. **The same range already guards quantities that are not concentrations.**
   `core/parameters.py`'s `PositiveFraction` validates `perfusion_fraction` and
   the MAC-awake ratio. A [0, 1] guard is a statement about the number.

**`core/concentration.py` and `Fraction`/`Percent` keep their names.** The
module is the implementation of `docs/MODEL.md` § "Concentrations" and takes
its subject from that section, which is the strongest traceability this project
can give a module name: the specification section and the module that
implements it are one word. That section defines all of the dimensionless forms
the model carries, which is also what let `PL-BQ46`'s `MacMultiple` land here
rather than needing a home of its own. And the `NewType`s are quantity types
rather than range types — their whole job is to refuse a percent of an
atmosphere where a fraction of one is wanted, which is a statement about
*which* quantity. `PL-BQ46` rules out the opposite reading independently: a
MAC-awake ratio may not be annotated `Fraction`, so `Fraction` cannot be "any
dimensionless number in [0, 1]".

**Consequence worth recording.** `tools/core_vocabulary_check.py` matched whole
identifiers rather than substrings because two live names would otherwise have
been reported, and this rename removes one of them. Measured 2026-09-14 across
`core/`: no live identifier contains a retired name as a substring, so a
substring rule would pass today and would have caught this guard by itself.
That is filed as `PL-JW9J` rather than done here — it is a different rule and
owes its own false-positive argument — and the tool's docstring, its test and
`docs/ARCHITECTURE.md` all now say so instead of citing a name that is gone.

`max_delivered_concentration_percent` under `src/anesthesia_sim/data/` is
untouched, as the brief required.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "A naming or placement decision that gives no wrong value either way".

> **Four are not apparatus and so need their own ground**, which is stated here rather than stretched from the argument above. `PL-6KNM` and `PL-BDNB` are what `PL-9SH6`'s accessor rename left behind. They ask whether the validator, `core/concentration.py` and the `Fraction` `NewType` name a representation or the quantity. They also ask whether one local variable inside the closed forms is renamed with them. Both are `refactor`-classed naming decisions that produce no wrong value today. Splitting them up would decide one question twice, and that is the ground on which `PL-BQ46` and `PL-KL2Q` were declined. `PL-SPN6` is the third item from that rename. Three compartments now raise one error string, so a refused step no longer says which compartment refused it. That message is a diagnostic that a developer reads, not a value that a clinician could act on. That is why it is `defect` rather than `safety`. It also owes work on the loosened assertions, and holding this gate open does not make that work cheaper. `PL-V67Q` is a y-axis range control that the project owner raised as a passing want. It is `needs-decision` for three reasons. The design round has not happened, half of its open questions are the owner's, and that round owes a review of the human-factors literature before any default is chosen. None of the four is inside this milestone's Required scope.

> The fifth non-apparatus item from that pass, `PL-DJYF`, is **admitted above** rather than declined, under the unconditional science exception.
