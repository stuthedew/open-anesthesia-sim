---
id: PL-PK4B
title: tools/fixture_id_check.py splits a Python file with splitlines() before ast.parse, so legal source holding a U+2028, U+0085 or form feed in a comment or string crashes make check with a SyntaxError traceback instead of a report
priority: P3
effort: S
status: ready
classes: defect
touches: tools/fixture_id_check.py, tests/unit/test_fixture_id_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-24 triage pass
added: 2026-09-23
payoff: make check reports on any source Python accepts instead of crashing on it
verify: grep -q 'def test_a_line_separator_python_accepts_is_scanned_rather_than_crashing' tests/unit/test_fixture_id_check.py
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

**Premise re-checked at triage, 2026-09-24.** Three one-line modules were
written, each accepted by `compile()`: one holds U+2028 in a string, one holds
U+0085 in a comment, and one holds a form feed in a comment. On each,
`fixture_id_check.main` raised `SyntaxError` from `scan_python`, which re-joins
`splitlines()` output before calling `ast.parse`. Nothing between that
function and `main` catches the error.

**Why it matters.** On source that Python itself accepts, `make check` stops
with a traceback that points at a line the file does not contain. The report
the tool exists to give never appears. No file in the tree holds such a
character today.

**Done when.** `scan_python` parses the text as read and takes its lines from
`split("\n")`. A test in `tests/unit/test_fixture_id_check.py` scans a module
holding each of the three characters without raising.

**Generator check.** This misreads the same fact as `PL-139L`: where a line
ends. That is two items and no head. `PL-139L`'s check gives the count that
would make one.
