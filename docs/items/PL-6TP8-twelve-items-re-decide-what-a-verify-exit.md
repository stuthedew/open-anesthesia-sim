---
id: PL-6TP8
title: Twelve items re-decide what a verify: exit status proves, because the field was specified as a command string and nothing else: one contract rather than twelve patches
priority: P2
effort: M
status: done
classes: defect, infra
feature: generator-heads
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/checks.py, subprojects/docket/README.md, .claude/skills/docket/SKILL.md, docs/items
added: 2026-09-17
closed: 2026-09-19
pr: 684
verify: grep -qF 'what the work adds, alone' .claude/skills/docket/SKILL.md
root-cause-of: PL-T7VS, PL-0M32, PL-Q8RQ, PL-6TN8, PL-D0K3, PL-3DXV, PL-6YWK, PL-2M4X, PL-6YL1, PL-Y4YX, PL-H9GV, PL-LBW5
---

**Problem.** `verify:` was specified as "a command that fails before the work
and passes after" and nothing else about it was written down. Every consumer -
`docket check --verify`'s landed sweep, the whole-store replay on `main`, the
delegated audit, the close-out - therefore reads its own meaning out of one
exit code, and a non-zero exit means all of "not started", "prerequisite
broken", "selected nothing", "timed out" and "finished under another name".
Twelve open items each answer some part of that for themselves.

**Why it matters.** The mechanism is the one `PL-6ZQY`'s map named under 47% of
the workflow lane: *the apparatus infers a fact it could have recorded.* What a
command's exit status is allowed to prove is a fact the field could carry and
does not, so each consumer infers it, each inference fails in a new way, each
failure is found singly, and each becomes its own item. Patching one closes an
item and leaves the generator standing - `PL-T7VS` (a red `doc_check` voids the
replay for the 29 items gated behind it) and `PL-6YWK` (a command killed at the
120 s limit claims nothing on any run) are the same sentence about two
different consumers.

It is not only queue churn. `bin/docket verify` accepts a delegated branch on a
command that cannot discriminate (`PL-D0K3`, ten `doc_check.py check`
commands), and `bin/docket delegable` hands a cheaper model a commission whose
command proves the wrong tree (`PL-2M4X`). Both are a check passing while the
guarantee it stands for is void, which is `CLAUDE.md`'s first
compounding-friction test.

**Why this item is the head, and no member is.** Confirmed against the store on
2026-09-18. `PL-LKGL` is the measurement `PL-6ZQY` cites and it is `done`
(`#658`): it names the root sentence - the field tests for the presence of the
fix, never for the presence of the fault - decided one facet, and explicitly
refused the recorded fault test, so the general contract was left unwritten.
`PL-0M32` is the sharpest sub-question ("can 'finished under a renamed test' be
told from 'not started' at all") and is scoped to that one ambiguity. `PL-D0K3`
is a policy question about ten specific `doc_check` commands. None settles what
an exit code may be read to mean, and promoting one of them would rank a narrow
item above every band but `P0` where nobody could work the cluster from it.

**Decided 2026-09-19, the reading half** - a session's decision, taken off the
code and the measurements below, and written where the consumers read it:
`subprojects/docket/README.md` § "What a `verify:` exit status proves, and to
whom", the `docket` skill's `verify:` section, and the docstrings of
`already_passing`, `verify_item`, `_check_landed` and `_check_selects_nothing`.

- **No fault test is recorded beside the fix test.** `PL-LKGL`'s refusal
  stands (project owner, 2026-09-17, ratified): a second command per item,
  written at the same moment as the first and wrong in the same ways, and the
  sweep is the mechanism with evidence behind it. The renamed-test case
  (`PL-0M32`, `PL-6TN8`) is the same undecidability from the other side and is
  recorded as such: a fix test cannot tell "absent" from "present under
  another name", so the author checks the code before pinning a name and the
  close-out reads the command against the diff.
- **A command that could not run is three decidable refusals and one that is
  not.** Killed at the limit, not found by the shell, and pytest's "selected
  nothing" are read off the run and reported under "not checked"; a red
  prerequisite clause is not decidable from the exit of an `&&` chain, so the
  replay reads nothing from any plain failure.
- **The replay may decline; the audit may not.** `already_passing` is
  one-directional - exit 0 is its finding, everything else is a refusal or
  nothing - and says so when it declines. `verify_item` reads every non-zero
  status as `REJECT` with the reason on the line, because the command is the
  thing being asked about.
- **The command owes its item three things** an exit status can never check
  afterwards: it discriminates on this item's own work (`PL-3DXV`, `PL-Q8RQ`),
  it reads the tree the item's `touches` declares (`PL-LBW5`, `PL-2M4X`,
  `PL-6YL1`), and it was run and watched fail for a reason the author
  understood.

**Decided 2026-09-19, the shape half** (project owner, 2026-09-19, ratified -
chosen over keeping the paired shape, and repair-as-started chosen over a
one-pass strip of the 162): the field does not carry a prerequisite clause.
The question as it was put, and the case, are kept below as the record. The
`docket` skill's table now prescribes the `grep` alone, the README's contract
section records the decision, and `PL-T7VS` and `PL-6YL1` dropped against it.

The question was whether the field carries a prerequisite clause at all. The
`docket` skill's table prescribed `pytest <file> && grep -q 'def test_x'
<file>` and `python3 tools/doc_check.py check && grep -qF '…' docs/MODEL.md`,
on the argument that the first half "proves the file's suite healthy".
Measured 2026-09-19 against the open store, that half is what generated the
cluster:

| | |
| --- | --- |
| open items carrying a `verify:` (`ready`, `needs-decision`) | 177 |
| ...whose command carries a prerequisite clause | 162 |
| whole-store replay, commands as recorded | 176 commands, 275.9 s wall, 1,884 s serial, slowest 102.2 s against the 120 s limit, one killed |
| the same commands with the prerequisite clauses removed | 175 commands, 0.9 s wall, 4.6 s serial, slowest 0.7 s |
| discriminators exiting 0 once the clause is removed (a pass the clause masked today) | 0 |
| name-pinning `grep 'def test_…'` clauses | 63, none naming a test that already exists |

**The recommendation, as ratified: the field records the discriminator only,
and the health check is the consumers' to run.** Every prerequisite clause in the store is a
line of `make check`, and every consumer that needs the tree proven already
proves it there: `docket verify` runs `config.check_command` as its own line
of the report, `docs/worker.md` runs `make check` after the command, and CI's
quality job runs `doc_check`, `bin/docket check` and the whole suite as steps
ahead of the replay. So the clause proves nothing twice and costs three
things: it makes a non-zero exit unreadable (`PL-T7VS`), it is 99.7% of the
replay's serial cost and the whole of its timeouts (`PL-6YWK`, `PL-8T83`), and
it is the half that can name the wrong tree (`PL-2M4X`, `PL-6YL1`). Under it
the skill's table becomes `grep -q 'def test_halted'
tests/unit/test_simulation_view.py` and `grep -qF 'the sentence'
docs/MODEL.md`, with the coverage row unchanged (`--cov` is the discriminator
there). What it costs: the skill's rationale for the pair is rewritten, and
162 recorded commands keep their clause until each item is started - the
repair-as-started policy `PL-D0K3` reaffirms - so the replay's bill falls as
the queue turns over rather than in one day. A mechanical pass stripping the
known prerequisite prefixes from the 162 is the alternative: it writes no new
command, since each discriminator stays as its author ran it, but it touches
162 item files in one pull request against every branch in flight, so it is
offered rather than recommended.

What would change the recommendation: a prerequisite clause that proves
something `make check` does not. None of the 162 does; the nearest is
`PL-4L6Z`'s whole `tests/reference/` run, and `make check`'s suite collects
that directory.

**The items this explains (12, confirmed 2026-09-18 against each brief).**
`PL-T7VS`, `PL-0M32`, `PL-Q8RQ`, `PL-6TN8`, `PL-D0K3`, `PL-3DXV`, `PL-6YWK`,
`PL-2M4X`, `PL-6YL1`, `PL-Y4YX`, `PL-H9GV`, `PL-LBW5`.

Eleven are the 2026-09-17 candidate list, each re-read and still open.
`PL-LBW5` is added: five items' commands `grep` a file their own `touches` does
not declare, which is `PL-2M4X`'s defect generalized, and it carries the
`verify-command-health` feature the project already groups this work under.
Two members carry a second question the head does not settle and are named
here for the half that is the mechanism: `PL-Y4YX` also asks whether
`app/theme.py`'s PySide6 invariant is right, and `PL-H9GV` also owes
`PL-01GD` a test.

**Considered and left out**, each on its own brief rather than on its title:
`PL-8T83` (a 62.6 s command in the scoped replay) and `PL-SHTR` (a nested
replay one level down) are costs of running a command, not readings of its
result; `PL-BGMK` (two items' `touches` and commands overlap and are never
compared) is duplicate detection using `verify:` as evidence; `PL-PFK1` (a
`REJECT` on a self-audited branch) is the commission audit's verdict rather
than the `verify:` command's; `PL-MSFB` and `PL-0HPV` are a stale workaround
and a placement question. Any of them may join on a later reading; none of
them was confirmable from its brief today.

**Done when.** The contract above is decided and written where the consumers
read it - the field's own documentation and `.claude/skills/docket/SKILL.md`'s
`verify:` section - each consumer in `verify.py` and `checks.py` states which
conclusion it is entitled to draw, and the twelve members are re-pointed at the
decision or dropped against it.

**Where this came from.** `PL-6ZQY` found six clusters under one mechanism -
*the apparatus infers a fact it could have recorded* - and `PL-VX5H` built the
way to rank one: `root-cause-of:` on the item that causes the cluster, which
`docket next` then offers above every band but `P0`. Marking the six on
2026-09-17 found only two with a causing item in the store (`PL-BHVM`,
`PL-L4YG`); this item was filed to record that this cluster had none. On
2026-09-18 it became the head itself rather than a tracker of one, which is the
cheaper of the two endings its own `Done when` offered: the diagnosis, the
decision and the membership were already written here, and a separate head
would have been one more item to work.

**The twelve, re-pointed 2026-09-19.** Each brief carries its own note; this
is the map.

| Item | Disposition |
| --- | --- |
| `PL-0M32` renamed test against not started | **done** - recorded in the contract as undecidable by any exit status |
| `PL-6TN8` a name-pinning `grep` proves less than the rule assumes | **done** - 63 such clauses, none already resolving, the judgment half not countable; the skill carries the sentence |
| `PL-D0K3` ten non-discriminating `doc_check` commands | **dropped** - population zero today; repair-as-started held |
| `PL-Q8RQ` a bare `-k` refused by `docket check` | stays `ready` - obligation 1 made mechanical, as briefed |
| `PL-3DXV` four qt-port commands a neighbour satisfies | stays `ready` - obligation 1, as briefed |
| `PL-LBW5` commands grep a file `touches` omits | stays `ready` - obligation 2, as briefed |
| `PL-H9GV` the test `PL-01GD` owed | stays `ready` - a closed command is a record; the test is ordinary work |
| `PL-Y4YX` `app/theme.py`'s toolkit rule | stays `needs-decision` - its `verify:` half closed with `PL-L9RD`; what remains is not this cluster's |
| `PL-T7VS` a red prerequisite voids the replay | **dropped** - the clause the hoist was for is retired; the legacy commands lose it as their items start |
| `PL-6YWK` `PL-4L6Z`'s command killed at the limit | stays `ready` - the repair is fixed: the command becomes the `grep` alone |
| `PL-2M4X` `PL-J45M`'s wrong pytest half | stays `ready` - the `touches` correction stands; the pytest half is removed, not replaced |
| `PL-6YL1` the docket-suite rule as a check | **dropped** - no new command carries a pytest target; the six legacy ones lose theirs as their items start |

**Standing, 2026-09-19, closed.** Both halves are decided and written where
the consumers read them; the skill's table prescribes the `grep` alone;
`PL-0M32` and `PL-6TN8` closed, `PL-D0K3`, `PL-T7VS` and `PL-6YL1` dropped,
the other seven re-pointed. The command recorded above was run before the
skill's table was rewritten (exit 1) and after (exit 0).
