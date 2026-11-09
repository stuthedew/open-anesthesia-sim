---
id: PL-6G7N
title: docs/ARCHITECTURE.md § 'Layering' says compartment defaults stay in core/ so a unit can be built bare, but § 'Where new code belongs' says a data-file value is a required argument with no default; new code cannot follow both (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: done
classes: defect, docs
feature: architecture-md-structure
touches: docs/ARCHITECTURE.md
deferred-from: v0.7.0 - a new problem: at the freeze (817a4d88) the compartments still had defaults in core/ and the document held no required-argument rule; 1f0e8b1e (PL-M85T, 2026-10-25) removed the defaults and added the rule without updating the older paragraph
added: 2026-11-05
closed: 2026-11-09
pr: 2072
payoff: a contributor adding a compartment meets one rule for data-file values, the one the code and the single-source principle follow, and does not write a second copy of a value into core/
verify: ! grep -qF 'so that a unit can be constructed bare' docs/ARCHITECTURE.md
reenters: PL-4FBP
---

**Problem.** docs/ARCHITECTURE.md § 'Layering' says compartment defaults stay in core/ so a unit can be built bare, but § 'Where new code belongs' says a data-file value is a required argument with no default; new code cannot follow both (copy editor structure read, 2026-11-05)

**The structure read's query** (row numbers are docs/ARCHITECTURE.md at cfb15a4a, before the line edit):

- **Query, defaults in `core/`.** The file contradicts itself. Layering 45-58 says compartment defaults "are still written in `core/` so that a unit can be constructed bare", each pinned by a test. Where new code belongs 1171-1174 says a compartment takes a data-file value "as a required argument, with no default that restates it". Which rule applies to new code?

**Checked 2026-11-09:** `grep -n 'constructed bare' docs/ARCHITECTURE.md` still finds the paragraph in § "Data files (`data/`)": "The defaults are still written in `core/`, so that a unit can be constructed bare." § "Where new code belongs" still says that a compartment takes a data-file value "as a required argument, with no default that restates it". The code agrees with § "Where new code belongs". `TissueGroup`, `VenousBloodCompartment` and `AlveolarCompartment` declare no default for a volume, a partition coefficient or a ventilation. `BreathingCircuit` declares none for its volume or its vaporizer maximum (`PL-M85T`). The one default left on a compartment that a data file also states is the opening fresh gas flow, `TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN` in `core/circuit.py`. A test in `tests/unit/test_circuit.py` keeps it equal to the shipped machine file. So the "constructed bare" paragraph in § "Data files" is the stale one.

**Why it matters.** A contributor adding a compartment reads two rules that cannot both be followed. One tells them to write a default in `core/`, which would put a second copy of a data-file value in the code. The code and the single-source rule both refuse that copy.

**Done when.** § "Data files (`data/`)" no longer says that defaults are kept in `core/` so that a unit can be built bare. It says that each compartment takes its data-file values as required arguments, and it names the opening fresh gas flow as the one code default left, with the test that keeps it equal to the machine file.

**Generator check.** Instance of `PL-4FBP`'s fact, "The link between a document sentence and the tree fact it restates": the paragraph went stale when `PL-M85T` removed the defaults, after `PL-4FBP` closed, and no check holds a `docs/ARCHITECTURE.md` sentence to the code.
