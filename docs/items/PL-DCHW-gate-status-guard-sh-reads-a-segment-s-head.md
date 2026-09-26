---
id: PL-DCHW
title: gate-status-guard.sh reads a segment's head twice before looking for a set, so FOO=1 time set -o pipefail; make check 2>&1 | tail -5 passes, though after an assignment or a redirection bash runs time as a program and pipefail is never set
status: untriaged
added: 2026-09-26
---

**Problem.** gate-status-guard.sh reads a segment's head twice before looking for a set, so FOO=1 time set -o pipefail; make check 2>&1 | tail -5 passes, though after an assignment or a redirection bash runs time as a program and pipefail is never set

**Found 2026-09-26 closing `PL-9RSP`**, as hook payloads on `17d47ec8`: `FOO=1
time set -o pipefail; make check 2>&1 | tail -5` and `2>/dev/null time set -o
pipefail; make check 2>&1 | tail -5` both pass the gate guard, while `FOO=1 make
check 2>&1 | tail -5` is refused. In bash 5.2.21 `FOO=1 time set -o pipefail;
false | true; echo $?` prints `time: command not found` and then 0: after an
assignment or a redirection `time` is a program's name, not the reserved word
(`PL-0X0G`), so no `set` runs. `pipefail_by_separator` hands `sets_pipefail`
the words `shell_split.command_words` has already stripped, and `sets_pipefail`
strips them again, where the second pass takes `time` for the reserved word and
credits the `set` behind it. A false pass rather than a refusal, though no
session has been seen writing one.
