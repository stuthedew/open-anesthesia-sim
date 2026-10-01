---
id: PL-M9R6
title: tools/doc_check.py check_tag_span_covers_its_notes tests the release notes for pull request #N as a substring, so #12 is covered by a note naming #123 and the check passes while the span it stands for is uncovered
status: untriaged
feature: recorded-not-inferred
added: 2026-10-01
---

**Problem.** tools/doc_check.py check_tag_span_covers_its_notes tests the release notes for pull request #N as a substring, so #12 is covered by a note naming #123 and the check passes while the span it stands for is uncovered

**Recorded alternative, from the 2026-10-01 survey.** Read the exact `— #N` token the notes already write (`release.REFERENCED_RE`) instead of testing for a substring; `PL-JLYG` names the function for a different defect. Shape C: a hard check deciding coverage from wording.
