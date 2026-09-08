---
id: PL-7Y27
title: docs/references/ holds no copy of the three vaporizer sources PL-5K5C wrote into docs/MODEL.md, so the numbers taken from their full texts cannot be re-checked
status: untriaged
added: 2026-09-07
---

**Problem.** docs/references/ holds no copy of the three vaporizer sources PL-5K5C wrote into docs/MODEL.md, so the numbers taken from their full texts cannot be re-checked

**What the gap is, concretely.** `PL-5K5C` put four figures into
`docs/MODEL.md` § "Known limitations" that came from full texts this
repository does not hold:

- the Tec 6 sump temperature of about 39 °C and desflurane's vapour pressure
  there of about 1460 mmHg, from Weiskopf, Sampson and Moore 1994. The PubMed
  abstract carries neither; it confirms the ±15% output accuracy in oxygen and
  nothing else this document relies on;
- the Datex-Ohmeda *Tec 6 Plus* passage quoted verbatim in that section, and
  the 1–18% concentration range beside it, from a manufacturer specification
  sheet (AN3307-A/1100) that is not a published paper and has no PubMed record
  at all;
- Boumphrey and Marshall's worked example — isoflurane dialled 2% at 101.3 kPa
  delivering 4.05% at 50 kPa — which is internally checkable arithmetic but
  whose attribution is not.

All three were supplied by the project owner and read in full on 2026-09-06,
and the item and the document both record that. What neither can supply is a
later session's ability to *check* one: `docs/MODEL.md` § "Source hierarchy"
says `docs/references/` exists "so that a session checking a claim can read the
source instead of recalling it", and for these three the only options are to
recall or to ask the owner again.

**Why it matters, and why it is small.** Nothing stored takes its authority
from any of them — `PL-5K5C` deliberately stored no number, and the section
says so — so no data file, equation or displayed value is at risk. What is at
risk is the prose: a future session revising that section, or implementing
ambient pressure, has a figure it cannot verify and a quotation it cannot
confirm is verbatim. The 1460 mmHg figure is the sharpest case, because the
commonly quoted value for desflurane at 39 °C is nearer 1500 mmHg (about two
atmospheres) and the document currently hedges to "close to two atmospheres"
for exactly that reason. That hedge is a workaround for a missing source, not
a resolution of it.

**Two dispositions, and the second is probably right.** Either the three full
texts are added to `docs/references/` with their `README.md` rows, which is
the mechanism the project already built for this; or the Datex-Ohmeda sheet and
the Boumphrey article are held to be unredistributable and the item instead
records, per source, exactly which sentence in `docs/MODEL.md` rests on an
unheld text — so a later reader knows which claims to treat as owner-attested
rather than checkable. The copyright question is the owner's, which is why this
is filed rather than decided.

**Found by.** `PL-5K5C` (record the model's sea-level assumption and the
vaporizer-class dependence of the delivered-concentration dial), 2026-09-07,
while writing the sources block those notes carry.
