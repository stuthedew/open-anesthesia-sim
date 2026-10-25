---
id: PL-VPF8
title: Re-read Baker and Farmery 2011 Table 2 (p. 572) once the review is in the private reference corpus, and confirm or correct the cross-check docs/MODEL.md's Parameter provenance cites from the 2026-09-03 reading, including desflurane fat printed as 30.9 where 30.9524 rounds to 31.0
priority: P2
effort: S
status: done
classes: docs
feature: model-spec-accuracy
touches: docs/MODEL.md, docs/references/README.md
added: 2026-10-25
closed: 2026-10-25
payoff: The published check on the tissue:blood division rests on a reading anyone can repeat, and the text says how far a second published set of coefficients differs.
verify: grep -qF 'Fiserova-Bergerova and Diaz' docs/MODEL.md && ! grep -qF "Baker's figures have not been re-read" docs/MODEL.md
---

**Problem.** Re-read Baker and Farmery 2011 Table 2 (p. 572) once the review is in the private reference corpus, and confirm or correct the cross-check docs/MODEL.md's Parameter provenance cites from the 2026-09-03 reading, including desflurane fat printed as 30.9 where 30.9524 rounds to 31.0

**Why it matters.** A cross-check is only worth citing if a reader can repeat it.
`PL-H536` (the published cross-check for the tissue:blood division)
cites Baker and Farmery's Table 2 from the reading recorded in that item on
2026-09-03, from a copy the project owner supplied. On 2026-10-25 no copy was
reachable: this repository's history never held it, the private reference
corpus does not hold it, PubMed has no full text (PMID 23737195), and
onlinelibrary.wiley.com answered 403 to an unattended client after the tunnel
opened, which is the publisher's block and not the gateway's.

**What it needs.** The project owner adds the review's PDF to
`stuthedew/open-anesthesia-sim-references`. A session then reads Table 2,
checks the nine tissue:blood figures and three blood:gas figures that
`docs/MODEL.md` § "Parameter provenance" sets beside the derived rows, and
either changes "recorded on 2026-09-03" to a fresh reading or corrects the
table. It also checks whether Baker prints desflurane's fat coefficient as
30.9, and whether the Fiserova-Bergerova column gives sevoflurane fat 71.7,
which the brief of `PL-H536` recorded and the shipped text does not use.

**Done when.** The paragraph names a reading of the source at full text with
its date, and `python3 tools/doc_check.py check` passes.

**Done 2026-10-25.** The project owner added the review to the private corpus
the same day, and Table 2 (p. 572) was read from the page image. All nine
tissue:blood figures and all three blood:gas figures match the 2026-09-03
reading, desflurane fat included (printed 30.9). Two things changed in
`docs/MODEL.md`. The matching figures are the table's bracketed set, which
footnote d attributes to Eger and Shafer 2005, a tutorial that ran in Gas Man
according to its abstract. The plain set, from Fiserova-Bergerova and Diaz
1986, differs widely (sevoflurane fat 71.7 against 52.3, isoflurane muscle 1.71
against 3.46). According to its PubMed abstract, that paper measured only
water-soluble solvents and fitted equations to predict the rest. So § "Known
limitations" now names it as a third set that does not reproduce the stored
brain and fat values and may be a prediction. This brief's claim that the public
repository never held the review was wrong. `docs/references/README.md`
records a copy removed on 2026-09-06, which the 2026-10-25 search of the
history did not find.
