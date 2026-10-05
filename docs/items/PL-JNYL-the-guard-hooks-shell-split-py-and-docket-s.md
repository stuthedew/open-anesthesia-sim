---
id: PL-JNYL
title: The guard hooks' shell_split.py and docket's shell.py read one shell grammar twice, so #1377 found and fixed the same three bash facts in each - an operator a backslash-newline splits, an unquoted here-document's logical lines, a ${...} - and the next one will be found in one and missed in the other
status: untriaged
feature: one-answer
touches: .claude/hooks/shell_split.py, subprojects/docket/src/docket/shell.py, subprojects/docket/tests/test_shell.py
added: 2026-10-05
---

**Problem.** The guard hooks' shell_split.py and docket's shell.py read one shell grammar twice, so #1377 found and fixed the same three bash facts in each - an operator a backslash-newline splits, an unquoted here-document's logical lines, a ${...} - and the next one will be found in one and missed in the other

**Decided 2026-10-05, in the thread for `PL-R417`'s shell slice.** Fix both
lexers in place in `#1377` and file the merge as its own item (project owner,
2026-10-05, ratified, over merging the two lexers in `#1377`). `#1377` fixed
`PL-97CF` in `.claude/hooks/shell_split.py` and `PL-2JYP` in
`subprojects/docket/src/docket/shell.py`, each against bash 5.2.21, with the
same three facts written twice.

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

**Done when.** One module reads a shell command for both docket and the guard
hooks. Each caller chooses its answer to an unended here-document, no guard
pays more import time than it does today, and both suites
(`subprojects/docket/tests/test_shell.py` and the four guard tests under
`tests/unit/`) pass with their expectations unchanged. Or the item closes with
the measured reason the two stay apart, and `PL-P72R`'s test holds their shared
table.
