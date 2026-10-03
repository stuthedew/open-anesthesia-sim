---
id: PL-PDVF
title: Rules the owner sets for sessions in the Projects trial's instructions reach no repository file, so a session outside the Project follows an older rule and a Project thread reads two that disagree: PL-8XQS, PL-F23S and the arm rule for read holds
priority: P1
effort: M
status: ready
classes: defect, infra
feature: owner-rules-in-repo
touches: docs/maintainer.md, CLAUDE.md, .claude/skills/docket, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21) and not safety or science; the Projects trial began on 2026-09-25, so the problem was not present at the freeze, and nothing on the frozen list names it
added: 2026-10-03
payoff: a rule the owner gives in the Project reaches every session from one record, so no session follows a rule he has replaced and no thread chooses between two
verify: grep -qF '## Rules for sessions live in the repository' docs/maintainer.md
root-cause-of: PL-8XQS, PL-F23S, PL-KKHD
generator: live - the Projects trial is running and its instructions are still edited as the owner gives rules: the arm paragraph cites #1283 of 2026-10-03, and its Combining items rule (asked 2026-09-30) has no counterpart in the repository outside item files
misread: The owner's current rules for sessions, as the Project's instructions and the repository hold them
---

**Problem.** Rules the owner sets for sessions in the Projects trial's instructions reach no repository file, so a session outside the Project follows an older rule and a Project thread reads two that disagree: PL-8XQS, PL-F23S and the arm rule for read holds

**The mechanism.** The Projects trial (`PL-NZC0`) gave the owner a second place
to set rules for sessions: the Project's instructions, which only the
coordinator and its threads receive and no repository file mirrors. A rule
given there, or written there by the coordinator for him, leaves the
repository's copy missing or older, so a session outside the Project follows
the old one and a Project thread receives both. `CLAUDE.md`'s "A behavior
change takes effect in the session that asks for it" binds the session that was
asked, and when that is the coordinator, the edit it makes is to the
instructions, or a section posted for the owner to paste.

**Members**, one fact read from two records:

- `PL-8XQS` (closed 2026-10-01): a review ask's plain-language summary was a
  "Review asks" rule in the instructions only. Its own check: "the request
  reached the Project's instructions and not the repository."
- `PL-F23S` (closed 2026-10-03): the instructions' Releases rule carried the
  owner's new wording for re-running `tag-release.yml`, while the release
  skill and `bin/docket release` still handed that step to him.
- `PL-KKHD` (2026-10-03): the arm rule for read holds.

`PL-NXRJ` met the same split from the other side for three days: the
instructions had asked for a direct squash merge since 2026-09-27, and the
repository's hook refused it from 2026-09-30.

**Why it matters.** Each such rule costs the owner twice. A session outside the
Project acts on the old rule (`PL-F23S` handed him a step he had already made a
session's), and a Project thread has to choose between two instructions that
each carry his authority. No check can catch it, since nothing in the
repository can read the Project's instructions.

**Why it is live.** The trial is running, and its instructions are still edited
as the owner gives rules: the arm paragraph cites `#1283` of 2026-10-03, and the
"Combining items" rule (asked 2026-09-30) has no counterpart in the repository
outside item files (`git grep`, 2026-10-03). `PL-NZC0`'s copy of the
instructions, taken 2026-09-25, already reads differently from today's.

**Recommendation: one record, the repository.**

1. Sweep the instructions once. Each rule about how a session works either has
   a repository home already, gets one by `CLAUDE.md`'s routing (a check, a
   skill, a path-scoped rule, then resident), or is the trial's own
   coordination: the Order, thread caps, model choice and where to post.
2. Cut the instructions to that coordination, plus one line: every rule about
   how a session works is the repository's, and where the two disagree the
   thread reports it rather than choosing. The owner pastes the result, since
   no session can edit the instructions.
3. One section in `docs/maintainer.md` for the owner's side: a rule for
   sessions given to the coordinator goes to a thread that writes it into the
   repository, and the instructions name it instead of restating it.

The cheaper route, a dated copy of the instructions in the repository for
sessions outside the Project to read, keeps both records and adds a third, and
`PL-NZC0`'s copy shows how it ends.

**Generator check.** This item is the head. No head's `misread:` in
`bin/docket generators --misread` states this fact (read 2026-10-03), and no
check can hold it, since the Project's instructions sit outside the tree.

**Done when.** Every rule about how a session works that the instructions carry
has a repository home, the instructions carry none of their own, and a
section of `docs/maintainer.md` says where a new one goes.
