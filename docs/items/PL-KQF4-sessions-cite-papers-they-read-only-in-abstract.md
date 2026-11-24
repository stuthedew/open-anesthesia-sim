---
id: PL-KQF4
title: Sessions cite papers they read only in abstract: CLAUDE.md asks only that a session say what it read (full text, abstract or index record), and the owner asked on 2026-11-24 that a cited paper's full text be read
status: untriaged
feature: provenance
added: 2026-11-24
filed-pr: 2318
---

**Problem.** Sessions cite papers they read only in abstract: CLAUDE.md asks only that a session say what it read (full text, abstract or index record), and the owner asked on 2026-11-24 that a cited paper's full text be read

**What the owner said.** "If looking at paper, don't just read abstract"
(project owner, 2026-11-24, in the thread running `PL-JT1C`, while subgroup
and non-inferiority sources were being read).

**What changes.** `CLAUDE.md` § "Proactive expert review and domain best
practices" now says "Read it in this session before citing it, and say what
was read: the full text, an abstract or an index record." It should say that a
paper's full text is read before it is cited, and that where no full text can
be reached, the reply says which paper, that only its abstract or index record
was read, and what was tried, and rests no recommendation on it alone. The
PubMed tool's full-text call reaches papers in PubMed Central; a publisher's
open-access page or an author's repository is the next place to look.

**Already done.** The rule is in project memory as `read-full-text-not-abstract`.

**Done when.** `CLAUDE.md` says it, and the file still fits the cap that
`tools/doc_check.py` sets on the files loaded at launch.

