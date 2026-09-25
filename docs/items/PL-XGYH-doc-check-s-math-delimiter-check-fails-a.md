---
id: PL-XGYH
title: doc_check's math-delimiter check fails a Markdown-escaped bracket pair around WIP and a regex inside an indented code block, in documents and in items
status: untriaged
feature: exact-gates
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-25
---

**Problem.** doc_check's math-delimiter check fails a Markdown-escaped bracket pair around WIP and a regex inside an indented code block, in documents and in items

Reproduced three, and a fourth by filing this item: its first title quoted the escaped pair, backslash and all, and `make doc-check` refused it as math GitHub does not render, so the title had to be reworded to satisfy the check it reports. The three: an escaped bracket pair, and a regex in an indented (four-space) code block in a document and in an item. 807 well-formed math spans exist; none of the tree's are malformed.

**Why it matters.** A hard error on content that contains no math.

**Done when.** Escaped brackets and indented code blocks are blanked before the delimiter scan; a test holds each through a clean run.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
