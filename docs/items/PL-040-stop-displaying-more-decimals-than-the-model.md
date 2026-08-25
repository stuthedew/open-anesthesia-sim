---
id: PL-040
title: Stop displaying more decimals than the model can support
status: done
closed: 2026-08-24
commit: 1971a9f
---

**Problem.** Stop displaying more decimals than the model can support

**Decision rationale (2026-08-24).** Two decimals, uniformly.

Per-state error at the shipped 0.1 s step, worst across the three agents,
against `tests/reference/test_coupled_dynamics.py`, in percentage points -
beside what those compartments actually read (sevoflurane, 5% delivered):

| | worst error | 60 s | 600 s | 3600 s |
| --- | --- | --- | --- | --- |
| circuit | 1.2e-3 | 2.012 | 4.025 | 4.422 |
| alveolar | 2.5e-3 | 0.833 | 3.122 | 3.846 |
| mixed venous | 8.8e-4 | 0.062 | 2.080 | 3.144 |
| vessel rich | 1.0e-3 | 0.124 | 2.730 | 3.836 |
| muscle | 3.4e-4 | 0.003 | 0.158 | 1.248 |
| fat | 2.4e-5 | 0.0002 | 0.009 | 0.080 |

The shape is the opposite of what a uniform decimal count assumes: the large
compartments are the least accurate in absolute terms and the small ones the
most, so at three decimals the last digit is noise for the four fast values
while remaining numerically real for muscle and fat.

Solver accuracy is not the binding constraint, though. A six-compartment
perfusion-limited model on reference-adult parameters supports no claim at
the third decimal however well it is integrated, and clinical agent monitors
read 0.1 percentage points. Two decimals sits one step finer than the
monitor, which suits a tool whose purpose is watching change, and well
coarser than any fidelity claim.

Rejected: per-compartment precision, which matches where the solver is
actually accurate but puts mixed precision across a row of similar-looking
values, inviting exactly the misreading the item exists to prevent; and
three significant figures, which is justified by the solver rather than by
fidelity and shifts its decimal count as values grow, costing scannability.

The objection that two decimals erases the slow-compartment wash-in does not
survive the numbers. Over the first hour fat reads 0.00, 0.00, 0.00, 0.01,
0.04, 0.08 and muscle 0.00, 0.00, 0.06, 0.16, 0.62, 1.25; both are legible
trends. Fat at 60 s carries 0.003% of its equilibrium load, and `0.00%` is
the truthful statement about it at any precision this model earns.
