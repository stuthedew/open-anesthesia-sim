---
id: PL-K1D6
title: Readers that split git or JSON output with str.splitlines() also break at U+2028, U+2029, U+0085 and \x1c-\x1e, so a ref name, a transcript record or a Python source line holding one reads as two; latent
priority: P3
effort: S
status: done
classes: defect
touches: subprojects/docket/src/docket/vcs.py, tools/context_reading.py, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-05
pr: 1364
payoff: A branch, tag or transcript record holding a Unicode line separator is answered about as itself, not as two refs that do not exist or a request the budget reading never counts
verify: grep -q 'def test_a_ref_name_holding_a_line_separator_is_read_as_one_ref' subprojects/docket/tests/test_vcs.py && grep -q 'def test_a_record_holding_a_raw_line_separator_is_read_as_one_record' tests/unit/test_context_reading.py
---

**Problem.** Readers that split git or JSON output with str.splitlines() also break at U+2028, U+2029, U+0085 and \x1c-\x1e, so a ref name, a transcript record or a Python source line holding one reads as two; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`str.splitlines()` breaks at more than `\n`. Git prints ref names raw and `check-ref-format` allows U+2028, so `vcs._unlanded_refs` (1574), `stranded` (4870), `ref_walk` (5634), `tags` (3675) and `_remotes` (1831) read a branch holding one as two unreadable names and drop it from `unlanded`; `remote_heads` and `_deleted_on_remote` already split on `\n`. `context_reading.read` splits a JSONL transcript the same way, and JSON.stringify leaves U+2028 raw, so one such record reads as two unread lines and is dropped - named in the report, so not silent. `fixture_id_check.scan_python` rebuilds a file's source from `splitlines()`, turning a raw U+2028 inside a string literal into a newline, and `ast.parse`'s `SyntaxError` is not caught by `collect` (377-387) on a file Python accepts. Not a member of `PL-R417`: a line read as two, not a statement read as one line. Latent: no such ref, record or literal exists today.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `8cc0698d`, with git 2.43.0: `git check-ref-format` accepts a branch name holding U+0085, U+2028 or U+2029, and refuses the ASCII separators. In a scratch repository holding one tag spelled `v1`, U+2028, `x` and one unmerged branch spelled `claude/a`, U+2028, `b`, `vcs.tags` returned two names, `v1` and `x`, and `vcs._unlanded_refs` against `main` with `include_remote=False` listed three refs for two branches, with `candidates` `claude/a` and `b`, `unlanded` empty and both fragments in `unreadable`. `context_reading.read` over one assistant record whose text holds a raw U+2028, as `json.dumps` with `ensure_ascii=False` writes it and `json.loads` reads it whole, returned no requests and `unread=2`. `fixture_id_check.scan_python` on a one-line module holding U+2028 in a string, which `compile()` accepts, raised `SyntaxError: unterminated string literal`.

**Why it matters.** Each such name is one git accepts, and each reader then answers about refs that do not exist: `_unlanded_refs` takes the branch's unmerged work out of `unlanded` and names it as two unreadable refs nobody can check out, and `tags` reports a tag `v1` the repository does not hold, in the set `docket release` reads to decide whether the current version was tagged. `context_reading.read` loses the record's usage, so where it was the latest request the spend reading behind the 150,000-token reset comes from the request before it, though the report does name the two unread lines. Latent: no ref, transcript record or tracked source line holds such a character today.

**Generator check.** A member of `PL-4YVK`: where one line ends in line-oriented text, which `str.splitlines()` breaks at more characters than git's output or a transcript does. With `PL-139L` and `PL-PK4B` before it, four items misread that fact and no head stated it, so it was recorded as a generator at triage, 2026-10-04.

**Done when.** `_unlanded_refs`, `stranded`, `ref_walk`, `tags` and `_remotes` in `vcs` split git's listings on `\n` alone, as `remote_heads` and `_deleted_on_remote` already do, and `context_reading.read` splits a transcript on `\n` alone, so a ref name or a JSONL record holding U+0085, U+2028 or U+2029 is read as one. `test_a_ref_name_holding_a_line_separator_is_read_as_one_ref` in `subprojects/docket/tests/test_vcs.py` creates such a tag and branch in a real repository and gets each back whole from `tags` and `_unlanded_refs`, and `test_a_record_holding_a_raw_line_separator_is_read_as_one_record` in `tests/unit/test_context_reading.py` reads such a record as one request with nothing unread. The `fixture_id_check.scan_python` case is `PL-PK4B`'s, `ready` with its own test and the same `split("\n")` repair, and is left to it.
