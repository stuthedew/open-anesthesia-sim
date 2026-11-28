---
id: PL-7R64
title: docs/references/README.md has no reading record for Hendrickx and De Wolf pp. 161-162, 167, 169 and 171, which docs/VERIFICATION.md cites for the model's symbols
priority: P2
effort: S
status: done
classes: defect
feature: references-structure
touches: docs/references/README.md
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-22
closed: 2026-11-27
pr: 2335
payoff: each page cited for the model symbols has a reading record, so a citation cannot be mistaken for one taken from memory
verify: grep -qF 'Pages 161-162, 167, 169 and 171 were read on 2026-11-27' docs/references/README.md
---

**Problem.** docs/references/README.md has no reading record for Hendrickx and De Wolf pp. 161-162, 167, 169 and 171, which docs/VERIFICATION.md cites for the model's symbols

**Where.** `docs/VERIFICATION.md` cites Hendrickx and De Wolf (*Handb Exp
Pharmacol* 2008;182:159-86) at pp. 161-162, 167, 169 and 171 for the model's
symbols. The chapter's entry in `docs/references/README.md` records reading
pp. 163 and 165-66 only.

**Why it matters.** `.claude/rules/citing-sources.md` requires each citation
to name the route and depth of the reading. A citation of pages with no
reading record cannot be told apart from one taken from memory.

**Fix.** Read those pages from the private reference corpus, add the reading
record and an extraction note as `docs/references/README.md` describes, or
narrow the citation to the pages that were read.

**Found by** the worker building `PL-R3J6`, 2026-11-22.

**Done when.** `docs/references/README.md` records a reading of each page `docs/VERIFICATION.md` cites from Hendrickx and De Wolf, with its route and date, or the citation names only pages that were read.

**Generator check.** A one-off: a citation moved into `docs/VERIFICATION.md` from older text whose reading record was not carried with it.

**Reproduced 2026-11-23.** The chapter's entry in `docs/references/README.md` records pages 163 and 166 and the machine survey's pages, and none of 161-162, 167, 169 or 171.

**Read 2026-11-27.** Pages 161-162, 167, 169 and 171, with pp. 159-173 around them, were read in the private corpus's text layer of `modern_anesthetics/03_Part_II_Ch1-3` (`text/modern_anesthetics/03_Part_II_Ch1-3.txt`, printed pages marked in the dump). Each page supports what `docs/MODEL.md` § "Units and symbols" and `docs/VERIFICATION.md` § "Symbols" cite it for: p. 161 defines $`F_D`$ at the common gas outlet, $`F_I`$ in the inspiratory limb and $`F_A`$ as the end-expired concentration; p. 162 says rebreathing below minute ventilation makes $`F_I`$ differ from $`F_D`$; p. 167 calls the $`F_A/F_I`$ curve "of great didactic value"; p. 169 attributes the $`F_D`$-$`F_I`$ discrepancy to rebreathing; p. 171 gives $`F_I - F_A`$ as uptake divided by alveolar minute ventilation. So no citation was narrowed. The reading record is now in `docs/references/README.md` § "Schüttler & Schwilden 2008 — *Modern Anesthetics*". Docs checked: that section, `docs/MODEL.md` § "Units and symbols" and `docs/VERIFICATION.md` § "Symbols", which cite the same pages for the same claims.
