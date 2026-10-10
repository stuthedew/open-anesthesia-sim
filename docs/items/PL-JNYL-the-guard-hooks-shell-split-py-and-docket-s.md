---
id: PL-JNYL
title: The guard hooks' shell_split.py and docket's shell.py read one shell grammar twice, so #1377 found and fixed the same three bash facts in each - an operator a backslash-newline splits, an unquoted here-document's logical lines, a ${...} - and the next one will be found in one and missed in the other
priority: P3
effort: L
status: done
classes: refactor
feature: one-answer
touches: .claude/hooks/shell_split.py, .claude/hooks/floor-interpreter-guard.sh, .claude/hooks/gate-status-guard.sh, .claude/hooks/no-prune-guard.sh, .claude/hooks/push-check-guard.sh, subprojects/docket/src/docket/shell.py, subprojects/docket/src/docket/__init__.py, subprojects/docket/tests/test_shell.py, tests/unit/test_shell_reader.py, tests/unit/test_doc_check.py, tests/unit/test_floor_interpreter_guard.py, tests/unit/test_no_prune_guard.py, tests/unit/test_push_check_guard.py, docs/ARCHITECTURE.md, subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py, docket.toml, CLAUDE.md, docs/maintainer.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-05 triage pass
added: 2026-10-05
closed: 2026-10-10
pr: 1390
payoff: each bash fact a shell reader learns lands once, for the guard hooks and for docket alike, instead of being found in one and left wrong in the other until somebody trips on it again
not-delegable: its Done-when has two endings - one module both sides import, or a measured close keeping two - and where the merged module lives is the design the work settles, so no grep written now proves either; it also edits .claude/hooks/, which docket verify will not judge
---

**Problem.** The guard hooks' shell_split.py and docket's shell.py read one shell grammar twice, so #1377 found and fixed the same three bash facts in each - an operator a backslash-newline splits, an unquoted here-document's logical lines, a ${...} - and the next one will be found in one and missed in the other

**Decided 2026-10-05, in the thread for `PL-R417`'s shell slice.** Fix both
lexers in place in `#1377` and file the merge as its own item (project owner,
2026-10-05, ratified, over merging the two lexers in `#1377`). `#1377` fixed
`PL-97CF` in `.claude/hooks/shell_split.py` and `PL-2JYP` in
`subprojects/docket/src/docket/shell.py`, each against bash 5.2.21, with the
same three facts written twice.

**Reopened 2026-10-06, in the thread for `PL-R417`'s closing sweep.** The
merge opens `PL-R417`'s shell batch, ahead of `PL-VJPH` and `PL-QSN5`, the
closing sweep's defects in these readers, one in each, so that each is fixed
once (project owner, 2026-10-06, ratified, over keeping both readers and
fixing each, as decided on 2026-10-05). The five points below are that
batch's first design round.

**What a merge has to settle first.** Each was read or measured on 2026-10-05.

1. **What a here-document its delimiter never ends does.** The hooks read the
   body to the end of the command, as bash does (it warns and runs it). docket
   refuses it, because a `<<` docket took for an introducer would otherwise
   skip the rest of a workflow script without a word;
   `test_the_rest_of_a_script_that_stops_reading_is_one_unreadable_piece` in
   `subprojects/docket/tests/test_shell.py` pins the refusal. One lexer needs
   both answers as a policy its callers choose, not one of them winning.
2. **The import every Bash call pays.** Four PreToolUse guards in
   `.claude/settings.json` (no-prune, floor-interpreter, gate-status and
   push-check) each start their own python3 and import `shell_split` on every
   Bash call. `shell_split` imports in about 12 ms, most of it `re` and
   `typing`. `docket.shell` takes about 25 ms, most of it the package
   `__init__` importing `docket.model`, which brings `dataclasses`, `inspect`
   and `pathlib`. Both are medians of five runs of `python3 -X importtime`
   under python3 3.11.15. Read through `docket.shell` as it stands, the merge
   adds about 12 ms to each guard, about 50 ms to every Bash call.
3. **The path each side can see.** `bin/docket` puts only docket's package on
   `sys.path`, and each guard puts only `.claude/hooks/`. Every guard fails open
   when its import fails, as the header of `.claude/hooks/gate-status-guard.sh`
   says, so a merged module one side cannot find turns that guard off with no
   error.
4. **The word shape.** docket keeps a word's quoting and its span (`Word`,
   `Reading.clauses`, `Reading.refusal`); the hooks drop the quoting (`words`,
   `segments`, `commands`). That split is `PL-B5VZ`'s design, so a merged lexer
   gives both views of one reading.
5. **The grammar each reads.** Since `#1377` docket reads `case`, `(( ))`,
   `$(( ))` and `[[ ]]`. The hooks still name all four as constructs they do
   not read, the construct side of `PL-61FT`'s known gaps. A merge either gives
   the guards that grammar, with their tests re-run, or keeps the gap named.

**Settled 2026-10-10, in the thread building `PL-R417`'s shell batch.** Each
of the five is decided in the round, on a measurement or on a rule this
repository already states, so none was put to the owner. The one reader is
`subprojects/docket/src/docket/shell.py`; `.claude/hooks/shell_split.py` keeps
the hooks' views over its reading.

1. **A caller chooses what input that ends early means, and the one switch
   covers two cases.** The reading either takes the input as `bash -c` takes a
   string, where an unended body runs to the end of the input and a trailing
   backslash is a backslash, or refuses both as unreadable, as docket does
   today. The hooks take the first, since the harness hands bash each Bash call
   as a string, and docket the second, for the reason point 1 gives. The
   trailing backslash is the same question: bash 5.2.21 keeps one under
   `bash -c` and `eval` (`echo a\` prints `a\`) and drops one read from a file
   or standard input, and today the hooks keep it and docket refuses it
   (measured 2026-10-10). The two tests pinning the answers,
   `test_an_unterminated_heredoc_runs_to_the_end` in
   `tests/unit/test_gate_status_guard.py` and the refusal point 1 names, stand
   unchanged.
2. **The import a guard pays is held by what it loads, not by a stopwatch.**
   Measured 2026-10-10 with `python3 -X importtime`, medians of nine, after the
   guards' own `import json, os, re, sys`: `shell_split` adds 5.3 ms under
   3.11.17 and 5.5 ms under 3.13.16, `typing` 2.3 to 2.8 ms of it, while
   `docket` and `docket.shell` add 19.7 and 23.0 ms, nearly all of it
   `docket.model`'s `dataclasses`, `inspect` and `pathlib`. So
   `docket/__init__.py` loads `model` only when a name it re-exports is asked
   for (PEP 562, and no module in the tree asks), `docket.shell` imports
   nothing a guard has not already loaded, its `Word`, `Clause` and `Reading`
   becoming plain classes rather than dataclasses, and a test pins the modules
   a guard's import of `shell_split` loads, so one that brings back
   `dataclasses`, `inspect`, `pathlib` or `typing` fails rather than slowing
   every Bash call unnoticed. A timing would be the direct measure, and a
   flaky one; the module set is the deterministic half of it. Built, the
   same measure gives 1.3 ms under 3.11.17 and 2.0 ms under 3.13.16 for
   `shell_split` with docket's lexer, against the 5.3 and 5.5 ms it cost
   with its own.
3. **The lexer lives in docket, and the hooks reach it by path.** `bin/docket`
   runs docket from a bare checkout with its own `src` alone on the path, so
   docket cannot import from `.claude/hooks/`; the hooks are this repository's,
   so `shell_split.py` puts `subprojects/docket/src` on `sys.path`, found from
   its own location, before it imports `docket.shell`. A guard whose import
   fails passes everything, so the failure has to be loud elsewhere: the four
   guard suites run each hook in a child process as `.claude/settings.json`
   runs it, where pytest's `pythonpath` does not reach, so a broken path turns
   every refusal they pin into a pass; and one more test runs the import alone
   in a bare interpreter and names the path.
4. **One reading, two views of it.** The lexer decides once where a word, a
   quote, an operator, a line, a here-document's body and a substitution end.
   docket's view is its `Word`s with their quoting and spans, cut into clauses
   with each substitution's body beside them; the hooks' is flat words with
   `Operator` and `Descriptor`, a newline read as `;` except after a separator
   or `(`, an unquoted `$( )` or `<( )` read inline as today, and a quoted
   one's commands kept in `substituted`. Both are built in the one pass. Where
   the two readers' tokens differ today on input both read alike, the
   difference is in what each view keeps - a substitution's text, a newline's
   spelling, a descriptor - not in where anything ends, so neither suite's
   expectations move.
5. **The guards read the grammar docket reads.** Keeping the gap would mean
   writing a second, weaker grammar into the one reader for the hooks alone,
   which is the duplication this item exists to remove. So `case` patterns,
   `(( ))` and `$(( ))`, a newline inside `[[ ]]` and a backquote's body leave
   the hooks' "What it does not read" list: an arithmetic `<<` no longer opens
   a body that swallows the lines after it, and a backquote's command is read
   as a command it runs. No row in the four guard suites pins any of these
   constructs (searched 2026-10-10), so their expectations do not move. Still
   on the list: `&&`, `||`, `<` and `>` inside `[[ ]]`, which docket reads as
   operators too, a `coproc`, a wrapper `WRAPPERS` does not name, `env -S`, and
   a reserved word read only at the head of a segment.

The merged reader also reads `$'...'` once, as the hooks and bash do (Bash
Reference Manual § 3.1.2.4), so docket's `script_lines` stops cutting at one.
That is `PL-C45K`'s defect, and it closes here (project owner, 2026-10-10,
ratified, over leaving it out of the batch as the Order did). `PL-P72R` closes here, as the paragraph below says,
since one `OPERATORS` table is left.

**A library in place of the lexer was weighed, 2026-10-10**, when the owner
asked whether one does all this. Four exist; none reads what the two views
need as bash reads it. bashlex is a port of bash's own parser, but GPL-3.0
where this repository is Apache-2.0, and its README says it has no support for
`$((..))`. tree-sitter-bash is a compiled extension the guards' bare python3
cannot import, and it parses for editors, recovering from errors rather than
saying bash refuses a command. `shfmt --to-json` prints mvdan/sh's syntax tree,
from a Go binary every environment would need, and its README lists where its
parse departs from bash's. Parable (MIT, one file, no imports, validated
against bash 5.3's own parse tree) came closest, run from its `main` source at
`src/parable.py`, since its v0.1.0 Python release fails to import with a
`SyntaxError` under 3.12.3 and 3.13.16. Over this batch's cases it read
`PL-QSN5`'s first form with the command after the substitution as the
here-document's text, where bash 5.2.21 runs that command, and it read the
carried here-document in the other order; it left a `$( )` inside an unquoted
body as text (`PL-P95F`); and its words carry no source position and keep
their quotes as written, so the spans and the quoting half of this lexer would
stay around it. Swapping one in later touches this one module.

**`PL-P72R` closes with this item** if one `OPERATORS` table is left. It stays
the cheaper fix, a test holding the two tables equal, if this item closes
without a merge.

**Not a recurrence of `PL-97CF`.** `bin/docket new` matched this filing to it
on `.claude/hooks/shell_split.py`. It is the decision `#1377` deferred, filed
beside that fix, so the match is withdrawn on this brief.

**Generator check.** Not a new instance of `PL-KGYT`'s fact, two spellings held
to each other by nothing. It is `PL-P72R`'s pair of files read whole rather
than by their operator tables, so `PL-74T0`'s count for that cluster does not
move.

**Reproduced 2026-10-05 at triage** on `main` at `b67dace8`, by the next bash
fact the brief predicts: over `"echo $'a\\'b'\necho next\n"`,
`.claude/hooks/shell_split.py`'s `segments` read two commands and docket's
`shell.script_lines` returned the whole script as one unreadable piece. The
hooks read `$'...'` as bash does (`_ansi_c_end`) and docket does not; that
divergence is `PL-C45K`, filed the same day.

**Why it matters.** The two lexers decide what the guard hooks let a Bash call
do and what docket and `tools/doc_check.py` read a `verify:` field, a workflow
step or a fenced command to run. Each bash fact is found by whichever reader
trips on it, so the other keeps reading it wrong until somebody trips again:
`#1377` paid for three facts twice, and `PL-C45K` is a fact one already
reads and the other does not. One reading would make each such fix land once,
for both.

**Done when.** One module reads a shell command for both docket and the guard
hooks. Each caller chooses its answer to an unended here-document, no guard
pays more import time than it does today, and both suites
(`subprojects/docket/tests/test_shell.py` and the four guard tests under
`tests/unit/`) pass with their expectations unchanged. Or the item closes with
the measured reason the two stay apart, and `PL-P72R`'s test holds their shared
table.

**Built 2026-10-10 (`#1390`).** `subprojects/docket/src/docket/shell.py` is the
one reader. Its `_Lexer` reads a command once and builds both views from that
pass: docket's words, clauses and substitutions (`shell_words`, `script_lines`,
`joined_text`) and the hooks' flat tokens (`flat_reading`). `bash_c` is point
1's one switch: the hooks read an unended body to the end and keep a trailing
backslash, as `bash -c` does, and docket refuses both.
`.claude/hooks/shell_split.py` keeps every function the guards call, now over
`flat_reading`, and finds docket's `src` from its own place; its own lexer and
its `OPERATORS` table went, which closes `PL-P72R`. `docket/__init__.py` loads
`docket.model` on first use (PEP 562), so a guard's import adds only `docket`,
`docket.shell` and `shell_split`: 1.3 ms under python3 3.11.17 and 2.0 ms under
3.13.16, medians of nine with `python3 -X importtime`, against 5.3 and 5.5 ms
for the hooks' own lexer. `tests/unit/test_shell_reader.py` pins that module
set and the path, from a bare isolated interpreter. Both suites pass with their
expectations unchanged: an import line and a comment are the only lines taken
out of the existing tests. Over 308 shell samples from the tree (workflow
steps, Makefile recipes, `.sh` files and fenced commands), `script_lines` and
`joined_text` answer as `main`'s did, and the two views part from `main`'s
readers only where this batch meant them to: a backquote's body is read as
commands in the hooks' view, and a process substitution is one word with its
body among the substitutions in docket's. `doc_check`'s gate-parity,
workflow-paths, coverage-gate and ruff-cache checks report the same over the
tree. `make check` found the new test outside `docket.toml`'s
`workflow_paths`, which now places it. Two fix-nows rode the batch, both one
stale count of three Bash guards sharing the reader, where there are four: in
three guard headers, and in the gate guard's redirection paragraph and the
reader's known-gaps paragraph, which now name the guards without a number.

**The lexer joins the owner's read list.** With the reader moved, what the four
Bash guards refuse is decided outside `.claude/hooks/`, which has waited on the
owner's read since 2026-10-03, so a change to it would have armed on green.
`arming.LEXER` holds `subprojects/docket/src/docket/shell.py` beside the hooks,
and `CLAUDE.md`, `docs/maintainer.md` and `docs/ARCHITECTURE.md` name it. Put
to the owner on 2026-10-10 as the recommendation, over arming lexer changes on
green; the answer is recorded here when it comes, and the commit carrying the
hold drops whole if the answer is to arm them.
