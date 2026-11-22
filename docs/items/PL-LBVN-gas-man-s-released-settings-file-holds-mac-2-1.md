---
id: PL-LBVN
title: Gas Man's released settings file holds MAC 2.1% sevoflurane and 1.1% isoflurane; we store De Wolf's 2.0% and 1.2%. Decide which MAC values to store
priority: P1
effort: L
status: ready
classes: safety, science
feature: gas-man-open-source
touches: src/anesthesia_sim/data/agents, src/anesthesia_sim/core, src/anesthesia_sim/app, docs/MODEL.md, docs/INTERFACE.md, tests
added: 2026-11-14
payoff: Every MAC multiple a learner reads is divided by a published MAC for a stated age, the same age for all three agents, so comparing agents at 1 MAC is no longer off by about 22% and age-adjusted MAC can follow without changing any reader.
---

**Problem.** Gas Man's released settings file holds MAC 2.1% sevoflurane and 1.1% isoflurane; we store De Wolf's 2.0% and 1.2%. Decide which MAC values to store

**The disagreement.** `docs/PARAMETERS.md` § "Source hierarchy" records that two
Gas Man simulation studies print different MAC values for Gas Man's set.
Weber et al. 2021 print 2.1% sevoflurane and 1.1% isoflurane. De Wolf et al.
2012 print 2.0% and 1.2%, and the simulator stores De Wolf's values.

**What the released source shows.** Gas Man's settings file, `gasman.ini`, in
<https://github.com/rasman/gasmanonline> at commit `d3a2dd3` (read 2026-11-13),
holds `MAC=2.1` for sevoflurane, `MAC=1.1` for isoflurane and `MAC=6.0` for
desflurane. The same values are in the repository's first commit, `883fd66`
(2022-09-26), and in both copies of the file (`gasman_api/gasman.ini`,
`src/gasman_main/gasman.ini`). So the program matches Weber's table. Every other
tier-3 value we store matches the file: the blood:gas and tissue:gas
coefficients for all three agents, the four tissue and alveolar volumes, and
the 76/18/6 flow fractions.

**Why it matters.** MAC divides every value shown in MAC multiples
(`docs/PARAMETERS.md` § "Where each stored value comes from"), so the choice changes
a displayed clinical value by about 5% for sevoflurane and 9% for isoflurane.
That makes it a safety-critical decision and the project owner's.

**The question.** Which MAC values should the simulator store for sevoflurane
and isoflurane, and on what authority?

**No recommendation yet.** A recommendation needs the primary MAC literature
read first, starting with Mapleson's 1996 meta-analysis, which `docs/MODEL.md`
cites beside the stored values but does not adopt. The released `gasman.ini`
is still tier 3, and it is one version of one program. It settles which values
Gas Man holds. It does not settle which values are right.

**Decided.** Filed as a decision for the project owner (project owner,
2026-11-14, ratified, over changing the stored values now).

**Recommendation (2026-11-14, after reading the MAC literature).** Store
Mapleson's MAC at age 40 and label it so: 1.80% sevoflurane, 1.17% isoflurane
and 6.6% desflurane (Mapleson, Br J Anaesth 1996;76:179-185, PMID 8777094,
read from its abstract; the same figures are Table 1 of Nickalls and Mapleson,
Br J Anaesth 2003;91:170-174, read in full from the private corpus). Three
reasons. The project owner wants the stored MAC tied to a sourced age, because
MAC is age-adjusted in practice and patient age will become an input
(`PL-8F9D`); neither De Wolf's values nor Gas Man's `gasman.ini` give an age.
Mapleson's is the one source that gives every agent's MAC at a stated age with
confidence limits, and the age equation that the future feature needs. And it
removes the 22% sevoflurane-versus-desflurane distortion that `docs/MODEL.md`
lists as a limitation of the MAC display.

**What it costs.** Every displayed MAC multiple changes: sevoflurane readings
rise about 11%, isoflurane about 2.6%, desflurane fall about 9%. The dial's
starting position changes to 1.80%, 1.17% and 6.6%. The MAC-awake band moves
with the divisor. It reopens the decision of 2026-09-04 (ratified, over
adopting Mapleson's age-40 values), whose second reason was that every other
parameter comes from the Gas Man set. That reason still holds, and the owner's
age requirement is the new constraint that outweighs it. Mapleson is tier 2
under `docs/PARAMETERS.md` § "Source hierarchy", so adopting it needs this recorded
decision.

**Alternative.** Keep De Wolf's values and label them "a single adult MAC
with no age", as `#2155` does. Nothing a learner sees changes, but the
age-adjustment feature would then need a new divisor anyway.

**Decided** (project owner, 2026-11-14, answering the card that put the
recommendation above): "so we can use MAC age 40 as the default, but age
adjusted MAC (setting arbitrary age) will be core feature. So that can be
default for now, but there will be no single "simulator MAC" value once that
is implemented so take that into account". Chosen over keeping De Wolf et
al.'s 2.0%, 1.2% and 6.0% and over Gas Man's `gasman.ini` 2.1%, 1.1% and 6.0%.
This reopens the decision of 2026-09-04 (ratified), which kept De Wolf's
values over Mapleson's.

**What to build.**

1. Store each agent's MAC at age 40 from Mapleson 1996: 1.80% sevoflurane,
   1.17% isoflurane, 6.6% desflurane. Name the data key for the age it holds,
   `mac_at_age_40_percent`, and add a Mapleson 1996 source entry to each
   agent file, tier 2, adopted on this decision. The De Wolf entry stops being
   the authority for MAC and stays cited.
2. Keep the agent's MAC at age 40 apart from the MAC a run divides by. The
   agent record holds the MAC at 40. The run's MAC is built in one function
   from the agent and the patient, and returns the MAC at 40 for the
   reference adult today. `PL-8F9D` puts Mapleson's age equation in that one
   function when age becomes an input, so no other reader changes then.
3. Show the age beside every 1 MAC the interface states, for example
   "1 MAC sevoflurane (age 40) = 1.80%", so a learner sees which patient the
   divisor belongs to.
4. Update `docs/MODEL.md` and `docs/INTERFACE.md`: the stored-value tables
   and provenance markers, the comparison table with Mapleson (the gap goes
   to zero), the 22% limitation (it no longer applies), the MAC-awake band's
   drawn centres and its comparison with Katoh, the MAC readout's step in
   percentage points, and the dial's starting positions. Describe the divisor
   as the MAC for the patient's age, 40 for the reference adult.
5. Update every test that pins 2.0, 1.2 or 6.0 as a MAC, or a value derived
   from one, with the expected value worked out from Mapleson's figures
   rather than read back from the code.

**Collision to check first.** `PL-19W8` (in flight on 2026-11-14) adds a test
for the MAC readout's step in percentage points, which this change moves.

**From the `PL-19W8` thread (2026-11-14).** `#2154` merges first. After the
MAC changes, rerun `tests/reference/test_displayed_precision_figures.py` and
update the printed figures in `docs/INTERFACE.md` § "Displayed precision"
(desflurane's MAC step prints 0.07 there). A test asserts that the dial opens
at the stored MAC. The dial keeps opening at 1 MAC, now the age-40 value:
1.80% sevoflurane, 1.17% isoflurane and 6.60% desflurane, all on the dial's
0.01-point steps. Decided here because it keeps the existing rule that every
run starts at a recognizable clinical anchor.

**Checked 2026-11-21:** `PL-RMNP` (the check of `docs/MODEL.md` against the code) found three places that the move to Mapleson's age-40 values must change with the stored numbers. `format_mac_reference` in `app/formatting.py` prints the MAC with one decimal (`{mac_percent:.1f}`), so isoflurane's 1.17% would be shown as "1.2%" and sevoflurane's 1.80% as "1.8%". The docstring of `MacPercent` in `core/concentration.py` and `docs/VERIFICATION.md` § "Concentrations" (where `PL-48MX` moved the model document's conventions) both say "The shipped MACs are 1.2% to 6.0%". `docs/MODEL.md` and the three agent files still hold De Wolf's 2.0, 1.2 and 6.0 today, which is this item's work and not a finding against the document.

**Checked 2026-11-21**, by `PL-5FMC` (the check of `docs/INTERFACE.md` against the code). `docs/INTERFACE.md` § "MAC-awake as a chart reference" says that the sevoflurane band "probably sits too high, by about 11% if Mapleson is right", and gives the washout crossing as 6.55 min at the drawn band centre of 0.68% against 7.30 min at 0.612%. Both figures are right for the run they describe, with the dial held at 2.0%. The paragraph's reason, "The traces are absolute partial pressures and do not depend on MAC", does not hold for a run left at its opening dial, because `AgentUptakeSystem.for_agent` opens the dial at the stored MAC. The model is linear in the dial setting. With the dial at 1.8%, the vessel-rich trace crosses 0.612% at 6.55 min, the same time as today's run crosses today's band. When this item stores Mapleson's values and rewrites that paragraph, the paragraph should say that the error it describes applied to a dial set in percent, and not to a run at its opening 1 MAC dial.

**Checked 2026-11-22**, at `d4e8200c`. `grep -n '"mac_percent":' src/anesthesia_sim/data/agents/*.json`
printed 6.0 for desflurane, 1.2 for isoflurane and 2.0 for sevoflurane. So
the simulator still stores De Wolf et al.'s values, and every MAC multiple a
learner reads today is divided by them. The three places that `PL-RMNP` named
on 2026-11-21 are unchanged: `format_mac_reference` in `app/formatting.py`
(line 701) still prints the MAC to one decimal, and both
`core/concentration.py` (line 266) and `docs/MODEL.md` (line 524) still say
"The shipped MACs are 1.2% to 6.0%".

**Done when.** Each agent file stores Mapleson's MAC at age 40 (1.80%
sevoflurane, 1.17% isoflurane, 6.6% desflurane) under a key that names the age,
with a Mapleson 1996 source entry adopted on the owner's decision of
2026-11-14. The MAC a run divides by is built in one function from the agent
and the patient. Every 1 MAC that the interface states shows its age and
prints the stored value in full, so 1.17% is not shown as 1.2%. The dial opens
at the age-40 value. `docs/MODEL.md` and `docs/INTERFACE.md` describe the
divisor as the MAC for the patient's age, 40 for the reference adult, and the
limitation about the 22% cross-agent distortion is removed. Tests derive each
expected MAC value from Mapleson's figures rather than from the code.

**Generator check.** The fact is which MAC the divisor holds, and for which
age. One-off: it is a choice between published sources that the owner made on
2026-11-14, not a misreading that other items share.
