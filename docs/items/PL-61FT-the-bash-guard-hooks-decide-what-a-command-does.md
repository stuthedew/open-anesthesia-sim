---
id: PL-61FT
title: The Bash guard hooks decide what a command does from its spelling and pass whatever their model of bash and git does not cover, so each fix's session probes the next spelling and files it: the six guard fixes merged on 2026-09-26 filed nine more, and none of the twelve records a session meeting it in ordinary work
priority: P2
effort: M
status: ready
classes: defect
feature: bash-guard-bound
touches: .claude/hooks/shell_split.py, .claude/hooks/gate-status-guard.sh, .claude/hooks/no-prune-guard.sh, .claude/hooks/floor-interpreter-guard.sh, tests/unit/test_gate_status_guard.py, tests/unit/test_no_prune_guard.py, tests/unit/test_floor_interpreter_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed as a generator head at triage
added: 2026-09-26
payoff: each Bash guard's header says what it promises, and a spelling found only by probing is recorded as a known gap beside its tests instead of filed, so fixing one guard spelling stops filing the next as work owed
verify: grep -q 'def test_a_known_gap_keeps_todays_verdict' tests/unit/test_gate_status_guard.py && grep -q 'def test_a_known_gap_keeps_todays_verdict' tests/unit/test_no_prune_guard.py && grep -q 'def test_a_known_gap_keeps_todays_verdict' tests/unit/test_floor_interpreter_guard.py && grep -q 'What it promises' .claude/hooks/gate-status-guard.sh && grep -q 'What it promises' .claude/hooks/no-prune-guard.sh && grep -q 'What it promises' .claude/hooks/floor-interpreter-guard.sh
root-cause-of: PL-0X0G, PL-K9QL, PL-TRMN, PL-9RSP, PL-KQ4Q, PL-R17X, PL-DCHW, PL-QMN0, PL-W9XN, PL-M2NV, PL-YFT4, PL-R5N0, PL-R295, PL-N6JP
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

**Design round, 2026-09-26.** Route 3, bounded by use, and the round's own
count is why. The number the brief named was members met in ordinary work, and
each of the twelve briefs was read for it: every one says "found while
working" or "at triage", most "by piping each as a hook payload", and none
quotes a refusal a session met or a false outcome a session recorded. What
sessions *have* met is already pinned, and all of it is plain spelling: the
pipe to `tail` (the run `PL-D0W8` records), the `$?` reader on the guard's
first live firing, a `{ set -o pipefail; ...; }` group refused while working
an unrelated item (`PL-1SFZ`), a `;` inside a quoted commit message
(`PL-WGFY`), a `python3 -c` reproduction with a `;` in it (`PL-GVFC`), a gate
after a heredoc's terminator (`PL-39LD`), and the bare `python3 -m compileall
src/` (`PL-JQJQ`). The line between those and the twelve is the line the
promise is drawn on, and it held while this round was written: the one gap met
in ordinary work in this session was a false refusal, `python3
tools/pr_body_check.py --help | head`, which no probing had found and which is
filed as `PL-N6JP` under the rule below.

**Route 2 was counted and refused.** Fail-closed on a construct the reader
does not model catches two of the twelve, `PL-R17X` and `PL-M2NV`, and only by
refusing every git option or subcommand its table does not name; the other ten
were misread by a construct the reader believed it modelled - a reserved word
read as a program, a `!` dropped as grouping, a head stripped twice, a regex
wanting a slash - which no fail-closed rule can see, since the reader does not
know it is wrong. What it would refuse is what the "What it does not read"
list in `shell_split.py` names: every `[[ ]]`, `case`, `$(( ))`, function or
`bash -c` with a gate's name inside it, which is `PL-1SFZ`'s false refusal made
policy, and the fail-open trade the three headers record turned round. Where
it belongs is inside a fix, on one construct, once that construct is met: the
gate guard already reads an `||` fallback that way, refusing what it cannot
prove keeps the status (`PL-KQ4Q`), and a met `!` would be read the same.

**A rewrite was counted and refused too.** A `PreToolUse` hook can return
`updatedInput` and prepend `set -o pipefail;` to every Bash call, which would
keep a piped gate's status by construction rather than by reading. Measured
2026-09-26 in bash 5.2.21: under `pipefail`, `git log --oneline | head -1` and
`bin/docket next | head -1` both exit 141, the writer's `SIGPIPE`, so every `|
head` a session writes - and `CLAUDE.md` asks for exactly those - would arrive
as a failure.

**Decided by the round, which ordinary evidence reopens.** Rule 14 puts these
with the session: they rest on what the project wants, and their blast radius
is three hook headers and three test files.

- **The promise, and its test.** A spelling is inside a guard's promise when
  it is written out to be run somewhere in this repository - the `Makefile`,
  the workflows, the hooks, a skill's or `README.md`'s example line, or the
  remedy a guard's own deny message prints - or a session has been seen
  writing it: the refusal it met, quoted in the item it filed, or the false
  outcome it recorded in a commit, a pull request body or a brief. A spelling
  that differs from one of those only in a path's form (`src`, `src/`,
  `./src`, an absolute path, a file below it), an option's order, a count or a
  target is the same spelling. A grammar's synopsis is not use: `bin/docket
  --no-fetch check` is a line argparse admits and nobody has written.
- **The prune guard's is wider, because its outcome cannot be undone.** Every
  spelling git 2.43's own usage documents that deletes refs without naming
  them one by one is inside it, written or not: the `fetch`, `pull` and
  `remote update` prune flags and settings `PL-R17X` read from `git -h`, `push
  --prune` and `--mirror` (`PL-M2NV`), and `remote remove` (`PL-R295`, filed
  by this round after a scratch remote lost every remote-tracking ref to it).
  What its header lists as out of reach - an alias, `GIT_CONFIG_PARAMETERS`,
  an abbreviated long option, a flag built from a variable, a command handed
  to another shell - stays out, since none is a spelling of git.
- **Bash's constructs are bounded by use, not by the manual.** The reader
  reads what sessions write around a guarded command: pipelines, `&&`, `||`,
  `;`, `&`, newlines, `( )`, `{ }`, `if` and the loops, redirections,
  assignments, `cd`, the wrappers `WRAPPERS` names, a bare `uv run`, `command`
  and `builtin`, quoting, heredocs and `$( )`. The "What it does not read"
  list in `shell_split.py`'s docstring is the construct side of the known gaps
  and stays where it is.
- **Each guard, then.** The gate guard promises the listed gates spelled as
  the `Makefile`, the workflows, the skills and its own remedies spell them
  and as sessions have written them - bare, by path, through a bare `uv run`
  or a `WRAPPERS` wrapper, after `cd`, an assignment, a redirection or a
  reserved word, in every list, group and compound its tests pin - and that
  every remedy it prints is admitted. Outside it today: a `!` ahead of a gate
  (`PL-W9XN`), `uv run` with options of its own (`PL-QMN0`), `time` or `!`
  after an assignment or a redirection (`PL-DCHW`), a gate run as `python -m`
  (`PL-7PB9`), `bin/docket` with options ahead of its subcommand (`PL-BM3Z`).
  The floor guard promises a bare interpreter, bare or behind a wrapper, given
  `src` or `tests` in any path form in an argument, a `-c` string or a
  redirection onto its input, or `compileall` or `py_compile` on `.`; outside
  it: a tree reached through `cd`, `find -exec` or a list on standard input,
  and an interpreter named by path, which is the deliberate spelling. The
  prune guard promises the git spellings above through every command shape
  `shell_split.py` reads.
- **A false refusal is worked when met and never probed for.** It announces
  itself - the session it refuses reads the reason and files it, as `PL-1SFZ`,
  `PL-WGFY` and `PL-N6JP` were filed - so recording one found by probing buys
  nothing that meeting it would not, and costs a session now.
- **Where the promise is written.** The first paragraph of each guard's header
  states what it promises and that a spelling outside it is a known gap and
  not a defect; the known gaps are a `KNOWN_GAPS` table in that guard's test
  file, one row per spelling - the command, the verdict it gets today, the
  verdict bash or git gives, and why it is outside the promise, citing the
  item or branch that found it - checked by a test asserting each row still
  gets today's verdict, so a fix that closes one, on purpose or by accident,
  fails the test and moves the row into the promise's own tables. Not
  `xfail`, which `bin/docket verify --self` counts as a test suppression and
  puts before a reviewer.
- **When a gap becomes an item.** A `KNOWN_GAPS` row met in ordinary work is
  worked as a defect at its own rank, with the evidence in its brief; where
  the construct's right reading is open-ended, the fix may refuse that
  construct ahead of a gate outright, as the `||` fallback is read. The number
  that reopens this bound is three rows met within a quarter, which would say
  the line was drawn too tight.
- **The members.** `PL-M2NV` (irreversible) and `PL-R5N0` (`python3 -m
  compileall src`, a path-form variant of the spelling `PL-JQJQ` counted
  sessions writing) are inside and stay ready. `PL-DCHW`, `PL-QMN0`, `PL-W9XN`
  and `PL-YFT4` are outside - probed, written nowhere, met by nobody - and
  become `KNOWN_GAPS` rows in the build, closed dropped with this bound as the
  reason; `PL-YFT4` leaves ready on that reading, a false refusal of spellings
  no session has written. `PL-BM3Z` and `PL-7PB9`, filed on
  `claude/project-thread-qt3onr` and on no other branch, are the same, and the
  build recovers them only to record and close them the same way. `PL-R295`
  and `PL-N6JP` are inside and are worked at their own ranks.
- **The parked `PL-QMN0` work.** `#1127` closed unmerged on 2026-09-26, and
  the branch's copy of the item is back to `blocked`, which releases its
  claim. The fix and its 16 tests stand at `59ea9d1c` on
  `claude/project-thread-qt3onr`, and `PL-QMN0`'s `KNOWN_GAPS` row names that
  commit as the fix ready to rebase should the spelling be met. It is not
  merged now: `uv run` with an option ahead of a gate is written nowhere in
  this repository and has been met by no session, and the fix carries some
  ninety lines of uv 0.12.19's option grammar into `shell_split.py`, a table
  that drifts with uv's releases and whose making filed two more members,
  `PL-BM3Z` and `PL-7PB9`, which is this head's rate.
- **`CLAUDE.md` does not change.** Its capture rule asks that a finding be
  recorded before the session ends and names `bin/docket new` as the
  procedure for a defect. The guard's header is what says a spelling outside
  the promise is not one, and the `KNOWN_GAPS` row is its record; a session
  probing a guard has that guard open. Nothing resident is added, so nothing
  is owed for it.
- **The build.** One thread, after `PL-M2NV` merges, since both edit the
  three headers: the promise paragraphs, the three `KNOWN_GAPS` tables and
  their test, and the six close-outs above. `M`, as triaged.

**The owner's half: what a session files.** A spelling of a guarded command
that a guard misreads is filed as an item only where it is inside the promise
above, or was met in ordinary work, or deletes a ref; one found by probing
the guard, outside the promise, is recorded as a `KNOWN_GAPS` row in the
guard's test file instead, and becomes an item when a session is seen writing
it. That changes what every session files for one class of finding, which is
how every session works, so it is the owner's to answer.

**Recommended: yes.** Over (1) filing every probed spelling as today, which
the count above says does not converge - nine members from six fixes, each
read by the queue as work owed - and over (2) fail-closed, counted and refused
above.

**Answered 2026-09-26: yes** (project owner, 2026-09-26, ratified, "Agree
with recs", over filing every probed spelling as today and over fail-closed).
Both recommendations: the bound above, and holding `PL-YFT4` so no thread
starts it before the build records it as a known gap. The build follows the
plan under "The build": one thread after `PL-M2NV` merges, writing the promise
paragraphs, the three `KNOWN_GAPS` tables and their test, and the close-outs of
`PL-DCHW`, `PL-QMN0`, `PL-W9XN`, `PL-YFT4`, `PL-BM3Z` and `PL-7PB9`; `PL-R295`
and `PL-N6JP` are worked at their own ranks. The design thread moved no
status, and the build thread readied the item on taking it; `bin/docket
generators` should report this head drained when the last of those
close-outs lands.
