---
id: PL-LPCB
title: The document check tests a § citation against the cited document's headings only where the citation sits in a docstring with the § mark and the document named on the same line, so a citation in a # comment, a possessive such as docs/MODEL.md's note, or a bare § strands silently when a section moves or is renamed
priority: P1
effort: M
status: ready
classes: defect
feature: doc-consistency-checks
touches: tools/doc_check.py
deferred-from: v0.7.0 - a workflow check with no link to what v0.7.0 ships: it decides no value a learner sees, and the citations it strands are filed as found
added: 2026-11-22
payoff: a section move that would strand a citation fails the document check at once, instead of reaching the queue as one item per stranded citation
root-cause-of: PL-10BC, PL-GC7Z, PL-Q2DK, PL-97S1, PL-CVTG
generator: live - PL-48MX and PL-SY7G will move more sections of docs/MODEL.md and docs/INTERFACE.md, and every move strands the citations the check cannot read
misread: Which heading of which document a § citation in a comment, possessive or bare § names
---

**Problem.** The document check tests a § citation against the cited document's headings only where the citation sits in a docstring with the § mark and the document named on the same line, so a citation in a # comment, a possessive such as docs/MODEL.md's note, or a bare § strands silently when a section moves or is renamed

Found by the triage pass of 2026-11-22. Five items name one fact: which section, in which document, a citation names. Each was a citation the document check could not test.

1. `PL-97S1` (done): two citations of a `docs/MODEL.md` note with no section mark.
2. `PL-CVTG` (done): open items still naming `docs/MODEL.md` for sections `PL-CTXZ` moved to `docs/INTERFACE.md`.
3. `PL-10BC` (open): code comments and docstrings citing `docs/MODEL.md` for text `#2109` moved, many written as a `#` comment, a possessive or a bare §.
4. `PL-GC7Z` (open): a `#:` comment above `REFERENCE_CONDITION_LABEL` citing a note without its section.
5. `PL-Q2DK` (open): two citations of a `ROADMAP.md` heading that has since gained the word "Completed", which the check passes because the new heading still holds the old words.

`PL-97S1`'s record gives the cause: the check reads a citation only in a docstring, and passes it when the cited document holds the words anywhere.

**Why it matters.** `PL-48MX` and `PL-SY7G`, the later stages of splitting `docs/MODEL.md` and `docs/INTERFACE.md` by reader, will move more sections. Each move strands every citation the check cannot read, and each stranded citation becomes a queue item found by hand. A reader who follows a stranded citation to a clinical document finds the wrong section or none.

**Done when.** The document check reads a § citation wherever this repository writes one: in a docstring, in a `#` or `#:` comment, in a possessive form, and as a bare § whose document is named on the line before. It refuses a citation whose heading the cited document does not hold exactly, rather than one whose words appear anywhere in it. A test shows each form refused after a heading is renamed.

**Generator check.** This item is the head. The misread fact is which heading of which document a § citation names, and no earlier head's `misread:` states it.
