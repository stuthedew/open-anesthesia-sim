---
id: PL-63TT
title: The Bash guard hooks' lexer glues a run of punctuation into one token, so a ')' touching a ';' or '|' hides the separator: '(true); make check 2>&1 | tail -45' passes gate-status-guard.sh and '(true); python3 src/a.py' passes floor-interpreter-guard.sh, though each is what its guard exists to refuse
priority: P2
effort: S
status: ready
classes: defect
feature: one-answer
touches: .claude/hooks/shell_split.py, .claude/hooks/gate-status-guard.sh, .claude/hooks/floor-interpreter-guard.sh, tests/unit/test_gate_status_guard.py, tests/unit/test_floor_interpreter_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; a member of PL-PVW2, worked with its step 2
added: 2026-09-26
payoff: a gate or bare interpreter written after a closing parenthesis is refused like any other command, instead of passing the guard that exists to refuse it
verify: grep -q 'def test_a_glued_punctuation_run_splits_into_bash_operators' tests/unit/test_gate_status_guard.py && grep -q 'def test_a_glued_punctuation_run_splits_into_bash_operators' tests/unit/test_floor_interpreter_guard.py
---

**Problem.** The Bash guard hooks' lexer glues a run of punctuation into one token, so a ')' touching a ';' or '|' hides the separator: '(true); make check 2>&1 | tail -45' passes gate-status-guard.sh and '(true); python3 src/a.py' passes floor-interpreter-guard.sh, though each is what its guard exists to refuse

**Found 2026-09-26 while working `PL-1SFZ`**, by piping each command as a hook
payload into the hook. `shlex.shlex(..., punctuation_chars=True)` returns a run
of the characters `();<>|&` as one token, so `);` and `)|` arrive as single
words that are not in either hook's separator set. The gate or interpreter
after them is then read as an argument of the command before it, and never
checked:

    (true); make check 2>&1 | tail -45        allowed by gate-status-guard.sh
    (make check)|tail                         allowed by gate-status-guard.sh
    (true); python3 src/a.py                  allowed by floor-interpreter-guard.sh
    (true) ; python3 src/a.py                 refused, as it should be

**Why it matters.** Each is a silent miss of the one thing its guard exists to
refuse: a gate whose red status arrives as exit 0 (`PL-2JRC`'s failure), or the
bare floor parse `PL-JQJQ` prevents. `(cd sub && uv run pytest -q); make check
2>&1 | tail -30` is an ordinary spelling, not a contrived one. `PL-1SFZ`'s
scoping counts a glued `)` by character so a group still ends where bash ends
it, but the separator the glue hides is still lost.

**Done when.** Each punctuation run is split into bash's operators before the
walk reads it - longest match first, so `&&`, `||`, `>&` and `2>&1` survive -
and the four commands above get the verdicts bash's reading implies, pinned in
both hooks' tests.

**Generator check.** An instance of `PL-PVW2`'s question of how a shell command
splits, as `PL-R5RF` is: the two hooks share lexer settings but not code, so
the split belongs in the one splitter both import, and `PL-R5RF`'s
backslash-newline join with it.
