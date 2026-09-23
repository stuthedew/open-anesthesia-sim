---
id: PL-BT2J
title: resumed_at, BranchedCase.fork_at, _resume_point_at and _setting_at take a case instant under the name elapsed_s, while the Keyframe it is matched against names the same instant instant_s
priority: P3
effort: S
status: needs-decision
classes: refactor
feature: core-domain-language
touches: src/anesthesia_sim/app/controller.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the first 2026-09-23 triage pass
added: 2026-09-22
payoff: the case instant a branch opens at is read under one name from the public door to the keyframe, so no reader meets a clock reading's name on a point in case time
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

**Measured 2026-09-23: the rename reaches no caller.** A search of `src/` and `tests/` for any of the four names called with
`elapsed_s=` finds nothing. All 49 calls to `resumed_at` and `fork_at`
pass the instant positionally, so renaming the parameter changes four
signatures and their docstrings and no call site. The cost the paragraph above
weighs against it is not there.

**Why it matters.** `PL-ZMRT` renamed the `elapsed_s` instants in
`core/run_definition.py` to `instant_s` because "the right number under a label
that lies is a safety failure", and it named the spelling collision with
`SimulationState.elapsed_s` as what made a wrong subtraction writable. These
four parameters are the last place a keyframe instant enters under the clock's
name, one call above the `Keyframe.instant_s` it is compared with.

**Decision needed.** Rename the four parameters to `instant_s`, or keep
`elapsed_s` because callers pass a clock reading. **Recommended: rename.** The
value is matched against `segment.opening.instant_s` and stored as
`fork.instant_s`, `PL-ZMRT` and `PL-CZTR` already settled the convention, and
the measurement above removes the cost. A session can take this. It is one
internal name with no behaviour behind it, not a question for the project owner.

**Done when.** `resumed_at`, `BranchedCase.fork_at`, `_resume_point_at` and
`_setting_at` take `instant_s`, their docstrings say "instant", and nothing in
`app/controller.py` compares an `elapsed_s` parameter with a keyframe's
`instant_s`.
