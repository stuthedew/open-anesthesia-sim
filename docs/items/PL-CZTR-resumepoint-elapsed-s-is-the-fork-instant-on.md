---
id: PL-CZTR
title: ResumePoint.elapsed_s is the fork instant on the case's axis and should be named fork_instant_s, now that the definition's own instants are instant_s
priority: P3
effort: S
status: ready
classes: refactor
feature: core-domain-language
touches: src/anesthesia_sim/app/controller.py, tests/integration/test_controller.py
added: 2026-09-14
verify: uv run pytest tests/integration/test_controller.py && ! grep -q 'resume_point.elapsed_s' src/anesthesia_sim/app/controller.py
---


**Problem.** ResumePoint.elapsed_s is the fork instant on the case's axis and should be named fork_instant_s, now that the definition's own instants are instant_s

**Verified 2026-09-14.** `ResumePoint` is at `app/controller.py:502` and its
`elapsed_s` is read at `:962` inside the settings-mismatch message. Since
`PL-ZMRT` the definition's own instants are `instant_s`, and a branch's
`ResumePoint` holds the instant on the *case's* axis - not an elapsed duration -
so the field name says the wrong kind of quantity.

**Why it matters.** `.claude/rules/core-domain.md` asks that the code read like
the domain, and the specific hazard here is the one `PL-59WB` names one module
over: a name that says "duration" receiving an instant is how a value gets used
in arithmetic that only makes sense for the other kind. The two are the same
defect and worth renaming in one pass. It also reaches a user-visible string -
`:962` interpolates it into the refusal `PL-NC62` is about - so the reader is
told "a branch at N s" where N is a case instant.

**Done when.** `ResumePoint`'s field is `fork_instant_s`, every reader is
updated, and no `resume_point.elapsed_s` remains in
`src/anesthesia_sim/app/controller.py`.
