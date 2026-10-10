---
id: PL-8NPN
title: doc_check's title, group and math patterns misread within a line or a container - MARKER_RE and TAGS_MARK_RE read no bold title after an ordered marker, a nested bullet or a block quote, GATE_GROUP_RE reads a count past an opening emphasis run, and MATH_SPAN_RE pairs a dollar inside one code span with one inside another - so a citation is refused, a count misread, or prose blanked; latent
status: untriaged
added: 2026-10-10
---

**Problem.** doc_check's title, group and math patterns misread within a line or a container - MARKER_RE and TAGS_MARK_RE read no bold title after an ordered marker, a nested bullet or a block quote, GATE_GROUP_RE reads a count past an opening emphasis run, and MATH_SPAN_RE pairs a dollar inside one code span with one inside another - so a citation is refused, a count misread, or prose blanked; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditors of
`tools/doc_check.py`.

```text
1. **Ordered title.** Text.
- top
  - **Nested title.** Text.
> **Quoted title.** Text.

*Note.* This list was frozen on 30 September - three entries were admitted later.

Run `echo $HOME` and then `cost $`.
```

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16: `_headings` returns none of the three titles, so a citation of one is
reported as a missing section (loud); `TAGS_MARK_RE` reads no tags statement
inside a container; `GATE_GROUP_RE` matches the emphasised line as a group
heading counting `three`; `MATH_SPAN_RE` pairs the two dollars across the
code spans and blanks the prose between. Latent: none in today's documents
changes a verdict (one closed brief holds the code-span form with no TeX).

**Generator check.** Not members of `PL-R417`: each reads within one line or
reads the wrong container.

**Done when.** Each pattern reads its construct where CommonMark places it,
inside containers and outside code spans, or declines by name; a test pins
each form above.
