---
id: PL-P95F
title: The hooks' shell_split drops an unquoted here-document's body whole, but bash runs a $( ) inside one, so cat <<EOF over $(git fetch --prune) passes no-prune-guard and the command runs; latent
priority: P2
effort: S
status: ready
classes: defect
touches: .claude/hooks/shell_split.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: The guard that stops a prune deleting the only copy of an unmerged item sees one inside an unquoted here-document substitution, which bash runs
verify: grep -q 'def test_a_prune_in_an_unquoted_heredoc_substitution_is_refused' tests/unit/test_no_prune_guard.py
recurrences: 2026-10-06 PL-X43T withdrawn 2026-10-06 PL-R417, 2026-10-06 PL-VJPH withdrawn 2026-10-06 PL-R417, 2026-10-06 PL-QSN5 withdrawn 2026-10-06 PL-R417, 2026-10-06 PL-1R9S withdrawn 2026-10-06 PL-R417
---

**Problem.** The hooks' shell_split drops an unquoted here-document's body whole, but bash runs a $( ) inside one, so cat \<\<EOF over $(git fetch --prune) passes no-prune-guard and the command runs; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

POSIX XCU § 2.7.4: with no part of the delimiter quoted, the body's parameter expansion, command substitution and arithmetic expansion run. `commands("cat <<EOF` / `$(git fetch --prune)` / `EOF")` returns only `cat`, so no-prune-guard allows it, while bash runs the substitution (`printf 'cat <<EOF\n$(echo SUBST-RAN)\nEOF\n' | bash` prints `SUBST-RAN`). The module's "What it does not read" list does not name it. Not a member of `PL-R417`: an expansion, not a continuation. Latent: the input is a Bash-tool command at run time.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `8cc0698d`: `shell_split.commands` over the three lines `cat <<EOF`, `$(git fetch --prune)` and `EOF` returned `[['cat']]`, and `words` returned `cat`, `<<`, `EOF` and `;`, the body gone. Fed that command as a Bash payload, `.claude/hooks/no-prune-guard.sh` exited 0 with no deny, while `echo $(git fetch --prune)` was denied. Bash 5.2.21 runs the body's substitution: `printf 'cat <<EOF\n$(echo SUBST-RAN)\nEOF\n' | bash` printed `SUBST-RAN`. No `KNOWN_GAPS` row in `tests/unit/test_no_prune_guard.py` pins the shape, and neither the guard's "Matched on the words" list nor the module's "What it does not read" list names it.

**Why it matters.** `no-prune-guard.sh` exists because a prune can delete the only surviving copy of an item captured on a branch nobody merged (`PL-HKF4`), and its header promises every ref-deleting spelling through every command shape `shell_split.py` reads, a `$( )` included. A here-document is a shape it reads, and it drops the body whole whatever the delimiter's quoting, so the one shape whose body bash expands is the one the guard cannot see. Latent: the here-documents sessions write here quote their delimiter, as `<<'EOF'`, whose body bash leaves alone.

**Generator check.** An instance of `PL-61FT`'s fact, what a shell command does when run: which program it runs, filed after that head closed on 2026-09-26: the one shell reader the hooks share drops a body bash expands. With `PL-GZXY`'s first half, the second such instance since the close; a third would make the head's fix one that did not hold. It changes `.claude/hooks/shell_split.py`, as `PL-97CF` in `PL-R417`'s shell slice does, so the two are best worked in one branch.

**Done when.** `shell_split.commands` reads each `$( )` in the body of a here-document whose delimiter has no quoted part as a command it runs, and still drops the rest of that body and every body under a quoted delimiter as text. `test_a_prune_in_an_unquoted_heredoc_substitution_is_refused` in `tests/unit/test_no_prune_guard.py` has the guard deny `cat <<EOF` over `$(git fetch --prune)` and over the same with `<<-EOF`, while the quoted-delimiter bodies `test_only_a_heredoc_body_is_removed` allows, and the gate guard's unquoted `cat <<-EOF` body of plain text, stay allowed.
