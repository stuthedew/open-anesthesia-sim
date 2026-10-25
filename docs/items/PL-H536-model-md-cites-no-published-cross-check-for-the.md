---
id: PL-H536
title: MODEL.md cites no published cross-check for the derived tissue:blood coefficients, though Baker and Farmery Table 2 tabulates all nine to the printed precision
priority: P2
effort: S
status: done
classes: docs
feature: model-spec-accuracy
touches: docs/MODEL.md
added: 2026-09-03
closed: 2026-10-25
verify: grep -qF 'Baker AB, Farmery AD' docs/MODEL.md && python3 tools/doc_check.py check
---

**Problem.** `docs/MODEL.md` § "Parameter provenance" derives nine tissue:blood
coefficients by dividing each stored tissue:gas value by the agent's blood:gas
value, and prints the division on each row. That transformation is currently
justified by arithmetic alone — no source is cited that publishes the *result*.

A published cross-check exists and matches exactly. Baker and Farmery's Table 2
tabulates blood-gas solubilities and tissue:blood partition coefficients for the
vessel-rich, muscle and fat groups, with an Eger and Shafer column:

| Agent | blood:gas | vessel-rich | muscle | fat |
| --- | --- | --- | --- | --- |
| Sevoflurane, this project | 0.65 | 1.69 | 3.69 | 52.31 |
| Sevoflurane, Baker Table 2 | 0.65 | 1.69 | 3.69 | 52.3 |
| Isoflurane, this project | 1.3 | 1.62 | 3.46 | 53.85 |
| Isoflurane, Baker Table 2 | 1.3 | 1.62 | 3.46 | 53.8 |
| Desflurane, this project | 0.42 | 1.29 | 2.31 | 30.95 |
| Desflurane, Baker Table 2 | 0.42 | 1.29 | 2.31 | 30.9 |

All twelve values agree to the precision Baker prints. Computed from the shipped
data files 2026-09-03.

**Why it matters.** `CLAUDE.md`'s safety-critical standard asks that numerical
implementations be validated against published reference cases or other
authoritative references wherever available, and treats covariate
transformations and unit conversions as safety-critical paths in their own
right. The tissue:gas-to-tissue:blood division is exactly such a
transformation, it feeds every tissue time constant, and a published table that
lands on the same nine numbers is the strongest evidence available that the
division is the right operation and not merely a consistent one.

Note what this does and does not establish. Baker's column is attributed to Eger
and Shafer, and this project's values reach it through Gas Man via De Wolf et
al. 2012, so the two chains are not independent in origin. What the agreement
establishes is that the project's stored primitive plus its conversion reproduce
the coefficients as the literature publishes them — a check on the
transformation and the arithmetic, not a second independent measurement. The
brief should say so rather than overclaiming.

**A second parameter set, and the uncertainty it makes concrete.** Baker's
Table 2 also carries values from Fiserova-Bergerova and Diaz that differ
substantially for the same agents — sevoflurane fat 71.7 against Eger and
Shafer's 52.3, a 37% difference; sevoflurane vessel-rich 2.17 against 1.69.
Hendrickx and De Wolf put the general case plainly: "Tissue solubilities vary up
to 150% between authors (Yasuda et al. 1989), and the tissue homogenates used to
determine these coefficients may not represent in vivo conditions."

`CLAUDE.md` requires model limitations to be visible rather than implied away by
numerical precision. A named alternative parameter set differing by 37% in the
fat compartment is the most concrete statement of that uncertainty the project
can make, and § "Known limitations" does not currently make it.

**Where.** `docs/MODEL.md` § "Parameter provenance" for the cross-check, with
the scope note above; § "Known limitations" for the between-author variation.
No data file and no modelled value changes.

**Done when.** § "Parameter provenance" cites the published cross-check and
states what it does and does not establish; § "Known limitations" names the
between-author variation with at least one quantified example;
`python3 tools/doc_check.py check` passes; no modelled value changed.

**Found.** Scoping session for planned-milestone item 29 (`core/` reads like the
domain), 2026-09-03, from references supplied by the project owner:

- Baker AB, Farmery AD. Inert gas transport in blood and tissues. Compr Physiol
  2011;1(2):569-592. https://doi.org/10.1002/cphy.c100011 (Table 2, p. 572).
- Hendrickx JFA, De Wolf A. Special aspects of pharmacokinetics of inhalation
  anesthesia. In: Schuttler J, Schwilden H (eds). Modern Anesthetics. Handbook
  of Experimental Pharmacology 182. Springer, 2008:159-186 (p. 165).

**Done 2026-10-25, with two departures from the brief.** First, Baker and
Farmery's Table 2 could not be re-read: neither this repository nor the
private reference corpus holds it, PubMed has no full text (PMID 23737195),
and the publisher refused an unattended client. So `docs/MODEL.md` cites the
2026-09-03 reading recorded above and says so. It also says that desflurane's
fat figure does not round: 30.9524 rounds to 31.0, and the brief records
Baker printing 30.9. The published statement of the operation itself is
taken from Eger and Saidman 2005, p. 1023, read in full text today. Second,
the quantified between-author example is not Baker's Fiserova-Bergerova
column, which could not be checked. It is Yasuda, Targ and Eger's own
comparison on p. 373 (kidney 115% to 150% greater, muscle 10% to 30% less,
brain and fat similar), Yasuda's own muscle spread, and Eger and Saidman's
Table 1 muscle range for sevoflurane, 1.1 to 2.4. All three were read in
full text from the private corpus.
