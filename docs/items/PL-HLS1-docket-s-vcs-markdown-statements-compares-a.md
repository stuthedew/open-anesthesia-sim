---
id: PL-HLS1
title: docket's vcs._markdown_statements compares a paragraph without the heading section it sits under, so a ref that deletes a heading between two sections - moving the paragraphs below it under the heading above - reads as holding nothing more, and stranded drops the edit; latent
status: untriaged
added: 2026-10-10
---

**Problem.** docket's vcs._markdown_statements compares a paragraph without the heading section it sits under, so a ref that deletes a heading between two sections - moving the paragraphs below it under the heading above - reads as holding nothing more, and stranded drops the edit; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`docket.vcs`. `_within` and `_standing` compare
each statement with its list-item markers but not the section it sits in.

```text
base:            ref:
## Allowed       ## Allowed
x                x
## Refused       y
y
```

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16: `_within` is true and `_standing` answers `behind`, though `y` now
reads as allowed. Latent: no ref in a fresh checkout carries such an edit.

**Generator check.** Not a member of `PL-R417`: a heading ends at its line
and a section is no CommonMark block, so this is the statement's context, not
where it ends. `PL-NGKW` is the block-level form.

**Done when.** A removed heading counts as a change to the statements of the
section it ended, so the form above reads as outstanding; a test pins it.
