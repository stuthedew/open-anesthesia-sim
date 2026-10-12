---
id: PL-6531
title: docket release's notes_bullets reads no top-level bullet whose marker is indented one to three spaces, though notes_ids claims its id, so unreferenced and restate_references pass the bullet by; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
milestone: v0.5.24
touches: subprojects/docket/src/docket/release.py, subprojects/docket/tests/test_release.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1434
payoff: A notes bullet indented by a space is checked and repaired for its pull request reference like every other bullet the notes claim.
verify: grep -q 'def test_a_bullet_indented_one_to_three_spaces_is_read_as_notes_ids_reads_it' subprojects/docket/tests/test_release.py
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

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`, under python3 3.13.16:
`notes_ids` gives `PL-BCDF` and `PL-HJKM`, and `unreferenced` gives `PL-HJKM`
alone. The indented bullet is in `notes_bullets`' list, its text starting at
the leading space; `NOTES_BULLET_RE`, anchored at the margin, is what
`unreferenced` and `restate_references` then fail to match, so the fix can
strip the bullet's first line in `notes_bullets` or let the pattern take the
indent. cmark-gfm (cmarkgfm 2025.10.22) renders both lines as items of one
list. Still latent: no file under `docs/releases/` indents a top-level bullet.

**Generator check.** Not a member of `PL-R417`: the bullet is read on its own
line, and its marker's indent is what is misread.

**Why it matters.** `notes_ids` is what `_check_release_notes` holds the
`milestone:` stamps against, and `unreferenced` is what reports a bullet with
no route back to its change, so where they disagree a bullet counted as shipped
is never checked for its reference nor repaired by `restate_references` - a
missing pull request link that reads as clean. A one-space indent is an easy
slip in a hand-edited notes file.

**Done when.** `notes_bullets` reads a top-level bullet whose marker is
indented up to three spaces, as `notes_ids` does, so `unreferenced` and
`restate_references` see every bullet `notes_ids` claims; a test pins the form
above.
