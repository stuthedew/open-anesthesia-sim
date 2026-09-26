---
id: PL-CWBJ
title: tools/doc_check.py's check_workflow_paths splits a CI step's run: script with its own quote-blind COMMAND_SPLIT_RE, beside docket's lexer and the hooks' shell_split.py, so a quoted path holding a space reads as another path - python3 "tools/my file.py" reads as tools/my
priority: P2
effort: S
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/items/PL-PVW2-predicates-the-apparatus-asks-repeatedly-which.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; a member of generator head PL-PVW2, triaged 2026-09-26
added: 2026-09-26
closed: 2026-09-26
payoff: a quoted CI path or gate script is read as the one word the shell reads, through the reading docket already holds, and PL-PVW2 can say spent
verify: grep -q 'def test_workflow_paths_reads_a_quoted_path_as_one_word' tests/unit/test_doc_check.py && grep -q 'def test_gate_parity_reads_a_quoted_script_as_one_word' tests/unit/test_doc_check.py
---

**Problem.** tools/doc_check.py's check_workflow_paths splits a CI step's run: script with its own quote-blind COMMAND_SPLIT_RE, beside docket's lexer and the hooks' shell_split.py, so a quoted path holding a space reads as another path - python3 "tools/my file.py" reads as tools/my

**Found 2026-09-26 triaging `PL-P7J7`**, by sweeping `tools/`, `.claude/` and
docket for other spellings of how a shell command splits. On `70818cfc`,
`doc_check._command_paths('python3 "tools/my file.py"')` yields `tools/my`, and
`check_workflow_paths` would report it as a path the step runs that does not
exist. `COMMAND_SPLIT_RE` (`[\s;|&()<>]+`) cuts inside quotes, and each token
has its quotes stripped at its ends only.

**Generator check.** `PL-PVW2`'s fact - how a shell command splits - spelled a
fourth way, in `tools/`, which that head's done-when has importing
`subprojects/docket/src`. Whether it is that head's member, and whether a
workflow's multi-line `run:` script can take docket's one-line reader at all,
is triage's call.

**Added to the Fix generators project's list 2026-09-26** (project owner,
2026-09-26, ratified, over leaving it untriaged in the queue), on the
coordinator's decision card in that project, which recommended adding it
because `PL-PVW2` could close only with it. Recorded here so the answer does
not live only on the card.

**Triaged 2026-09-26 as `PL-PVW2`'s member.** Its fact is the head's: how a
shell command splits, spelled a fourth way. Reproduced on `39a7a31f` before
the build, as the brief states: `_command_paths('python3 "tools/my file.py"')`
yields `tools/my`, and `_gate_scripts` has the same split, so a quoted script
in a recipe was never seen at all - a silent miss in the gate-parity check,
where `check_workflow_paths`' miss is a false error.

**Can a multi-line `run:` script take docket's one-line reader? Measured, yes,
one line at a time.** On `39a7a31f` every line of the 42 `run:` steps in the
three workflows and every `Makefile` recipe line reads through
`docket.shell.shell_words` with none unreadable, and yields exactly the paths
and gate scripts the pattern yielded. What a one-line reading cannot place is a
quote, a command substitution or a backslash running past the line's end;
today's tree has none, so such a line is declined by name rather than read as
empty or guessed at. The one multi-line construct present, `drift.yml`'s
`python3 - <<'PY'`, has its body read as lines of commands by both readings,
as before; it yields no path.

**Why it matters.** A path quoted because it holds a space is reported as a
missing script the step runs, and a quoted gate script is compared by neither
gate, while the head this belongs to cannot say spent.

**Done when.** `tools/doc_check.py` keeps no split of its own: both of its
readers of a shell line take `docket.shell.shell_words`, a line it cannot read
is declined by name, and a test holds a quoted path for each reader.

**Built 2026-09-26.** `COMMAND_SPLIT_RE` is gone. `_shell_words` reads a line
through `docket.shell.shell_words`, substitution bodies included, and declines
one that runs past its end; `_command_paths` and `_gate_scripts` read its
words. The backquote joins `UNRESOLVABLE`, since a word keeps a substitution as
written. `test_workflow_paths_reads_a_quoted_path_as_one_word`,
`test_gate_parity_reads_a_quoted_script_as_one_word` and
`test_a_line_running_past_its_end_is_declined_rather_than_read` failed before
the change and pass after it; `python3 tools/doc_check.py check` reports the
tree as before, with nothing declined.
