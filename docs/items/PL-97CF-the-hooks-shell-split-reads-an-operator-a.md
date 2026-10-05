---
id: PL-97CF
title: The hooks' shell_split reads an operator a backslash-newline splits as two operators and matches an unquoted here-document's delimiter against physical lines, so cat <<\ over -EOF hides a following git fetch --prune from no-prune-guard, gate-status-guard and floor-interpreter-guard while bash and dash run it; latent
priority: P2
effort: S
status: ready
classes: defect
feature: one-answer
touches: .claude/hooks/shell_split.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by PL-R417's shell slice, 2026-10-05
added: 2026-10-04
payoff: a guarded command after a here-document a continuation reshapes, or after a ${...} carried across lines, reaches the prune, gate and floor guards, so none of the three can be passed by spelling a command the way bash still runs it
verify: grep -q 'hook commands, an operator a backslash-newline splits is one operator' tests/unit/test_doc_check.py
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

**Why it matters.** `.claude/hooks/shell_split.py` is the one reading four
Bash guard hooks take of a command before it runs, and three of them hold a
floor: `no-prune-guard.sh` the remote-tracking refs, `gate-status-guard.sh` a
gate's exit status, and `floor-interpreter-guard.sh` the interpreter a floor
check runs under. A command the splitter reads as less than bash runs passes
all three in silence, so each guarantee is void for that command while the
guard reports nothing. Latent: it takes a command written to the shape, and no
session has been seen to write one.

**Reproduced 2026-10-05, at triage.** On `main` at `c479363e`, under python3
3.11.15, through each hook end to end with the payload the harness sends.
`cat <<\` over `-EOF`, a tab-indented body and a tab-indented `EOF` before the
guarded command; `cat <<\` over `< word` before it; and `cat <<EOF`, `abc` and
`EO\` over `F` before it are each allowed by all three guards, which deny the
guarded command written alone. `cat <<EOF`, `abc\` over `EOF`, the guarded
command and `EOF` is denied by all three. bash 5.2.21 runs the guarded command
in the first three and not in the fourth; dash 0.5.12 agrees but on the third,
whose body it reads to the end, and refuses the second, having no `<<<`. And
`segments` reads `make check &\` over `& tail -5 log` as `&`, `&`, and `|`
over `|` as two pipes, where both shells read `&&` and `||`.

**Found at triage: a `${...}` carried across lines.** Bash reads a parameter
expansion to the `}` that closes it, across newlines (Bash Reference Manual
§ 3.5.3; POSIX XCU § 2.3 rule 5 and § 2.6.2), and the splitter ends the word at
the newline. So `echo ${x:-<<EOF` over `}`, then the guarded command and `EOF`,
reads the `<<` inside the expansion as a here-document whose body hides the
command: all three guards allow it, while bash prints the expansion and runs
the command. The same fact in the same reader, so it is this item's rather than
a new one.

**Done when.** `shell_split` reads, as bash 5.2 does: an operator a
backslash-newline splits as the one operator (`&&`, `||`, `<<-`, `<<<`); an
unquoted here-document's body in logical lines, a line ending in an odd run of
backslashes going on to the next and the delimiter compared with the joined
line, its leading tabs stripped for `<<-`, where a quoted delimiter's body
keeps its lines as written; and a `${...}` to its closing `}` across lines,
any `$( )` inside it read as the command it runs. Where bash and dash differ, on
a delimiter a continuation splits, bash is followed, the module's stated
reference. Each bypass above is denied by the three guards and the false
refusal allowed, and `PL-R417`'s guard gains a `hook commands, ` case per form,
each failing on today's reader.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
