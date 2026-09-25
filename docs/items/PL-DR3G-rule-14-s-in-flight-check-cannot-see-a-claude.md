---
id: PL-DR3G
title: Rule 14's in-flight check cannot see a Claude Code Projects thread: list_sessions(mine) omitted the running 'Stream B: PL-J16N' session (origin claude-in-hearth, tag hearth-thread) across two pages, and its tags filter answers 'not currently available', so during the trial only a pushed claim reveals a thread's work
priority: P3
effort: S
status: ready
classes: docs
feature: projects-trial
touches: .claude/rules/instruction-writing.md
added: 2026-09-25
payoff: a session checking for other sessions' work knows a Projects thread never appears in list_sessions and where the trial records what its threads will take, so it does not triage or start work a thread holds
verify: grep -qF 'hearth-thread' .claude/rules/instruction-writing.md
---

**Problem.** Rule 14's in-flight check cannot see a Claude Code Projects thread: list_sessions(mine) omitted the running 'Stream B: PL-J16N' session (origin claude-in-hearth, tag hearth-thread) across two pages, and its tags filter answers 'not currently available', so during the trial only a pushed claim reveals a thread's work

Reproduced 2026-09-25 against 46954a81, in the triage session that filed this: `list_sessions` (`mine: true`) returned 20 sessions over two pages, none of them the Projects trial's threads. `bin/docket flight` meanwhile showed `PL-J16N` under a live claim on `origin/claude/pl-j16n-xfppe6`, and the claim commit's `Claude-Session:` line named `session_01PdQP3NoDQUzXnuUfR76Eff`. `get_session` on that id answered `RUNNING`, titled "Stream B: PL-J16N", `origin: claude-in-hearth`, tags `hearth-thread` and `config:hearth`, with a `parent_session_id` (the coordinator). `list_sessions` with `tags: ["hearth-thread"]` answered `tags filter is not currently available`.

**Why it matters.** `.claude/rules/instruction-writing.md` rule 14 makes `list_sessions` the one call that shows work nobody has claimed yet: a release cut, a merge, and a triage pass. `PL-NZC0`'s project instructions reserve the triage of each untriaged Stream item for "the thread that takes it" (`PL-KX73`, `PL-1X56`, `PL-ZLJ9` today). No thread has claimed those yet, and the claim is the only thing a checkout can read, so a session following rule 14 finds nothing and triages them. The collision then happens at the merge, which is the `PL-N1JK` failure. This session avoided it only because it read `PL-NZC0`'s brief. The rule already says an empty result "means nothing", so no check is claiming a guarantee it lacks. What is missing is the reason it means nothing here: the rule does not say.

**Done when.** Rule 14's `list_sessions` bullet says that Projects threads (tag `hearth-thread`) are not listed and cannot be filtered for, and names where their reserved work is recorded while a trial runs. That is `PL-NZC0`'s Order list. The rule's closing sentence says the edit's character cost and what it replaces, per `CLAUDE.md`. Or, if the harness starts listing them by then, this item is dropped with that measurement.

**Generator check.** The fact misread is "who holds an item now", which is `PL-MB2W`'s `misread:`. It is read here from the harness's session list, which sees only some holders. `PL-MB2W`'s claim record is the reader that sees every holder, so this is a one-off documentation gap at an external reader, not a new head.
