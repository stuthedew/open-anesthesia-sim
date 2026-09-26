---
id: PL-61FT
title: The Bash guard hooks decide what a command does from its spelling and pass whatever their model of bash and git does not cover, so each fix's session probes the next spelling and files it: the six guard fixes merged on 2026-09-26 filed nine more, and none of the twelve records a session meeting it in ordinary work
priority: P2
effort: M
status: needs-decision
classes: defect
feature: bash-guard-bound
touches: .claude/hooks/shell_split.py, .claude/hooks/gate-status-guard.sh, .claude/hooks/no-prune-guard.sh, .claude/hooks/floor-interpreter-guard.sh, tests/unit/test_gate_status_guard.py, tests/unit/test_no_prune_guard.py, tests/unit/test_floor_interpreter_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed as a generator head at triage
added: 2026-09-26
root-cause-of: PL-0X0G, PL-K9QL, PL-TRMN, PL-9RSP, PL-KQ4Q, PL-R17X, PL-DCHW, PL-QMN0, PL-W9XN, PL-M2NV, PL-YFT4, PL-R5N0
generator: live - each fix reads one more spelling as bash or git reads it, and the session making it probes the spellings beside it and files each gap: the six member fixes merged on 2026-09-26 filed nine more members in their own closing commits
misread: What a shell command does when run: which program it runs, on what, and whether its status survives
---

**Problem.** The Bash guard hooks decide what a command does from its spelling and pass whatever their model of bash and git does not cover, so each fix's session probes the next spelling and files it: the six guard fixes merged on 2026-09-26 filed nine more, and none of the twelve records a session meeting it in ordinary work

**How the members were found, measured 2026-09-26.** Each was filed in the
closing commit of another guard fix, by the session making it:

- `PL-WGFY`'s close (`2983adfe`, the last `PL-PVW2` member) filed `PL-0X0G`
  and `PL-R17X`.
- `PL-0X0G`'s (`4d6f86b9`) filed `PL-KQ4Q`, and `PL-KQ4Q`'s (`324ce685`) filed
  `PL-W9XN`.
- `PL-R17X`'s (`0d8ffd1a`) filed `PL-TRMN`, `PL-M2NV` and `PL-YFT4`.
- `PL-TRMN`'s (`de5f1c02`) filed `PL-K9QL`, `PL-9RSP` and `PL-QMN0`, and
  `PL-9RSP`'s (`2de8cb0b`) filed `PL-DCHW`.
- `PL-GVFC`'s (`041e1603`, a `PL-PVW2` member) filed `PL-R5N0`.

The six member fixes merged that day filed nine more members, 1.5 per fix,
above the 1.0 at which `PL-NZC0`'s trial reads a run as growing the queue
faster than it drains it. Each brief says it was found working or triaging
another guard item; none records a session meeting its spelling in ordinary
work, and `PL-9RSP`, `PL-DCHW` and `PL-W9XN` say that none has. Nine of the
twelve are false allowances and three are false refusals (`PL-9RSP`,
`PL-KQ4Q`, `PL-YFT4`). Piped as hook payloads on `origin/main` the same day,
all six open members still reproduce as filed.

**The mechanism.** Each guard decides whether a command has the effect it
exists to stop - a red gate's status lost down a pipe, a ref pruned, a 3.14
tree parsed by 3.11 - from the command's spelling, reading bash's grammar and
each program's options with a model of its own, and passes whatever the model
does not cover. That grammar and those options are open-ended, so the
spellings never run out: each fix reads one more construct, and the session
making it probes the constructs beside it and files each gap, as the capture
rule tells it to. The members misread different constructs of one fact, what
a shell command does when it runs. `PL-K9QL`'s check declined a head at this
altitude because they are gaps "in one reader ... not one fact read by
several"; triage's test counts items rather than readers ("Sharing a misread
fact is sharing one, across any number of readers"), and the lineage above is
the one reader handing them out.

**Why it matters.** At the measured rate the stream does not converge: each
fix costs a session and files one and a half more, and each has been for a
spelling no session is recorded as writing, so the work is not buying the
safety it appears to.

**Decision needed.** What the three guards promise, so that a spelling outside
the promise is not a defect:

1. Every spelling with the guarded effect - today's practice, which the count
   above says does not converge.
2. Fail closed: refuse, naming the rewrite, any command holding a construct
   the reader does not model. It ends false allowances by construction, turns
   them into refusals that cost a call when met, and needs the reader to know
   exactly which constructs it models.
3. Bounded by use: each guard's docstring names what it promises - the
   canonical spellings of the command it guards and their common variants,
   and any spelling whose unguarded outcome cannot be undone - and a spelling
   found only by probing is recorded as a known gap in the guard's test file
   rather than filed, becoming an item when a session is seen writing it.

**Recommendation: 3.** The number that would change it is the one measured
above, members met in ordinary work, which stands at none of twelve; one met
argues for 2 on that construct. It is the standard placement of a pattern
filter: OWASP calls a denylist relied on as the barrier "a massively flawed
approach", notes that such filters "frequently prevent authorized input",
and places one "as an additional layer of defense ... to help catch some
commonly observed attacks or patterns" (OWASP Cheat Sheet Series, *Input
Validation Cheat Sheet*, § "Allowlist vs Denylist", read 2026-09-26 from
https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Input_Validation_Cheat_Sheet.md).
The gate guard sits in front of that barrier already: CI's required gate,
which a red tree cannot merge past. `PL-M2NV` (a mirror push deletes other
sessions' branches on the remote, and cannot be taken back), `PL-R5N0`
(`python3 -m pytest tests` is the canonical spelling) and `PL-YFT4` (canonical
reads refused) stay owed under 3, so they are left `ready` at their own
ranks; `PL-DCHW`, `PL-QMN0` and `PL-W9XN` turn on the answer and are blocked
on this item. Choosing the route is the session's that takes this item.
Writing 3 down changes what a session files for one class of finding, which
is how every session works, so that half goes to the owner with this
recommendation.

**Done when.** The bound is decided and written where a session editing each
guard reads it, in its docstring; each open member is worked, dropped with the
bound as its reason, or recorded as a known gap against it; and `bin/docket
generators` no longer reports this head still generating.
