---
id: PL-PLT9
title: tools/context_reading.py printed a negative spend (baseline 381,829, context 254,293, spend -127,536) in a Projects thread after the harness moved the session's working directory to /home/user and back, because the first request of the transcript it read is not the session's floor, so the budget check had no usable reading
status: untriaged
touches: tools/context_reading.py, tests/unit/test_context_reading.py
added: 2026-10-17
---

**Problem.** tools/context_reading.py printed a negative spend (baseline 381,829, context 254,293, spend -127,536) in a Projects thread after the harness moved the session's working directory to /home/user and back, because the first request of the transcript it read is not the session's floor, so the budget check had no usable reading

**Evidence.** The thread that ran link 1 of `tests-detect-wrong-values`
(session `session_01QbA6MdJsBsnXZWFXnQ6CHV`, the Projects thread "Tests
detect wrong values") ran `python3 tools/context_reading.py` at
2026-10-17 20:05Z. It printed `baseline 381,829`, `context 254,293` and
`spend -127,536`. Earlier in that session the harness had moved the
session's working directory to `/home/user` and back. A spend below zero
cannot be true, so the reading had no use for the budget check in
`CLAUDE.md` § "Session and tool-use efficiency". The thread recorded this in
`/mnt/project-files/v0.6.0/test-features.md` § "Handoff for link 2", and
the link 2 thread filed it.

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
