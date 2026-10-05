---
id: PL-V2HK
title: doc_check's TEST_DEF_RE and DEFINITION_RE read a def or class line inside a triple-quoted string as a definition, so a cited test that does not exist passes and the candidates search gains terms; 20 such lines live, advisory only
priority: P3
effort: M
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit/test_doc_check.py, subprojects/docket/src/docket/python.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by PL-R417's Python slice, 2026-10-05
added: 2026-10-04
payoff: a document's test citation is checked against the tests the suite defines, so a fixture string can no longer stand in for a deleted test, and the close-out sweep searches only for names the change defines
verify: grep -qF '"test definitions, ' tests/unit/test_doc_check.py && grep -qF '"changed definitions, ' tests/unit/test_doc_check.py
recurrences: 2026-10-04 PL-4MLK withdrawn 2026-10-04 PL-R417
---

**Problem.** doc_check's TEST_DEF_RE and DEFINITION_RE read a def or class line inside a triple-quoted string as a definition, so a cited test that does not exist passes and the candidates search gains terms; 20 such lines live, advisory only

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

Python Language Reference § 2.1 and § 2.4.1: a triple-quoted string carries one logical line across physical lines, so a `def` inside one defines nothing.

- `TEST_DEF_RE`: a test file whose fixture string holds "def test_ghost():" makes `check_named_tests` accept a document naming `test_ghost`, which `ast` does not define. It also misses `async def test_...`.
- `DEFINITION_RE`, over `git diff -U0` in `changed_tokens`: changing a fixture string's `class Old:` to `class SimulationView:` with `def _refresh_view(self):` yields both names as search terms.

Live in form: 20 `def` and `class` lines sit inside triple-quoted strings in tracked Python (`tests/unit/test_agent_identity_check.py`:38, `tests/unit/test_contrast_check.py`:73), reaching only the candidates advisory; no cited test is a ghost today.

**Reproduced 2026-10-05, at triage.** On Python 3.11.15, against `main` at `a8d9b02a`: `check_named_tests` over a scratch tree whose one test file holds `def test_ghost():` inside a triple-quoted string reports no error for a document citing `test_ghost`, and reports `async def test_awaited()` as defined by no test; `changed_tokens` over a fixture string rewritten from `class Old:` with `def _old(self):` to `class SimulationView:` with `def _refresh_view(self):` returns `SimulationView`, `_refresh_view` and `_old` beside the file's own name. Over the 221 tracked Python files, read by 3.14.7's tokenizer, 20 `def` and `class` lines sit inside a string, in five test files, and none is a `def test_` line under the two test roots.

**Why it matters.** `check_named_tests` is what holds a document's claim that a named test pins it, and a fixture string defining the cited name makes a dead citation pass, the silent wrong answer the check exists to catch, while an `async def` test is reported as defined by nothing. The candidates sweep seeds its search with names no code defines, so a close-out reads lines about nothing. Both readers take a physical line for a statement.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** Both read a Python file's definitions from its statements, through docket's one Python reader, `read_logical_lines`: a `def` or `class` inside a string is none, an `async def` test is one, and a changed line counts toward the definition whose statement holds it, a signature continued across lines included. A file the tokenizer refuses is named rather than read as statements: a citation that only such a file may define is declined, neither passed nor failed, and the sweep reads that file's changed lines a line at a time and says so. `CONTINUED_STATEMENTS` gains `test definitions, ` and `changed definitions, ` cases, each failing on today's readers.
