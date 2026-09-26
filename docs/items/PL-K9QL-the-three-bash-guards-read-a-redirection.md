---
id: PL-K9QL
title: The three Bash guards read a redirection written ahead of a command as the command's name, so 2>/dev/null make check | tail -5, 2>/dev/null python3 -m compileall -q src/ and 2>/dev/null git fetch --prune pass all three, though bash runs make, python3 and git
status: untriaged
added: 2026-09-26
---

**Problem.** The three Bash guards read a redirection written ahead of a command as the command's name, so 2>/dev/null make check | tail -5, 2>/dev/null python3 -m compileall -q src/ and 2>/dev/null git fetch --prune pass all three, though bash runs make, python3 and git

**Found 2026-09-26 triaging `PL-TRMN`**, by piping each as a hook payload
into the three guards on `6d92df95`: all three pass. Bash 5.2.21 runs the
command after a leading redirection - `2>/dev/null echo ran` prints `ran` - and
POSIX.1-2017 XCU §2.9.1 reads a simple command as assignments and redirections
in any order, then the name. `shell_split.command_words` drops assignments but
not redirections, and the lexer returns `2>/dev/null` as the word `2`, the
operator `>` and the word `/dev/null`, so the guard reads `2` as the command.
Its docstring says it drops everything bash reads ahead of a command's name,
which is what `PL-0X0G` (done, #1093) made it do for reserved words.

**Generator check.** A re-entry of `PL-0X0G`: the same fact - which word bash
reads as a command's name, past what it reads ahead of it - at a sibling site
its fix should have covered, closed the same day.
