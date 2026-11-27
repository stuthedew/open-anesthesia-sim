---
id: PL-VT87
title: Check each refusal and halt notice that a user reads for what to do next, now that a refusal must say it (NUREG-0700 guideline 2.7.3-1)
priority: P3
effort: S
status: ready
classes: ux
feature: interface-design-review
touches: src/anesthesia_sim/core/supported_ranges.py
added: 2026-11-27
filed-pr: 2330
payoff: a user who meets a refused setting or a halted run is told how to go on, not only what went wrong
---

**Problem.** Check each refusal and halt notice that a user reads for what to do next, now that a refusal must say it (NUREG-0700 guideline 2.7.3-1)

**Where this comes from.** `PL-HWZK` added to
`.claude/rules/sources-and-docstrings.md` that a refusal a user reads also says
what to do next, such as the range a setting must fall in or the action that
clears the state. The existing messages were written to the earlier rule, which
asked for the condition, the value that failed it and where to read why.

**What to do.** List every string under `src/anesthesia_sim/app/` and
`src/anesthesia_sim/core/supported_ranges.py` that a user reads when a setting
is refused or a run halts. Mark each one that already says what to do next,
and reword each one that does not.

**Why it matters.** A refused setting or a halted run that names only the
problem leaves the user to work out the remedy, which NUREG-0700 Rev. 3
guideline 2.7.3-1 asks the message to give.

**Done when.** Every such message names the next step, and this item lists the
ones that were changed.

**Generator check.** One-off: the rule that these messages now miss was
written on 2026-11-27.
