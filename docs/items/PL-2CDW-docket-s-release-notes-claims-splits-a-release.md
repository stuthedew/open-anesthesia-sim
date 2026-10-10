---
id: PL-2CDW
title: docket's release.notes_claims splits a release-notes file at the first occurrence of SPAN_HEADING's text, so that heading's text inside an HTML comment, a fence or a line of prose ends the file's claims there, and notes_by_version, unreferenced_by_version, restate_references and doc_check's _pull_requests_named lose every bullet above the real heading; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/release.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
payoff: a release notes file's claims end at the span heading GitHub renders, so the heading's words in a comment or a fence lose no claimed item
verify: grep -qF '"release notes, a span heading inside a comment' tests/unit/test_doc_check.py && grep -qF '"release notes, a span heading inside a fence' tests/unit/test_doc_check.py
---

**Problem.** docket's release.notes_claims splits a release-notes file at the first occurrence of SPAN_HEADING's text, so that heading's text inside an HTML comment, a fence or a line of prose ends the file's claims there, and notes_by_version, unreferenced_by_version, restate_references and doc_check's _pull_requests_named lose every bullet above the real heading; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`docket.release`. `notes_claims` takes the part of a notes file before
`SPAN_HEADING` with `text.partition`, whose first match may sit anywhere. A
heading-shaped line inside an HTML comment, which runs to its `-->` across lines
(CommonMark 0.31.2 § 4.6), or inside a fence, which runs to its closer (§ 4.5),
is no heading, and the heading's text inside a line of prose, a bullet or a code
span is none either.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against markdown-it-py 4.2.0 and `docket.markdown.headings`. A notes file whose
version heading is followed by an HTML comment holding the span heading's line,
then two claimed bullets naming `PL-BC12` and `PL-CD34`, then the real span
heading and a pointer bullet naming `PL-DF56`: the claims ended inside the
comment, so `notes_ids` of the claims was empty and both claimed items were
lost, where reading the whole file finds all three ids. markdown-it puts the
headings at lines 0 and 9 and the comment at lines 2 to 5, and
`docket.markdown.headings` agrees. The same holds with a fence in place of the
comment. Latent: the span heading appears once in each of 24 tracked notes
files, always at column 0 as a heading, and no notes file holds a comment or a
fence.

**Why it matters.** `notes_claims` decides which items a release's notes claim, so the span heading's words in a comment or a fence above the real heading lose every claimed bullet between them from the release checks and from `doc_check`'s pull-request reader.

**Generator check.** A member of `PL-R417`: a reader takes a heading-shaped
line inside a multi-line literal block for a heading, the class `PL-T1X0`'s
fence half was. The mid-line form is a fault within one line, which the same
change removes.

**Done when.** `notes_claims` ends the claims at the span heading
`docket.markdown.headings` reads, pinned by a `release notes, ` case in
`PL-R417`'s guard for the comment and the fence, failing on today's reader.
