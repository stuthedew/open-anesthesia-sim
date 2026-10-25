---
id: PL-VPF8
title: Re-read Baker and Farmery 2011 Table 2 (p. 572) once the review is in the private reference corpus, and confirm or correct the cross-check docs/MODEL.md's Parameter provenance cites from the 2026-09-03 reading, including desflurane fat printed as 30.9 where 30.9524 rounds to 31.0
status: untriaged
touches: docs/MODEL.md
added: 2026-10-25
---

**Problem.** Re-read Baker and Farmery 2011 Table 2 (p. 572) once the review is in the private reference corpus, and confirm or correct the cross-check docs/MODEL.md's Parameter provenance cites from the 2026-09-03 reading, including desflurane fat printed as 30.9 where 30.9524 rounds to 31.0

**Why.** `PL-H536` (the published cross-check for the tissue:blood division)
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
