---
id: PL-L46W
title: Obtain and read the Dräger Vapor 2000 sevoflurane specification and Kelly and Kong 2011's full text, which no route reached on 2026-10-17, and type their locators into the test that pins the sevoflurane and isoflurane vaporizer maxima
priority: P3
effort: S
status: ready
classes: test, docs
touches: tests/unit/test_parameters.py
added: 2026-10-17
payoff: every vaporizer maximum is pinned by a test whose comment names the page that states it, so none of the three repeats only the data file's own quotation of its source
verify: ! grep -q 'was not checked here' tests/unit/test_parameters.py && ! grep -q 'specification itself was not read' tests/unit/test_parameters.py
---

**Problem.** Obtain and read the Dräger Vapor 2000 sevoflurane specification and Kelly and Kong 2011's full text, which no route reached on 2026-10-17, and type their locators into the test that pins the sevoflurane and isoflurane vaporizer maxima

The reading needs the project owner. Neither document could be reached from
the container, so this item waits on the project owner adding them to the
private references corpus, or on a route that reaches them.

**Evidence.** `test_vaporizer_maximum_matches_its_cited_specification` in
`tests/unit/test_parameters.py` (`PL-FY35`) pins each agent's
`max_delivered_concentration_percent` beside its source. Only desflurane's
18% was read at its source, in the abstract of Johnston et al. 1994 (PMID
8067562). The other two pins rest on the agent files' own source entries:

- Sevoflurane's 8% cites a "Drager Vapor 2000 Sevoflurane vaporizer
  specification: calibrated concentration range 0.2-8%", at a distributor's
  page on zurichcorp.com. On 2026-10-17 the egress gateway refused that host
  and www.draeger.com at CONNECT. A web search named Dräger's own data sheet,
  "Vapor 2000 and D-Vapor" (document pi 102223), but a search summary is not a
  reading. Two readings in the corpus agree with 8%: the Workbook for Gas Man,
  printed page 82, and Hendrickx and De Wolf in Modern Anesthetics, page 171.
- Isoflurane's 5% cites Kelly JM, Kong K-L, Anaesthesia 2011;66(8):682-688
  (PMID 21749341). The source entry reads it as both studied vaporizers being
  calibrated 0-5%. The abstract names the Penlon Sigma Delta and the
  Datex-Ohmeda Isotec 5 but not their scale. The full text is not in PubMed
  Central, and the publisher answered 403 on 2026-10-17.

**Why it matters.** The maximum bounds the delivered-concentration control a
learner turns. Two of the three pins repeat the data file's own quotation of
its source, and `.claude/rules/test-oracles.md` rule 3 says such a pin cannot
catch a value that was wrong when it was stored. Nothing suggests either value
is wrong; this is a gap in traceability, not a known error.

**Done when.** Both documents have been read, and each pin's comment names the
page, table or section that states the value, in place of the comments that
say the source was not read or not checked. If a source does not state the
stored value, that is a finding against the data file instead. Reading Dräger's
own data sheet may also show that `sevoflurane.json` should cite it rather
than a distributor's page; that change would add the data file to `touches`.
