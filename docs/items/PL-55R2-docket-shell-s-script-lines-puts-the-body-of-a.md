---
id: PL-55R2
title: docket.shell's script_lines puts the body of a here-document whose delimiter has no quoted part in no piece, so a substitution in that body, which bash runs (PL-P95F), is a command no per-piece reader sees: doc_check's _make_mentions, workflow_commands and workflow_runs' line-at-a-time fallback all miss it; latent
priority: P3
effort: S
status: ready
classes: defect
feature: shell-reads-as-bash
touches: subprojects/docket/src/docket/shell.py, subprojects/docket/tests/test_shell.py, tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-12 triage pass
added: 2026-10-12
payoff: a command in an unquoted here-document body is checked by every doc_check reader that reads a script a piece at a time, as bash runs it
verify: grep -q 'def test_script_lines_hands_a_here_document_body_s_substitutions_a_piece' subprojects/docket/tests/test_shell.py && ! grep -qF 'id="PL-55R2"' subprojects/docket/tests/test_shell.py
---

**Problem.** docket.shell's script_lines puts the body of a here-document whose delimiter has no quoted part in no piece, so a substitution in that body, which bash runs (PL-P95F), is a command no per-piece reader sees: doc_check's _make_mentions, workflow_commands and workflow_runs' line-at-a-time fallback all miss it; latent

**Found 2026-10-12** by `PL-C4XY`'s bash comparison in
`subprojects/docket/tests/test_shell.py`, which runs generated scripts through
bash with every command recording its words and compares them with docket's
reading, whole and summed over `script_lines`' pieces. The whole reading
matched bash on every script; the pieces missed each command a body ran.

**Reproduced 2026-10-12** on `main` at `98673556`, for this script:

```text
cat <<EOF
body $(p from-a-body) line
EOF
p after
```

```text
bash runs:                    cat; p from-a-body; p after
shell_words(script) clauses:  cat << EOF  and  p after,  and the body's  p from-a-body
script_lines(script) pieces:  'cat <<EOF'   'p after'
```

So each piece reads whole, and no piece holds `p from-a-body`.
`script_lines`' docstring says a body belongs to no piece "since bash reads
them as input rather than as commands", which `PL-P95F` made untrue for a body
whose delimiter has no quoted part: bash runs its substitutions (Bash Reference
Manual §3.6.6 "Here Documents").

**Reach.** Three readers in `tools/doc_check.py` take a script a piece at a
time: `_make_mentions` (a `make` target a fenced sample's body substitution
names is not a mention), `workflow_commands`, and `workflow_runs` where one
`shell_words` pass cannot read a step's script to its end. Latent: on
2026-10-12 none of the 60 workflow steps has a body substitution the pieces
lose, and the one fenced sample that does is `PL-GJKN`'s own example in its
brief.

**Why it matters.** `script_lines` is how `tools/doc_check.py` reads what a
workflow's `run:` steps and a fenced shell sample execute, a piece at a time,
so a command in an unquoted here-document's body escapes every check made on
those pieces: a path it names is not held to the tree, and a `make` target it
names is no mention. `PL-P95F` closed the hole for the Bash guards, which read
a command whole; the per-piece readers still have it, and `PL-C4XY`'s
comparison subtracts a body's commands from the pieces' sum to pass, so a
regression there would go unseen.

**Not a recurrence of `PL-GJKN`**, which `docket new` matched on the shared
`touches`: that item is where a nested body ends inside an expanded body, a
rule of the lexer's single pass, and this is which piece `script_lines` hands a
body's substitutions to, with the pass reading them correctly. The match is
withdrawn because of this paragraph.

**Generator check.** Found by `PL-C4XY`'s comparison, which is what stops a
departure of this kind reaching `main` from now on; read against `bin/docket
generators --misread` on 2026-10-12, it misreads no recorded fact.

**Route, measured 2026-10-12.** Keep the line pieces, and add each outermost
substitution that `_Lexer.expanded` reads in a top-level unquoted body, which
lies in a gap between two pieces, as a piece of its own: record a span where
the call grew `bodies`, in a new list `expanded` rolls back with the rest of
its state on `_Unreadable`, keep the outermost spans, and merge them into the
pieces in offset order. Refuted: a body and its delimiter in the opening
line's piece, since pieces would then hold input text, which breaks
`check_coverage_gate`'s substring test, `_make_mentions`' line fallback, and
`workflow_commands`' contract and its test. With the route, `_make_mentions`
reads a body's `$(make check)` as a mention on the body's line and
`workflow_commands` yields it, so its paths are held to the tree, while the
one-word command that is the substitution itself names no program a check
resolves. `workflow_commands`' docstring sentence that a body and delimiter
are no line at all is amended, and the comparison's `p top-body` command and
the subtraction that drops it go.

**Done when.** Every command bash runs from a script is a command of one
`script_lines` piece's reading, a body's substitutions included, and the
comparison's subtraction of body commands from the pieces' sum, which pins
today's reading, is gone.
