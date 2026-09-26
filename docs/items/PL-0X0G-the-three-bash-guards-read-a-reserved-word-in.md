---
id: PL-0X0G
title: The three Bash guards read a reserved word in front of a command as the command's name, so a gate, a floor parse or a prune written after do, then, else or time passes the guard that exists to refuse it: for f in a; do make check | tail; done keeps tail's status unrefused
priority: P2
effort: M
status: done
classes: defect
touches: .claude/hooks/shell_split.py, .claude/hooks/gate-status-guard.sh, .claude/hooks/floor-interpreter-guard.sh, tests/unit/test_gate_status_guard.py, tests/unit/test_floor_interpreter_guard.py, tests/unit/test_no_prune_guard.py, docs/worker.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
closed: 2026-09-26
pr: 1093
payoff: a gate, a floor parse or a prune written inside an if or a loop, or after time, is refused like the same command on its own, so a red make check piped to tail there no longer reaches a session as exit 0
verify: grep -q 'def test_a_reserved_word_opens_the_command_after_it' tests/unit/test_gate_status_guard.py && grep -q 'def test_a_reserved_word_opens_the_command_after_it' tests/unit/test_floor_interpreter_guard.py && grep -q 'def test_a_reserved_word_opens_the_command_after_it' tests/unit/test_no_prune_guard.py
---

**Problem.** The three Bash guards read a reserved word in front of a command as the command's name, so a gate, a floor parse or a prune written after do, then, else or time passes the guard that exists to refuse it: for f in a; do make check | tail; done keeps tail's status unrefused

**Found 2026-09-26 while working `PL-WGFY`**, by piping each command as a hook
payload into the three guards on its branch. Every one is allowed:

    for f in a; do make check | tail; done           gate-status-guard.sh
    if true; then make check | tail; fi              gate-status-guard.sh
    time make check | tail                           gate-status-guard.sh
    for f in a; do python3 -m compileall src/; done  floor-interpreter-guard.sh
    time python3 -m compileall src/                  floor-interpreter-guard.sh
    for x in a; do git fetch --prune; done           no-prune-guard.sh
    if true; then git fetch --prune; fi              no-prune-guard.sh

Since `PL-WGFY` all three read where a command starts from
`shell_split.command_words`, which drops a leading `(`, `{`, `!` and
assignments, and nothing else, so `do`, `then`, `else`, `elif`, `while`,
`until`, `if` and `time` read as the command's name. Bash reads each of those
as a reserved word with a command after it: `compgen -k` in bash 5.2.21 lists
them among its keywords, and `help time` gives `time [-p] pipeline`. The gate
guard's miss is `PL-2JRC`'s hazard: a gate run in a loop and piped into `tail`
exits with `tail`'s status.

**Why it matters.** Each guard stands for one failure a session has already
had. The gate guard is `PL-2JRC`'s false green, a red `make check` read through
`tail`'s exit 0, and `time make check | tail` reaches a session the same way
unrefused. The floor guard is `PL-JQJQ`'s SyntaxError misread as a defect on
`main`, and the prune guard `PL-HKF4`'s near-loss of an item held only by a
stale remote ref. A guard that refuses `make check | tail` and allows the same
pipe after `do` reads as protection it does not give.

**Done when.** `shell_split.command_words` drops the reserved words bash reads
with a command after them - `if`, `then`, `elif`, `else`, `while`, `until`,
`do`, and `time` with its `-p` and `--` - so each command above is refused by
its guard, pinned in the three guards' tests. The gate guard then reads the
`if` or loop it can now see as bash runs it (`help if`, `help for` and `help
while` in bash 5.2.21): a gate ending an `if` branch leaves with the `if`, one
ending an `if`, `while` or `until` test is read by it as `$?` is, and one ending
a loop body is refused, because the next pass replaces its status. And a `set
-o pipefail` inside an `if` or loop that is piped ends with it, as one inside a
piped `{ }` group does.

**Joined the Fix generators project's list 2026-09-26** (project owner,
2026-09-26, ratified, over leaving it to a session outside that project). Asked
in the `PL-WGFY` thread whether this item and `PL-B5VZ` could join the list,
with a recommendation of yes to both, the owner answered "Agree". Recorded here
by the thread that triaged it.

**Generator check.** One-off: a gap in the one answer the three guards share,
not a second spelling of it, so it is not `PL-PVW2`'s. The fix is one place.
