---
id: PL-0CJC
title: docket.shell's grammar does not take the word after function NAME {, time -p or coproc for the head of a command, so a case, a (( or a [[ there is lexed as words: a case pattern's parenthesis closes the enclosing command substitution, and a newline inside the (( or [[ ends a line, so script_lines, shell_words and flat_reading cut one command into fragments; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
milestone: v0.5.24
touches: subprojects/docket/src/docket/shell.py, subprojects/docket/tests/test_shell.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1433
payoff: a case, (( or [[ after function NAME {, time -p or coproc is read as one command by docket, doc_check and the Bash guards alike, instead of as fragments that each read as complete
verify: grep -q 'def test_a_compound_command_after_function_time_p_or_coproc_is_read_whole' subprojects/docket/tests/test_shell.py
---

**Problem.** docket.shell's grammar does not take the word after function NAME {, time -p or coproc for the head of a command, so a case, a (( or a [[ there is lexed as words: a case pattern's parenthesis closes the enclosing command substitution, and a newline inside the (( or [[ ends a line, so script_lines, shell_words and flat_reading cut one command into fragments; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
docket's shared readers. `shell._Grammar.word`
marks a command's head through `OPENS_A_COMMAND`, which does not reach the word
after `function NAME {`, after `time -p`, or after `coproc`. bash reads a
compound command there (POSIX XCU § 2.4 reserved words, § 2.9.4 compound
commands, § 2.6.3 command substitution; Bash Reference Manual § 3.3
`function`, § 3.2.6 `coproc`, § 3.2.3 `time -p`), so a `case` pattern's `)`
belongs to the `case`, and a newline inside `((` or `[[` does not end the
command.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against bash 5.2.21 (`bash -n` passes, and the script prints `b`, so
its first three lines are one command; dash has no `function` keyword):

```text
x=$(function f { case a in
  a) echo in1 ;;
esac; }; f)
echo b
```

`script_lines` gives three pieces, the first ending after `echo in1 ;;`, and
the substitution's body is read as ending at the pattern's `)`.
`function g { ((1 +` over `2)) && ...; }` and `time -p ((1 +` over `2))` are
both cut after the `+`; on one line, `x=$(time -p case a in a) p in1;; esac)`
closes at `a)`, and `coproc case ...` the same. Also seen, and left to the fix
to settle: an unended `[[` at the end of the input is read on rather than
declined, where an unended `$(` is declined and `bash -n` refuses both.

Latent: no tracked script or fence holds `function NAME {`, `time -p` or
`coproc` followed by `case`, `((` or `[[`.

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`: `script_lines` still cuts
the first form into three pieces, the first ending after `echo in1 ;;`;
`function g { ((1 +` and `time -p ((1 +` are still cut after the `+`; and both
one-line forms still close the substitution at `a)`, where a plain `$(case a
in a) ...; esac)` is read whole. bash 5.2.21 still prints `in1` then `b`. A
`git grep` outside `docs/items/` finds none of the three forms.

**Why it matters.** `docket.shell` is the one shell reader that docket's
verify audits, `tools/doc_check.py`'s workflow readers and, through
`.claude/hooks/shell_split.py`, the Bash guards share (`PL-JNYL`), so a command
it cuts short is misread by all of them at once: an arm read as a command, a
guarded command after the fragment read in the wrong place. Nothing warns,
because every piece reads as complete.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is the gap
closed `PL-2JYP`'s and `PL-M3M4`'s fixes left; the
rewrite in `#1390` kept it. Re-read 2026-10-11: latent, so an ordinary item
under that closed, spent head; found live, it would reopen it.

**Done when.** The word after each of the three is read as a command's head,
and each form above is a shell case in the reader's tests holding docket to
bash's reading.

**Done 2026-10-12** (`#1433`). `docket.shell._Grammar` reads a head past what
a word in the new `LEADS` takes before its command, as bash 5.2.21's parse.y
does (`special_case_tokens`, `reserved_word_acceptable`): after `time`, its
`-p`, and a `--` after either; after the name `function` takes, though not on
the name itself; and after `coproc` and the name it may take, unless the word
there is the `for` or `select` it runs. A newline or an operator ends what a
`LEADS` word waits for. The unended `[[` this brief left to the fix is
declined, at the end of the input and at the `)` closing its `$( )`, as an
unclosed `$(` is: read on, it took every line left for the words of its test.
`flat_reading` reads it incomplete, so the gate and floor guards fail open on
it as on any command bash refuses (`PL-WGFY`). An unclosed subshell or `case`
is still read a line at a time, as every compound command docket does not
track is - an `if` with no `fi` reads as its lines - since reading those lines
on takes no command for a word. Pinned by
`test_a_compound_command_after_function_time_p_or_coproc_is_read_whole` (nine
scripts), `test_a_case_after_time_p_or_coproc_on_one_line_stays_in_its_substitution`
(the brief's one-line forms) and `test_a_test_bash_finds_unclosed_is_unreadable`
in `subprojects/docket/tests/test_shell.py`, all twelve cases red on `main`,
each script run through bash 5.2.21 first. bash also reads a reserved word
after a closing word such as `fi` or `]]`, where docket still takes none:
filed as `PL-9NMR`.
