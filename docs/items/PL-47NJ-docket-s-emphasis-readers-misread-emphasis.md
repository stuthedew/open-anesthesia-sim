---
id: PL-47NJ
title: docket's emphasis readers misread emphasis inside one statement - checks' _marks_recommendation takes a multiplication's asterisks for emphasis, _heading_words matches a heading by prefix, _sections pairs an unclosed heading's opener with a run that cannot close it, _labels reads no heading inside a list item, and picks.bold_lead takes asterisks inside a code span - so a missing recommendation, a missing section or a bold lead is read wrongly; latent
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/picks.py, subprojects/docket/src/docket/markdown.py, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_picks.py, subprojects/docket/tests/test_markdown_reference.py, subprojects/docket/README.md, docs/apparatus.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1431
payoff: a brief is judged ready, answered or recommending by emphasis paired as CommonMark pairs it, so a heading that only begins with Done when, a multiplication or a nested answer no longer decides the gate or the advisory
verify: grep -q 'def test_a_multiplication_does_not_mark_a_recommendation' subprojects/docket/tests/test_checks.py && grep -q 'def test_a_heading_word_is_matched_whole' subprojects/docket/tests/test_checks.py && grep -q 'def test_an_unclosed_heading_pairs_with_no_run_that_cannot_close_it' subprojects/docket/tests/test_checks.py && grep -q 'def test_an_answer_heading_inside_a_list_item_is_an_answer' subprojects/docket/tests/test_checks.py && grep -q 'def test_bold_lead_reads_past_asterisks_in_a_code_span' subprojects/docket/tests/test_picks.py
---

**Problem.** docket's emphasis readers misread emphasis inside one statement - checks' _marks_recommendation takes a multiplication's asterisks for emphasis, _heading_words matches a heading by prefix, _sections pairs an unclosed heading's opener with a run that cannot close it, _labels reads no heading inside a list item, and picks.bold_lead takes asterisks inside a code span - so a missing recommendation, a missing section or a bold lead is read wrongly; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditors of
`docket.checks` and of docket's cli, picks and
trend modules. CommonMark 0.31.2 § 6.2 decides which delimiter runs open and
close emphasis (left- and right-flanking), and § 6.1 makes a code span's
content literal:

```text
The cost is 2 * 3 and we recommend nothing x * y here.
**Problems with the dose** ...        **Done whenever** ...
**Done when. The suite
passes and **foo** is bar.
**Decision needed.** Which?

- ## Answers 2026-10-01

  Take A.
- **`a ** b`** lead
```

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16: `_marks_recommendation` returns true on the first (no
`_NOT_EMPHASIS`, which `_labels` applies); `_heading_words` opens the
`**Problem.**` and `**Done when.**` sections on the second; `_sections` takes
the run before `foo` for the heading's closer, where CommonMark leaves the
opener literal; `_answered_beneath` finds no answer label in the fourth, where
the same heading at the top level is one (the README says a heading is one as
CommonMark reads it); `bold_lead` stops inside the code span. Latent: no
answer on today's store changes.

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`: `_marks_recommendation`
returns true on the first line; `_heading_words` matches `**Problem` and
`**Done when` on the second; `_sections` gives the text under the unclosed
heading as `foo** is bar.`; `_answered_beneath` returns nothing for the
list-item heading and `Answers 2026-10-01` for the same heading at the top
level; `bold_lead` returns the text up to the `**` inside the code span.

**Why it matters.** These readers decide whether a brief has the sections
`--status ready` requires, whether a `needs-decision` brief marks a
recommendation or carries an answer, and what a Required scope entry is
called. Misread, a brief passes the `ready` gate on a heading that only
begins with `Done when`, or a recommendation or an answer is reported that
is not there.

**Generator check.** Not a member of `PL-R417`: each reads the right
statement and pairs emphasis wrongly inside it. The `_sections` form is the
remainder of closed `PL-M890` within a statement.

**Done when.** Each reader pairs emphasis by § 6.2's flanking rules over the
statement's text with code spans blanked, matches a heading word whole, and
reads headings inside containers; a test pins each form above.

**Done 2026-10-12** (`#1431`). `docket.markdown.emphasis` pairs a statement's
emphasis by § 6.2's flanking rules and the appendix's "process emphasis" -
`*` and `_` alike, rule 9's multiple-of-3 test, escapes - with the caller's code
spans as literals. `_marks_recommendation`, `_labels` and `_sections` in
`checks` and `picks.bold_lead` read it; `_heading_words` matches the words
whole, `-` joining a word to the next; `markdown.headings(nested=True)` gives
`_labels` the headings inside a list item or a block quote. One form beyond the
brief's: a heading a wrapped code span carries to a line's start is a literal,
not an unclosed heading, since `PL-JL2M`'s brief has that shape and would
otherwise read as an empty `**Done when.**`. Held to markdown-it-py on all
1,322 vendored specification examples
(`subprojects/docket/tests/test_markdown_reference.py`), and on
every tracked Markdown file once (54,404 texts, none differing); links, images,
autolinks and raw HTML are not read, the departure the docstring names. Over
today's store no answer changed: every `_marks_recommendation`,
`_answered_beneath`, required-section and stub reading, and every scope entry's
bold lead, is as on `main`; 43 items' label lists changed beneath those answers
(`__init__` is strong emphasis, a nested span is part of its outer label, a
gap between stray `*`s is no label), and `PL-JL2M`'s `**Done when.**` text lost
the literal's share and kept its real section's.
