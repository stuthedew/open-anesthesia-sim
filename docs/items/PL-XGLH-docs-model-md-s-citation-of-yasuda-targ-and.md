---
id: PL-XGLH
title: docs/MODEL.md's citation of Yasuda, Targ and Eger 1989 in § "Desflurane's residual, and why the parameter file was not changed" says its brain:blood values were read from the abstract on 2026-09-08, while § "Known limitations" and § "Parameter provenance" rely on the paper's p. 373 and Tables 1 and 2 in full text; check those values against the full text and record that reading beside the citation (first blind review pass on PL-52KB, 2026-11-11)
priority: P1
effort: S
status: ready
classes: science
feature: provenance
touches: docs/MODEL.md
deferred-from: v0.7.0 - not live: checked 2026-11-22 at d4e8200c: the brain:blood values are quoted only as support for leaving desflurane's coefficient unchanged, and no stored or displayed value is computed from them, so no learner can see a wrong value now
added: 2026-11-11
payoff: A clinician checking why desflurane's vessel-rich coefficient was not changed finds its supporting values read at the depth the document claims.
---

**Problem.** docs/MODEL.md's citation of Yasuda, Targ and Eger 1989 in § "Desflurane's residual, and why the parameter file was not changed" says its brain:blood values were read from the abstract on 2026-09-08, while § "Known limitations" and § "Parameter provenance" rely on the paper's p. 373 and Tables 1 and 2 in full text; check those values against the full text and record that reading beside the citation (first blind review pass on PL-52KB, 2026-11-11)

**What is known.** § "Parameter provenance" records that the 1989 paper was
read in full on 2026-09-13, five days after the abstract reading, and takes
its tissue:gas values from Table 1. Nothing records whether the brain:blood
values quoted beside the citation (desflurane 1.29 ± 0.05, isoflurane
1.57 ± 0.10, sevoflurane 1.70 ± 0.09, halothane 1.94 ± 0.17) were checked
against the full text. § "Desflurane's residual" uses them to refuse a change
to desflurane's vessel-rich coefficient, and since `PL-52KB` § "Known
limitations" points readers to that citation as the paper's full one.

**Done when.** The brain:blood values are checked against the paper's own
table in the private corpus, and the note beside the citation names that
reading and its date. A value that differs is a science finding and goes to
the project owner.

**Why it matters.** A reader checking the support for the refusal finds the
values recorded at abstract depth only, though the paper has since been read
in full.

**Checked 2026-11-22**, at `d4e8200c`. `grep -n "Read from the abstract and checked against PubMed on 2026-09-08" docs/MODEL.md` still finds the note under the Yasuda, Targ and Eger 1989 citation in § "Desflurane's residual, and why the parameter file was not changed". The brain:blood values are quoted there and in the `sources` note of `src/anesthesia_sim/data/agents/desflurane.json`. No stored coefficient is computed from them, so the stored tissue:gas values do not depend on this reading.

**Generator check.** A one-off. The misread fact is the depth at which one source was read, recorded once at abstract depth and not updated when the paper was read in full five days later. No head's `misread:` states a citation's reading depth.
