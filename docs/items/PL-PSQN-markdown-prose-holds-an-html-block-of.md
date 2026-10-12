---
id: PL-PSQN
title: markdown.PROSE holds an HTML block of CommonMark § 4.6's kinds 6 and 7 - a details or div block, whose raw lines GitHub renders until a blank line ends it - as a literal, so a sentence written on those lines (a host refusal with no date, a Tags exception) is read by no prose reader; latent
priority: P3
effort: S
status: dropped
classes: defect
touches: subprojects/docket/src/docket/markdown.py, tools/doc_check.py
added: 2026-10-12
closed: 2026-10-12
reason: markdown.PROSE is the one record of which block is prose and CommonMark parses no inline Markdown in an HTML block, so a sentence on a details block's raw lines is its writer's to move into a paragraph; latent, one closed brief quotes the form
---

**Problem.** markdown.PROSE holds an HTML block of CommonMark § 4.6's kinds 6 and 7 - a details or div block, whose raw lines GitHub renders until a blank line ends it - as a literal, so a sentence written on those lines (a host refusal with no date, a Tags exception) is read by no prose reader; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep**, as the other direction of
`PL-2B0B`, whose reproduction records that `_undated_host_claims` reads no
`details` block GitHub does render; filed on its own by the second workflow
decision batch on 2026-10-12, when `PL-2B0B`'s decision narrowed that item to
readers that read too much. CommonMark 0.31.2 § 4.6 ends an HTML block of
kinds 6 and 7 at a blank line, and GitHub renders the raw lines of a `details`
or `div` block as HTML, so a sentence written on those lines is on the page;
`markdown.PROSE` (`subprojects/docket/src/docket/markdown.py`) holds every HTML
block literal, so no prose reader in `tools/doc_check.py` reads it.

**Dropped 2026-10-12, at filing.** `markdown.PROSE` is the one record of which
block is prose, and CommonMark parses no inline Markdown in any HTML block, so
a sentence on those lines is not prose by the grammar the record follows: it
is its writer's to move into a paragraph, which a blank line after the opening
tag makes it. A per-reader reading of a block kind would be the second list
`PL-KR6M` retired. Latent, and counted: one tracked Markdown file opens such a
block, `PL-KR6M`'s own closed brief, quoting the form. Refiled if one is met
live.

**Generator check.** An instance of `PL-KR6M`'s fact met in the opposite
direction and found by reading rather than live, so the head stays spent on
its own terms, which reopen it for a member found live.
