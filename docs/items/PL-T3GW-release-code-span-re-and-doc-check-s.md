---
id: PL-T3GW
title: release.CODE_SPAN_RE and doc_check's _InlineReader both still find Markdown code spans, and on an escaped backtick they disagree - CODE_SPAN_RE reads \`a` b `c` as two spans where CommonMark and _InlineReader read one
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/checks.py, tools/doc_check.py, subprojects/docket/tests/test_release.py, tests/unit/test_doc_check.py, subprojects/docket/src/docket/picks.py, subprojects/docket/src/docket/markdown.py, subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_markdown_reference.py, docs/apparatus.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
closed: 2026-10-12
pr: 1464
payoff: a code span reads the same in every checker, escaped backtick included
verify: grep -q 'def test_an_escaped_backtick_opens_no_code_span' subprojects/docket/tests/test_release.py
---

**Problem.** release.CODE_SPAN_RE and doc_check's _InlineReader both still find Markdown code spans, and on an escaped backtick they disagree - CODE_SPAN_RE reads \`a` b `c` as two spans where CommonMark and _InlineReader read one

- `release.CODE_SPAN_RE`, read by `checks` four times and by `doc_check._absent_paths` and `_without_code`, beside `doc_check.SPAN_AT` and `_InlineReader`, read through `_statement_spans`. On `\`a` b `c`` the export finds `a` and `c`; `_InlineReader` finds one span, ` b `, which is CommonMark's answer.
- `PL-9L39` moved four readers onto the export and `PL-Z8RS` moved `_without_code`, so the escape now sits in the export every one of them reads. `PL-CQC9` (ready) holds the same escape in `release.markdown_title` only.

**Why it matters.** Each copy is held to the others by nothing, so the first input they part on is answered one way by docket and another by the hook or check a session trusts at that moment; every pair below was read at both sites by the sweep, and the parting input is the sweep's reading, to re-confirm at start.

**Done when.** One reader of code spans, honouring a backslash-escaped backtick, serves `release`, `checks` and `doc_check`, and a test pins the escaped form. Land with or after `PL-CQC9`.

**Generator check.** A member of `PL-5DZ8`, filed by that head's closing sweep on 2026-10-12 and named in its `root-cause-of:`. The fact is the head's: which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it. It is neither a post-close instance nor a new generator.
