---
id: PL-P95F
title: The hooks' shell_split drops an unquoted here-document's body whole, but bash runs a $( ) inside one, so cat <<EOF over $(git fetch --prune) passes no-prune-guard and the command runs; latent
status: untriaged
touches: .claude/hooks/shell_split.py, tests/unit
added: 2026-10-04
---

**Problem.** The hooks' shell_split drops an unquoted here-document's body whole, but bash runs a $( ) inside one, so cat \<\<EOF over $(git fetch --prune) passes no-prune-guard and the command runs; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

POSIX XCU § 2.7.4: with no part of the delimiter quoted, the body's parameter expansion, command substitution and arithmetic expansion run. `commands("cat <<EOF` / `$(git fetch --prune)` / `EOF")` returns only `cat`, so no-prune-guard allows it, while bash runs the substitution (`printf 'cat <<EOF\n$(echo SUBST-RAN)\nEOF\n' | bash` prints `SUBST-RAN`). The module's "What it does not read" list does not name it. Not a member of `PL-R417`: an expansion, not a continuation. Latent: the input is a Bash-tool command at run time.
