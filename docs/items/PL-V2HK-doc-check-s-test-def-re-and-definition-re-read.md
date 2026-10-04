---
id: PL-V2HK
title: doc_check's TEST_DEF_RE and DEFINITION_RE read a def or class line inside a triple-quoted string as a definition, so a cited test that does not exist passes and the candidates search gains terms; 20 such lines live, advisory only
status: untriaged
feature: one-answer
touches: tools/doc_check.py, tests/unit
added: 2026-10-04
recurrences: 2026-10-04 PL-4MLK withdrawn 2026-10-04 PL-R417
---

**Problem.** doc_check's TEST_DEF_RE and DEFINITION_RE read a def or class line inside a triple-quoted string as a definition, so a cited test that does not exist passes and the candidates search gains terms; 20 such lines live, advisory only

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

Python Language Reference § 2.1 and § 2.4.1: a triple-quoted string carries one logical line across physical lines, so a `def` inside one defines nothing.

- `TEST_DEF_RE`: a test file whose fixture string holds "def test_ghost():" makes `check_named_tests` accept a document naming `test_ghost`, which `ast` does not define. It also misses `async def test_...`.
- `DEFINITION_RE`, over `git diff -U0` in `changed_tokens`: changing a fixture string's `class Old:` to `class SimulationView:` with `def _refresh_view(self):` yields both names as search terms.

Live in form: 20 `def` and `class` lines sit inside triple-quoted strings in tracked Python (`tests/unit/test_agent_identity_check.py`:38, `tests/unit/test_contrast_check.py`:73), reaching only the candidates advisory; no cited test is a ghost today.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
