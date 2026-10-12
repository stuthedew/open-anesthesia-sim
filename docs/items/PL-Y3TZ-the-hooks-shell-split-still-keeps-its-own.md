---
id: PL-Y3TZ
title: The hooks' shell_split still keeps its own reserved-word, assignment and redirection tables beside docket.shell's after PL-JNYL merged the lexers, so a quoted "if", X+=1 and {fd}> read differently in a hook than in docket
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: .claude/hooks/shell_split.py, subprojects/docket/src/docket/shell.py, subprojects/docket/tests/test_shell.py, .claude/hooks/floor-interpreter-guard.sh, .claude/hooks/gate-status-guard.sh, tests/unit/test_gate_status_guard.py, tools/doc_check.py, tools/fact_home_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
closed: 2026-10-12
pr: 1469
payoff: a hook finds the command a line runs by the same grammar docket reads it by
verify: grep -q 'def test_shell_split_reads_command_words_as_docket_shell_does' tests/unit/test_gate_status_guard.py
---

**Problem.** The hooks' shell_split still keeps its own reserved-word, assignment and redirection tables beside docket.shell's after PL-JNYL merged the lexers, so a quoted "if", X+=1 and {fd}> read differently in a hook than in docket

- Reserved words that open a command: `shell_split.GROUPING`, `OPENS_A_COMMAND` and `_past_openers` beside `shell.OPENS_A_COMMAND` and `_Grammar.word`. On `"if" make check` docket takes the quoted word as no reserved word; `shell_split.command_words` drops it, because its flat tokens have lost the quoting, and returns `make check`.
- An assignment word: `shell_split.ASSIGNMENT` beside `shell._assigns_a_list`. On `X+=1 make check` the hook reads `X+=1` as the command, so the gate guard sees no `make`; docket reads an assignment, as bash 5.2 does. They also part on a non-ASCII name.
- Redirections and descriptors: `shell_split.REDIRECTIONS`, `SEPARATORS` and `_redirection` beside `shell.HEADS` and `_names_a_descriptor`; the operator sets agree (`PL-P72R` unified `OPERATORS` only).
- A Python interpreter word: the same `INTERPRETER` regex in `floor-interpreter-guard.sh` and `gate-status-guard.sh`; they agree, applied to the bare word and the basename by design.

**Why it matters.** Each copy is held to the others by nothing, so the first input they part on is answered one way by docket and another by the hook or check a session trusts at that moment; every pair below was read at both sites by the sweep, and the parting input is the sweep's reading, to re-confirm at start.

**Done when.** `shell_split` takes these tables from `docket.shell` (it already imports docket), and a test pins `"if" make check` and `X+=1 make check` through the gate guard.

**Generator check.** A member of `PL-5DZ8`, filed by that head's closing sweep on 2026-10-12 and named in its `root-cause-of:`. The fact is the head's: which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it. It is neither a post-close instance nor a new generator.

**Resolution, 2026-10-12.** The quoting was the obstacle: the hooks' flat
tokens had lost it, so no table there could tell `"if"` from `if`. So
`docket.shell`'s lexer tags the flat tokens itself - `Reserved` where its
`_Grammar` reads a word opening a command, `time`'s options included, and
`Assignment` for a word opening with an unquoted `name=` or `name+=` - and
`shell_split` reads the tags, `REDIRECTIONS` and `HEADS` from it. `_Grammar`
heads a command after every `)` now, as bash 5.2.21 does (`if (true) then`
runs), which `commands` relied on. The interpreter pattern is
`shell_split.PYTHON`, read by both guards, and `tools/doc_check.py`'s third
copy of the redirection set imports docket's. A side effect closes
`PL-DCHW`'s three known gaps: after an assignment or a redirection docket
marks no `time` or `!` reserved, so the gate guard refuses them.
