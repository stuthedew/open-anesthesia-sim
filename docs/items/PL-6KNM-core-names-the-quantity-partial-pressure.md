---
id: PL-6KNM
title: core/ names the quantity partial_pressure_fraction but still validates it with require_concentration_fraction, from a module called concentration.py
status: untriaged
added: 2026-09-13
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
