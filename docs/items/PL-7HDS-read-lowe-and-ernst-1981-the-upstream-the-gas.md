---
id: PL-7HDS
title: Read Lowe and Ernst 1981, the upstream the Gas Man Workbook names for its volume and flow values
priority: P1
effort: M
status: done
classes: science, docs
feature: model-spec-accuracy
milestone: v0.4.10
touches: src/anesthesia_sim/data/patients/reference_adult.json, docs/MODEL.md
added: 2026-09-06
closed: 2026-09-08
pr: 465
not-delegable: No command can prove that a person opened a 1981 Williams and Wilkins monograph, and no session can do the opening. Every route this container has was tried on 2026-09-06 and refused, and the book was reached on 2026-09-08 by interlibrary loan through the project owner's institution - which is exactly the step no command could have taken. A `verify:` command here could only check that some sentence had been written into the data file, which is exactly the thing that must not be gameable on a provenance item.
---

**Problem.** The Gas Man Workbook's Model Parameters table (Appendix B, page
168), read at the source 2026-09-06, carries this note under it:

> Values for volume, flow and relative flow are taken from Lowe and Ernst, 1981

Its reference 23 is *Lowe HJ, Ernst EA. The Quantitative Practice of
Anesthesia: Use of Closed Circuit. Baltimore: Williams & Wilkins; 1981* - the
bibliography prints the first initial as `HF` there and as `HJ` at references
22 and 24, so the entry is internally inconsistent and `HJ` is the reading
taken.

That is the upstream for seven of this file's eleven stored values, and it has
not been read. Whether the book reports those volumes and flows as
measurements, derives them, or reproduces them from somewhere else again is
unknown.

**Why it matters.** This is the second link in the only provenance chain the
reference patient has, and it is the one that decides whether the chain ends in
a measurement or in another compilation. Until it is read, `docs/MODEL.md`'s
source hierarchy cannot place it: a monograph on closed-circuit practice could
be tier 1 for a value it measured, tier 2 for one it collected, and the file
must not guess which.

**This replaces a wrong guess, which is the reason to be careful with it.**
Until 2026-09-06 this file named Mapleson's 1963, 1964 and 1973 papers as "the
primary lineage" - on the strength of their titles, never having been opened.
`PL-6Q8N` removed that framing, and the Workbook turns out to attribute nothing
to Mapleson. Recording Lowe and Ernst as read, or as tier 1, before anybody has
opened it would be the identical error one citation later.

**What was established on 2026-09-06, at one remove.** The project owner
supplied two peer-reviewed papers that used the book; both were read at
full-text depth and both are now `sources` entries in the data file. They
narrow the question sharply without answering it.

- **The initial is `HJ`.** Both papers cite `Lowe HJ, Ernst EA`, and PubMed
  indexes this author as `Lowe H J` on every closed-circuit paper from 1968 to
  1994. The Workbook's `HF` is a misprint.
- **The book gives this material as fractions**, not as measured quantities:
  Lerou and Booij's Table 6 (*Br J Anaesth* 2001;86:12-28) prints eight
  body-compartment volumes as fractions of body mass and blood flows as
  fractions of cardiac output, captioned as data given by Lowe and Ernst and
  cited to **page 57**. Their Table 5 cites the book again at **page 83**.
  Couto da Silva, Mapleson and Vickers (*Br J Anaesth* 1997;79:103-12) cite it
  for a cardiac output of 0.2 x M^(3/4), which is 4.84 L/min at 70 kg.
- **The Workbook's attribution has been checked for the first time, and it
  holds for two of the seven.** Vessel-rich volume and perfusion fraction
  reproduce exactly from Lerou and Booij's table at 70 kg (6.02 kg, 0.760);
  muscle and fat do not, under any grouping of the eight compartments; alveolar
  volume is untouched by either paper.

None of that is a reading of the book, so the tier is still unassigned, and
nothing has been promoted or adopted. Two findings that fell out of it are
filed separately: `PL-YKSM` (the allometric cardiac output against the stored
fixed 5.0) and `PL-8ZJQ` (a published blood-pool structure for `PL-3YZW`).

**Reachability, and why the last step is not delegable.** Tried 2026-09-06 from
a session container and refused at every route: direct HTTPS to `archive.org`,
`babel.hathitrust.org`, `catalog.hathitrust.org`, `openlibrary.org`,
`books.google.com` and `scholar.google.com` each returned `CONNECT tunnel
failed, response 403` from the egress proxy; `WebFetch` returned
`EGRESS_BLOCKED` for the same hosts; and PubMed holds no record for the book,
monographs being outside what it indexes. So this needs the project owner's
institutional or library access, as the Workbook itself did. `PL-XJ5P` carries
the general gap.

What changed is the size of the ask. It began as "read a 1981 monograph" and is
now **page 57**, with page 83 next, and pages 19, 67-97, 175-179 and 215 as the
ranges da Silva and colleagues used. ISBN 0683052004 (9780683052008); a
HathiTrust catalog record is reported at
<https://catalog.hathitrust.org/Record/000103271>, surfaced by web search and
not opened from here.

**Done when.** The tier of Lowe and Ernst 1981 is established by someone who
has opened it, and for each of the seven values the book is credited with, the
file records whether the book measured it, collected it, or cites it onward -
or the file records that the book could not be reached and by whom it was
tried.

The second branch is now **partly** met: the data file and `docs/MODEL.md`
record the attempt, the routes and the date. It is deliberately not treated as
closing the item, because the attempt that failed is the one the item predicted
would fail, and closing on it would retire the question without answering it.
What remains is one page and a person with a library card.

## Outcome, 2026-09-08

**The book was opened.** The project owner supplied pages 55-60 and 82-84 as an
interlibrary-loan scan (RapidILL; lender University of Sydney Main Library,
borrower University of Wisconsin-Madison Memorial Library), the range having
been narrowed to pages 57 and 83 by the two second-hand readings this item
recorded. The scan is publisher-copyright material and this repository is
public, so it is not held here; only the reading is. `PL-GN8C` carries
recording that route in `docs/references/README.md`, where `PL-XJ5P` will want
it.

**The tier is 2, and the chain does not end at the book.** Page 56 says of
figure 4.1b, in these words: "The figure models a 100-kg patient with normal
physiologic organ volumes and blood flows (9, 19, 20, 26)." So Lowe and Ernst
collect these figures and cite them onward. Chapter 4's narrative names three
of the four as Mapleson, Smith et al. and Zwart et al.; the reference list is
outside the supplied pages, and `PL-8SDL` (identify references 9, 19, 20 and
26) carries the next link. Nothing was promoted or adopted: all seven values
the Workbook credits to the book stay tier 3 and unadopted, because reading
where Gas Man's numbers came from is not evidence that they were measured.

**Per value, which is what the Done-when asked for.**

| Stored value | What the book does |
| --- | --- |
| `tissue_groups.vessel_rich.volume_l` 6.0 | Reproduces exactly, and uniquely: kidney + heart + brain + liver = 8.6% of body weight = 6.02 L at 70 kg. Collected, not measured. |
| `tissue_groups.vessel_rich.perfusion_fraction` 0.76 | Reproduces exactly: 25 + 5 + 16 + 30 = 76% of cardiac output. Collected, not measured. |
| `tissue_groups.muscle.volume_l` 33.0 | Does not reproduce. The book's muscle row is 42.6% of body weight, 29.8 L at 70 kg. |
| `tissue_groups.muscle.perfusion_fraction` 0.18 | Does not reproduce. The book's muscle row is 13% of cardiac output. |
| `tissue_groups.fat.volume_l` 14.5 | Does not reproduce. The book's adipose row is 15.0% of body weight, 10.5 L at 70 kg. |
| `tissue_groups.fat.perfusion_fraction` 0.06 | Does not reproduce. The book's adipose row is 5% of cardiac output. |
| `alveolar_gas_volume_l` 2.5 | Is not in the book at any value: page 58 lumps the circuit volume and the patient's FRC into one ventilatory volume of "about 100 dl", and no alveolar gas volume is stated. |

The four failures are exhaustive rather than a failure to find the right
grouping: searching all 1023 non-empty groupings of the book's ten compartments
at a tolerance of half a percentage point returns exactly one grouping matching
both the stored volume and the stored flow fraction for the vessel-rich group,
and zero for muscle and zero for fat.

**Three findings fell out of it.**

1. **The model patient is 100 kg**, chosen (page 56) so that "the organ weights
   can also be read as per cent of total body weight". That is why the material
   reaches this project as fractions, and it means Lerou and Booij's Table 6 is
   the book's own table divided by 100 rather than a normalization of theirs.
   Their report was checked against the document and is faithful in every
   figure, including their eight-compartment lumping, which is the book's own
   in chapter 5.
2. **The allometric cardiac output is confirmed at the source.** Page 59 gives
   it as 2 kg^(3/4) dl/min, "or 63.25 dl" for the 100 kg patient - so 0.2 x
   M^(3/4) L/min, 4.84 L/min at 70 kg against the stored 5.0. The book's own
   worked 63.25 dl fixes the exponent independently of reading a superscript
   off a scan, and two further figures inside the book agree with it.
   `PL-YKSM` carries the decision that poses.
3. **What Gas Man kept was the split, not the values.** The book's five
   non-vessel-rich compartments take 24% of cardiac output and the stored
   muscle and fat fractions sum to exactly 0.24, over a tissue volume 11.0 L
   smaller at 70 kg. That is this project's arithmetic and it convicts nobody.

**Where it is recorded.** `src/anesthesia_sim/data/patients/reference_adult.json`
gains a `sources` entry for the book - its first, deliberately withheld while it
was unread - and `docs/MODEL.md`'s "Parameter provenance" replaces its
"read at one remove, and is still not opened" paragraphs with the reading.
