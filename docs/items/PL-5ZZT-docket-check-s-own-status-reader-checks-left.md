---
id: PL-5ZZT
title: docket check's own-status reader, checks._left_statuses, matches OWN_STATUS over the whole brief rather than a statement at a time, so a status phrase inside a fence, or one whose words straddle a heading and the paragraph under it, is advised on as the item's own claim about its status; latent
status: untriaged
feature: one-answer
added: 2026-10-06
---

**Problem.** docket check's own-status reader, checks._left_statuses, matches OWN_STATUS over the whole brief rather than a statement at a time, so a status phrase inside a fence, or one whose words straddle a heading and the paragraph under it, is advised on as the item's own claim about its status; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`checks.py`. `_left_statuses` runs `OWN_STATUS.finditer` over `item.body`
whole. It is the one brief-prose reader in `checks.py` that does: every other
reads statement by statement through `_statements`, which also leaves fences
out. A fence's content is literal (CommonMark 0.31.2 § 4.5), an ATX heading is
one line (§ 4.2), and a paragraph ends at a blank line (§ 4.8), so the
pattern's `\s+` between its two words crosses a block's end.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against markdown-it-py 4.2.0. Two briefs at `ready`. The first quotes a capture
template in a fence, a line saying the item is left at the `needs-decision`
status until the owner answers, written with the two words together. The
second has a heading reading `What remains`, a blank line, and a paragraph
opening `Untriaged captures go to the next pass.`. `_left_statuses` advised that
the first brief says it is at `needs-decision`, and the second that it is at
`untriaged`, the last word of the heading and the first of the paragraph read as
one phrase. markdown-it puts the first phrase in a fence and the second's words
in two blocks, and `OWN_STATUS` over `_statements`' spans finds nothing in
either; the same phrase wrapped inside one paragraph is still found. Latent:
reading every tracked item whole and by statement gives the same advisories.
`PL-20PT`'s brief already quotes front matter in a fence, which is the shape.

**Generator check.** A member of `PL-R417`: a reader matches a phrase across
the end of the statement it stands in. `PL-2GY0`, open, is this reader's other
fault (reading the word in its sense of departing), a different fact.

**Done when.** `_left_statuses` reads through `_statements`, as
`_prerequisite_matches` does, pinned by a `left statuses, ` case in
`PL-R417`'s guard for the fence and the heading, each failing on today's
reader.
