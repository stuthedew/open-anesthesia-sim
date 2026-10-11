---
id: PL-703R
title: docket release's notes_bullets takes a setext heading's whole block, underline included, for a release-notes bullet's text, so restate_references appends a pull request reference to the underline and the write destroys the heading; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/release.py, subprojects/docket/tests/test_release.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
payoff: Restating references can never append to a heading underline and change what a released notes page renders.
verify: grep -q 'def test_a_setext_underline_in_a_bullet_is_not_its_text_and_takes_no_reference' subprojects/docket/tests/test_release.py
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

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`, under python3 3.13.16, and
against cmark-gfm (cmarkgfm 2025.10.22): `notes_bullets` gives the first
bullet's text as `- PL-BCDF A title wrapped ---`, and `restate_references` with
a pull request of 7 appends ` — #7` to the underline's `---` line, after
which cmark-gfm renders the item as a paragraph where it rendered a heading. Still
latent: no release notes file holds a setext underline inside a bullet.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is the gap
closed `PL-CL8R`'s fix left. Latent, so an ordinary item under the head's spent
ruling (re-checked 2026-10-11).

**Why it matters.** `restate_references` is a writer, and it rewrites a
released notes file in place: here the repair changes what a shipped page
renders, which its docstring says it never does - every byte but the appended
reference is meant to be untouched. The readers sharing `notes_bullets` take
the underline for part of the title too.

**Done when.** A bullet's text is its statement's - a setext heading's title
lines without the underline - and a reference is written where that text
ends; a test pins the form above.
