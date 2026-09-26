---
id: PL-9RSP
title: gate-status-guard.sh reads command set -o pipefail as no set at all, so command set -o pipefail; make check 2>&1 | tail -45 is refused, though command runs the set builtin in this shell and the pipe keeps the gate's status
priority: P3
effort: S
status: done
classes: defect
touches: .claude/hooks/shell_split.py, .claude/hooks/gate-status-guard.sh, tests/unit/test_gate_status_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
closed: 2026-09-26
pr: 1112
payoff: a session that sets pipefail through command or builtin - command set -o pipefail; make check 2>&1 | tail -45 - is let through, as bash holds the setting for that pipe, while every spelling that runs no set in this shell is still refused
verify: grep -q 'def test_pipefail_set_through_command_or_builtin_keeps_the_status' tests/unit/test_gate_status_guard.py
---

**Problem.** gate-status-guard.sh reads command set -o pipefail as no set at all, so command set -o pipefail; make check 2>&1 | tail -45 is refused, though command runs the set builtin in this shell and the pipe keeps the gate's status

**Found 2026-09-26 triaging `PL-TRMN`**: the hook refuses the command on
`6d92df95`, and in bash 5.2.21 `command set -o pipefail; false | true; echo $?`
prints 1, so the `set` held. `sets_pipefail` reads the head through
`shell_split.command_words`, which does not step past `command`; `command` is
the one wrapper that runs a builtin in this shell (`help command`). A false
refusal costs one retry, and no session has been seen writing it.

**Reproduced 2026-09-26 on `17d47ec8`** (`PL-K9QL`'s merge), as hook
payloads: `command set -o pipefail; make check 2>&1 | tail -45` is refused, and
so are the same line opening `command -p set` and `builtin set`, while `set -o
pipefail; make check 2>&1 | tail -45` passes. Against bash 5.2.21, `false |
true; echo $?` prints 1 after each of `command set -o pipefail`, `command -p
set`, `command -- set`, `command -p -- set`, `builtin set` and `builtin --
set`, after `command builtin set` and `builtin command set`, after `"command"
set` and `'builtin' set`, and with an assignment or a redirection among the
words. It prints 0 after `command -v
set` and `command -pv set`, which describe `set` and run nothing; after
`builtin -p set`, refused as an invalid option, since `builtin` takes no option
but `--`; and after `exec set`, `timeout 5 set`, `env set` and
`/usr/bin/command set`, each of which looks for a program and finds none.

**Why it matters.** The refusal's own remedy is `set -o pipefail`, which it
calls "never wrong to add", so refusing a spelling that sets it tells a session
its remedy failed. `PL-1SFZ` was filed on that lesson: a false refusal reads as
the guard being wrong, and a guard read as wrong is the one sessions learn to
route around, where the guard exists because a red gate was once reported green
(`PL-2JRC`).

**Done when.** `sets_pipefail` in `.claude/hooks/gate-status-guard.sh` reads
past each bare `command`, with its `-p` and `--`, and each bare `builtin`, with
its `--`, to the `set` they run in this shell. The three refused spellings above
pass, and so do `command -- set`, the two nested spellings and `FOO=1 command
set`; `command -v set`, `builtin -p set`, `exec set`, `timeout 5 set` and
`/usr/bin/command set` are still refused, since none runs `set` in this shell.
What `command` runs is read through the grammar `.claude/hooks/shell_split.py`
already holds for it, so the gate guard's two readers of `command` cannot
disagree about its options. The gate guard's suite pins each.

**Generator check.** A re-entry of `PL-TRMN` (done, #1107, closed
2026-09-26): the same fact - what a command runs past a word that runs another -
at the one site its fix left, `sets_pipefail`, whose docstring it rewrote to say
that reader must not read past a wrapper. That holds for `timeout`, which runs a
program named `set`, and not for `command`, the one wrapper in its table that
runs a builtin in this shell. The other reader of a builtin's name in that hook,
the `||` fallback's `exit` and `false`, reads nothing past its first word by
design (`PL-KQ4Q`), so it is no sibling site. A gap in the one answer the
guards share, not a second spelling of it, so not `PL-PVW2`'s.
