---
id: PL-KQF4
title: Sessions cite papers they read only in abstract: CLAUDE.md asks only that a session say what it read (full text, abstract or index record), and the owner asked on 2026-11-24 that a cited paper's full text be read
status: done
feature: provenance
added: 2026-11-24
closed: 2026-11-24
pr: 2319
filed-pr: 2318
verify: grep -qF 'For a paper, read the full text, not only the abstract' CLAUDE.md
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


**Built, 2026-11-24.** `CLAUDE.md` § "Proactive expert review and domain best
practices" now says to read a paper's full text before citing it, and, where
none can be reached, to say which paper, that only its abstract or index
record was read, and what was tried, and to rest no recommendation on it
alone. The change adds 213 characters to the files loaded at launch, which
come to 53,886 against the cap of 55,120. `docs/resident-instructions.md`
§ "Never cite a source from memory, added 2026-11-10" records it.

Files checked for the old wording: `CLAUDE.md`, `docs/resident-instructions.md`
and `.claude/rules/citing-sources.md`. The rule file already says that a
paywalled article "yields the abstract and no more, so an assertion that needs
the methods section cannot be made from it". That agrees with the new
sentence, so the rule file needed no change.
