---
id: PL-DH17
title: Sessions skip the copy edit of a long reply or a decision request: the PL-BSYT and PL-W6JM sessions sent four replies over 150 words with none, one of them a decision request, and nothing checks a reply
status: untriaged
feature: copy-editor
added: 2026-11-04
---

**Problem.** Sessions skip the copy edit of a long reply or a decision request: the PL-BSYT and PL-W6JM sessions sent four replies over 150 words with none, one of them a decision request, and nothing checks a reply.

**Evidence** (`PL-J1ZM` § "Measured, 2026-11-04"). Rule 16 of `.claude/rules/instruction-writing.md` merged in #2017, before every session measured. The `PL-BSYT` session sent three replies over 150 words, one a decision request, and the `PL-W6JM` session sent one of 192 words. None went through the copy editor. The `PL-J37P` and `PL-9331` threads ran it on one reply and two, and each still sent a long reply or a decision request without it.

**What a fix needs.** The design round recorded that no check enforces replies: hooks do not run in project threads (`PL-D1FD`), and a stop hook cannot rewrite a reply already sent. So a fix either finds a moment before sending that a check can reach, or puts back to the owner whether the rule earns its cost, with this adherence as the evidence.
