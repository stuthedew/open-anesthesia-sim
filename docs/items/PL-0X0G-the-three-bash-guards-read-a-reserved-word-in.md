---
id: PL-0X0G
title: The three Bash guards read a reserved word in front of a command as the command's name, so a gate, a floor parse or a prune written after do, then, else or time passes the guard that exists to refuse it: for f in a; do make check | tail; done keeps tail's status unrefused
status: untriaged
added: 2026-09-26
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

**Generator check.** One-off: a gap in the one answer the three guards share,
not a second spelling of it, so it is not `PL-PVW2`'s. The fix is one place.
