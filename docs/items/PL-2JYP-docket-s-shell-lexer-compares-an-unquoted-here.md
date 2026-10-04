---
id: PL-2JYP
title: docket's shell lexer compares an unquoted here-document's body with its delimiter one physical line at a time, cuts a ${...} at a newline, and closes a multi-line $( ) at a case pattern's ), so script_lines hands doc_check fragments as commands; latent
status: untriaged
feature: one-answer
touches: subprojects/docket/src/docket/shell.py, subprojects/docket/tests, tests/unit
added: 2026-10-04
---

**Problem.** docket's shell lexer compares an unquoted here-document's body with its delimiter one physical line at a time, cuts a ${...} at a newline, and closes a multi-line $( ) at a case pattern's ), so script_lines hands doc_check fragments as commands; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

POSIX XCU § 2.7.4 with § 2.2.3, § 2.3 rule 5 with § 2.6.2, and § 2.6.3 with § 2.9.4.3; bash 5.2.21 and dash agree on each.

- `script_lines` over "cat <<EOF", "a\" , "EOF", "echo inside-body", "EOF", "echo after" yields `echo inside-body` and `EOF` as commands, where both shells read the body to the second `EOF`; through `_make_mentions` a `make` line there names a phantom target.
- "echo ${y:-three" over "four}" yields `four}` as a command; both shells run `echo three four`.
- "x=$(case a in", "  a) echo A;;", "esac)" is cut at the case pattern's `)`, so `esac)` reads as a command.
- bash's `(( ))` and `[[ ]]` carried across lines are cut too; POSIX defines neither, so they count only if bash's grammar is in scope.

`PL-Q9LK`'s forms all still read whole. Latent: no tracked shell host or `sh` fence holds an unquoted here-document with a continued body line, a `${` left open at a line end, or a `$(case`.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
