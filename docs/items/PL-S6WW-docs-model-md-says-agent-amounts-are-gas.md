---
id: PL-S6WW
title: docs/MODEL.md says agent amounts are gas volumes 'at one documented reference temperature and pressure' but documents no temperature anywhere, and a liquid-equivalent conversion moves 5.8 percent between a 20 C and a 37 C reference
priority: P1
effort: S
status: done
classes: science, docs
feature: liquid-agent-consumption
milestone: v0.4.28
touches: docs/MODEL.md, docs/references/README.md, ROADMAP.md
added: 2026-09-16
closed: 2026-09-17
pr: 669
verify: python3 tools/doc_check.py check && grep -qF 'where the ideal-gas molar volume is 24.055 L/mol' docs/MODEL.md && grep -qF 'One reference condition, where the model physically has two' docs/MODEL.md
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

**Written on `claude/agent-amounts-ref-temp-vk1c39` at 20 °C, 2026-09-17, and
the item stays open for one word from the project owner.** The whole
deliverable is on the branch — `docs/MODEL.md` § "Agent amount" states the
condition, § "Assumptions" points at it from "temperature is constant", and
§ "Known limitations" carries the single-condition note and its 5.8 % — so
what is outstanding is the ratification, not the work. No pull request was
opened for that reason.

**One ground the original brief did not have, and it is the strongest.**
Biro's composite constants can be *derived* rather than taken on authority,
from Laster, Fang and Eger's 20 °C densities and the ideal-gas molar volume.
Run at 20 °C the derivation gives sevoflurane 182.8, isoflurane 195.8 and
desflurane 209.7 mL of vapour per mL of liquid, against Biro's 184, 195 and
210 — within 0.7 % on all three. Run at 37 °C it gives 193.4, 207.2 and 221.9,
which is 5.1–6.3 % high and matches none of them. So "the published constants
are 20 °C constants" is arithmetic that anyone can re-run, not a convention
being appealed to. That reproduction is what moved this from a balanced
two-sided decision to a recommendation with a measurement under it.

**The second ground was also sharpened.** `ROADMAP.md` planned-milestone item
28's figure converts $`M_{\mathrm{delivered}}`$ (`PL-H4N8`), which integrates
$`\dot V_F`$ — the flow at the common gas outlet, at operating-room
temperature. Declaring 20 °C makes that term exact. Declaring 37 °C would not
merely relabel it: it would call for an ambient-to-body correction on
$`\dot V_F`$ that no governing equation here carries, which is a change to the
model rather than to a unit definition.

**What the case against now amounts to.** 37 °C remains where the partition
coefficients were measured and where the alveolar, venous and tissue
compartments are, so the *stores* are natively exact there. The branch does
not hide this — it is the "Known limitations" note, sized at 5.8 % on those
three terms and at zero on the fresh-gas terms. The trade is therefore
explicit: 20 °C puts the error on the stores and none on the amounts a
consumption figure converts; 37 °C would reverse that and would disagree with
the published constants.

**To flip it to 37 °C** takes the one sentence in § "Agent amount" that names
the condition, the molar volume beside it (25.450 L/mol), the "Why 20 °C"
block, the `verify:` string above, and the direction of the "Known
limitations" note — which would then say the fresh-gas terms are the
approximated ones. Under an hour; nothing outside `docs/MODEL.md`.

**To close it at 20 °C** takes `status: done`, `closed:`, the pull request,
and one edit outside this item's `touches`: `ROADMAP.md`'s Gate entry for
`PL-S6WW` says the document "documents no temperature anywhere", which stops
being true the moment this branch merges. `PL-KZ99` (store each agent's molar
mass and liquid density with the density's measurement temperature) and
`PL-0S0V` (agent volume display decimals) are both `blocked-by` this item and
are released by either answer, not only by this one.

**Docs swept 2026-09-17**, against the branch: `docs/MODEL.md` and
`docs/references/README.md` (both edited, `make doc-check` clean), `README.md`,
`docs/WORKING_NOTES.md` and `docs/interface-provenance.md` (none names the
amount unit's condition), `ROADMAP.md` (the Gate entry above, accurate until
this closes), and `app/dashboard_frame.py`'s `ACCOUNTING_UNIT_CAPTION` with
`app/formatting.py`'s two amount docstrings — all three still read correctly,
because they name the unit and the condition is read only by a conversion out
of it, which nothing performs today.

**Widened `touches` mid-work, deliberately.** `docs/references/README.md`
gained the extraction note for Appendix C's `Volatility` line, which
`.claude/rules/citing-sources.md` requires of any reading taken from the
private reference corpus and which did not exist — the entry recorded three
values Appendix C carries beyond Appendix B's table and this is a fourth. It
is the in-repo carrier the § "Agent amount" citation now points at, so it is
this item's work rather than a drive-by fix. Two things in it could not be
re-verified: the corpus could not be attached this session (`add_repo` was
declined by the sandbox's permission classifier, and an unauthenticated clone
fails), so p. 174 sitting outside the pp. 171–72 span the entry gives, and
which agent each `Volatility` value belongs to, are both recorded as open.

**What the literature does, checked 2026-09-17 on the project owner's
question — and it is not what either candidate assumed.** The field has no
single reference condition. It has a *rule*, which is to state the condition
on the quantity, and three conventions that different quantities own:

- **STPD (0 °C, 760 mmHg, dry; 22.414 L/mol)** for an *amount of gas
  transferred*. This is the respiratory-physiology convention and it is
  written on the number: "carbon dioxide elimination 151 ± 38 ml (STPD)"
  (Jonsson & Wahlgreen, *Acta Anaesthesiol Scand* 1989;33(4):331-5,
  PMID 2497618); "173 ml·min⁻¹ (STPD)" (Jonsson & Zetterström, same journal
  1985;29(3):309-14, PMID 3922197); "standard temperature and pressure, dry,
  correction of airway VCO2 and VO2" (Rosenbaum, Kirby & Breen,
  *Anesthesiology* 2004;100(6):1427-37, PMID 15166562).
- **BTPS** for a *ventilated volume*: "VE (BTPS)" beside "CO2 production
  (ATPD)" in one sentence (Bowie et al., *J Clin Monit* 1995;11(6):354-7,
  PMID 8576717); "PETCO2 ... corrected for BTPS conditions" (Laffon et al.,
  *Can J Anaesth* 1998;45(6):561-3, PMID 9669011).
- **20 °C** for the agent's own liquid-to-vapour ratio, which this brief
  already establishes.

**So the project owner's instinct is the BTPS convention and it is correct
for what it covers** — a gas volume physically in the body is stated at body
temperature. It does not settle this item, because the amounts here are not
all in the body.

**No classic uptake model answers this, because none of them carries an
amount.** Mapleson, Eger and Gas Man are written in fractions and partial
pressures, which are dimensionless and carry no condition. The question
exists here only because this model carries a *volume* as its amount unit.

**The models that do carry amounts carry mass, not volume.** The PBPK
literature works in mg, mg/L and mg/kg/h against blood:air and tissue:blood
partition coefficients — Fisher et al., *Toxicol Appl Pharmacol*
1989;99(3):395-414 (PMID 2749729) and 1998;152(2):339-59 (PMID 9853003);
Simmons et al., *Toxicol Sci* 2002;69(1):3-15 (PMID 12215655). That is the
third option and it is the one that actually removes the 5.8 %.

**What that third option costs, worked.** Carrying moles changes exactly one
term. With $`n_C = F_I V_C / V_m(20)`$ and the alveolar and tissue stores
built on $`V_m(37)`$, the alveolar, venous and tissue balances reduce to
exactly the equations already in § "Governing equations" — the molar volume
cancels — and the *circuit* balance becomes

    V_C dF_I/dt = V̇_F(F_D − F_I) − 0.9452 · V̇_A(F_I − F_A)

where 0.9452 is $`V_m(20)/V_m(37)`$. One factor, on one term. But it costs a
**circuit gas temperature**, which no source publishes as a model parameter
and which varies with fresh-gas flow, absorber activity and whether an HME is
fitted; and it moves $`F_I`$, and through it $`F_A`$, off Gas Man's
trajectory and off the published wash-in comparison in § "Required tests".
That makes it a milestone-sized change to the gas-phase model, not a unit
decision — it belongs on `ROADMAP.md` if it is wanted, not inside this item.

**And it is the smaller of the two condition effects it would sit beside.**
Temperature moves only volume↔moles; it does not touch any fraction, so it
reaches no partial pressure and no pharmacology. Humidification does the
opposite: it changes the *fraction* by 47/760 = 6.2 % and therefore the
partial pressure, which is what the model is about. That is `PL-7DMJ`, filed
the same day. Correcting the 5.8 % while leaving the 6.2 % is picking the one
of the two that cannot reach a clinical reading.

**Which leaves the decision sharper than the two-way framing above.** The
5.8 % is the size of a simplification the model already makes, and no label
removes it — 20 °C puts it on the stores, 37 °C puts it on the fresh-gas
terms, STPD puts it on both. The question is only *which terms should be
exact*, and that follows from what gets displayed: today, and under
planned-milestone item 28, that is delivered and exhausted.

**RATIFIED AT 20 °C** (project owner, 2026-09-17): *"Ok, sounds good. let's not
reinvent the wheel."* Recorded as `ratified` rather than specified, per
`CLAUDE.md` — it was taken on this session's recommendation, over 37 °C.

**The ground it was ratified on is worth keeping, because it is narrower than
the case that was put.** The reply that earned the answer was the one about
what Gas Man actually does, and the reason given back was not the arithmetic:
it was that this project should not diverge from its reference implementation
without cause. So a later session reopening this on ordinary evidence — a
measurement, a cost the case did not carry — should understand that the
decision rests on *lineage consistency with Gas Man* first and on the 20 °C
reproduction second. Changing the reference condition means accepting that this
model's litre and Gas Man's litre are different quantities.

**Ground 3 was rebuilt before the close**, on the same question. It had rested
on a comment in `GASMAN.INI`; it now rests on the five expansion constants the
Workbook prints in chapter 10 (halothane 228, enflurane 198, isoflurane 196,
sevoflurane 183, desflurane 209 mL vapour per mL liquid), recorded in
`PL-B396`. Derived from Laster, Fang and Eger's 20 °C densities they reproduce
within 0.35 % on all five; at 37 °C the same derivation is 5.6–6.2 % high on
every one. Two of the five are agents this model does not carry, so it is not
a fit to the set.

**`ROADMAP.md` was added to `touches` at the close**, for the Gate entry under
v0.5.0 that described the finding in the present tense — "documents no
temperature anywhere" — which the merge falsifies. It now records the
resolution instead.

**Released by this close:** `PL-KZ99` (store each agent's molar mass and liquid
density with the density's measurement temperature) has this as its only
blocker and is promotable. `PL-0S0V` (display-precision constants per quantity
and unit) also lists `PL-B396`, which is still open, so it stays blocked.
