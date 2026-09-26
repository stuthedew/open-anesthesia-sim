---
id: PL-9RSP
title: gate-status-guard.sh reads command set -o pipefail as no set at all, so command set -o pipefail; make check 2>&1 | tail -45 is refused, though command runs the set builtin in this shell and the pipe keeps the gate's status
status: untriaged
added: 2026-09-26
---

**Problem.** gate-status-guard.sh reads command set -o pipefail as no set at all, so command set -o pipefail; make check 2>&1 | tail -45 is refused, though command runs the set builtin in this shell and the pipe keeps the gate's status

**Found 2026-09-26 triaging `PL-TRMN`**: the hook refuses the command on
`6d92df95`, and in bash 5.2.21 `command set -o pipefail; false | true; echo $?`
prints 1, so the `set` held. `sets_pipefail` reads the head through
`shell_split.command_words`, which does not step past `command`; `command` is
the one wrapper that runs a builtin in this shell (`help command`). A false
refusal costs one retry, and no session has been seen writing it.
