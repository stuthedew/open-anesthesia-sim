---
id: PL-BT2J
title: resumed_at, BranchedCase.fork_at, _resume_point_at and _setting_at take a case instant under the name elapsed_s, while the Keyframe it is matched against names the same instant instant_s
status: untriaged
feature: core-domain-language
added: 2026-09-22
---

**Problem.** resumed_at, BranchedCase.fork_at, _resume_point_at and _setting_at take a case instant under the name elapsed_s, while the Keyframe it is matched against names the same instant instant_s

**Found 2026-09-22, closing `PL-CZTR`.** That item deleted `ResumePoint.elapsed_s`
so a branch's fork instant is read only as `fork.instant_s`. The parameters one
call up still carry the case instant under the duration's name:
`SimulationController.resumed_at(elapsed_s)` (`app/controller.py:777`, documented
as "The case instant to open at"), `_resume_point_at(elapsed_s)` (`:1099`), which
matches it with `segment.opening.instant_s == elapsed_s` (`:1118`),
`_setting_at(control, elapsed_s, current)` (`:1232`), which `_branch_from` now
passes `fork_at_s`, and `BranchedCase.fork_at(elapsed_s)` (`:1846`, "The case
instant to branch at").

**Whether it is worth doing is the open question, and a reason it may not be.**
`snapshot().elapsed_s` is the case clock, and on this project's one case axis
the clock's reading and the instant it stands at are the same number, so a
caller passing `snapshot().elapsed_s` to `resumed_at` reads naturally. What
argues for `instant_s` is that these take a *point to open at* - a keyframe
instant - rather than a clock reading, and that `PL-ZMRT` and `PL-CZTR` moved
every other such point to that name. `resumed_at` and `fork_at` are public, so
the rename reaches every caller in `app/` and `tests/`.
