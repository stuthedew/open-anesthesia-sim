---
id: PL-JT6L
title: The resident growth advisory says "grew 1 lines" because it formats the count directly instead of using _plural
priority: P3
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.2.8
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-01
closed: 2026-09-01
pr: 173
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_one_line_of_growth_is_reported_in_the_singular' tests/unit/test_doc_check.py
---

**Problem.** `check_resident_instructions` interpolated the growth count into a
hardcoded plural: `f"resident instructions grew {growth} lines"`. A one-line
addition to `CLAUDE.md` therefore reported "resident instructions grew 1 lines
against origin/main", which is what a real +4/-3 edit to the live tree printed
when the advisory was exercised end to end on 2026-09-01.

`_plural` already exists for exactly this, sits about eighty lines below in the
same module, and is used by `_format_resident` - the line printed immediately
above this advisory on every run. So the two halves of the same report
disagreed about how to count.

**Why it matters.** This is presentation of a number, in the output a session
reads when deciding whether a rule belongs resident. It is the lowest-stakes
place in the repository for that kind of error and still worth fixing, because
the advisory's whole job is to be read carefully by whoever is about to edit
the instructions every session loads - and text that cannot count its own lines
invites being skimmed.

`PL-BKQW` rewrote both advisory strings hours earlier and did not reach for the
helper, so this is a miss in that change rather than only an inherited one.

**Where.** `tools/doc_check.py`'s `check_resident_instructions`. The second
advisory carries no count and needs no change.

**Approach.** Use `_plural(growth, "line", "lines")`, with the inner quotes
single: `tools/ruff.toml` targets `py311` because these scripts are run by
whatever bare `python3` is on PATH, and same-quote nesting inside an f-string
is a syntax error before 3.12.

**Done when.** A one-line growth reports "grew 1 line", and a test pins it so
the next rewrite of this string cannot lose it again.

**Closed 2026-09-01, in the session that found it.** The new assertion was
confirmed to fail against `origin/main`'s `doc_check.py` - which already
carried `PL-BKQW` - and to pass after the fix.
