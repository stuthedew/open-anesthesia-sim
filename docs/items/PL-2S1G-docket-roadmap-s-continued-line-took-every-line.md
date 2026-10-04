---
id: PL-2S1G
title: docket.roadmap's CONTINUED_LINE took every line opening with < or with three backticks for a new block, so a paragraph wrapped before a placeholder, an autolink or a triple-backtick code span was read as ending there - 33 paragraphs in 29 tracked files, cut for doc_check's GAP readers and the list walker; no finding changed
priority: P2
effort: S
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-04
pr: 1352
payoff: where a Markdown paragraph goes on is answered as CommonMark answers it, so no reader of a soft break cuts a paragraph at a placeholder, an autolink or a code span
verify: grep -qF '"soft break, a line opening with a placeholder"' tests/unit/test_doc_check.py
---

**Problem.** docket.roadmap's CONTINUED_LINE took every line opening with \< or with three backticks for a new block, so a paragraph wrapped before a placeholder, an autolink or a triple-backtick code span was read as ending there - 33 paragraphs in 29 tracked files, cut for doc_check's GAP readers and the list walker; no finding changed

**Found 2026-10-04, building `PL-R417`'s Markdown slice (`#1352`).** `CONTINUED_LINE` refused, outright, a line opening with `<` and one opening with three backticks, as the opening of a block that ends a paragraph. CommonMark lets only an HTML block of kinds 1 to 6 interrupt a paragraph (0.31.2 § 4.6), so a placeholder such as `<id>`, or an autolink, carries the paragraph on; and a backtick fence's info string holds no backtick (§ 4.5), so a line opening with a triple-backtick code span carries it on too. Measured against markdown-it-py 4.2.0 over every tracked Markdown file: 33 paragraphs in 29 files read split, 32 at a `<` and one at a code span. Every reader of a soft break took the cut - doc_check's `GAP` and `STATEMENT_RE` readers, and the list walker, which ended an entry there unrefused - though no finding on the tree changed.

**Reproduced 2026-10-04, at triage.** `doc_check.STATEMENT_RE` reads `It wraps\n<PL-GGGG> here.` as its first line, and the same before a line opening with a triple-backtick span; a frozen-list entry carried on from the margin by `<PL-GGGG> (S)` ends there, unrefused.

**Why it matters.** The pattern is the one statement of where a Markdown paragraph goes on, shared by every reader of a soft break, so a wrong refusal in it is a silent short read in all of them at once.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names. Found by checking the walker this slice builds against markdown-it, rather than by a sweep.

**Done when.** `CONTINUED_LINE` refuses only what CommonMark lets interrupt a paragraph, checked against markdown-it-py over the tracked documents, pinned by `soft break, ...` cases and a `frozen list, a lazy line opening with a placeholder ...` case in `PL-R417`'s guard.

**Built 2026-10-04 (`#1352`).** `CONTINUED_LINE` refuses a `<` only where an HTML block of kinds 1 to 6 opens, and three backticks only where the fence's info string holds no backtick. It still refuses every ordered marker, every pipe line and every block's opening indented four columns or more, though each can carry a paragraph on: whether one does turns on the paragraph's list item or the line under it, which a pattern cannot see, so `statement_lines` reads that context. Over the tracked documents the walker now splits no paragraph markdown-it reads whole, and doc_check reports the same before and after. Three guard cases, each failing on main's pattern.
