---
id: PL-8XMV
title: A setting chooses whether returning to a mark forks or truncates, so the default is the learner's rather than the build's
priority: P3
effort: S
status: blocked
blocked-by: PL-ZW0J
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md, docs/ARCHITECTURE.md, tests/integration/test_controller.py
added: 2026-09-20
---

**Problem.** A setting chooses whether returning to a mark forks or truncates, so the default is the learner's rather than the build's

**Why it matters.** `PL-ZW0J` picks one of two behaviours for every learner.
Which one suits depends on what they are doing - trialling several settings
quickly wants the run truncated, comparing two managements wants both kept - and
that changes within a single sitting rather than between users.

**Asked for by the project owner, 2026-09-20**, in the same breath as the
truncate decision: "add a setting at some point so user can change default
behavior either way".

**Why it is a separate item rather than a line in `PL-ZW0J`.** The two
behaviours are one decision; which one a given learner gets by default is
another, and it only exists once both are built. Filed so the request is not
lost inside a brief that may well close having built only one of them.

**What it has to avoid.** A mode the learner cannot see is the hidden state
`.claude/rules/expert-review.md` asks to be designed out: returning to a mark
would silently either keep the old future or discard it, and the two are not
recoverable from each other. Whatever carries the setting, the act itself has to
say which one it is about to do at the moment it is taken - which is what Gas
Man's confirm already does for the destructive one.

**Done when.** A learner can choose whether returning to a mark forks or
truncates; the choice persists across sessions; and the act states which of the
two it is taking at the point of taking it, so the setting cannot be read off
the result after the fact.
