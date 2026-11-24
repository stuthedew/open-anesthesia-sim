---
id: PL-C38D
title: Bring Projects threads into the effort trial: each new thread draws high or xhigh at its start and its arm is recorded where the model review can read it, because threads do five in six of the implementation items and cloud sessions alone cannot reach an answer
status: untriaged
feature: effort-trial
added: 2026-11-24
filed-pr: 2318
---

**Problem.** Bring Projects threads into the effort trial: each new thread draws high or xhigh at its start and its arm is recorded where the model review can read it, because threads do five in six of the implementation items and cloud sessions alone cannot reach an answer

**Decided** (project owner, 2026-11-24, ratified, chosen on a card over keeping
the trial to cloud sessions and over stopping it): bring Projects threads into
the effort trial. The model review of 2026-11-24 (`PL-JT1C`) found that
threads merged 498 implementation items in 31 days against the cloud
sessions' 100, and that with threads in the trial a doubling in failed fixes
becomes detectable in about 2 to 6 months. This is new workflow machinery,
which the pause in `CLAUDE.md` § "What this project is" allows because the
owner asked for it.

**What the build has to settle.**

1. **How a thread draws and applies its arm.** A thread never reads
   `.claude/settings.local.json`, where the start hook writes the cap
   (`PL-CR81`). A thread can set its own level with the Projects tool
   `set_effort_level`, which this thread used on 2026-11-24. So the draw can
   be the hook's existing hash of the session id, printed for a thread as an
   instruction to set that level on its first turn. Check that the tool
   accepts both `high` and `xhigh`, and what happens when the owner or the
   coordinator has already set a level: that is a moved session, counted in
   the arm it drew (`PL-JT1C`, decision 1).
2. **Where the arm is recorded.** The review now reads arms from the
   harness's session events, which took four background readers about 25
   minutes for 139 sessions (`PL-JYC2`). With about five times as many
   sessions, recording the arm at the draw, for example as a ledger column,
   is the route to take. Build `PL-JYC2` with this item or before it.
3. **Safety-critical work.** The model review skill says never to randomize
   safety-critical work, and the owner's new cost rule gives that work a
   margin of zero (`PL-1WTY`). The hook draws an arm per session whatever the
   session works on. Decide whether a session that takes a safety-classed item
   leaves the trial at its strongest level, and how the review counts it.
4. **Analysis.** Threads are a different way of working, so origin (thread or
   cloud session) becomes a stratum beside split period and model, as the
   skill's effort monitoring step 5 already asks for the historical data.
   The trial's record in `docs/model-review.md` gets an amendment dated with
   the change, and thread items count only from that date, as Evans' staged
   design does (`PL-JT1C`, decision 7).

**Done when.** New threads draw an arm and run at it, the arm is recorded
where the review reads it, the trial's record carries the amendment, and the
model review skill's step 6 says how threads are counted.

