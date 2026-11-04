---
id: PL-JP35
title: A triage pass publishes nothing until its first push, so two passes started minutes apart cannot see each other: on 2026-11-03 a Projects thread pushed triage of 17 guard items at 16:21 CST, six minutes after this session sent agents to triage the same items, and list_sessions lists no Projects thread
priority: P2
effort: S
status: ready
classes: defect, session-cost
feature: claim-record
touches: .claude/skills/docket/modes/triage.md
deferred-from: v0.7.0 - captured after the freeze; an apparatus defect in the workflow lane, not safety or science
added: 2026-11-03
payoff: a second triage pass sees which ids a first pass has taken before either spends anything on them
verify: grep -qF 'Claim the ids this pass will answer' .claude/skills/docket/modes/triage.md
reenters: PL-MB2W
---

**Problem.** A triage pass publishes nothing until its first push, so two passes started minutes apart cannot see each other: on 2026-11-03 a Projects thread pushed triage of 17 guard items at 16:21 CST, six minutes after this session sent agents to triage the same items, and list_sessions lists no Projects thread

**What happened, 2026-11-03.** This session ran `bin/docket triage` at 16:12 CST.
No ref then held any of the 28 untriaged items except `PL-3D2F` and `PL-R1HT`,
so it sent four agents to triage the rest at about 16:15 CST. A Projects thread
committed its triage of 17 guard-review items on `claude/project-thread-cp7ce8`
at 16:21 CST and pushed it. `bin/docket flight` showed the collision only when
the owner asked about it. The re-read before each push that
`.claude/skills/docket/modes/triage.md` requires (`PL-XJ22`) would have caught it
before anything merged, so no work was lost. The cost was the duplicated work: three agents
used about 620,000 tokens between them, and most of that went on items the
thread had already answered. `list_sessions` from the `claude-code-remote` MCP server lists no Projects thread
(measured 2026-09-25, `.claude/rules/instruction-writing.md` rule 14), so nothing a
session can read at the start of a pass shows another pass that has not pushed.

**Earlier instances.** `PL-N1JK` (2026-09-06, one of two identical answers
discarded at merge) and `PL-XJ22` (two of about nine passes between 2026-09-24
and 2026-10-11). Both fixes catch a collision at push or merge time, after the
work is spent.

**A route to weigh at triage.** A pass publishes which ids it is taking before
it spends anything on them, for example by pushing its branch with a marker
per id, so a second pass's `bin/docket triage` shows them `IN FLIGHT`. That would be a new
workflow mechanism, so the generator pause in `CLAUDE.md` applies to it while a
workflow-lane head is live.

**Why it matters.** When two passes overlap, the second one's work is spent
twice. The overlap on 2026-11-03 cost about 620,000 tokens, and each of the two
earlier instances threw away a finished answer at merge. Nothing a session can
read when it starts shows a pass that has not pushed. So only the first pass
can prevent the overlap, by publishing what it is taking.

**Route taken, 2026-11-04.** The marker per id already exists. `bin/docket
claim` writes one `Claim:` trailer per id in one commit and pushes it at once.
`bin/docket triage` marks a claimed id `IN FLIGHT` for every other session,
because both commands read `claims.holdings`. Measured on this branch: after
`bin/docket claim PL-JP35`, `bin/docket triage` printed "IN FLIGHT on
claude/pl-jp35-4kmsu9" under this item. So the fix is a step in the triage
procedure that uses two existing commands. It adds no command, check or field,
which is why the sentence above about the generator pause does not apply. The
project owner also started this item by name on 2026-11-04, which lifts the
pause for it in any case (`PL-6Q9L`). `PL-MB2W`'s design round named this gap,
"a queue-only round that forgets to claim", and decided against a check for
it, so none is added here.

Two facts from the code shape the step. A claim on several ids is all or
nothing: where another branch holds one id first, the whole call is refused and
the refusal names that id (`claiming.claim`). And an open claim stops
`bin/docket arm` from arming the branch. Leaving an item at `ready` or
`needs-decision` does not release a claim; only a closed or newly blocked
status does (`claims.releases`). So the pass ends each claim it leaves open
with `bin/docket yield` before the push that arms it. Once pushed, the status
the pass wrote keeps the item marked in flight until the branch merges, as the
`claims` module docstring describes for a disposition.

**Generator check.** The fact misread is who holds an item now, which
`PL-MB2W`'s `misread:` states. This item is an instance filed after that head
closed, so it is recorded `reenters: PL-MB2W`. It is the second such filing,
after `PL-XJ22`, one short of the three that would make it a generator.

**Done when.** `.claude/skills/docket/modes/triage.md` tells a pass to claim the
ids it will answer before it reads a brief or sends an agent, to claim the rest
when one id is refused, and to yield the ids it leaves open before the push
that arms the branch.
