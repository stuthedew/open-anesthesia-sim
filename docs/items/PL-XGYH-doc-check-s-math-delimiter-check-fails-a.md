---
id: PL-XGYH
title: doc_check's math-delimiter check fails a Markdown-escaped bracket pair around WIP and a regex inside an indented code block, in documents and in items
priority: P3
effort: S
status: done
classes: defect
feature: exact-gates
milestone: v0.5.12
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-25 triage pass
added: 2026-09-25
closed: 2026-09-26
pr: 1086
payoff: a regex shown in an indented code block passes make check, instead of being refused as math GitHub does not render
verify: grep -q 'def test_math_in_an_indented_code_block_is_quiet' tests/unit/test_doc_check.py
---

**Problem.** doc_check's math-delimiter check fails a Markdown-escaped bracket pair around WIP and a regex inside an indented code block, in documents and in items

Reproduced three, and a fourth by filing this item: its first title quoted the escaped pair, backslash and all, and `make doc-check` refused it as math GitHub does not render, so the title had to be reworded to satisfy the check it reports. The three: an escaped bracket pair, and a regex in an indented (four-space) code block in a document and in an item. 807 well-formed math spans exist; none of the tree's are malformed.

Re-confirmed 2026-09-25 against 46954a81: `check_math_delimiters` over a scratch tree errored on all three - the escaped pair around WIP in running text, and a regex in a four-space indented code block, once in a document and once in an item file - because `_without_code` blanks fences and backtick runs and nothing else.

**The escaped-bracket half has no exact rule, so this item no longer carries it** (narrowed at triage, 2026-09-25). The escaped pair around WIP and the `\[F = 0.02\]` that `test_math_latex_block_delimiters_are_reported` requires to be refused are one syntax, differing only in what sits between the brackets, so blanking escaped brackets would delete the block-delimiter half of the rule rather than exempt a case of it. Whether that half stays a hard error is `PL-GPJ7`'s question, under its rule that wording-recognition leaves the hard gates. The indented code block is exact - CommonMark defines it - with one trap: four spaces inside a list item continue the item rather than open a code block, so blanking every indented line would hide real delimiters in list prose.

**Generator check.** The fact misread is whether a backslash-bracket is a math delimiter, recognised by the characters alone - `PL-GPJ7`'s `misread:`, and a member of it correctly.

**Why it matters.** A hard error on content that contains no math.

**Done when.** Indented code blocks are blanked before the delimiter scan, as fences already are; a test holds the indented regex through a clean run.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

**Built 2026-09-26, as step 2 of `PL-GPJ7`'s split.** `_without_code` blanks an indented code block by CommonMark's rule: a line four columns past the innermost open list item's content column, or past column 0 outside a list, that does not continue a paragraph. Where the reading is unsure it keeps a list item open or a line as prose, so a doubt costs a false refusal, which a fence repairs, and never a delimiter left unread. On this tree it newly blanks 206 lines in 62 markdown files, each a genuine block - command output, shell, tables of measured values - and none held a delimiter, so no finding was lost. The escaped-bracket half stays a hard error, as `PL-GPJ7` decided.
