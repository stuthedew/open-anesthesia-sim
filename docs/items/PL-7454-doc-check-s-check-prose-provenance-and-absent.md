---
id: PL-7454
title: doc_check's check_prose_provenance and _absent_paths read a complete marker line that closes a longer HTML comment as a marker of its own, where CommonMark ends the comment's one HTML block at that line, so a commented-out provenance marker is held to its data file and an absent marker inside a comment silences a citation; latent
status: untriaged
feature: one-answer
added: 2026-10-10
---

**Problem.** doc_check's check_prose_provenance and _absent_paths read a complete marker line that closes a longer HTML comment as a marker of its own, where CommonMark ends the comment's one HTML block at that line, so a commented-out provenance marker is held to its data file and an absent marker inside a comment silences a citation; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`tools/doc_check.py`'s first part.
`PROSE_MARKER_RE` and `ABSENT_MARKER_RE` match a marker on its own line, and
`_split_markers` looks for a marker kind only at a comment's opening. An HTML
block of kind 2 runs from its opening comment to the first line holding the
comment's end (CommonMark 0.31.2 § 4.6), so a marker line written under an
earlier comment's still-open opening is that comment's last line, not a marker.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against markdown-it-py 4.2.0 (one `html_block` over all three lines)
and cmark-gfm 0.29 (one comment, omitted):

```text
<!-- an old note, kept for the record:
The volume was 9 L.
<!-- provenance: data/x.json a = 9 -->
```

In a copy of `docs/MODEL.md`'s place, `check_prose_provenance` reports that the
prose states `a = 9` where the data file holds another value: a commented-out
marker held to the data. A `derived:` marker in the same position whose figure
has no number passes as checked.

Latent: 77 marker lines stand in HTML blocks across the documents, and none is
off its block's first line.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is the gap
closed `PL-GT0J`'s fix left.

**Done when.** A marker is read only where its line opens its HTML block, and
a marker line closing a longer comment is either ignored with the comment or
declined by name; a test pins the form above.
