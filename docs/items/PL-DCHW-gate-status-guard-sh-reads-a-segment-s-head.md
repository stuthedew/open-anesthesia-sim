---
id: PL-DCHW
title: gate-status-guard.sh reads a segment's head twice before looking for a set, so FOO=1 time set -o pipefail; make check 2>&1 | tail -5 passes, though after an assignment or a redirection bash runs time as a program and pipefail is never set
priority: P3
effort: S
status: blocked
classes: defect
feature: bash-guard-bound
touches: .claude/hooks/gate-status-guard.sh, tests/unit/test_gate_status_guard.py
blocked-by: PL-61FT
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
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

**Why it matters.** A false allowance of the failure the guard exists for:
after an assignment or a redirection no `set` runs, so a red `make check`
piped to `tail` reaches the session as exit 0. Reproduced as filed on
`origin/main` (`6efd8c41`) at triage, 2026-09-26, beside `FOO=1 make check
2>&1 | tail -5`, which is refused.

**Generator check.** A member of `PL-61FT` (the Bash guards read what a
command does from its spelling): filed by `PL-9RSP`'s close, at the reader
`PL-0X0G` and `PL-9RSP` fixed. Blocked on it, because the bound it sets
decides whether this spelling is worked, dropped or kept as a known gap.
