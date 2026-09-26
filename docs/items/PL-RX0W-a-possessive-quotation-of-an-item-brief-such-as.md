---
id: PL-RX0W
title: A possessive quotation of an item brief, such as PL-CNJ1's "writes nothing" in PL-SSQW, is read by no check: QUOTED_SOURCE_RE reads only a .md document and PL-QYN4 holds only the section mark after an item id; of the eleven such quotations on 2026-09-26 the one that misses quotes across emphasis (the brief has writes **nothing**), so reading them needs doc_check's comparison to fold markup first
status: untriaged
added: 2026-09-26
---

**Problem.** A possessive quotation of an item brief, such as PL-CNJ1's "writes nothing" in PL-SSQW, is read by no check: QUOTED_SOURCE_RE reads only a .md document and PL-QYN4 holds only the section mark after an item id; of the eleven such quotations on 2026-09-26 the one that misses quotes across emphasis (the brief has writes **nothing**), so reading them needs doc_check's comparison to fold markup first

Found 2026-09-26 working `PL-QYN4`, which holds a section mark after a code-spanned item id to that item's brief by containment and was scoped to the mark alone. Counted that day over what `check_quoted_sources` reads (the documents, the live briefs and the docstrings), the possessive after an item id stood eleven times, ten of them contained in the cited brief. The eleventh is the example in the title: `docs/items/PL-CNJ1-the-qt-spike-writes-screenshots-to-a-caller.md` writes the phrase with its last word in bold, and `_comparable` folds case, dashes and quote style but not emphasis, so a faithful quotation would be refused. The same limit holds after a document today, and nothing trips it only because no such quotation stands in the tree. Not taken into `PL-QYN4`, because it is a second connective and needs the comparison changed first; the other connectives after an item id are not citations of the brief at all (`under "X"` names the heading an item is listed under elsewhere), so the possessive is the only one left.
