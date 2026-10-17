---
id: PL-PLT9
title: tools/context_reading.py printed a negative spend (baseline 381,829, context 254,293, spend -127,536) in a Projects thread after the harness moved the session's working directory to /home/user and back, because the first request of the transcript it read is not the session's floor, so the budget check had no usable reading
priority: P3
effort: S
status: ready
classes: defect
touches: tools/context_reading.py, tests/unit/test_context_reading.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-17
payoff: the budget check either reads a session's real spend or says it cannot, so no session decides whether to start an item on a negative number
verify: grep -q 'def test_a_negative_spend_is_not_printed' tests/unit/test_context_reading.py
---

**Problem.** tools/context_reading.py printed a negative spend (baseline 381,829, context 254,293, spend -127,536) in a Projects thread after the harness moved the session's working directory to /home/user and back, because the first request of the transcript it read is not the session's floor, so the budget check had no usable reading

**Evidence.** The thread that ran link 1 of `tests-detect-wrong-values`
(session `session_01QbA6MdJsBsnXZWFXnQ6CHV`, the Projects thread "Tests
detect wrong values") ran `python3 tools/context_reading.py` at
2026-10-17 20:05Z. It printed `baseline 381,829`, `context 254,293` and
`spend -127,536`. Earlier in that session the harness had moved the
session's working directory to `/home/user` and back. A spend below zero
cannot be true, so the reading had no use for the budget check in
`CLAUDE.md` § "Session and tool-use efficiency". The thread recorded this in the
project's shared notes for the v0.6.0 test features (a file outside the
repository), under "Handoff for link 2", and the link 2 thread filed it.

**Likely cause (inferred, not verified).** The script takes the first
request of the transcript it reads as the session's floor. A move of the
working directory probably starts a new transcript file under another
project directory, or the script found a transcript whose first request
came after a compaction. Either way the first request it read was larger
than the context at the end, so the subtraction went negative.

**What a fix would show.** The script either finds the session's real first
request, or says that it could not and prints no spend. Per
`.claude/rules/apparatus-standard.md`, a reading it cannot stand behind
should say what it could not read rather than print a negative number.

**Suggested triage.** Workflow lane, P3. Projects threads do not follow the
repository's budget rule (the project's own instructions, 2026-10-04), so
the cost falls on ordinary sessions that move their working directory.

**Why it matters.** `CLAUDE.md` asks a session to check its spend before it
starts an item. A negative reading gives no answer, and a wrong positive one
could tell a session it has room it does not have.

**Done when.** When the transcript's first request is not the session's floor,
or the script cannot tell, it says what it could not read and prints no spend.
A test reproduces a transcript whose first request is larger than its last and
pins that no negative spend is printed.

**Generator check.** One-off. The fact is "which request is the session's first",
and only `tools/context_reading.py` reads it. `PL-W80S` and `PL-BZVY` were about
`get_session`'s reading, which is a different fact.
