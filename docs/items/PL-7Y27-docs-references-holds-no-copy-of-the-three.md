---
id: PL-7Y27
title: docs/references/ holds no copy of the three vaporizer sources PL-5K5C wrote into docs/MODEL.md, so the numbers taken from their full texts cannot be re-checked
priority: P2
effort: S
status: done
closed: 2026-09-08
classes: docs
feature: provenance
touches: docs/MODEL.md
added: 2026-09-07
verify: python3 tools/doc_check.py check && grep -qF 'owner-attested rather than checkable' docs/MODEL.md
---

**Problem.** `docs/references/` holds no copy of the three vaporizer sources
`PL-5K5C` wrote into `docs/MODEL.md`, so the numbers taken from their full
texts cannot be re-checked.

**What the gap was.** `PL-5K5C` (record the model's sea-level assumption and
the vaporizer-class dependence of the delivered-concentration dial) put four
figures into `docs/MODEL.md` § "Known limitations" that came from full texts
this repository does not hold:

- the Tec 6 sump temperature of about 39 °C and desflurane's vapour pressure
  there of about 1460 mmHg, from Weiskopf, Sampson and Moore 1994. The PubMed
  abstract carries neither; it confirms the ±15% output accuracy in oxygen and
  nothing else the document relied on;
- the Datex-Ohmeda *Tec 6 Plus* passage quoted verbatim in that section, and
  the 1–18% concentration range beside it, from a manufacturer specification
  sheet (AN3307-A/1100) that is not a published paper and has no PubMed record
  at all;
- Boumphrey and Marshall's worked example — isoflurane dialled 2% at 101.3 kPa
  delivering 4.05% at 50 kPa — which is internally checkable arithmetic but
  whose attribution is not.

All three had been supplied by the project owner and read in full on
2026-09-06, and both the item and the document recorded that. What neither
could supply was a later session's ability to *check* one.

**Why it mattered, and why it was small.** Nothing stored took its authority
from any of them — `PL-5K5C` deliberately stored no number, and the section
says so — so no data file, equation or displayed value was at risk. What was
at risk was the prose: a future session revising that section, or implementing
ambient pressure, had a figure it could not verify and a quotation it could not
confirm was verbatim.

**What settled it, and how the disposition narrowed to one.** The item was
filed proposing two routes: add the full texts to `docs/references/`, or record
per source which sentences rest on an unheld text. **The first is not
available.** `docs/references/README.md` § "Redistribution" states that the
repository is public and a file placed there is redistributed rather than read
privately; `PL-SHG5` removed two publisher-copyright full texts on 2026-09-06
for exactly that reason. *Br J Anaesth* 1994;72:474-479 has no PMC record and
is not open access (checked against PubMed 2026-09-07), and the same bar
applies to the Boumphrey and Marshall article; the Datex-Ohmeda sheet carries
its own copyright line. So the second route was the only one, and it is what
was done.

**And the Weiskopf half resolved differently.** The project owner supplied the
full text again on 2026-09-08 and it was read in this session. Both figures are
the paper's own and are stated twice: *"to heat desflurane to a constant
temperature of approximately 39 °C, thus providing a constant vapour pressure
of approximately 1460 mm Hg"*, and again for the regulator, *"the pressure of
desflurane vapour (1460 mm Hg) leaving the sump"*. The paper also carries the
22.8 °C boiling point and the ±15% relative / ±0.5% absolute accuracy, and it
says nothing about ambient pressure or altitude — so it is not, and is no
longer implied to be, the source for the altitude behaviour. The hedge
`PL-5K5C` had written for want of the source (*"close to two atmospheres"*) is
gone, and the sentence now also records why 39 °C was the temperature chosen:
the resulting pressure clears the vaporizer's own internal resistances.

**Done when.** `docs/MODEL.md`'s sources block marks the Datex-Ohmeda sheet and
the Boumphrey and Marshall article **owner-attested**, with a note saying what
that means, why `docs/references/` cannot hold them, and which specific claims
rest on that reading alone — and the three journal articles are distinguished
from them as reachable by any reader through a DOI or PMID.

**Found by.** `PL-5K5C`, 2026-09-07, while writing the sources block those
notes carry.
