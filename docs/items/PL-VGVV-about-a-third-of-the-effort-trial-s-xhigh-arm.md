---
id: PL-VGVV
title: About a third of the effort trial's xhigh-arm sessions run at high, because a level picked when a cloud session is opened wins over the level the session-start hook writes: 18 of 53 by 2026-11-24, all opened at high from the desktop or iOS app, which weakens the comparison toward no difference
status: untriaged
feature: effort-trial
added: 2026-11-24
filed-pr: 2318
---

**Problem.** About a third of the effort trial's xhigh-arm sessions run at high, because a level picked when a cloud session is opened wins over the level the session-start hook writes: 18 of 53 by 2026-11-24, all opened at high from the desktop or iOS app, which weakens the comparison toward no difference

**Why it matters.** The trial compares the arm each session drew. A session
drawn `xhigh` that runs at `high` makes the two arms more alike, so a real
difference shows up smaller than it is. The Claude Code documentation puts "An
explicit choice" ahead of "Your settings" in its order for the effort level,
and the hook writes the arm as a setting (*Model configuration*, section
"Adjust effort level", https://code.claude.com/docs/en/model-config, read
2026-11-24 by a subagent of `PL-JT1C`). The page does not describe the effort
control of the desktop, web or mobile app. On 2026-11-24 the ledger showed 18
of the 53 sessions drawn `xhigh` opened at `high`: 10 on Fable 5.2 from the
desktop app, 7 on Opus 5.5 from the desktop app and 1 on Fable 5.2 from iOS.

**What fixes it.** The owner opens every cloud session at `xhigh` or above, so
the hook's cap decides the level. The review already reports the level each
session ran at as a secondary result.
