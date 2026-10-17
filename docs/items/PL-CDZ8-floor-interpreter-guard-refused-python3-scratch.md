---
id: PL-CDZ8
title: floor-interpreter-guard refused python3 <scratch>/guard.py with a string argument naming tests/unit/test_doc_check.py, where nothing parsed that tree - the tree name was only text in an argument; kin of PL-7LCY and possibly a post-close instance of PL-61FT (met by the 2026-10-11 triage pass's batch A)
priority: P3
effort: S
status: done
classes: defect
feature: friction-batch
touches: .claude/hooks/floor-interpreter-guard.sh, tests/unit/test_floor_interpreter_guard.py, .claude/hooks/shell_split.py, .claude/hooks/gate-status-guard.sh
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-12 triage pass
added: 2026-10-11
closed: 2026-10-17
payoff: a session running its own script with a tree path as an argument is let through, while a real floor parse of src or tests is still refused
verify: grep -q 'def test_a_scripts_own_argument_naming_a_tree_is_left_alone' tests/unit/test_floor_interpreter_guard.py
reenters: PL-61FT
---

**Problem.** floor-interpreter-guard refused python3 \<scratch>/guard.py with a string argument naming tests/unit/test_doc_check.py, where nothing parsed that tree - the tree name was only text in an argument; kin of PL-7LCY and possibly a post-close instance of PL-61FT (met by the 2026-10-11 triage pass's batch A)

**Reproduced 2026-10-12** on `main` at `0461f111`, feeding the hook
its tool input: `python3 /tmp/x/guard.py "see tests/unit/test_doc_check.py"` is
denied with the 3.14 floor explanation, and `python3 /tmp/x/guard.py` alone is
let through. An argument after a script path is the script's `argv`, which the
interpreter never parses, so the first runs a floor parse of the scratch script
only and nothing under `tests/` is compiled. The header's promise refuses a tree
"as an argument" without saying whose.

**Why it matters.** A false refusal costs the session that meets it a round
and a workaround, and the workaround - naming the interpreter by path - is the
spelling the guard leaves open for a deliberate floor parse, so it teaches
sessions to step around the guard where it is right too.

**Done when.** A tree path standing after a script path outside both trees is
left alone, while one handed to the interpreter itself, to `-m compileall` or
`-m py_compile`, or inside a `-c` string is still refused;
`test_a_scripts_own_argument_naming_a_tree_is_left_alone` in
`tests/unit/test_floor_interpreter_guard.py` pins both, and the header's promise
says whose arguments it reads as a parse. One session should take it beside
`PL-7LCY`, the `-c` half of the same reading, since both change the one argument
reader.

**Generator check.** An instance of `PL-61FT`'s fact - what a shell command
does when run, here on what - filed after that head closed, and recorded as
`reenters: PL-61FT`. `PL-4097` answered `PL-61FT` on 2026-10-12 with no
successor head: a misread met in use is worked as an item at its own rank,
which is this one.
