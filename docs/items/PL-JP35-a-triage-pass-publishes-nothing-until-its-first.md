---
id: PL-JP35
title: A triage pass publishes nothing until its first push, so two passes started minutes apart cannot see each other: on 2026-11-03 a Projects thread pushed triage of 17 guard items at 16:21 CST, six minutes after this session sent agents to triage the same items, and list_sessions lists no Projects thread
priority: P2
effort: S
status: blocked
classes: infra
feature: triage-collisions
touches: .claude/skills/docket/modes/triage.md
blocked-by: PL-J1ZM
added: 2026-11-03
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

**Why it matters.** Each collision spends a pass's work on items another pass has already answered. On 2026-11-03 that was about 620,000 tokens. The re-read before each push stops a lost answer, but it comes after the spend.

**Recommended, for when the pause lifts.** Use the claim machinery that exists instead of a new marker. At the start of a pass, `bin/docket claim <ids> --push` on the items it will answer, so a second pass's `bin/docket triage` marks them `IN FLIGHT`. Check first whether a claim on an untriaged item survives the triage write that moves its status.

**Blocked on the generator pause.** Either route is a new rule or mechanism for the workflow, which `CLAUDE.md` holds while a workflow-lane head carries `generator: live`. `PL-J1ZM` is that head on 2026-11-04.

**Generator check.** Re-entry of `PL-MB2W`'s fact, who holds an item now: a triage pass holds ids before anything records that it does. `PL-MB2W` closed on 2026-09-25, so this is an instance after the head closed, recorded as `reenters`.
