---
id: PL-WMCJ
title: docs/MODEL.md's Known limitations never names intertissue diffusion, the route Eger and Saidman 2005 describe for agent reaching fat, though every tissue group here exchanges only with arterial blood
priority: P1
effort: S
status: done
classes: science, docs
feature: model-spec-accuracy
touches: docs/MODEL.md, docs/references/README.md
added: 2026-09-23
closed: 2026-09-26
pr: 1135
payoff: a reader of the fat compartment learns that one published route by which agent reaches fat is not modelled, and which way leaving it out biases what the chart draws
verify: grep -qiF 'intertissue diffusion' docs/MODEL.md
---

**Problem.** docs/MODEL.md's Known limitations never names intertissue diffusion, the route Eger and Saidman 2005 describe for agent reaching fat, though every tissue group here exchanges only with arterial blood

**Found 2026-09-23 in `PL-QYBW`'s design round** (the chart's percent axis
compressing fat).

`src/anesthesia_sim/core/tissue.py` models each tissue group as exchanging
agent "with arterial blood in proportion to its own blood flow, independently
of every other tissue group". That excludes intertissue diffusion: agent
moving directly from a lean tissue into fat lying next to it. `docs/MODEL.md`
never names this, not in § "Assumptions" and not in § "Known limitations".
The list does have "diffusion limitation", which is a different mechanism.

The uptake literature names it for exactly the compartment the chart draws
near zero: "Obesity increases the depots available for storage of anesthetic,
including anesthetic that reaches fat by intertissue diffusion. Such
anesthetic returns to the circulation to delay recovery ... However, the
increased anesthetic in fat occurs at a lower partial pressure and thus might
not influence emergence materially." (Eger EI II, Saidman LJ. Illustrations of
inhaled anesthetic uptake, including intertissue diffusion to and from fat.
*Anesth Analg* 2005;100(4):1020-1033,
https://doi.org/10.1213/01.ANE.0000146961.70058.A1. Retrieved from PubMed,
PMID 15781517, and verified against the abstract 2026-09-23.) Carpenter et al.
needed a fifth compartment to fit human washout, with "a time constant that
lies between the time constants predicted for muscle and fat" (*Anesth Analg*
1986;65(6):575-82, PMID 3706798, https://doi.org/10.1213/00000539-198606000-00004;
the abstract, as read by this session's research agent, does not attribute it
to intertissue diffusion).

**Fix.** Add intertissue diffusion to § "Known limitations", saying which way
it biases fat's modelled partial pressure and amount, and with the source.
Establishing the direction and size needs more than an abstract, so check the
Eger and Saidman full text, or the private reference corpus's uptake chapters,
before writing the sentence.

**Why it matters.** The fat compartment is drawn on the chart and read by
learners reasoning about slow uptake and delayed emergence - the setting in
which the cited paper says this route matters, in obese patients and with the
more soluble agents. `docs/MODEL.md` is the one place this project states what
the model leaves out, so a limitation missing there reads as none. The
safety-critical standard asks for model limitations to be visible rather than
implied away. Classed `science` with `docs`, as `PL-7DMJ` and `PL-DZQT` were
for the same kind of gap. That class re-enters the v0.6.0 gate whenever it is
found, so it is on that gate's frozen list rather than deferred.

**Premise re-checked at triage, 2026-09-24.** `grep -niE "inter-?tissue"
docs/MODEL.md` exits 1, and `src/anesthesia_sim/core/tissue.py`'s module docstring still
says each group exchanges "independently of every other tissue group". PubMed's
record for PMID 15781517 matches the citation and the quoted abstract sentence
as filed. So does its record for PMID 3706798, including the fourth
compartment's time constant "between the time constants predicted for muscle
and fat".

**Done when.** § "Known limitations" names intertissue diffusion, its effect on
the fat compartment and its source.

## Worked 2026-09-26

**Premise re-confirmed**, then written. `docs/MODEL.md` now names the route in
§ "Assumptions" (the perfusion-limited bullet says a tissue group exchanges
agent only with its own blood) and in § "Known limitations" (a bullet beside
"diffusion limitation", which it distinguishes itself from, and a note after
the fat-perfusion note).

**The direction and size came from primary full text, not from the review.**
Eger and Saidman 2005 is in neither PubMed Central nor the private corpus, and
`journals.lww.com` is blocked from this environment, so it stays abstract-only
and nothing is sized from it. The corpus supplied what the brief asked for
instead: both Yasuda 1991 papers fit a five-compartment washout and read the
fourth compartment as fat reached by intertissue diffusion (the *Anesthesiology*
one is a scan, read as page images of pp. 493-96); the Gas Man Workbook states
the omission itself (App. B, p. 170); and Hendrickx and De Wolf's chapter
carries the interpretive caution (pp. 163, 166). The model's fat time constant
matches the fitted *fifth* compartment, so the fourth is what is missing, and
the note states three biases from that: fat holds too little agent (the
missing store is 0.9-2.2x the modelled fat group's uptake over a 0.5-4 h case),
the fat trace draws the slow fat alone, and the late washout loses the term
that dominates it from about hour 2-3 to hour 21-29.

**Carpenter 1986's DOI is not carried forward.** The brief gave
`10.1213/00000539-198606000-00004`, which PubMed's record and its ID converter
do not return, so the note cites the PMID and says PubMed records no DOI.

**Captured, not fixed here:** `PL-HBH2` (the fat-perfusion note weighs
Heinonen alone, where the Yasuda fits sit on the stored parameters),
`PL-YD2V` and `PL-KK1Q` (feature `late-washout-evidence`: the run-length
rationale does not name the missing compartment, and the model's first-day
washout has never been compared with the fits), and `PL-7LCY` (a false
refusal by the floor-interpreter guard, met in this work).
