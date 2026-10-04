---
id: PL-K1D6
title: Readers that split git or JSON output with str.splitlines() also break at U+2028, U+2029, U+0085 and \x1c-\x1e, so a ref name, a transcript record or a Python source line holding one reads as two; latent
status: untriaged
touches: subprojects/docket/src/docket/vcs.py, tools/context_reading.py, tools/fixture_id_check.py, subprojects/docket/tests, tests/unit
added: 2026-10-04
---

**Problem.** Readers that split git or JSON output with str.splitlines() also break at U+2028, U+2029, U+0085 and \x1c-\x1e, so a ref name, a transcript record or a Python source line holding one reads as two; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`str.splitlines()` breaks at more than `\n`. Git prints ref names raw and `check-ref-format` allows U+2028, so `vcs._unlanded_refs` (1574), `stranded` (4870), `ref_walk` (5634), `tags` (3675) and `_remotes` (1831) read a branch holding one as two unreadable names and drop it from `unlanded`; `remote_heads` and `_deleted_on_remote` already split on `\n`. `context_reading.read` splits a JSONL transcript the same way, and JSON.stringify leaves U+2028 raw, so one such record reads as two unread lines and is dropped - named in the report, so not silent. `fixture_id_check.scan_python` rebuilds a file's source from `splitlines()`, turning a raw U+2028 inside a string literal into a newline, and `ast.parse`'s `SyntaxError` is not caught by `collect` (377-387) on a file Python accepts. Not a member of `PL-R417`: a line read as two, not a statement read as one line. Latent: no such ref, record or literal exists today.
