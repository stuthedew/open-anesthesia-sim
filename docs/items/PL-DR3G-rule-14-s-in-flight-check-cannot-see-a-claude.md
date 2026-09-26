---
id: PL-DR3G
title: Rule 14's in-flight check cannot see a Claude Code Projects thread: list_sessions(mine) omitted the running 'Stream B: PL-J16N' session (origin claude-in-hearth, tag hearth-thread) across two pages, and its tags filter answers 'not currently available', so during the trial only a pushed claim reveals a thread's work
priority: P3
effort: S
status: done
classes: docs
feature: projects-trial
touches: .claude/rules/instruction-writing.md, .claude/skills/docket/modes/start.md, docs/resident-instructions.md
added: 2026-09-25
closed: 2026-09-25
payoff: a session checking for other sessions' work knows a Projects thread never appears in list_sessions and where the trial records what its threads will take, so it does not triage or start work a thread holds
verify: grep -qF 'hearth-thread' .claude/rules/instruction-writing.md
---

**Problem.** Rule 14's in-flight check cannot see a Claude Code Projects thread: list_sessions(mine) omitted the running 'Stream B: PL-J16N' session (origin claude-in-hearth, tag hearth-thread) across two pages, and its tags filter answers 'not currently available', so during the trial only a pushed claim reveals a thread's work

Reproduced 2026-09-25 against 46954a81, in the triage session that filed this: `list_sessions` (`mine: true`) returned 20 sessions over two pages, none of them the Projects trial's threads. `bin/docket flight` meanwhile showed `PL-J16N` under a live claim on `origin/claude/pl-j16n-xfppe6`, and the claim commit's `Claude-Session:` line named `session_01PdQP3NoDQUzXnuUfR76Eff`. `get_session` on that id answered `RUNNING`, titled "Stream B: PL-J16N", `origin: claude-in-hearth`, tags `hearth-thread` and `config:hearth`, with a `parent_session_id` (the coordinator). `list_sessions` with `tags: ["hearth-thread"]` answered `tags filter is not currently available`.

**Why it matters.** `.claude/rules/instruction-writing.md` rule 14 makes `list_sessions` the one call that shows work nobody has claimed yet: a release cut, a merge, and a triage pass. `PL-NZC0`'s project instructions reserve the triage of each untriaged Stream item for "the thread that takes it" (`PL-KX73`, `PL-1X56`, `PL-ZLJ9` today). No thread has claimed those yet, and the claim is the only thing a checkout can read, so a session following rule 14 finds nothing and triages them. The collision then happens at the merge, which is the `PL-N1JK` failure. This session avoided it only because it read `PL-NZC0`'s brief. The rule already says an empty result "means nothing", so no check is claiming a guarantee it lacks. What is missing is the reason it means nothing here: the rule does not say.

**Done when.** Rule 14's `list_sessions` bullet says that Projects threads (tag `hearth-thread`) are not listed and cannot be filtered for, and names where their reserved work is recorded while a trial runs. That is `PL-NZC0`'s Order list. The rule's closing sentence says the edit's character cost and what it replaces, per `CLAUDE.md`. Or, if the harness starts listing them by then, this item is dropped with that measurement.

**Generator check.** The fact misread is "who holds an item now", which is `PL-MB2W`'s `misread:`. It is read here from the harness's session list, which sees only some holders. `PL-MB2W`'s claim record is the reader that sees every holder, so this is a one-off documentation gap at an external reader, not a new head.

**Outcome, 2026-09-25.** Re-measured before editing, so the drop branch of "Done when" did not apply. `list_sessions` left out both the Stream B thread and the trial's coordinator (`session_01Csp2RS7xQhgonKyR47cRvu`, tag `hearth-overview`), with `mine: true` (28 rows over two pages) and without it (12 rows). The `tags` filter still answered "tags filter is not currently available", which the tool's own description says it does for an in-session caller, and `ListAgents` listed no session at all. Rule 14's bullet now ends: "`list_sessions` lists no Projects thread (measured 2026-09-25): those, tagged `hearth-thread`, are left out with or without `mine`, and the `tags` filter is refused inside a session. So while `PL-NZC0`'s Projects trial runs, triage and start nothing its Order list reserves (`PL-DR3G`)." `.claude/skills/docket/modes/start.md` said the call "returns every session's title". It now excepts a Projects thread and points at rule 14. The cost (311 characters), why nothing was cut, and what retires each sentence are in `docs/resident-instructions.md` § "Rule 14's Projects-thread sentence, added 2026-09-25". That ledger is where the project keeps `CLAUDE.md`'s "names what it replaces", so it is not in the rule itself.

**The generator pause.** This corrects what an existing rule said about an existing tool, which is a defect in what exists, so it needed no lift. The owner's request to fix it would have lifted the pause for this work in any case (`PL-6Q9L`).

**Found on the way.** `PL-WX87` (claim takes the harness's startup tracking ref for the remote's copy of the branch, and skips its push) recurred on this branch. The ref was written at 21:51:40Z, six seconds after the session started, and `claim` printed "not pushed" for a branch `git ls-remote` did not list. `PL-7XGR` was filed here: this item's live claim read as spent from `#1019`'s squash merge until the branch merged `main`.
