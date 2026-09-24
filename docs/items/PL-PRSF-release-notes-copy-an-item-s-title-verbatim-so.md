---
id: PL-PRSF
title: Release notes copy an item's title verbatim, so an angle-bracket placeholder in it renders on GitHub as an HTML tag and vanishes: six bullets across six notes files, v0.2.10 to v0.5.9
status: untriaged
added: 2026-09-24
---

**Problem.** Release notes copy an item's title verbatim, so an angle-bracket placeholder in it renders on GitHub as an HTML tag and vanishes: six bullets across six notes files, v0.2.10 to v0.5.9

**Found 2026-09-24 while cutting v0.5.9 (`PL-R498`).** A notes bullet is the
id, the title as filed and the reference, and a title is prose, so a
placeholder such as `refs/pull/<n>/head` reaches the notes outside a code span.
GitHub's renderer reads `<n>` as inline HTML and its sanitizer drops the unknown
tag, so the bullet reads `refs/pull//head` - the hazard `PL-1DN9` recorded for
pull request bodies, arriving through a file instead. Not yet confirmed on a
rendered page; the six bullets below are a grep, with code spans stripped
first:

- `docs/releases/v0.2.10.md`, `PL-G1MF`
- `docs/releases/v0.4.11.md`, `PL-20PT`
- `docs/releases/v0.4.14.md`, `PL-4LT9`
- `docs/releases/v0.4.15.md`, `PL-VV4D`
- `docs/releases/v0.5.7.md`, `PL-R808`
- `docs/releases/v0.5.9.md`, `PL-LF2C`

The item files carry the same titles, so their own rendered pages lose the
placeholder too. The fix belongs where `docket.release` renders a bullet, not
in the six files: a hand edit to one bullet is overwritten by nothing and fixes
nothing upstream.
