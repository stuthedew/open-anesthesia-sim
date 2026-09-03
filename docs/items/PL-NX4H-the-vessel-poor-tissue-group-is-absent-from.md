---
id: PL-NX4H
title: The vessel-poor tissue group is absent from Known limitations
priority: P2
effort: S
status: ready
classes: docs
feature: model-spec-accuracy
touches: docs/MODEL.md
added: 2026-09-01
verify: python3 tools/doc_check.py check && grep -qi 'vessel-poor' docs/MODEL.md
---

**Problem.** The reference adult carries three tissue groups — vessel-rich
6.0 L, muscle 33.0 L, fat 14.5 L — totalling 53.5 L for a 70 kg patient. Bone,
cartilage, ligament and tendon, roughly 20% of body mass at near-zero
perfusion, are not modelled. `docs/MODEL.md` does not say so anywhere: the
strings "vessel-poor", "bone" and "cartilage" appear nowhere in it, nor in
`ROADMAP.md`.

**Why it matters.** This is a documentation finding, not a modelling one, and
the brief should not be read as proposing a fourth compartment. The omission
matches the Gas Man reference simulator, whose Table 1 also carries exactly
three groups, and a compartment at near-zero perfusion takes up a negligible
quantity of agent over any case length this simulator is used to teach. The
model is right.

What is wrong is that the reader cannot tell that from the document.
`docs/MODEL.md`'s "Known limitations" list is otherwise close to exhaustive —
it names shunt, dead space, V/Q mismatch, diffusion limitation, multiple
alveolar units, compound A, hypothermia, age-dependent MAC and about twenty
more. Precisely because the list is that complete, a reader who knows Eger's
four- or five-group scheme and goes looking for the vessel-poor group finds
nothing, and an exhaustive list with a hole in it reads as an oversight rather
than as a decision. Under `CLAUDE.md`'s standard, making model limitations
visible is part of what stops polished output implying more coverage than the
model has; a limitation that is invisible is not disclosed.

**Where.** `docs/MODEL.md`, "Known limitations". Possibly one clause in
"Assumptions" as well, where "tissue volumes and flow fractions are constant"
already sits and where the 53.5 L against 70 kg accounting could be stated.
No other file.

**Approach.** One bullet, in the voice of the surrounding list. It should say
what is absent (a vessel-poor group: bone, cartilage, ligament, tendon), that
the three modelled groups sum to 53.5 L of a 70 kg body, that the omission
follows the Gas Man reference structure, and that the group's near-zero
perfusion makes its effect negligible over realistic case lengths — so a
reader meets a decision rather than a gap.

Do not add a fourth compartment. Do not change a tissue volume, a perfusion
fraction, or any other modelled value; this item touches documentation only.

**Found.** External multi-domain review, relayed by the project owner
2026-09-01. The tissue volumes, the 53.5 L total, and the absence of any
vessel-poor mention from `docs/MODEL.md` and `ROADMAP.md` were confirmed
against the tree in this session; Gas Man's three-group structure was
confirmed against De Wolf et al. 2012 Table 1 (PMC3502091,
https://doi.org/10.1186/1471-2253-12-22).

**Stronger citation available, added 2026-09-03.** The brief justifies the
omission by matching Gas Man. A primary-literature justification exists and is
better, because it is the argument made by the author who defined the groups:
Eger's four-compartment model carries the vessel-poor group, and his
five-compartment model deletes it — "the VPG is deleted because its
contribution to uptake is considered insignificant" — while adding a lung and
an intertissue-diffusion compartment (Carpenter RL, Eger EI, Johnson BH, et al.
Pharmacokinetics of inhaled anesthetics in humans. Anesth Analg
1986;65:575-582). Reported in Hendrickx JFA, De Wolf A. Special aspects of
pharmacokinetics of inhalation anesthesia. In: Schuttler J, Schwilden H (eds).
Modern Anesthetics. Handbook of Experimental Pharmacology 182. Springer, 2008,
p. 163. The three modelled groups therefore match Eger's own 5C structure minus
its lung and intertissue compartments, rather than merely matching a simulator.

The same chapter (p. 165) also supplies a citable uncertainty statement for the
partition coefficients: "Tissue solubilities vary up to 150% between authors
(Yasuda et al. 1989), and the tissue homogenates used to determine these
coefficients may not represent in vivo conditions."

**Done when.** `docs/MODEL.md`'s "Known limitations" names the absent
vessel-poor group with the reason it is absent and why the omission is
tolerable, `python3 tools/doc_check.py check` passes, and no modelled value
changed.
