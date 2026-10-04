---
id: PL-KT0H
title: doc_check's LINK_RE takes no line ending after a link's destination, nor a title or an angle-bracket destination at all, so a link whose ) or title follows on the next line is never checked and its missing target passes; latent
status: untriaged
feature: one-answer
touches: tools/doc_check.py, tests/unit
added: 2026-10-04
---

**Problem.** doc_check's LINK_RE takes no line ending after a link's destination, nor a title or an angle-bracket destination at all, so a link whose ) or title follows on the next line is never checked and its missing target passes; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

CommonMark § 6.3: whitespace, including up to one line ending, may follow a link's destination before its title or `)`. `[the notes](docs/missing.md` over `)`, and the same with its title on the next line, give `LINK_RE` nothing where markdown-it-py 4.2.0 reads `docs/missing.md`, so `check_citations` never reports the missing file. A title on the destination's own line and a `<...>` destination are missed too; neither is a continuation, but the reading is the same pattern's. Latent: the documents' 17 relative links agree with markdown-it.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
