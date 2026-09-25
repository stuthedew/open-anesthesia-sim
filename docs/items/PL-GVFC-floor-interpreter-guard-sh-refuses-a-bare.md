---
id: PL-GVFC
title: floor-interpreter-guard.sh refuses a bare python3 aimed at subprojects/docket/src/, the 3.11 floor tree it exists to protect, because GUARDED's lookbehind admits docket/src/; and plain shlex.split glues a ; to the word before it, so a path in the next command is read as the interpreter's argument
priority: P3
effort: S
status: ready
classes: defect
touches: .claude/hooks/floor-interpreter-guard.sh, tests/unit/test_floor_interpreter_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-23 triage pass
added: 2026-09-23
payoff: the interpreter guard stops refusing the 3.11 floor code it exists to protect, so its refusals stay worth obeying
verify: grep -q 'def test_the_docket_subproject_is_floor_code_and_is_admitted' tests/unit/test_floor_interpreter_guard.py && grep -q 'def test_a_path_after_a_semicolon_is_another_commands' tests/unit/test_floor_interpreter_guard.py
recurrences: 2026-09-25 PL-BBV7
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
