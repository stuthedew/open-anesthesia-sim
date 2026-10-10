---
id: PL-703R
title: docket release's notes_bullets takes a setext heading's whole block, underline included, for a release-notes bullet's text, so restate_references appends a pull request reference to the underline and the write destroys the heading; latent
status: untriaged
feature: one-answer
added: 2026-10-10
---

**Problem.** docket release's notes_bullets takes a setext heading's whole block, underline included, for a release-notes bullet's text, so restate_references appends a pull request reference to the underline and the write destroys the heading; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`docket.release`. `notes_bullets` reads each list
item's block span as the bullet's text, and `restate_references`,
`unreferenced_by_version` and `doc_check`'s `_pull_requests_named` read
through it. A setext heading inside a list item ends before its underline
(CommonMark 0.31.2 § 4.3, § 5.2).

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against cmark-gfm 0.29, which renders the item as a heading, and
markdown-it-py 4.2.0, whose heading content excludes the underline:

```text
## v1.0.0 - 2026-10-10

### defect

- PL-BCDF A title wrapped
  ---
- PL-GHJK B title — #12
```

`notes_bullets` gives the first bullet's text with the underline in it, and
`restate_references` appends its reference to the underline line, after which
cmark-gfm renders the item as a paragraph. Latent: no release notes file holds
a heading inside a list item.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is the gap
closed `PL-CL8R`'s fix left.

**Done when.** A bullet's text is its statement's - a setext heading's title
lines without the underline - and a reference is written where that text
ends; a test pins the form above.
