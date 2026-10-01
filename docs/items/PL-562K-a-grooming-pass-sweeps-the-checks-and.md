---
id: PL-562K
title: A grooming pass sweeps the checks and advisories that fired for obvious fluff, on the retirement clause's decision test, and files what it would retire (project owner, 2026-10-01)
priority: P3
effort: S
status: done
classes: docs
touches: .claude/skills/docket/modes/triage.md
added: 2026-10-01
closed: 2026-10-01
pr: 1270
payoff: a check that fires every run and changes nothing is asked the retirement question on a cadence, instead of waiting for a session to happen to work beside it
verify: grep -qF 'sweep what fired for obvious fluff' .claude/skills/docket/modes/triage.md
---

**Problem.** A grooming pass sweeps the checks and advisories that fired for obvious fluff, on the retirement clause's decision test, and files what it would retire (project owner, 2026-10-01)

**Why it matters.** The retirement clause ratified today (`PL-1XZD`) says how a check is judged once somebody has noticed it, and `PL-ZBJ0` recorded that nothing notices: no counter and no sweep, so a check firing every run unread stays until a session working beside it happens to count it (`PL-G6J5`, `PL-Z909`). The owner asked for an occasional, non-aggressive sweep. Routed as a step of the grooming pass (`CLAUDE.md`'s second disposition, a skill, over a check and over resident prose): it fires when a pass is already reading the gate's output, costs no resident context, and adds no mechanism - which matters while `PL-KGYT` holds the pause. A dated advisory would be a new check under that pause, and `PL-ZBJ0`'s counter is the aggressive version and stays dropped.

**Done when.** `.claude/skills/docket/modes/triage.md` carries the step under the grooming pass: bounded to what one `make check` run and `bin/docket check`'s advisories printed, the retirement clause's decision test asked of each line that fired without failing anything, and each outcome (route it, retire it) filed as an item with the count `.claude/rules/expert-review.md` asks for.

**Generator check.** Work the owner asked for, 2026-10-01; its `touches` is under `workflow_paths`. The request lifts the pause for it (`PL-6Q9L`), and the session says so.
