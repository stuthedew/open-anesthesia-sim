---
id: PL-PK4B
title: tools/fixture_id_check.py splits a Python file with splitlines() before ast.parse, so legal source holding a U+2028, U+0085 or form feed in a comment or string crashes make check with a SyntaxError traceback instead of a report
status: untriaged
touches: tools/fixture_id_check.py
added: 2026-09-23
---

**Problem.** tools/fixture_id_check.py splits a Python file with splitlines() before ast.parse, so legal source holding a U+2028, U+0085 or form feed in a comment or string crashes make check with a SyntaxError traceback instead of a report

**Found 2026-09-23** while closing `PL-JD4L`. A comment in
`subprojects/docket/src/docket/model.py` briefly held a literal U+2028. Python
compiles that file, since its tokenizer breaks lines only on `\n`, `\r\n` and
`\r`. But `scan_python` reads it with `splitlines()` and re-joins with `"\n"`
before `ast.parse`, which moves the comment's tail onto a line of its own.
`test_the_repository_carries_no_malformed_id` then failed with `SyntaxError:
leading zeros in decimal integer literals`, pointing at a line the file does
not contain. The likely repair is `split("\n")`, the split `model.py`'s
front-matter reader and writers now share. No file in the tree carries such
a character today.
