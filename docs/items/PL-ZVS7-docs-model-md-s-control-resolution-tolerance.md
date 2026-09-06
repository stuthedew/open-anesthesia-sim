---
id: PL-ZVS7
title: docs/MODEL.md's control-resolution tolerance table is a measured safety claim with no regression test; re-measuring it 2026-09-06 reproduced it, but nothing would have caught a drift
status: untriaged
added: 2026-09-06
---

**Problem.** `docs/MODEL.md` § "Supported simulation step" publishes three
measured displacements - 6.7e-3, 5.0e-2 and 1.4e-1 pp for the case opening, the
unperfused load and the ventilator start - as the tolerance
`MAXIMUM_SIMULATION_STEP_S` declares, and `core/uptake_system.py` repeats two of
them in the comment deriving the constant. Nothing in `tests/` computes any of
them. `grep` for the figures across the suite returns one unrelated comment.

**Why it matters.** This is the quantity the step bound *is* since `PL-X9KD`
retired the accuracy derivation: the constant is no longer a numerical limit but
a declared control-resolution tolerance, stated in percentage points of a value
the interface displays. So the three numbers are the whole content of a
safety-critical claim, and they are held only by prose in two files. A change to
the governing equations, to a partition coefficient, to the reference adult's
volumes, or to the supported input envelope moves them silently: `make check`
passes, both documents keep asserting the old figures, and the tolerance a
reader is told the tool holds to is no longer the one it holds to. That is the
same failure `PL-NBWP` describes one level up, and `PL-NBWP`'s own "Done when"
names the cause - "a claim about interruptibility that no test holds is how this
one survived".

**Confirmed reproducible, which is what makes the gate cheap.** Re-measured
2026-09-06 while working `PL-NBWP`, by an independent harness driving
`AgentUptakeSystem` directly: 6.66e-3, 5.03e-2 and 1.43e-1 pp, matching the
published table to the digit. So the gate is a pin against known-good values
rather than a new derivation, and the manoeuvres it needs already exist as
`SETTING_CHANGE_SCENARIOS` and the operating points around them in
`tests/reference/test_coupled_dynamics.py`.

**Where.** `docs/MODEL.md` § "Supported simulation step", the table under "The
tolerance, in percentage points of one atmosphere"; the comment deriving
`MAXIMUM_SIMULATION_STEP_S` in `src/anesthesia_sim/core/uptake_system.py`, which
quotes the case-opening and ventilator-start figures; `tests/reference/`, where
the manoeuvres and the envelope constants already live.

**Sequenced after `PL-NBWP`, not blocked on it.** `PL-NBWP` decides whether the
table stays a 1x-only statement or becomes a per-rate one, so building the gate
first risks pinning a table that is about to gain four columns. Its measured
per-rate figures are in that item and are the values this gate would pin under
the disclose-and-correct option.

**It also owes the step the table was measured at, added 2026-09-06 when
`PL-NBCJ` closed.** Nothing pins `MAXIMUM_SIMULATION_STEP_S` to its value
either - `test_the_shipped_step_is_within_the_maximum_simulation_step` asserts
only `SIMULATION_STEP_S <= MAXIMUM_SIMULATION_STEP_S`, a relation both sides of
which could move together. Since `PL-NBCJ` the value is an argued decision with
three recorded reasons rather than a default, and every figure in the table
above is measured *at* it, so a silent change to the constant would leave two
documents describing a tolerance the code no longer holds. A bare pin was
deliberately not written into `PL-NBCJ`: it would be a weaker duplicate of what
this item builds, and the two belong in one test that says the table and the
step are one decision.

**Done when.** A reference test computes the displacement for each manoeuvre in
`SETTING_CHANGE_SCENARIOS` plus the case opening, over all three agents, and
asserts the figures `docs/MODEL.md` publishes - so that moving the model moves
the test before it moves a reader's understanding of the tolerance. The
tolerance is a bound rather than a prediction, so the assertion is against the
published value with a stated relative tolerance, and the test names
`docs/MODEL.md`'s section so the two are found together. The same test pins
`MAXIMUM_SIMULATION_STEP_S` to the step those figures were measured at, so the
table and the constant cannot part company.
