---
id: PL-WBW3
title: The effort trial records a session's arm only from its start-of-session line, so a session the owner moves to another level mid-session (session_01GnrHQs9QJ7TXfJF2dw2JpV, high to xhigh on 2026-11-03, PL-TN0G) is counted in the arm it left: give the model review a record of the move, or have it exclude such sessions
status: untriaged
feature: effort-trial
added: 2026-11-03
---

**Problem.** The effort trial records a session's arm only from its start-of-session line, so a session the owner moves to another level mid-session (session_01GnrHQs9QJ7TXfJF2dw2JpV, high to xhigh on 2026-11-03, PL-TN0G) is counted in the arm it left: give the model review a record of the move, or have it exclude such sessions

**Found 2026-11-03, after compaction.** The session-start hook also runs on compaction, and it wrote the `high` cap back over the owner's `xhigh` change. The owner's move therefore lasts only until the next compaction, unless the session writes it again. A fix should leave a cap the owner set mid-session in place, or record the move so the hook can respect it.
