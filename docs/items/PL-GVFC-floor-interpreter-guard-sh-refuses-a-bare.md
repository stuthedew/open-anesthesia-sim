---
id: PL-GVFC
title: floor-interpreter-guard.sh refuses a bare python3 aimed at subprojects/docket/src/, the 3.11 floor tree it exists to protect, because GUARDED's lookbehind admits docket/src/; and plain shlex.split glues a ; to the word before it, so a path in the next command is read as the interpreter's argument
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: .claude/hooks/floor-interpreter-guard.sh, tests/unit/test_floor_interpreter_guard.py, docs/items/PL-BBV7-the-three-bash-guard-hooks-split-a-command-into.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-23 triage pass
added: 2026-09-23
closed: 2026-09-26
pr: 1064
payoff: the interpreter guard stops refusing the 3.11 floor code it exists to protect, so its refusals stay worth obeying
verify: grep -q 'def test_the_docket_subproject_is_floor_code_and_is_admitted' tests/unit/test_floor_interpreter_guard.py && grep -q 'def test_a_path_after_a_semicolon_is_another_commands' tests/unit/test_floor_interpreter_guard.py
recurrences: 2026-09-25 PL-BBV7, 2026-09-26 PL-R5N0
---

**Problem.** floor-interpreter-guard.sh refuses a bare python3 aimed at subprojects/docket/src/, the 3.11 floor tree it exists to protect, because GUARDED's lookbehind admits docket/src/; and plain shlex.split glues a ; to the word before it, so a path in the next command is read as the interpreter's argument

**Found 2026-09-23 at triage**, when a `python3 -c` reproduction followed by `;
sed -n ... subprojects/docket/src/docket/verify.py` was refused. Replayed
through the hook with the Bash tool's JSON: `python3 -m py_compile
subprojects/docket/src/docket/verify.py` is refused, and so is `python3 -c
'print(1)'; sed -n 1p subprojects/docket/src/docket/verify.py`; `python3 -m
compileall src/` is refused, correctly. Two causes:
- `GUARDED = (?<![\w-])(?:src|tests)/` lets a `/` precede the match, so
  `subprojects/docket/src/` and `subprojects/docket/tests/` read as the 3.14
  trees, when they are the 3.11 floor code that must run under the bare
  interpreter.
- The hook tokenises with plain `shlex.split`, so `'print(1)';` is one word and
  the `;` never separates; `gate-status-guard.sh` passes
  `punctuation_chars=True` for exactly this.

**Why it matters.** It refuses the one tree the floor exists to run, with a
message saying the bare interpreter is wrong for it, which is false - how a
session learns to route around a guard.

**Done when.** A bare `python3` aimed only at `subprojects/docket/` is admitted
and a path after a `;` in another command is not read as the interpreter's,
while `src/`, `./src/` and `tests/` stay refused, all pinned in
`tests/unit/test_floor_interpreter_guard.py`.

**Generator check.** One-off, kin to `PL-1SFZ`: the two Bash hooks each tokenise
a command by their own rules and each has a false refusal from it. Two items
sharing no function are not a generator, and a shared tokeniser would be a new
mechanism nothing here argues for yet.

**Built 2026-09-26, and the two choices the done-when left open.**

- **The exclusion names `subprojects/docket/`, not every subproject.**
  `GUARDED` gains a second lookbehind, `(?<!subprojects/docket/)`. That
  subproject's `pyproject.toml` is the one declaring the 3.11 floor. A general
  `subprojects/<name>/` rule would be falsified silently by a subproject
  targeting 3.14, where this one is falsified loudly, by a refusal, on a second
  3.11 one. The product tree is still refused bare, after `./`, absolute, and
  named beside docket's.
- **The tokeniser is `gate-status-guard.sh`'s, plus one line.**
  `shlex.shlex(punctuation_chars=True)` with `whitespace_split`, a newline read
  as `;`, and `(`, `{` and `!` stripped at a segment's start. The one line
  joins a backslash-newline pair first: reading every newline as `;` would
  otherwise have turned `python3 -m compileall \` followed by `src/` on the
  next line, which plain `shlex` refused by accident, into a missed refusal.
  The gate guard lacks that line and false-refuses the same shape, filed as
  `PL-R5RF`. One splitter the hooks import is `PL-PVW2`'s to build, and
  `PL-NZC0`'s Stream A holds that head, so it is not built here.

The default `commenters` came with the lexer, so a path in a trailing
`# comment` is no longer read as an argument. `PL-BBV7`'s missed refusals are
refused now too, pinned under the two test names its `verify:` reads, so it
closes with this item; the one splitter its done-when also names is
`PL-PVW2`'s question, and its closing note says so.

Tests: `test_the_docket_subproject_is_floor_code_and_is_admitted`,
`test_a_path_after_a_semicolon_is_another_commands_argument`, `PL-BBV7`'s two,
and four `FLOOR_PARSE` cases holding the product tree refused beside the new
exclusion. Against the unfixed hook 18 of the new cases fail.

Found and filed rather than fixed: `PL-R5N0`, the guard missing
`python3 -m compileall src` written without a trailing slash.
