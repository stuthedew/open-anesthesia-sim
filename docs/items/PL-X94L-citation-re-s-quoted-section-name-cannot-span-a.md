---
id: PL-X94L
title: CITATION_RE's quoted section name cannot span a source line, so every citation whose section title wraps is invisible to check_citations in the documents it already reads
status: untriaged
added: 2026-09-07
---

**Problem.** CITATION_RE's quoted section name cannot span a source line, so every citation whose section title wraps is invisible to check_citations in the documents it already reads

Both branches of `CITATION_RE` (`tools/doc_check.py:264-268`) quote as
`"[^"\n]+"`, so the match stops at the first newline. This repository
hard-wraps prose at about 78 characters, so any section title long enough to
wrap is silently unexamined - `check_citations` reports success over text it
never read, which is the "gives a wrong answer silently" shape rather than a
gap in coverage. It is not confined to the queue: it applies to `CLAUDE.md`,
`ROADMAP.md`, `docs/*.md` and the rules files, all of which the check already
reads today.

Measured 2026-09-07 while working `PL-X2XX`: making the quote newline-tolerant
is what surfaces `PL-042`'s stale `docs/WORKING_NOTES.md` citation, which is
one of the two instances `PL-8B1K` was filed for and which no amount of
widening `DOC_GLOBS` reaches.

Fixing it needs a bounded, non-greedy quote and normalised whitespace before
`_cites_heading` sees the term, or a citation spanning a paragraph break will
match text that is not a title.
