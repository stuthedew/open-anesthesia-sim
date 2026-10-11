---
id: PL-XJ22
title: A triage pass checks the in-flight marks when it starts and not when it pushes, so an item claimed while the pass runs gets a second answer: #1124 triaged PL-QMN0 seven minutes after another branch claimed it, and merged first (2026-09-26)
status: untriaged
feature: claim-record
touches: .claude/skills/docket/modes/triage.md
added: 2026-10-11
---

**Problem.** A triage pass checks the in-flight marks when it starts and not when it pushes, so an item claimed while the pass runs gets a second answer: #1124 triaged PL-QMN0 seven minutes after another branch claimed it, and merged first (2026-09-26)

**Found by `PL-99YZ`'s count, 2026-10-11.** It is the same-id half of what
that item measured: every guard keys on the id here, and the id matched. What
missed is the window between the pass reading the marks and pushing its answer.

**The two instances since claims were pushed at start (#987, 2026-09-24).**
About nine multi-capture triage passes have merged since then, read from
`main`'s subjects, and two met a claim made while they ran.

- 2026-09-26. `claude/project-thread-qt3onr` claimed `PL-QMN0` at 19:45:26 UTC
  (`47b3f928`), triaged it to P2 ready at 19:48:57 and committed the fix at
  19:59:48 (`59ea9d1c`). `PL-61FT`'s pass committed its ten triage answers at
  19:52:08 (`8441ef70`), `PL-QMN0` among them as P3, blocked on the generator
  head the same pass recorded, and #1124 merged at 19:59:08. The fix opened as
  #1127 at 20:04 and closed unmerged at 20:09; #1128 parked it on its branch and
  #1138 dropped `PL-QMN0` into a `KNOWN_GAPS` row. The pass did read the marks -
  its body names the branches it left four items to - so it read them before the
  claim reached `origin` (inferred: when the claim was pushed is not recorded).
- 2026-10-01. `claude/read-facts-through-docket-0yo78k` claimed `PL-DHGC` and
  `PL-W560` at 19:13:57 (`0cb10e58`). #1278's pass committed answers for both at
  19:22:11 (`f63d0da5`) and restored `main`'s copies two minutes later
  (`a938142c`): "pushed after this pass read the queue". Its session re-read the
  marks before pushing on its own; nothing in triage mode asks for that.

**What the skill says now.** `.claude/skills/docket/modes/triage.md` has the pass
skip an item marked `IN FLIGHT` or `Its file is already edited on <branch>`, and
says the mark "is bounded by what has been pushed". It says nothing about
reading the marks again once the pass has written its answers, which is when a
claim made during the pass first becomes readable. The first instance cost a
finished fix that had passed `verify --self`; whether it would have merged
otherwise is unknowable, since #1128's bound might have dropped the item anyway.

**Done when.** A triage pass cannot push an answer for an item another branch
claimed or edited after the pass read the marks without being told so at that
moment, or the rate above is recorded as not worth the line it would take.
