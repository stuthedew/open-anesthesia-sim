---
id: PL-8SDL
title: Identify Lowe and Ernst's references 9, 19, 20 and 26, the upstream the book itself cites for the reference patient's volumes and flows
priority: P1
effort: S
status: done
classes: science, docs
feature: model-spec-accuracy
touches: docs/MODEL.md
added: 2026-09-08
closed: 2026-09-10
verify: python3 tools/doc_check.py check && grep -qF 'Report of Committee II on Permissible Dose' docs/MODEL.md
---

**Problem.** Identify Lowe and Ernst's references 9, 19, 20 and 26, the upstream the book itself cites for the reference patient's volumes and flows (`PL-7HDS`, 2026-09-08).

Page 56 of *The Quantitative Practice of Anesthesia* says of figure 4.1b, the
table the Gas Man Workbook credits for its volume and flow values: "The figure
models a 100-kg patient with normal physiologic organ volumes and blood flows
(9, 19, 20, 26)." The book therefore collects those figures rather than
measuring them, which is what makes it tier 2 - and the four references are the
next link in the only provenance chain the reference patient has.

Chapter 4's own narrative on page 55 names three of the four in passing, as
authors of compartmental or multiple-model uptake models: **9 Mapleson**, **19
Smith et al.**, **20 Zwart et al.** Reference **26 is named nowhere in the
pages supplied** (55-60 and 82-84), and chapter 4's reference list is outside
them, so none of the four has a full citation yet.

**Why it matters.** `docs/MODEL.md`'s source hierarchy places a value by what
its authority did, and every stored physiologic parameter in
`reference_adult.json` is currently tier 3 with no primary measurement adopted
for any of them. This is the shortest remaining route to finding out whether a
primary measurement exists at all: if one of these four measured the organ
volumes and flows, the reference patient has a tier-1 source it has never had;
if all four are models like the book, the chain is a compilation of
compilations and the `provenance_gap` should say so in those terms.

**What it needs.** Chapter 4's reference list - roughly pages 60-62 of the same
monograph, immediately after the pages already supplied - reached the same way
the rest was. Then each of the four resolved to a citation and read far enough
to say whether it measured these quantities.

**Not delegable in its first step**, for the same reason `PL-7HDS` was not: the
egress proxy refuses the Internet Archive, HathiTrust, Open Library and Google
Books, and PubMed does not index monographs. Once the four citations are in
hand, the papers themselves may well be reachable through the PubMed MCP
server, which is a different and cheaper problem.


## Outcome, 2026-09-10: all four are identified, and three of them are models

**The pages arrived.** The project owner supplied pages 17–21 and 60–66 as a
second interlibrary-loan scan (RapidILL; lender Michigan State University Main
Library, borrower University of Wisconsin–Madison Memorial Library, processed
2026-09-08), the range having been named by this item — "roughly pages 60–62,
immediately after the pages already supplied" — and by `PL-YKSM`, which asked
for 17–21. Chapter 4's reference list is on pages **64–65**, so the ask was
right and one page short. The scan is publisher-copyright material and this
repository is public, so it is not held here; only the reading is.

**The four references, transcribed from page 64 and page 65 and then checked
against PubMed** (metadata only; none of the three has an abstract or a PMC
record, so none was read beyond its record):

| # | As the book prints it | PubMed |
| --- | --- | --- |
| 9 | Mapleson, W.W. An electrical analogue for the uptake and exchange of inert gases and other agents. *J Appl Physiol* 18:197, 1963. | PMID 13932730, `10.1152/jappl.1963.18.1.197`, 18:197–204 |
| 19 | Smith, N.T., Zwart, A., and Beneken, J.W. Interaction between the circulatory effects and the uptake and distribution of halothane: Use of a multiple model. *Anesthesiology* 37:47, 1972. | PMID 5050101, `10.1097/00000542-197207000-00008`, 37(1):47–58 |
| 20 | Zwart, A., Smith, N.T., and Beneken, J.W. Multiple model approach to uptake and distribution of halothane: The use of an analog computer. *Comput Biomed Res* 5:228, 1972. | PMID 5031801, `10.1016/0010-4809(72)90084-5`, 5(3):228–38 |
| 26 | *Recommendations of the International Commission on Radiological Protection*, p. 151. Report of Committee II on Permissible Dose for Internal Radiation. Pergamon Press, Oxford, 1960. | not indexed — a monograph |

Two transcription differences, recorded because this chain has already been
bent once by a misprint (the Workbook's `HF` for `HJ`, `PL-7HDS`). PubMed
titles reference 9 as "An electric analogue for uptake and exchange of inert
gases and other agents" — *electric*, and no *the*. And the book prints
**Beneken, J.W.** where PubMed indexes **Beneken J E** on both 1972 papers;
`JE` is the reading taken, on the same grounds as `HJ` — two independent
records against one.

**Three of the four are uptake-and-distribution models, which is what this
item was asking.** Reference 9 is Mapleson's electric analogue; 19 and 20 are
the Smith–Zwart–Beneken multiple model in its two 1972 write-ups. A model
*consumes* organ volumes and blood flows; it does not measure them. So they
cannot be where figure 4.1b's figures were measured, and the honest reading of
page 56's citation is that Lowe and Ernst are naming the modelling tradition
they are working in as much as sourcing a table.

**Reference 26 is the one that could hold a measurement, and it is the only
one.** ICRP Committee II's permissible-dose report is a radiological-protection
reference document, not an anesthetic model, and Lowe and Ernst cite it to a
single page — 151 — which is the narrowing that made the last loan cheap enough
to place. Nothing in this item claims what is on that page: it has not been
read, and asserting that a 1960 ICRP report tabulates standard organ masses
would be the same error as the Mapleson guess `PL-6Q8N` removed.

**Mapleson is back in the chain, one link further up, and that does not
vindicate the guess that was removed.** Until 2026-09-06 `docs/MODEL.md` named
Mapleson's papers as the reference patient's "primary lineage" on the strength
of their titles. That was wrong about *the Workbook*, which attributes nothing
to Mapleson, and it stays wrong. What is true is narrower and arrives from a
different direction: the book the Workbook does cite names Mapleson 1963 as one
of four sources for a table it collected. A guess that lands near a fact it had
no evidence for is still a guess, and the distinction is the whole point of the
source hierarchy.

**Where it is recorded.** `docs/MODEL.md`'s "Parameter provenance" replaces the
sentence saying chapter 4's reference list is outside the pages supplied.

**What remains is a different item**, because it needs four sources this
container cannot reach: `PL-LT51` (obtain and read Lowe and Ernst's four
upstream references, starting with ICRP Committee II page 151). Every route
this container has was tried again on 2026-09-10 and refused - `www.icrp.org`,
`journals.sagepub.com` and `doi.org` each returned no response through the
egress proxy -
and PubMed holds no abstract and no PMC record for any of the three papers, so
their records are the whole of what is reachable from here.

**The `verify:` command was run both ways before it was recorded**, per
`.claude/skills/docket/SKILL.md`: exit 1 against the tree before this item's
edit (the string is absent from `docs/MODEL.md` on `origin/main`) and exit 0
after it. The needle is one line of the document rather than the full citation,
because the citation wraps in the bullet that carries it and `grep -F` is
line-based.

