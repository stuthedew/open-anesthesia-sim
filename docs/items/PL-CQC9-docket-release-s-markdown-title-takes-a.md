---
id: PL-CQC9
title: docket.release's markdown_title takes a backslash-escaped backtick for a code span's opener, so in a title holding one before a placeholder in angle brackets the placeholder is copied unescaped into the notes bullet or capture line, where GitHub drops it as an HTML tag; latent
priority: P3
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/release.py, subprojects/docket/tests/test_release.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-06
payoff: A placeholder after an escaped backtick in a title survives into release notes and capture lines rather than being dropped by GitHub.
verify: grep -q 'def test_a_backslash_escaped_backtick_opens_no_code_span_in_a_title' subprojects/docket/tests/test_release.py
---

**Problem.** docket.release's markdown_title takes a backslash-escaped backtick for a code span's opener, so in a title holding one before a placeholder in angle brackets the placeholder is copied unescaped into the notes bullet or capture line, where GitHub drops it as an HTML tag; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`docket.release`. `markdown_title` escapes each `<` outside a code span, so a
placeholder such as `refs/pull/<n>/head` survives in the rendered notes
(`PL-PRSF`), and copies a code span as it stands. `CODE_SPAN_RE` finds the
spans, and it does not ask whether a backtick is backslash-escaped. In
CommonMark 0.31.2 an escaped backtick is a literal character and opens no code
span (§ 2.4, whose example reads it as not code).

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against markdown-it-py 4.2.0, with a title holding an escaped backtick, then
`refs/pull/<n>/head`, then a code span: `markdown_title` returned it
unchanged, the `<` not escaped, because the span it found ran from the escaped
backtick to the code span's opener. markdown-it rendered that output with `<n>`
as raw HTML, and the escaped form as the text `<n>`. Latent: no tracked title
holds an escaped backtick.

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`, under python3 3.13.16: the
title from the reproduction above comes back from `markdown_title` unchanged,
its `<` unescaped, where the same title without the escaped backtick comes back
escaped; cmark-gfm (cmarkgfm 2025.10.22) renders the unchanged form with the
placeholder omitted as raw HTML. Still latent: no item's `title:` holds an
escaped backtick. `CODE_SPAN_PATTERN` is also taken into `verify.NON_CODE_RE`,
so a fix made in the pattern reaches that reader too.

**Generator check.** Not a member of `PL-R417`: a title is one line, and the
misread is inside it.

**Why it matters.** `markdown_title` exists so a placeholder in a title
survives into a notes bullet and a capture's Problem line (`PL-PRSF`); where it
fails, GitHub drops the placeholder and the page prints a wrong command rather
than a missing word, with nothing reporting it. A release's notes are permanent
once cut.

**Done when.** `markdown_title` reads code spans as CommonMark does, an escaped
backtick opening none, pinned by a test with the title above.
