---
id: PL-Q8LJ
title: doc_check's check_quoted_sources tests a quotation against the cited file collapsed into one string, so a quotation spliced from a heading and the paragraph under it, or from two paragraphs, passes as words the file holds; latent
status: untriaged
feature: one-answer
added: 2026-10-10
---

**Problem.** doc_check's check_quoted_sources tests a quotation against the cited file collapsed into one string, so a quotation spliced from a heading and the paragraph under it, or from two paragraphs, passes as words the file holds; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`tools/doc_check.py`'s middle part.
`check_quoted_sources` asks whether the quoted words stand in the cited file
after `_comparable` normalizes it, and `_normalized` collapses the whole file's
whitespace, so the containment test runs across every statement end the file
has. CommonMark 0.31.2 makes a heading and the paragraph under it two blocks
(§ 4.2, § 4.8), so no quotation of the file's words crosses between them.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against markdown-it-py 4.2.0 and cmark-gfm 0.29, which read the
source as a heading and a separate paragraph:

```text
SRC.md:
## Known limitations

The model ignores shunt.

citing document:
`SRC.md`'s "Known limitations The model ignores shunt" is the source.
```

The quotation passes. Latent: of the 507 quotations that pass today, none
depends on crossing a statement end in its source.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It reads the
whole text as one statement - the direction
`PL-BYJ5` and `PL-T73L` fixed on the quoting side.

**Done when.** A quotation passes only where one statement of the cited file
holds it (a soft break inside that statement still crossed), with a test on
the form above.
