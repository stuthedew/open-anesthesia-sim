---
id: PL-CZTR
title: ResumePoint.elapsed_s is the fork instant on the case's axis and should be named fork_instant_s, now that the definition's own instants are instant_s
priority: P3
effort: S
status: ready
classes: refactor
feature: core-domain-language
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/chart_frame.py, tests/integration/test_controller.py, tests/unit/test_chart_frame.py
added: 2026-09-14
payoff: a branch's fork instant is read under one name, fork.instant_s, so no reader meets a duration's name on an instant and _open_at stops reading one value two ways
verify: ! grep -rqE '(opened_from|resume_point)\.elapsed_s' src/anesthesia_sim/app tests/integration/test_controller.py tests/unit/test_chart_frame.py && ! grep -q 'def elapsed_s' src/anesthesia_sim/app/controller.py
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

**Re-verified 2026-09-22, while closing `PL-59WB`; not started, for session
length.** The brief above predates `PL-B8MK`. `ResumePoint` now holds
`fork: Keyframe`, and `elapsed_s` is no longer a field but a property
returning `self.fork.instant_s`, so what is left is an alias. Its readers in `src/` are `controller.py`'s
`began_at_s`; `_branch_from`, for the settings replay and its "the settings
replayed for a branch at" refusal; the "this run is a branch opened at"
refusals in `set_agent` and in `BranchedCase`; the "this run is itself a
branch opened at" refusal in `_require_forkable`; and `chart_frame.py`'s
`_run_frame`, where it places `branch_point_s`. Tests read it in two
assertions in `tests/integration/test_controller.py` and one docstring in
`tests/unit/test_chart_frame.py`. A fork reads the one value under both names
on one path: `_branch_from` as `resume_point.elapsed_s`, then `_open_at` as
`resume_point.fork.instant_s` to advance the definition.

**Approach, decided 2026-09-22 (internal structure only): delete the alias
rather than rename it.** Every reader writes `fork.instant_s`, which already
reads as the domain says it: the fork's instant. A `fork_instant_s` property
beside `fork.instant_s` would keep two spellings of one value, which is the
state the fork path is in now. The displayed strings keep their text, since the
value is unchanged.

**Done when, as re-verified 2026-09-22.** `ResumePoint` has no `elapsed_s`,
every reader above reads `fork.instant_s`, and the suite passes unchanged apart
from those readers.
