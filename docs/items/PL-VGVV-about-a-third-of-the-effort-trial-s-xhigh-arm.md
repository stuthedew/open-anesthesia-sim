---
id: PL-VGVV
title: About a third of the effort trial's xhigh-arm sessions run at high, because a level picked when a cloud session is opened wins over the level the session-start hook writes: 18 of 53 by 2026-11-24, all opened at high from the desktop or iOS app, which weakens the comparison toward no difference
priority: P2
effort: S
status: blocked
classes: defect
feature: effort-trial
touches: docs/maintainer.md
blocked-by: 2026-12-11
deferred-from: v0.7.0 - workflow tooling outside the schematic release, and it changes no displayed value (triage 2026-11-27)
added: 2026-11-24
filed-pr: 2318
payoff: the effort trial compares high with xhigh rather than with a mix of the two, so its answer is not biased toward no difference
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

**Reproduced 2026-11-27.** `docs/maintainer.md` § "Match effort to the standard the work is held to" already asks the owner to keep the app's effort picker at `xhigh` for the length of the trial, and says why: the hook's cap only lowers a level. The 18 sessions were opened at `high` regardless, so the instruction did not reach the moment a session is opened. The ledger count was not taken again; the 2026-11-24 figure above is the latest.

**Done when.** The model review counts the sessions drawn `xhigh` that were opened from 2026-11-27 onward and ran below `xhigh`, and records the count in this brief. Where the count is above zero, `docs/maintainer.md` says the measured cost in the sentence that asks for the picker at `xhigh`.

**Generator check.** Touches the apparatus, so asked. The fact is which setting decides the effort level a session runs at. `PL-8MZ9` (the setup script never ran the draw) and `PL-6LVZ` (generator work forced to `xhigh`) were different mechanisms, both closed, and the review now records the level each session ran at beside its arm. So this is a one-off: an owner action the documentation already asks for.
