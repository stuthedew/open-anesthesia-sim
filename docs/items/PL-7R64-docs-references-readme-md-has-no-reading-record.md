---
id: PL-7R64
title: docs/references/README.md has no reading record for Hendrickx and De Wolf pp. 161-162, 167, 169 and 171, which docs/VERIFICATION.md cites for the model's symbols
status: untriaged
feature: references-structure
touches: docs/references/README.md
added: 2026-11-22
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
