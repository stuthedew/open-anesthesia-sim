---
id: PL-ZT47
title: docs/MODEL.md still reads as machine-written after PL-BZR4's rewrite: tautological asides, 'X, not Y' and 'rather than' contrasts, and narration about its own provenance; the plain-writing rule names none of these patterns, and the close-out prose review reads only .py files, so MODEL.md's 2,348 lines added since were never reviewed
status: untriaged
feature: prose-quality
added: 2026-11-02
---

**Problem.** docs/MODEL.md still reads as machine-written after PL-BZR4's rewrite: tautological asides, 'X, not Y' and 'rather than' contrasts, and narration about its own provenance; the plain-writing rule names none of these patterns, and the close-out prose review reads only .py files, so MODEL.md's 2,348 lines added since were never reviewed

**The owner's reading (2026-11-02).** The document "just reads like the worst
kind of AI slop writing in terms of phrasing". The example given was line 395,
which `PL-BZR4`'s own rewrite (#1808, 2026-10-25) wrote: "The naming is
Hendrickx and De Wolf's, which is the field's naming."

**What was measured on 2026-11-02, at `main` 4007ad8e and later.**

- The file is 13,640 lines and about 140,800 words. It was 10,931 lines before
  `PL-BZR4` and 11,532 after it.
- 36 commits have changed it since `PL-BZR4` merged, adding 2,348 lines and
  removing 240. None of those lines passed a prose review, because
  `tools/new_prose.py` keeps only `.py` files.
- Counts of phrases that mark the style the owner objects to: "rather than"
  396, "That is" 238, ", not " 233, "is what" 76, "This is" 60, "so that" 48,
  ", which is the" 47, "deliberately" 37, "is recorded" 33, "the project
  owner" 28. A count is not a verdict, since many of these uses are fine.
- 439 lines cite an item id (489 ids in all). Much of the document narrates
  how a decision was reached and who supplied what, which is audit trail for
  sessions rather than specification for a clinician.

**Why the existing rule did not prevent it.** `.claude/rules/plain-writing.md`
targets compressed wording: dropped small words, private senses, stacked
clauses. `PL-8ZTQ` measured that as the main defect, and `PL-BZR4` fixed for
it. The patterns here are a different failure, and the rule names none of
them:

1. Tautological asides that restate the clause they sit in.
2. Reflexive contrast ("X, not Y", "rather than Z") where nobody claimed Z.
3. Narration about the document itself: "is recorded at that depth", "the
   pages above are what the citation is being used for".
4. Defensive scope statements that say what a passage does not rely on.

**Example rewrite of line 395's paragraph.** "Symbols and the gas-phase
cascade ($`F_D`$, $`F_I`$, $`F_A`$) follow Hendrickx and De Wolf (pp.
161-162). They attribute the $`F_D - F_I`$ gradient to rebreathing (p. 169)
and the $`F_I - F_A`$ gradient to uptake (p. 171), and describe the teaching
role of the $`F_A/F_I`$ curve (p. 167)." The full citation follows unchanged.

**Open questions for the design round.** Whether the audit trail (decision
histories, item ids, re-measurement narratives) moves out of `docs/MODEL.md`
into the items that hold it, leaving a specification a clinician can read.
That would shorten the file most, and it is the owner's call because the
document is the authoritative specification. Whether the plain-writing rule
gains the four patterns above. Whether `tools/new_prose.py` reviews changed
paragraphs of `docs/MODEL.md` as well as `.py` units.

**Constraint.** As in `PL-BZR4`: no equation, unit, assumption, limitation or
provenance note may be lost. A citation stays; narration about the citation
may go.
