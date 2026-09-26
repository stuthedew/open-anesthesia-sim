---
id: PL-TRMN
title: The three Bash guards read a command only where its name is the program itself, so a gate, a floor parse or a prune run through a wrapper passes all three: timeout 600 make check | tail -5, timeout 60 python3 -m compileall -q src/anesthesia_sim/, and timeout, env, command or a path to git ahead of git fetch --prune
status: untriaged
added: 2026-09-26
---

**Problem.** The three Bash guards read a command only where its name is the program itself, so a gate, a floor parse or a prune run through a wrapper passes all three: timeout 600 make check | tail -5, timeout 60 python3 -m compileall -q src/anesthesia_sim/, and timeout, env, command or a path to git ahead of git fetch --prune

**Found 2026-09-26 while working `PL-R17X`**, by piping each command as a
hook payload into the hooks on its branch. `make check | tail -5` is refused by
`gate-status-guard.sh` and `timeout 600 make check | tail -5` passes it;
`python3 -m compileall -q src/anesthesia_sim/` is refused by
`floor-interpreter-guard.sh` and `timeout 60 python3 -m compileall -q
src/anesthesia_sim/` passes it; and `no-prune-guard.sh` passes `timeout 60 git
fetch --prune`, `env GIT_TRACE=1 git fetch --prune`, `command git fetch
--prune` and `/usr/bin/git fetch --prune`. Those were run; `nice`, `nohup`,
`xargs` and `exec` are the same shape and were not.

`shell_split.command_words` drops what bash reads ahead of a command's name -
grouping, the reserved words that open a command, `time` and its options,
assignments - and each guard compares the first word left with the program it
guards. A program that runs another is read as the command, and a path to the
program as a different one. `timeout N make check 2>&1 | tail` is a spelling a
session reaches for on a long suite, which is the shape the gate guard exists
to refuse: a red check reaching the session as exit 0.

**Generator check.** One mechanism, one item so far: nothing else in the store
names it.
