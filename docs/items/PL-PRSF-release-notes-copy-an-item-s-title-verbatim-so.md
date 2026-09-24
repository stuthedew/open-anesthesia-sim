---
id: PL-PRSF
title: Release notes copy an item's title verbatim, so an angle-bracket placeholder in it renders on GitHub as an HTML tag and vanishes: six bullets across six notes files, v0.2.10 to v0.5.9
priority: P3
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_release.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-24 triage pass
added: 2026-09-24
payoff: release notes and item pages keep the command shapes their titles give, instead of printing a wrong command
verify: grep -q 'def test_an_angle_bracket_placeholder_in_a_title_survives_the_rendered_notes' subprojects/docket/tests/test_release.py && grep -q 'def test_a_captures_problem_line_keeps_an_angle_bracket_placeholder' subprojects/docket/tests/test_cli.py
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

**Premise re-checked at triage, 2026-09-24, on the rendered page.** GitHub's
HTML rendering of `docs/releases/v0.5.9.md` shows `refs/pull//head`.
`release_notes` in `subprojects/docket/src/docket/release.py` builds each
bullet from the title without escaping it.

A second writer does the same. `CAPTURE_TEMPLATE` in `cli.py` opens every
brief with `**Problem.** {title}`. So `PL-LF2C`'s own rendered page loses the
placeholder in its Problem line, while its front-matter table keeps it.

Twelve item titles carry such a placeholder outside a code span. Five are
still open, so the next notes will carry more: `PL-FH61`, `PL-PNW6`,
`PL-S0MB`, `PL-SL4L` and `PL-Y5ZB`.

**Why it matters.** Notes and item pages are the record a later reader
trusts. A placeholder is where a command's shape was being given, so
`refs/pull//head` is a wrong command, not a missing word.

**Done when.** A title holding an angle-bracket placeholder outside a code span
keeps it in two places: the rendered notes bullet, and a new capture's Problem
line. A placeholder already inside backticks is left alone. Tests in
`subprojects/docket/tests/test_release.py` and
`subprojects/docket/tests/test_cli.py` pin both.

**Generator check.** The fact is what GitHub's renderer does to an unknown
angle-bracket tag outside a code span. `PL-TDBT` misreads it for
`docs/pr-bodies`. `PL-1DN9` looks like a third, but its fact is how a stored
pull request body gets rewritten when it is written. `PL-DMNX` found `<id>`
intact inside a code span in `#779`, so that is a different mechanism. That
leaves two items and no head. A third instance at render time would make one.
