---
id: PL-97CF
title: The hooks' shell_split reads an operator a backslash-newline splits as two operators and matches an unquoted here-document's delimiter against physical lines, so cat <<\ over -EOF hides a following git fetch --prune from no-prune-guard, gate-status-guard and floor-interpreter-guard while bash and dash run it; latent
status: untriaged
feature: one-answer
touches: .claude/hooks/shell_split.py, tests/unit
added: 2026-10-04
recurrences: 2026-10-04 PL-P95F withdrawn 2026-10-04 PL-R417
---

**Problem.** The hooks' shell_split reads an operator a backslash-newline splits as two operators and matches an unquoted here-document's delimiter against physical lines, so cat \<\<\ over -EOF hides a following git fetch --prune from no-prune-guard, gate-status-guard and floor-interpreter-guard while bash and dash run it; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

POSIX XCU § 2.2.1 removes a backslash-newline before tokens are split, § 2.3 reads an operator as the longest match, and § 2.7.4 lets a backslash-newline continue a line in an unquoted here-document's body. `_Reader.read` removes one between words, but `_operator_at` reads the raw text, and `_body` keeps only `(word, strip_tabs)`, so it cannot tell a quoted delimiter from an unquoted one.

- `segments("make check &\` over `& tail -5 log")` reads `&`, `&` where both shells read `&&`; `|` over `|` reads as two pipes.
- **Bypass:** "cat <<\" over "-EOF", a tab-indented "hello" and "EOF", then "git fetch --prune": `commands` returns only `cat`, its delimiter read as `-EOF`, while bash 5.2.21 and dash print hello and run the command. no-prune-guard, gate-status-guard (with `make check | tail -5` in that place) and floor-interpreter-guard (with `python3 -m compileall src/`) all allow it, though each denies the command written alone. "cat <<\" over "< word" is read as nothing by `segments`, which the gate and floor guards treat as allow.
- **Bypass, bash only:** "cat <<EOF", "abc", "EO\" over "F", then "git fetch --prune": `commands` reads the rest as body, while bash joins the delimiter and runs the command; dash does not.
- The other direction, "abc\" over "EOF" in the body, denies a command neither shell runs.

Latent: the input is a Bash-tool command at run time and no tracked file feeds it; the module's docstring names bash 5.2 as its reference.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
