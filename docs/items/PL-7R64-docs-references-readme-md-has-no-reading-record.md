---
id: PL-7R64
title: docs/references/README.md has no reading record for Hendrickx and De Wolf pp. 161-162, 167, 169 and 171, which docs/VERIFICATION.md cites for the model's symbols
priority: P2
effort: S
status: ready
classes: defect
feature: references-structure
touches: docs/references/README.md
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-22
payoff: each page cited for the model symbols has a reading record, so a citation cannot be mistaken for one taken from memory
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
