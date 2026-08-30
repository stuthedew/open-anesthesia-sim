---
id: PL-4YY1
title: Record provenance for the circuit volume and default fresh gas flow
priority: P2
effort: S
status: ready
classes: defect, docs
feature: model-spec-accuracy
touches: src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/data, docs/MODEL.md, docs/ARCHITECTURE.md, tools/doc_check.py, tests/reference/test_coupled_dynamics.py
added: 2026-08-30
verify: python3 tools/doc_check.py check
---

**Problem.** `core/circuit.py:46` hardcodes `circuit_volume_l: float = 6.0` and
`:47` `fresh_gas_flow_l_min: float = 4.0`. Neither is in a data file, neither
has a row in `docs/MODEL.md`'s provenance table, and 6.0 is restated a third
time as `CIRCUIT_VOLUME_L` at `tests/reference/test_coupled_dynamics.py:53`.

**The value is settled: keep 6.0.** The project owner has ruled that which
value is used is not critical. This item is provenance work only and must not
change any modelled number.

**Why it matters.** Circuit volume sets the fresh-gas wash-in time constant
(tau = V/FGF, 90 s at the defaults), so it sits between the vaporizer dial and
every displayed value. A learner watching the early lag attributes it to
uptake, when at these settings a large part of it belongs to the machine — that
is the anesthesia circuit's most-taught teaching point, and the constant
governing it currently has no recorded source at all. It is exactly the kind of
"clinically meaningful transformation" `CLAUDE.md` requires provenance for.

The tooling cannot see it, and that is the second half of the finding.
`tools/doc_check.py`'s `check_provenance` walks *data files* in both
directions, so a scientific constant that never entered one is structurally
invisible to the only tool built to catch this class of omission. And
`docs/ARCHITECTURE.md:26-27` claims "`core/` never contains hardcoded
scientific constants for the agent or patient it loads by default" — literally
true, and the machine-parameter carve-out is what these two escape through.

**Where.** `core/circuit.py:46-47`; `tests/reference/test_coupled_dynamics.py:53`;
`docs/MODEL.md`'s provenance table; `docs/ARCHITECTURE.md:26-27`;
`tools/doc_check.py` (`check_provenance`).

**Approach.** Move both constants into a versioned, cited data file beside
`data/patients/` — machine parameters are their own kind, not patient or agent
parameters — and add their provenance rows. Record there that the published Gas
Man convention is 8 L (De Wolf AM, Van Zundert TCRV, De Cooman S, Hendrickx JFA.
*Theoretical effect of hyperventilation on speed of recovery and risk of
rehyperventilation.* BMC Anesthesiol 2012;12:22) and that 6.0 L is retained
deliberately, so a later reader finds a decision rather than an accident.
Reconcile `docs/ARCHITECTURE.md:26-27` with whatever carve-out remains.

Consider extending `tools/doc_check.py` to flag float literals in `core/`
dataclass field defaults against an allowlist. That is the check that would
have caught this, and it stays on the decidable side of the line the tool is
built around: it can see that a literal exists and is unlisted, and makes no
attempt to judge whether the value is right.

**Done when.** Circuit volume and default fresh gas flow are loaded from a
versioned, cited data file with provenance rows in `docs/MODEL.md`, the Gas Man
8 L convention and the deliberate retention of 6.0 are recorded,
`docs/ARCHITECTURE.md`'s claim matches what `core/` now holds, the third
restatement in the reference test reads from the same source, and no modelled
value has changed.
