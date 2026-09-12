---
id: PL-4YY1
title: Record provenance for the circuit volume and default fresh gas flow
priority: P1
effort: S
status: ready
classes: defect, science, docs
feature: model-spec-accuracy
touches: src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/data, docs/MODEL.md, docs/ARCHITECTURE.md, tools/doc_check.py, tests/reference/test_coupled_dynamics.py
added: 2026-08-30
verify: grep -rq 'circuit_volume_l' src/anesthesia_sim/data/ && python3 tools/doc_check.py check
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
Man convention is 8 L (De Wolf AM, Van Zundert TC, De Cooman S, Hendrickx JF.
*Theoretical effect of hyperventilation on speed of recovery and risk of
rehypnotization following recovery - a Gas Man simulation.* BMC Anesthesiol
2012;12:22) and that 6.0 L is retained
deliberately, so a later reader finds a decision rather than an accident.
Reconcile `docs/ARCHITECTURE.md:26-27` with whatever carve-out remains.

Consider extending `tools/doc_check.py` to flag float literals in `core/`
dataclass field defaults against an allowlist. That is the check that would
have caught this, and it stays on the decidable side of the line the tool is
built around: it can see that a literal exists and is unlisted, and makes no
attempt to judge whether the value is right.


**Appended 2026-09-01 — an open class question for the owner's triage; not
re-classed here.** This item is currently `classes: defect, docs` at `P2`. An
external review argues it reads as `science`, and the argument is worth
recording because the class is currently deciding something other than
labelling.

`circuit_volume_l = 6.0` is not an internal implementation constant. It
appears in `docs/MODEL.md`'s Symbols table as $`V_C`$ (`:148`) and inside the
breathing-circuit governing equation, and $`\tau_C = V_C / \dot V_F`$ sets the
machine lag that a learner will attribute to uptake — 90 s at this project's
defaults against 120 s at Gas Man's published 8 L. `docs/MODEL.md:662-664`
states that no scientific parameter may be added without a full source
citation. This one has none, which is the whole of the **Problem.** above.

If that makes it a scientific parameter, `science` is the class, and the
consequence is not cosmetic: `ROADMAP.md`'s debt-gate rules admit `P0`,
`safety` and `science` findings into the *current* gate regardless of the
presence presumption, while `defect` follows the ordinary rule. So the class
on this item is deciding its gate membership as a side effect of a labelling
choice nobody made deliberately. `docket check` would also pin a `science`
item to `P1` or `P0`, so the priority moves with it.

**This is flagged, not decided.** Re-classing it would move an item between
gates on a session's judgment, which is the project owner's call. Nothing here
is changed.

**Done when.** Circuit volume and default fresh gas flow are loaded from a
versioned, cited data file with provenance rows in `docs/MODEL.md`, the Gas Man
8 L convention and the deliberate retention of 6.0 are recorded,
`docs/ARCHITECTURE.md`'s claim matches what `core/` now holds, the third
restatement in the reference test reads from the same source, and no modelled
value has changed.

**Re-classed 2026-09-12** from `defect, docs` at P2 to `defect, science, docs`
at P1, on the project owner's decision. The class was the defect underneath the
defect: `subprojects/docket/src/docket/checks.py` pins `safety`- and
`science`-classed items to P1, so while this item read as `docs` the band that
exists for "a clinician could be misled" was never consulted about it. Both
constants are scientific parameters by `CLAUDE.md`'s own list - it requires
provenance for "constants, parameter sets" - and tau = V/FGF puts them between
the vaporizer dial and every displayed concentration. Found by the `PL-6ZQY`
consolidation sweep and recorded in `PL-NGLV`.
