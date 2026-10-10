---
id: PL-TJ1S
title: docket.markdown does not take a lazy continuation line for a table's header row where the delimiter row under it sits inside the list item or block quote, so a table cmark-gfm renders inside the container is read as the paragraph above it going on; latent
status: untriaged
feature: one-answer
added: 2026-10-10
---

**Problem.** docket.markdown does not take a lazy continuation line for a table's header row where the delimiter row under it sits inside the list item or block quote, so a table cmark-gfm renders inside the container is read as the paragraph above it going on; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
docket's shared readers. `markdown._parse` reads a
table where its header row and delimiter row both match the open containers.
A lazy continuation line (CommonMark 0.31.2 § 5.1, § 5.2) can be a table's
header row in cmark-gfm when the delimiter row under it is inside the
container (GFM 0.29 § 4.10), and the module's docstring says tables are read
where cmark-gfm reads one.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against cmark-gfm 0.29, which renders a paragraph and then a table
with rows `a | b` and `c | d` inside the list item:

```text
- x
a | b
  --|--
  c | d
```

docket gives one paragraph over all four lines; the block-quote form reads the
same. The references split: markdown-it-py 4.2.0 makes a top-level table and
ends the list, and pandoc's commonmark-hs reads as docket does. GitHub renders
with cmark-gfm. Latent: table counts agree with cmark-gfm across all 2,508
tracked Markdown files.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is a shared
reader's own gap: the paragraph is read past the point
where cmark-gfm ends it.

**Done when.** `docket.markdown` reads the form above as cmark-gfm does, or the
module's docstring and its markdown-it test name it as a departure; a test
pins the choice.
