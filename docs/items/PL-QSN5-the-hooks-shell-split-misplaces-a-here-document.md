---
id: PL-QSN5
title: The hooks' shell_split misplaces a here-document's body around a command substitution carried across lines - a body pending at a newline inside an unquoted $( ) or process substitution starts there, one opened in a double-quoted $( ) or a ${...} that closes on its own line is dropped and its lines read as commands, and one whose delimiter line goes on with the substitution's closing parenthesis runs to the end of the input - so a guarded command after it passes the no-prune, gate, floor and push-check guards while bash runs it; latent
priority: P2
effort: M
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/shell.py, .claude/hooks/shell_split.py, tests/unit/test_floor_interpreter_guard.py, tests/unit/test_no_prune_guard.py, tests/unit/test_push_check_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
payoff: a guarded command after a here-document beside a substitution carried across lines reaches the no-prune, gate, floor and push-check guards, as bash runs it
verify: grep -q 'def test_a_here_document_beside_a_substitution_carried_across_lines_hides_no_prune' tests/unit/test_no_prune_guard.py && grep -q 'def test_a_push_after_a_here_document_its_substitution_closes_is_checked' tests/unit/test_push_check_guard.py && grep -qF 'x=$(echo a\necho b); PARSE' tests/unit/test_floor_interpreter_guard.py
---

**Problem.** The hooks' shell_split misplaces a here-document's body around a command substitution carried across lines - a body pending at a newline inside an unquoted $( ) or process substitution starts there, one opened in a double-quoted $( ) or a ${...} that closes on its own line is dropped and its lines read as commands, and one whose delimiter line goes on with the substitution's closing parenthesis runs to the end of the input - so a guarded command after it passes the no-prune, gate, floor and push-check guards while bash runs it; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`_Reader` in `.claude/hooks/shell_split.py`, the one shell reader the four Bash
guards share. POSIX XCU § 2.3 rule 5 reads a `$(` to its end as part of the
token, and § 2.7.4 starts a here-document's body after the next newline, which
for a `<<` ahead of a substitution carried across lines is the newline after
the line the substitution closes on. `_Reader` reads an unquoted `$(` or `<(`
inline, as operators, so it starts the pending bodies at a newline inside the
substitution; the nested reader for a double-quoted `$( )` or a `${...}`
returns at its `)` with the heredocs it holds pending, which never reach the
outer reader; and `_body` ends a body only at a logical line equal to the
delimiter.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against bash 5.2.21 and dash, with a prune as the guarded command:

```text
cat <<EOF; x=$(echo a
echo b); git fetch --prune
body
EOF

x="$(cat <<EOF)"; git fetch --prune
it's
EOF

git commit -m "$(cat <<'EOF'
PL-0000: a message
EOF)" && git push -u origin HEAD
```

For the first, `shell_split` took the second line through `EOF` for the body,
`commands` returned `cat` and `echo a`, and the no-prune, gate and floor guards
allowed it, where bash and dash both printed `body` and ran the prune; with
`<(` in place of `$(` bash does the same. For the second, the body's quote left
`segments` None, so the gate and floor guards fail open, and bash read `it's`
as the body and ran the prune, as dash did before refusing the third line. For
the third, `commands` returned only `git commit -m`, so the push-check guard
saw no push, where bash ended the body at `EOF)`, warned that the
here-document was delimited by end-of-file, and committed and pushed; dash
refuses the script. Controls: a double-quoted `$( )` spanning lines with a
heredoc pending outside it is read correctly, and a subshell spanning lines
starts the body inside it in both shells, as the splitter does. Latent: the
input is a Bash-tool command at run time and no session is known to have
written one, though the third is one slip from the commit form sessions use,
which closes the substitution on a line of its own.

**Reproduced 2026-10-10 at triage** on this branch at `b6b9c382`, whose readers are `main`'s at `fe2e5132`, with a prune as the guarded
command. The first form, and the same with `<(` for `$(`: `commands` read `cat`
and `echo a` and no prune, and the no-prune and floor guards both allowed it.
The second: `segments` answered None, so the floor guard allowed the parse it
held; the no-prune guard refused it, since `commands` reads the tokens ahead
of the unreadable quote, the prune among them. The third: `commands` read only
`git commit -m`. So the no-prune guard's test pins the first form and its `<(`
twin, which fail today, the push-check guard's the third, and the floor guard's
`RESHAPED` table all four.

**Why it matters.** `no-prune-guard.sh` promises every ref-deleting spelling
through every command shape `shell_split.py` reads, and a here-document and a
`$( )` are both shapes it reads; a prune can delete the only copy of an item
captured on a branch nobody merged (`PL-HKF4`).

**Generator check.** A member of `PL-R417`: the reader starts or ends a
here-document's body at the wrong physical line where a substitution carries a
command across lines, as `PL-97CF`, a member, did for a continuation inside a
`<<-` and a delimiter one joins. The same forms inside a backtick or in
arithmetic belong to constructs the module lists as unread, and the sweep
extended that list to say that a `<<` inside a backtick opens a heredoc of the
command around it. `PL-P95F`, open, changes the same reader for the
substitutions inside an unquoted body; the two are best worked in one branch.

**Done when.** `_Reader` reads an unquoted `$( )` and a `<( )` as the nested
commands they are when placing a pending body, carries a nested reader's
pending heredocs out to the line bash reads them from, and ends a body at a
delimiter line the substitution's `)` follows, pinned by a case for each form
above in the floor guard's `RESHAPED` table and in the no-prune and push-check
guards' tests, failing on today's reader.

**Decided 2026-10-06.** Fixed once, in the shell reader `PL-JNYL` merges from
the hooks' and docket's two, which opens `PL-R417`'s shell batch (project
owner, 2026-10-06, ratified, over fixing each shell reader in place).
