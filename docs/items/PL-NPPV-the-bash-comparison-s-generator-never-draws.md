---
id: PL-NPPV
title: The bash comparison's generator never draws while, until, elif or else, !, || between commands, >>, >|, <>, &>> or a closed descriptor, and no test holds the lexer's refusals to bash -n over mvdan/sh's published parser and error cases
priority: P3
effort: M
status: done
classes: test
feature: reader-checks
touches: subprojects/docket/tests/test_shell.py, subprojects/docket/tests/mvdan-sh
added: 2026-10-12
closed: 2026-10-18
pr: 1563
payoff: a lexer change that misreads a loop, a negation, an || or an append redirection fails CI, and the lexer's refusals are held to bash -n over 1,165 published cases
verify: grep -q 'def test_the_lexer_agrees_with_bash_n_on_mvdan_sh_cases' subprojects/docket/tests/test_shell.py
---

**Problem.** The bash comparison's generator never draws while, until, elif or else, !, || between commands, >>, >|, \<>, &>> or a closed descriptor, and no test holds the lexer's refusals to bash -n over mvdan/sh's published parser and error cases

Filed 2026-10-12 from the thread answering the owner's question of that day,
whether a published test corpus exists to verify this repository's lexers
against ("Agree with recs", project owner, 21:54 UTC). The measurements, sources
and rerunnable probes are in `/mnt/project-files/v0.6.0/lexer-corpora.md` and
`/mnt/project-files/v0.6.0/lexer-corpora-probes/`, outside the repository.

**What holds it now.** Since `PL-C4XY` (#1444) the lexer is compared with bash:
`test_the_lexer_reads_generated_commands_as_bash_does` in
`subprojects/docket/tests/test_shell.py` draws 300 derandomized scripts and
requires the commands bash runs to equal the commands the lexer reads. The
generator's statement table (`COMPOUND`) draws group, subshell, `if`, `time`,
assignment, array, `case`, `for`, `[[ ]]` and `(( ))`; its `SEPARATORS` draw
`;`, `&&`, `|`, `&` and `|&`; its redirections are eight forms plus `<<<`.
It never draws `while`, `until`, `elif`/`else`, `!`, `||` between commands,
`>>`, `>|`, `<>`, `&>>` or a closed descriptor, though `docket.shell` reads
them all.

**Measured 2026-10-12, so this is a coverage gap rather than a departure.**
23 hand-written scripts using those forms, each command running exactly once,
agreed with bash word for word through `test_shell.py`'s own `_bash_runs` and
`_lexer_runs`, once the harness's `RESERVED` took `while`, `until`, `elif`,
`else` and `!` and its `ENDS` took `||`.

**The published corpus.** mvdan/sh, the Go parser behind `shfmt`
(https://github.com/mvdan/sh, BSD-3-Clause), holds 570 parse cases in
`syntax/filetests_test.go` and 387 error cases in `syntax/parser_test.go`, each
confirmed against real bash, dash, mksh and zsh with `-n`. Over its 1,165
distinct inputs plus 717 Oils spec-test bodies
(https://github.com/oils-for-unix/oils, Apache-2.0), on 2026-10-12, 1,837 were
compared after 45 runtime-option inputs were set aside. The lexer's
`flat_reading(...).complete` and `bash -n -c` agreed on 1,626. The lexer
refused 2 that `bash -n` accepts and bash refuses on running (a backquote
holding a lone `"`), so none that bash would run. The lexer read 209 that bash
refuses: 197 grammar errors, 11 token-level (`((`, `$[`, `a[` unclosed) and one
harness artifact. About 4 seconds in all. POSIX's official suite, The Open
Group's VSC-PCTS, is licensed for twelve months, not redistributable, and tests
a shell's behaviour rather than its parse, so it is not usable here.

**Why it matters.** The four Bash guard hooks read through this lexer. A change
that misreads a loop or an `||` passes CI today, and the lexer's refusals are
held only to cases this repository thought of.

**Done when.** The generator also draws `while`, `until`, `elif`/`else`, `!`,
`||` between commands, `>>`, `>|`, `<>`, `&>>` and `n>&-` (the harness's
`RESERVED` and `ENDS` widened to match), and a test reads mvdan/sh's parse and
error inputs, vendored with their licence, and holds that the lexer never
reports incomplete an input `bash -n` accepts and bash runs.

**Generator check.** Work the owner asked for: regression cover for forms the
lexer already reads correctly.

**Resolved 2026-10-18.** The generator in `subprojects/docket/tests/test_shell.py`
now draws each form the done-when names. An `if` may carry `elif` and `else`.
Each condition that `!` makes fail skips a body that is only an assignment, so
every command still runs once. A `while` or `until` loop runs its body once,
because the body sets a flag the condition reads. Each depth has its own flag,
and a loop only opens a pipeline, since its flag is cleared by a command of
its own. `! S1 || S2` runs both sides. The redirections add `>>`, `>|`, `<>`,
`&>>` and `4>&-`, descriptor 4 because `p` writes its record to 3. The
harness's `RESERVED` took `elif`, `else`, `!`, `while` and `until`, and its
`ENDS` took `||`. An unseeded run of 3,000 scripts drew each new form between
467 and 1,909 times and disagreed with bash 5.2.21 on none.

`subprojects/docket/tests/mvdan-sh/` vendors mvdan/sh's 1,165 parse and error
inputs from commit `c873cb44a6a0ade219d132c7dcd837ff631a4173`, with its BSD
3-Clause notice and a README saying how they were taken.
`test_the_lexer_agrees_with_bash_n_on_mvdan_sh_cases` holds that the lexer
reads complete every input `bash -n` accepts, except the two inputs bash
refuses on running, a backquote holding a lone `"`. `bash -n` accepted 881 of
the inputs. The test takes about 3 seconds.
