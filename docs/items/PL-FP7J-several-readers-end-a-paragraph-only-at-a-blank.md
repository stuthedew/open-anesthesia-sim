---
id: PL-FP7J
title: Several readers end a paragraph only at a blank line - release.CODE_SPAN_PATTERN under doc_check's _code_spans and _without_code, and checks' _PARAGRAPH, _cued_paragraphs and _marks_recommendation - so a code span, an emphasis run or a cued clause reads across a list item, block quote, heading or HTML block; live in five closed briefs, no wrong verdict today
status: untriaged
feature: one-answer
touches: subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/checks.py, tools/doc_check.py, subprojects/docket/tests, tests/unit
added: 2026-10-04
recurrences: 2026-10-04 PL-VQBY withdrawn 2026-10-04 PL-R417, 2026-10-04 PL-4ZDZ withdrawn 2026-10-04 PL-R417
---

**Problem.** Several readers end a paragraph only at a blank line - release.CODE_SPAN_PATTERN under doc_check's _code_spans and _without_code, and checks' _PARAGRAPH, _cued_paragraphs and _marks_recommendation - so a code span, an emphasis run or a cued clause reads across a list item, block quote, heading or HTML block; live in five closed briefs, no wrong verdict today

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

The mirror of the head's usual direction: these read past where a statement ends. CommonMark § 6.1 keeps a code span inside its paragraph, and a paragraph also ends where a list item (§ 5.2), a block quote (§ 5.1), an ATX heading (§ 4.2) or an HTML block (§ 4.6) starts; `CODE_SPAN_PATTERN`'s own comment says those are not read.

- `CODE_SPAN_RE` over "A stray ` backtick in prose" followed by "- an item with `code` in it" pairs the stray backtick with the item's, where markdown-it-py 4.2.0 reads `code`; a heading, a list item and a block quote each do the same.
- doc_check reads the two lines below as one code span and blanks it, so TeX
  delimiters GitHub shows literally go unreported:

  ```markdown
  Run `a
  - \(F_D\) b` here.
  ```
- `checks._marks_recommendation` flattens whitespace before applying the pattern, erasing its one guard: "The open question is whether a stray ` backtick matters.", a blank line, then "Recommendation: take `x`, because it is cheaper." returns False.
- `checks._PARAGRAPH` pairs emphasis across blocks (the label sets differ in four closed items, and no answer changes), and `_cued_paragraphs` ends a paragraph only at a blank line, so "- Blocked on `PL-GHJK` until it lands." over "- This reports on `PL-MNPQ` and on `PL-ZZZZ`." reads `PL-ZZZZ` as a prerequisite.

Live: five closed briefs pair a span across a block start (`PL-D2GW`:127-129, `PL-DL4M`:23-24, `PL-KQHN`:109-110, `PL-Q2BJ`:49-50, `PL-RLTK`:61-62); no reader reads a closed brief, so no verdict changes. `statement_lines` already holds where each paragraph ends.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
