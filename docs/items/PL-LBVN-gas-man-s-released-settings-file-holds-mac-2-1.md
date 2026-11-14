---
id: PL-LBVN
title: Gas Man's released settings file holds MAC 2.1% sevoflurane and 1.1% isoflurane; we store De Wolf's 2.0% and 1.2%. Decide which MAC values to store
status: untriaged
feature: gas-man-open-source
added: 2026-11-14
---

**Problem.** Gas Man's released settings file holds MAC 2.1% sevoflurane and 1.1% isoflurane; we store De Wolf's 2.0% and 1.2%. Decide which MAC values to store

**The disagreement.** `docs/MODEL.md` § "Source hierarchy" records that two
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
(`docs/MODEL.md` § "Where each stored value comes from"), so the choice changes
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
under `docs/MODEL.md` § "Source hierarchy", so adopting it needs this recorded
decision.

**Alternative.** Keep De Wolf's values and label them "a single adult MAC
with no age", as `#2155` does. Nothing a learner sees changes, but the
age-adjustment feature would then need a new divisor anyway.
