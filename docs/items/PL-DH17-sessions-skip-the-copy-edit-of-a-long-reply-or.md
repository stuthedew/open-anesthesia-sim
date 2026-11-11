---
id: PL-DH17
title: Sessions skip the copy edit of a long reply or a decision request: the PL-BSYT and PL-W6JM sessions sent four replies over 150 words with none, one of them a decision request, and nothing checks a reply
priority: P1
effort: M
status: dropped
classes: defect
feature: copy-editor
touches: .claude/rules/instruction-writing.md, .claude/hooks, .claude/settings.json
deferred-from: v0.7.0 - a new problem, not present at the freeze: the reply copy edit arrived in efc1dc3f (PL-22T5); deferred with PL-J1ZM, which waits on it
added: 2026-11-04
closed: 2026-11-10
reason: moot: on 2026-11-10 the project owner took replies out of the copy editor's scope (PL-JYWB, #2079; .claude/rules/plain-writing.md now says the copy editor does not edit replies), so no reply copy edit is left for a session to skip. The payoff named this outcome: the owner has decided whether the step earns its cost (project owner, 2026-11-10, ratified, over keeping the item open)
payoff: a long reply or a decision request reaches the owner copy edited, or the owner has decided on the evidence whether the step earns its cost
not-delegable: whether a hook can see a reply before the owner does is found while the item is worked, and the other outcome is a decision for the owner, so no command can prove it beforehand
---

**Problem.** Sessions skip the copy edit of a long reply or a decision request: the PL-BSYT and PL-W6JM sessions sent four replies over 150 words with none, one of them a decision request, and nothing checks a reply.

**Evidence** (`PL-J1ZM` § "Measured, 2026-11-04"). Rule 16 of `.claude/rules/instruction-writing.md` merged in #2017, before every session measured. The `PL-BSYT` session sent three replies over 150 words, one a decision request, and the `PL-W6JM` session sent one of 192 words. None went through the copy editor. The `PL-J37P` and `PL-9331` threads ran it on one reply and two, and each still sent a long reply or a decision request without it.

**What a fix needs.** The design round recorded that no check enforces replies: hooks do not run in project threads (`PL-D1FD`), and a stop hook cannot rewrite a reply already sent. So a fix either finds a moment before sending that a check can reach, or puts back to the owner whether the rule earns its cost, with this adherence as the evidence.

**Checked 2026-11-09:** Rule 16 of `.claude/rules/instruction-writing.md` still asks for the copy edit, and nothing in `.claude/hooks/` or `.claude/settings.json` names `copy_edit` or `new_prose`, so no check reaches a reply.

**A premise has moved.** "What a fix needs" says that hooks do not run in Projects threads. `PL-CR81` records a thread on 2026-11-03 in which the repository's hooks ran, copied into the user settings by `.claude/hooks/thread_hooks.py` through the environment's setup script (`PL-X6VN`). So a hook may now reach a thread as well as a session. A stop hook still cannot rewrite a reply already sent, but it might refuse to end a turn whose long reply has no copy-edit record. Check that route before putting the rule's cost back to the owner.

**Why it matters.** The owner reads replies to decide. In the measurement, four long replies, one of them a decision request, skipped the copy edit, so the step that `PL-J1ZM`'s design chose for replies is not taking place.

**Done when.** Either a check reaches a long reply or a decision request before the owner reads it, and refuses one the copy editor did not see, or the owner has decided whether rule 16 stays, with this adherence as the evidence. In the second case the item moves to `needs-decision` with a marked recommendation.

**Generator check.** Part of the fix for the live head `PL-J1ZM`, which is blocked on it; one of the three failures its 2026-11-04 measurement found, and not a member of its `root-cause-of`. The pause on new workflow mechanisms does not hold it, because it fixes that generator.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Not present. Rule 16 of `.claude/rules/instruction-writing.md`, the copy edit of long replies, did not exist at 817a4d88. It arrived in efc1dc3f (`PL-22T5`, 2026-11-04), so this is a new problem. It is deferred with `PL-J1ZM`, which waits on it.
