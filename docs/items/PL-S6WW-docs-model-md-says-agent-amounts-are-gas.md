---
id: PL-S6WW
title: docs/MODEL.md says agent amounts are gas volumes 'at one documented reference temperature and pressure' but documents no temperature anywhere, and a liquid-equivalent conversion moves 5.8 percent between a 20 C and a 37 C reference
status: untriaged
feature: liquid-agent-consumption
added: 2026-09-16
---

**Problem.** docs/MODEL.md says agent amounts are gas volumes 'at one documented reference temperature and pressure' but documents no temperature anywhere, and a liquid-equivalent conversion moves 5.8 percent between a 20 C and a 37 C reference

**Where it stands today.** `docs/MODEL.md` § "Agent amount" (line 499) reads
"Every compartment stores the agent as an equivalent gas volume at one
documented reference temperature and pressure", and § "Assumptions" documents
the pressure — "ambient pressure is constant, and it is one atmosphere — 760
mmHg" — and the temperature only as "temperature is constant". No temperature
value appears in `docs/MODEL.md`, in `src/anesthesia_sim/core/`, or in any
file under `src/anesthesia_sim/data/`. The sentence asserts a documented
condition that is not documented.

**Why it has cost nothing so far.** Every gas volume in the model is
referenced to the *same* unstated condition, and the partition coefficients
are ratios, so the whole system is invariant to which temperature it is. The
mass-balance identity closes at 1e-14 L regardless. Nothing displayed today
divides a gas volume by a constant carrying a temperature of its own.

**Why it stops being free.** The moment an agent amount is converted to a
liquid-equivalent volume (`PL-B396`), the reference temperature is a factor in
the answer: ideal-gas molar volume is 24.055 L/mol at 20 °C and 25.450 L/mol
at 37 °C, a ratio of 1.0580. For sevoflurane, 1 L of vapour is 5.47 mL of
liquid on a 20 °C reference and 5.17 mL on a 37 °C one. The candidate answers
are not arbitrary — the circuit and the flows are plausibly ambient and the
partition coefficients are measured at 37 °C — so this is a real question with
a 5.8 % spread and no answer on record.

**What done looks like.** `docs/MODEL.md` § "Agent amount" states the
temperature as it already states the pressure, with the reasoning for the
choice, and § "Known limitations" records what the single-condition
assumption costs (a circuit at ambient and tissues at 37 °C are not the same
condition, and this model treats them as one). Either that, or the sentence at
line 499 is corrected to say the model is invariant to the condition and that
no conversion out of the unit may assume one — which is the weaker option,
because `PL-B396` is exactly such a conversion.
