---
id: PL-S6WW
title: docs/MODEL.md says agent amounts are gas volumes 'at one documented reference temperature and pressure' but documents no temperature anywhere, and a liquid-equivalent conversion moves 5.8 percent between a 20 C and a 37 C reference
priority: P1
effort: S
status: needs-decision
classes: science, docs
feature: liquid-agent-consumption
touches: docs/MODEL.md
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

**GAS MAN ANSWERS THIS, AND MORE DIRECTLY THAN EXPECTED (2026-09-16).** The
Gas Man Workbook's Appendix C documents `GASMAN.INI` and one of its per-agent
parameters is, verbatim:

> Volatility=209           Vapor/Liquid volume ratio (20'C)

with `Volatility=200` in the second example (printed pp. 171 and 174 of the
Workbook; `stuthedew/open-anesthesia-sim-references`,
`text/gasman_workbook/05_Appendices_Bibliography.txt`). So the reference
implementation whose parameter set this project adopted states its vapour/
liquid ratio **at 20 °C**, which means its own gas volumes are referenced
there. Its cost formula on the same page, `Cost = DELIVERED Flow x Cost/mL
vapor`, confirms the amounts it converts are vapour volumes.

**Why that is more than corroboration.** This project's partition
coefficients, MAC divisors and reference patient are the Gas Man set
(`docs/MODEL.md` § "Source hierarchy"), so the trajectories these gas volumes
come out of are that program's arithmetic. Adopting a different reference
temperature for the same volumes would mean this model's litre and Gas Man's
litre are not the same quantity while every parameter feeding them is.

**Still the project owner's to decide, and here is the tension.** 20 °C is
where the parameter lineage points. 37 °C is where the *partition
coefficients* are measured and where the tissue and blood compartments
physically are, and `docs/MODEL.md` § "Assumptions" already records
"temperature is constant" without saying which. The honest resolution is
probably to state 20 °C as the reference and record in § "Known limitations"
that one condition is used for a circuit at ambient and tissues at 37 °C,
which is a real approximation this model makes and does not currently
disclose.

**Why it matters.** `docs/MODEL.md` § "Agent amount" asserts a documented
reference condition that is not documented, which is a provenance failure in the
authoritative model specification rather than a gap in prose. Today it costs
nothing because every gas volume shares the same unstated condition and the
partition coefficients are ratios. It stops being free at the first conversion
out of the unit, where the choice moves the answer 5.8% - ideal-gas molar volume
is 24.055 L/mol at 20 C and 25.450 L/mol at 37 C - and `ROADMAP.md`
planned-milestone item 28 is exactly such a conversion, now that the project
owner has settled its display unit as millilitres of liquid equivalent.

**Decision needed.** Which reference temperature the model's gas volumes are
stated at: **20 C** or **37 C**.

*Recommendation: 20 C*, recorded here rather than only in a reply, per `PL-M21Q`.
Three reasons, strongest first. The parameter lineage points there - this
project's partition coefficients, MAC divisors and reference patient are the Gas
Man set, and `GASMAN.INI` states its own vapour/liquid ratio as `Volatility=209
Vapor/Liquid volume ratio (20'C)`, so those trajectories are arithmetic
referenced at 20 C. Adopting 37 C for the same volumes would mean this model's
litre and Gas Man's litre are not the same quantity while every parameter
feeding them is. The primary density measurement this project would derive from
(`PL-KZ99`, Laster/Fang/Eger 1994) is also at 20 C. And the derivation
reproduces the published composite constants at 20 C to within 1%.

The case against, stated so the decision is taken over both: 37 C is where the
partition coefficients are measured and where the tissue and blood compartments
physically are. Choosing 20 C therefore means one condition is used for a
circuit at ambient and tissues at 37 C, which is a real approximation this model
makes and does not currently disclose.

**Done when** `docs/MODEL.md` § "Agent amount" states the temperature as it
already states the pressure, with the reasoning for the choice and its source,
and § "Known limitations" records what the single-condition assumption costs.
