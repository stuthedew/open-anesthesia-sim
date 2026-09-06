---
id: PL-8PS6
title: Fresh gas flow range is a machine property held in supported_ranges.py, not a global constant
status: blocked
blocked-by: PL-FG9D
added: 2026-09-06
priority: P2
effort: M
classes: safety, anticipated, refactor
feature: anesthesia-machine
touches: src/anesthesia_sim/core/supported_ranges.py, src/anesthesia_sim/core/circuit.py, docs/MODEL.md
---

**Problem.** `MINIMUM_FRESH_GAS_FLOW_L_MIN = 0.0` and
`MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10.0` sit in
`src/anesthesia_sim/core/supported_ranges.py` as global constants, and
`require_supported_fresh_gas_flow` enforces them for every simulation. But the
deliverable fresh gas flow range is a property of the anesthesia machine — its
flowmeters, its minimum-flow floor, whether it supports minimal- or
closed-circuit flow — and it differs between machines. It belongs on an
anesthesia-machine profile, not in a module of model-wide constants.

**Why it matters.** Two separate constraints currently coincide in one number,
and conflating them is the safety hazard rather than the tidiness problem:

1. **The model's validated envelope** — the range over which the compartment
   model's error bound was measured, which is what the module docstring and
   the refusal message actually claim ("the domain this compartment model is
   claimed to represent a patient over", `docs/MODEL.md` § "Supported input
   ranges"). That is a model property and stays where it is.
2. **The machine's deliverable range** — what a given machine can physically
   set. That is the machine property this item is about.

The effective limit on a control is the **intersection** of the two, and each
side needs its own name, its own source and its own refusal message. If they
stay merged, adding a machine profile whose flowmeter goes higher silently
widens the model's claimed validity envelope — a plausible-looking number
produced outside the domain anything was measured over, which is exactly what
`CLAUDE.md`'s safety-critical standard forbids. Conversely a machine with a
higher floor than 0.0 (no true off position on the common gas outlet) would,
under a single constant, either be unrepresentable or would move the model's
floor for every machine.

**Where.**

- `src/anesthesia_sim/core/supported_ranges.py:55-57` — the two constants.
- `src/anesthesia_sim/core/supported_ranges.py:100-108` —
  `require_supported_fresh_gas_flow`, whose message cites `docs/MODEL.md` §
  "Supported input ranges" as the authority for the interval.
- `src/anesthesia_sim/core/circuit.py:84` (`__post_init__`) and
  `src/anesthesia_sim/core/circuit.py:168` (`set_fresh_gas_flow`) — the two
  call sites.
- `src/anesthesia_sim/core/circuit.py:77` — `fresh_gas_flow_l_min: float = 4.0`,
  the default, which is a machine/practice convention on the same footing.
- `docs/MODEL.md` § "Supported input ranges" — the prose that would have to
  separate the two claims.

The precedent for the split already exists in the same file: the vaporizer's
calibrated maximum is agent-specific and therefore lives on `BreathingCircuit`
as instance state rather than as a constant here
(`supported_ranges.py:36-39`). The fresh gas flow range is the same shape with
the machine, rather than the agent, as the carrier.

**Related.** `PL-FG9D` (design the base anesthesia-machine abstraction so a real
commercial machine is a data-plus-plugin addition) is where the carrier gets
designed; this item is a concrete property that abstraction has to hold.
`PL-4DCG` (survey the anesthesia machines in current clinical use for the
variables that change a simulated result) is where the per-machine numbers come
from. `PL-WZVZ` (make an inter-machine difference attributable) is the display
half. `PL-4YY1` (record provenance for the circuit volume and default fresh gas
flow) covers the 4.0 L/min default.

**Blocked on `PL-FG9D`, and classed `anticipated` for the same reason.** There
is one implicit machine today, and over it the constants are the model's own
envelope and are enforced correctly - so nothing displayed is wrong yet, and
the `safety` class describes the hazard the second machine introduces rather
than a live one. `docket check` seats such an item at its blocker's band
(`checks.py`, the `anticipated` exemption), which is why this sits at P2 behind
`PL-FG9D` instead of in the top band. The split cannot be made earlier than the
carrier: naming the machine's range is only meaningful once there is a machine
profile to name it on.

**Done when.** The machine's deliverable fresh gas flow range is read from a
validated, versioned machine profile with its own primary source (an
operator's manual or manufacturer specification, not a reference
implementation), the model's
validated envelope stays separately named in `supported_ranges.py`, a setting
outside either is refused with a message that says which of the two it
violated, and `docs/MODEL.md` distinguishes the two claims.
