---
id: PL-55R2
title: docket.shell's script_lines puts the body of a here-document whose delimiter has no quoted part in no piece, so a substitution in that body, which bash runs (PL-P95F), is a command no per-piece reader sees: doc_check's _make_mentions, workflow_commands and workflow_runs' line-at-a-time fallback all miss it; latent
status: untriaged
feature: shell-reads-as-bash
touches: subprojects/docket/src/docket/shell.py, subprojects/docket/tests/test_shell.py, docs/items/PL-GJKN-docket-shell-s-lexer-applies-the-command.md
added: 2026-10-12
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

**Not a recurrence of `PL-GJKN`**, which `docket new` matched on the shared
`touches`: that item is where a nested body ends inside an expanded body, a
rule of the lexer's single pass, and this is which piece `script_lines` hands a
body's substitutions to, with the pass reading them correctly. The match is
withdrawn because of this paragraph.

**Generator check.** Found by `PL-C4XY`'s comparison, which is what stops a
departure of this kind reaching `main` from now on; read against `bin/docket
generators --misread` on 2026-10-12, it misreads no recorded fact.

**Done when.** Every command bash runs from a script is a command of one
`script_lines` piece's reading, a body's substitutions included, and the
comparison's subtraction of body commands from the pieces' sum, which pins
today's reading, is gone.
