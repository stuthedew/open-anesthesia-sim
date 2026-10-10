---
id: PL-6531
title: docket release's notes_bullets reads no top-level bullet whose marker is indented one to three spaces, though notes_ids claims its id, so unreferenced and restate_references pass the bullet by; latent
status: untriaged
added: 2026-10-10
---

**Problem.** docket release's notes_bullets reads no top-level bullet whose marker is indented one to three spaces, though notes_ids claims its id, so unreferenced and restate_references pass the bullet by; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`docket.release`. A list marker indented up to three spaces still opens a
top-level item (CommonMark 0.31.2 § 5.2). `notes_ids` strips each line before
it reads the marker, so it claims such a bullet's id; `notes_bullets` reads the
marker with `NOTES_BULLET_RE`, which is anchored at the margin, so
`unreferenced` and `restate_references` never see the bullet.

```text
## Fixed

 - PL-BCDF a title with no reference
- PL-HJKM another title
```

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16: `notes_ids` gives `PL-BCDF` and `PL-HJKM`, and `unreferenced` gives
`PL-HJKM` alone; with the first bullet at the margin it gives both.
markdown-it-py 4.2.0 reads both lines as items of one list. Latent: no file
under `docs/releases/` indents a top-level bullet.

**Generator check.** Not a member of `PL-R417`: the bullet is read on its own
line, and its marker's indent is what is misread.

**Done when.** `notes_bullets` reads a top-level bullet whose marker is
indented up to three spaces, as `notes_ids` does, so `unreferenced` and
`restate_references` see every bullet `notes_ids` claims; a test pins the form
above.
