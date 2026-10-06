---
id: PL-K02Q
title: tools/dead_ends.py reads a dead end only from a bullet opening with a dash at column 0, so one written with a star or plus bullet, or indented one to three spaces, is neither shown in the session-start digest nor checked, with nothing reported; latent
status: untriaged
added: 2026-10-06
---

**Problem.** tools/dead_ends.py reads a dead end only from a bullet opening with a dash at column 0, so one written with a star or plus bullet, or indented one to three spaces, is neither shown in the session-start digest nor checked, with nothing reported; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`tools/dead_ends.py`. `ENTRY` and `OPENING` anchor on a dash and a space at the
start of the line. CommonMark 0.31.2 opens a bullet list item with a dash, a
plus or a star, after up to three spaces of indentation (§ 5.2), so each of
those forms is the same entry to a reader of `docs/dead-ends.md`.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15:

```text
* **Star bullet** - written with a star.
  - **Indented two** - indented two spaces.
+ **Plus bullet** - written with a plus.
```

`entries` returned nothing for each and `check` reported nothing, where the
same entry led by a dash at column 0 is emitted. Latent: every tracked entry is
written with a dash at column 0.

**Generator check.** Not a member of `PL-R417`: each form is one line, read
whole and not matched. `PL-QFFF`, open, is the same pattern missing an entry
whose title is followed by a parenthetical; one fix to `ENTRY` should take both.

**Done when.** `dead_ends` reads an entry in every bullet form CommonMark gives
one, or refuses an unread bullet by name as `PL-F5B9` does for a wrapped title,
pinned by a test for each form above.
