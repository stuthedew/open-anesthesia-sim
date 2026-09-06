---
id: PL-4GN8
title: The mass-balance release gate's absolute tolerance tracks whichever dial its test happens to run at
priority: P1
effort: S
status: done
classes: science, test
feature: numerical-domain
milestone: v0.4.6
touches: tests/reference/test_multi_agent.py, tests/reference/test_sevo_patient.py, docs/MODEL.md
added: 2026-09-02
closed: 2026-09-06
pr: 407
verify: uv run pytest tests/reference/test_multi_agent.py tests/reference/test_sevo_patient.py && grep -q 'relative_error <=' tests/reference/test_multi_agent.py && grep -q 'relative_error <=' tests/reference/test_sevo_patient.py
---

**Problem.** Three reference tests assert `validation.absolute_error_l <=
1e-12` on a mass-balance total that scales with the delivered concentration.
The tolerance does not, so how demanding the gate is depends on the dial the
test happens to be written at, and moving a dial silently moves the gate.

**Measured** while working PL-019, isoflurane and desflurane over 600 s
wash-in plus 600 s washout:

| Dial | Delivered | `absolute_error_l` | Headroom under 1e-12 |
| --- | --- | --- | --- |
| 8% | 3.2 L | 1.73e-13 / 1.80e-13 | x5.8 / x5.5 |
| 4% | 1.6 L | 8.64e-14 / 9.02e-14 | x11.6 / x11.1 |

Halving the dial halves the error and doubles the headroom. Nothing about
the numerics changed.

**Why it matters.** The gate still has 5-12x headroom either way and a real
conservation defect is orders of magnitude, not factors of two, so this is
not a defect in what shipped. It is a gate that does not mean a fixed thing:
`docs/MODEL.md` documents 1e-12 as a release tolerance, and what that
sentence certifies now varies with an unrelated test-setup choice. A later
session that lowers a dial for an unrelated reason strengthens the
conservation gate by a factor of two without knowing it, and one that raises
a dial weakens it the same way. That is the case `CLAUDE.md`'s
deterministic-tooling section calls a check passing while the guarantee it
stands for is void, and it is why this is classed `science` rather than as
test hygiene: what is wrong is the meaning of a documented scientific
guarantee, not the arithmetic under it.

**Approach.** Assert on the relative quantity the validator already carries
so the gate is dial-independent, and restate the documented tolerance in
those terms.

**The validator is already the right shape; only the tests are not.**
Checked 2026-09-02: `core/agent_simulation_validation.py` computes both
`absolute_error_l` and `relative_error` (`absolute_error_l /
max(initial_agent_l + delivered_agent_l, MINIMUM_RELATIVE_SCALE_L)`), and its
own halt threshold passes on `absolute <= AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L
or relative <= AGENT_ACCOUNTING_RELATIVE_TOLERANCE`. So the dial-independent
quantity exists and is exported on `AgentAccountingCheck`; the reference tests
simply ignore it. The change is to the assertions and to `docs/MODEL.md`, not
to the validator - confirm that reading before touching `core/`, and if the
halt threshold does turn out to need a change, that is a separate item.

**It is also a property of the run length, not only of the dial** (measured
2026-09-03, sevoflurane, stepping 0.1 s and reading `absolute_error_l` after
every step). The residual accumulates monotonically, so the assertion has a
horizon past which it is simply false:

| Settings | `absolute_error_l` first exceeds 1e-12 L at | At 4 h |
| --- | --- | --- |
| The reference tests' own (FGF 4 L/min, 1 MAC) | t = 6212 s | 7.24e-11 L |
| Envelope corner (FGF 10, V_A 12, Q 10, 8%) | t = 876 s | 4.71e-10 L |

The tests run to 1200 s, which is why they pass. At the corner the assertion
would fail inside the 1800 s horizon `test_published_wash_in.py` already runs
at, and inside a case length a user of a teaching simulator would call
ordinary.

This sharpens the diagnosis rather than changing it: the fix is still to assert
the dial-independent relative quantity, which stays at 2.45e-12 after 4 h at
the corner - three orders inside the 1e-9 the guard uses - while the absolute
figure has moved by three orders. It also settles the "unless the halt
threshold is wrong too" question left open above: the halt threshold is right,
and it is the `or` that makes it right. The absolute branch goes dead after an
hour or two of simulated time and the relative branch carries the guard from
then on, which is exactly what the disjunction is for.

**Where.** `tests/reference/test_multi_agent.py:77`,
`tests/reference/test_sevo_patient.py:222`,
`src/anesthesia_sim/core/agent_simulation_validation.py` (read only, unless
the halt threshold is wrong too), `docs/MODEL.md`.

**Done when.** Both reference tests assert a dial-independent conservation
bound, the numeric tolerance is stated as a relative one with the reasoning
for its value, and `docs/MODEL.md`'s release-gate sentence says the same
thing the tests now assert - so that changing a dial in a test cannot change
what the gate certifies.

**What v0.4.1 does to this (added 2026-09-03).** The fix is method-independent: asserting
`relative_error` rather than `absolute_error_l` is right whatever solves the
step, and `AgentSimulationValidator` already exports both. What must be
re-measured are the two tables the brief carries - the per-dial absolute errors
and the "first exceeds 1e-12 L at t = 6212 s" horizon - both taken on the
shipped split. `PL-P0BB` also notes that mass conservation "stops being
structural, deliberately" under the exact step and that `PL-GS5X` must state the
new tolerance's derivation, so this item's tolerance and that one's have to
agree.

**Worth doing before `PL-GS5X`, not after.** The conservation gate is the check
most likely to move when the exhaust integral is recomputed under coupled
dynamics. Making it dial-independent first means it certifies a fixed thing
across the method change, instead of being re-tuned to whatever the new method
produces - which is the difference between a gate and a rubber stamp.

**`PL-GS5X` landed 2026-09-06 and makes this item's question live rather than
theoretical.** Measured the same day over a 3600 s run at 1 MAC, the worst
accounting residual at any step is 1.0e-12 L for sevoflurane, 2.4e-12 L for
isoflurane and 1.3e-11 L for desflurane — against
`AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L = 1e-12`. Every one of those runs passes,
because `check_agent_accounting` passes on *either* tolerance and the relative
error is at most 9.2e-13 against a 1e-9 bound.

The absolute branch is therefore now dead on any long run, and the relative
branch alone is carrying the check. That is not a defect in the numbers: the
split moved agent between compartments as amounts, so its equal-and-opposite
pairs cancelled to the last bit and left ~2e-15 L; the exact step's conservation
is a property of the matrix and its arithmetic is done in fractions, so the
pairs cancel to floating-point precision relative to the largest quantity in
play — about 43 L of delivered agent over an hour at desflurane's dial, which
is where four orders of magnitude come from.

What it means for this item is that the choice it poses — assert
`relative_error` rather than `absolute_error_l` — now has a measurement behind
it, and that an absolute tolerance which scales with nothing is the wrong
shape for a quantity that scales with how much agent a run has handled. The
two measured tables in the brief were taken under the split and need re-running.

**Closed 2026-09-06. Both tables re-measured on the shipped exact step, and
both moved.**

The dial table is now a cleaner demonstration than the original. Over 600 s
wash-in plus 600 s washout, halving the dial halves the absolute residual
exactly and leaves the relative one unchanged to four significant figures:
isoflurane 3.589e-13 L at 4% against 1.794e-13 L at 2%, relative 2.243e-13 in
both; desflurane 9.262e-14 L against 4.631e-14 L, relative 5.789e-14 in both.
The brief's 8% row could not be re-measured as written - isoflurane's
calibrated maximum is 5%, so `BreathingCircuit` refuses that dial - which is
itself worth knowing: the original table predates that guard.

The horizon table moved a long way in the direction that mattered. Under the
exact step `absolute_error_l` first exceeds 1e-12 L at t = 3452 s at the
reference runs' own settings, not 6212 s, and at t = 538 s at the sevoflurane
envelope corner. At 4 h the absolute residual reaches 1.246e-9 L at the
desflurane corner while the relative residual is 2.884e-12. So the assertion
these tests carried was not merely dial-dependent, it was false past about an
hour of ordinary simulated time and passed only because the tests stop at
1200 s.

**What shipped.** Both reference runs assert `validation.relative_error <=
MASS_BALANCE_RELATIVE_GATE`, with `MASS_BALANCE_RELATIVE_GATE = 1e-10`
restated in each file and the derivation in `docs/MODEL.md`, which is the
specification and therefore the single source of what the gate means.

A first attempt put the constant in a shared `tests/reference/mass_balance_gate.py`
instead, and `PL-JBZK`'s lane check - which merged onto `main` while this was
being worked - refused it: a file under `tests/` that imports no
`anesthesia_sim` is apparatus by that rule, and the check's suggested remedy
would have declared simulator content as workflow. Restating the bound per file
is the repository's own idiom anyway, for the reason
`tests/unit/test_agent_simulation_validation.py` records, and putting the
derivation in the specification rather than in a test helper is the better half
of the trade. `PL-12P8` carries what the check's premise misses. `docs/MODEL.md`
separates the run-time halt thresholds from the release gate - it called the
halt thresholds "the release tolerance", which was half the confusion - states
the gate and its derivation, and settles the question it had left open against
this item.

**Why 1e-10.** Worst relative residual at any step, measured over 8 h at the
reference settings and at the envelope corner with each agent at its calibrated
maximum: 2.3e-13 at the 1200 s these runs cover, at most 1.04e-12 at 1 h, and
at most 6.36e-12 at 8 h. 1e-10 leaves about 450x headroom at the horizon the
runs use and about 16x at 8 h, so neither a dial change nor a plausible
lengthening changes what the gate certifies. It stays an order of magnitude
inside the 1e-9 halt threshold, so passing says strictly more than "the run did
not stop", and a real conservation defect is orders of magnitude rather than
factors of two.

**`core/` was not touched**, as the brief expected. The halt threshold is
right and the disjunction is what makes it right: the absolute branch catches a
gross error early in a run, when little has been delivered and the relative
denominator is small, and the relative branch carries the check from then on.
