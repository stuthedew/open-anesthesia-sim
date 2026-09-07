---
id: PL-L2F2
title: The fixed-volume alveolus blocks nitrous oxide, not just omits it
priority: P1
effort: S
status: done
classes: science
touches: docs/MODEL.md
added: 2026-09-01
closed: 2026-09-07
verify: python3 tools/doc_check.py check && grep -qF 'fixed alveolar volume' docs/MODEL.md
---

**Problem.** `core/alveolar.py` holds `gas_volume_l` as a fixed float
(`:24`), and `apply_blood_uptake()` (`:63`) subtracts the transferred volume
from `agent_amount_l` while leaving `gas_volume_l` untouched. Nothing
augments inspired flow to replace the volume that left the compartment.
`docs/MODEL.md`'s "Alveolar gas" section makes the same assumption
explicitly: it substitutes $`M_A = V_A F_A`$ and divides through by a
constant $`V_A`$. Implementation and specification agree, and both are
correct for the model as shipped.

They stop being correct the moment a gas is administered at a concentration
high enough for its uptake to be a material fraction of alveolar ventilation.
`docs/MODEL.md`'s "Known limitations" lists nitrous oxide, simultaneous
gases, and concentration or second-gas effects as three separate absent
features, and says nothing about their sharing one structural cause. Read as
written, they look like three additive extensions over the current equations.
Two of the three are blocked on the same change, and the third is nearly free
once it is made.

**Why it matters.** The arithmetic is what separates the two cases, computed
from the shipped defaults in `data/patients/reference_adult.json`
($`Q = 5`$ L/min, $`V_A = 2.5`$ L, $`\dot V_A = 4`$ L/min) through the
model's own pulmonary uptake term $`Q\lambda_{b:g}(F_A - F_v)`$ at the early
induction gradient, where $`F_v \approx 0`$:

| Gas | $`\lambda_{b:g}`$ | $`F_A - F_v`$ | Uptake | Per 0.1 s step | Of $`V_A`$ per second | Of $`\dot V_A`$ |
| --- | --- | --- | --- | --- | --- | --- |
| Sevoflurane at 2% | 0.65 | 0.02 | 0.065 L/min | 108 µL | 0.043% | 1.6% |
| Nitrous oxide at 70% | 0.47 | 0.50 | 1.18 L/min | 1.96 mL | 0.78% | 29% |

The last column is the one that decides it. Uptake removes 1.6% of each
inspired alveolar volume for sevoflurane, which the fixed volume can ignore
and does. It removes 29% for nitrous oxide, and that removal *is* the
concentration effect: the gas remaining in the alveolus is concentrated by
the volume that left, and replacement inspired gas is drawn in to fill the
deficit. A fixed-volume compartment cannot represent either half of that.

The safety consequence is not in today's output — the single-agent volatile
model is right. It is that a session scoping planned item 6 from
`docs/MODEL.md`'s limitations list would reasonably plan nitrous oxide as a
second agent object beside the volatile, discover the coupling late, and be
tempted into a partial fix that produces a plausible $`F_A`$ curve that is
wrong by tens of percent during induction — precisely the "plausible-looking
number" `CLAUDE.md` names.

**What lifting it would take.** Two standard formulations, equivalent to
first order, either of which planned item 6 could adopt:

1. **Variable alveolar volume.** Let $`V_A`$ be state:
   $`dV_A/dt = \dot V_{A,\mathrm{in}} - \dot V_{A,\mathrm{out}} - \sum_k \dot M_{\mathrm{uptake},k}`$,
   and the concentration equation picks up the volume term,
   $`dF_A/dt = (dM_A/dt - F_A\,dV_A/dt)/V_A`$.
2. **Fixed volume with augmented inspired flow.** Hold $`V_A`$ constant and
   let the volume lost to total uptake be replaced by inspired gas, so the
   effective inspired ventilation becomes
   $`\dot V_A + \sum_k \dot M_{\mathrm{uptake},k}`$.

Formulation 2 is the less invasive of the two here and is how the classical
treatment writes it. Whichever is chosen, the second-gas effect (planned item
7) falls out of it automatically once the alveolus holds more than one gas —
it is not separate machinery. That is the sense in which items 6 and 7 are
not additive over the current equations: item 7 is nearly free if item 6 is
built this way, and unreachable if item 6 is built as nitrous oxide bolted on
beside a volatile.

`ROADMAP.md`'s planned item 6 already instructs that the patient be modeled
as a set of substances rather than a volatile with nitrous oxide bolted on.
The alveolar-volume coupling is the mechanism behind that instruction; the
roadmap states the conclusion without the reason, so nothing there tells a
session *why* the shortcut fails.

**Where.**

- `src/anesthesia_sim/core/alveolar.py:24` (`gas_volume_l`), `:63`
  (`apply_blood_uptake`) — read, not edited by this item.
- `docs/MODEL.md` — "Alveolar gas" (the $`M_A = V_A F_A`$ substitution),
  "Assumptions" ("carrier gases do not affect sevoflurane kinetics", the
  closest existing statement), and "Known limitations" (the three bullets:
  nitrous oxide; simultaneous gases; concentration or second-gas effects).
  This is the file the item edits.
- `ROADMAP.md` "Planned milestones" items 6 and 7 — read, not edited.

**Not current-milestone work, deliberately, and no guard either.**
Implementing a variable-volume alveolus now would build planned item 6's
equations ahead of the milestone that scopes them, which `CLAUDE.md` forbids;
it would also be premature, since item 6 names defining the coupled-gas
equations and reference cases as its own precondition and neither exists.

No runtime guard belongs in `alveolar.py` today. No code path can produce an
uptake large enough for the fixed volume to matter, so a check would guard an
unreachable state and would be dead code carrying a safety-shaped name. The
constraint is a fact about the model, and the place a fact about the model
goes is `docs/MODEL.md`.

**Arithmetic correction to the finding as relayed.** The review put
sevoflurane's per-step uptake "on the order of 5 microlitres"; recomputed from
the shipped defaults it is ~108 µL, about twenty times larger. The conclusion
is unchanged — 108 µL against a 2.5 L compartment is still 0.0043% per step —
and the comparison that carries the argument is the last column, 1.6% versus
29% of alveolar ventilation. The number in the table above is the one that was
checked. The nitrous oxide figures as relayed (~1.2 L/min, ~0.8% of alveolar
volume per second) reproduce exactly.

Nitrous oxide's $`\lambda_{b:g} = 0.47`$ is used above as the conventional
value only. No `data/agents/nitrous_oxide.json` exists, and the parameter will
need its own provenance entry to this project's standard when item 6 is
scoped; do not carry 0.47 into a data file on the strength of this brief.

**Found.** Outside review, relayed by the project owner on 2026-09-01 in a
capture-only session.

**Done when.** `docs/MODEL.md` states, where a reader scoping nitrous oxide
will meet it, that the fixed alveolar volume is what excludes nitrous oxide
and the concentration and second-gas effects; that this is one structural
constraint rather than three independent omissions; and which of the two
formulations above would lift it. `python3 tools/doc_check.py check` still
passes.

**Closed 2026-09-07.** `docs/MODEL.md` states it in three places, one of them
substantive and two of them routes into it.

- **§ "Alveolar gas"**, immediately after the pulmonary uptake rate the
  argument is about, because that is where the constraint is created: the
  $`M_A = V_AF_A`$ substitution divides through by a constant $`V_A`$, and
  `apply_blood_uptake` does the same thing in code. It carries the comparison
  table (1.6% of alveolar ventilation for sevoflurane against 29% for nitrous
  oxide), the statement that the removal *is* the concentration effect, both
  formulations that lift it, and why planned items 6 and 7 are not additive.
- **§ "Assumptions"** gained a bullet. The constant alveolar volume was not in
  that list at all, which was its own small gap: every other structural
  assumption of the alveolar compartment is there.
- **§ "Known limitations"** gained a paragraph saying the three bullets are one
  constraint, so a reader scoping nitrous oxide from that list meets it there
  rather than only if they happen to read the governing equations.

**The arithmetic was recomputed rather than transcribed**, all six columns,
from the shipped defaults: sevoflurane $`5 \times 0.65 \times 0.02 = 0.065`$
L/min, which is 1.6% of $`\dot V_A = 4`$ L/min; nitrous oxide
$`5 \times 0.47 \times 0.50 = 1.175`$ L/min, 29%. Both reproduce the brief.

**Two corrections to the brief itself.** It cited
`data/patients/reference_adult_70kg.json`, which does not exist under that name
— the file is `reference_adult.json`, and the path is corrected above.
And 0.47 is written into `docs/MODEL.md` explicitly as an unstored,
conventional figure used only to size the comparison, with a sentence saying
nothing in the section is a nitrous oxide parameter set, per the brief's own
warning.

**Nothing under `src/` changed**, deliberately: no code path can produce an
uptake large enough for the fixed volume to matter, so a runtime guard would be
dead code carrying a safety-shaped name. The constraint is a fact about the
model, and `docs/MODEL.md` is where a fact about the model goes.
