---
id: PL-4R3W
title: Fraction and Percent are NewTypes, which the interpreter erases, so their ranges of 0 to 1 and 0 to 100 are checked by hand wherever a value enters - require_percent at four sites in circuit.py and governing_equations.py - the hand-checked pattern PL-51B7 replaces with checked types for the supported-range quantities; whether a concentration becomes a checked type too is undecided, because concentration.py chose NewTypes to catch a missing conversion, and whether a fraction computed at a bound can round past it is unmeasured
status: untriaged
feature: numerical-domain
touches: src/anesthesia_sim/core/concentration.py, src/anesthesia_sim/core/validation.py
added: 2026-10-04
---

**Problem.** Fraction and Percent are NewTypes, which the interpreter erases, so their ranges of 0 to 1 and 0 to 100 are checked by hand wherever a value enters - require_percent at four sites in circuit.py and governing_equations.py - the hand-checked pattern PL-51B7 replaces with checked types for the supported-range quantities; whether a concentration becomes a checked type too is undecided, because concentration.py chose NewTypes to catch a missing conversion, and whether a fraction computed at a bound can round past it is unmeasured
