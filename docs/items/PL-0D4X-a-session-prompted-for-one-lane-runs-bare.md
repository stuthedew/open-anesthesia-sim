---
id: PL-0D4X
title: A session prompted for one lane runs bare `docket next` and takes the other lane's item
priority: P2
effort: S
status: done
classes: defect
feature: parallel-sessions
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, CLAUDE.md, .claude/skills/docket/SKILL.md
added: 2026-09-04
closed: 2026-09-04
verify: uv run pytest subprojects/docket/tests/test_cli.py && grep -q 'def test_next_without_a_lane_names_the_lane_of_its_answer' subprojects/docket/tests/test_cli.py
---
**Problem.** A session opened with the prompt "Next workflow item" ran bare
`bin/docket next`, was handed `PL-DR1Z` - product-lane work - and started it.
Observed 2026-09-04; the project owner caught it, not the tooling.

The right answer was already on screen. The session-start digest had printed
`By lane, for a second session: product PL-DR1Z, workflow PL-CP74`, and the
session read past it.

**Why it matters.** The owner runs two sessions at once precisely so one can
take the simulator while the other takes the apparatus, and that arrangement is
what `PL-5KR2`, `PL-S1P1`, `PL-PRHN` and `PL-SK88` were all paid for. A lane
the session ignores costs the whole arrangement: both sessions rank onto the
same half of the queue, which is the collision the split exists to prevent,
arriving through the one command that was never taught to mention it. It is
also silent - the answer is correctly ranked and looks right, so nothing about
the output invites a second look.

**Why the guards did not fire.** Three causes, and they compound:

- **The tool is silent about lanes in exactly the call that needs it.**
  `_say_lane_holdouts` returns immediately when `lane is None`, so asking for
  a lane tells you what the lane hid, while asking for no lane does not tell
  you a lane exists. `next` is the first command a session runs and the one
  that hands over the answer, and it is the only place in the flow where
  nothing names the split.
- **`CLAUDE.md` names the bare command in its resident text** ("Pick up cold
  from the session-start digest, `bin/docket next`, and the one item being
  worked"), which is what a session reads before it would think to load the
  `docket` skill.
- **The skill's lane rule triggers on the wrong fact.** It fires on being
  *told this session is the workflow one*, under a heading saying to ask for a
  lane only when a second session is genuinely running - so a prompt that
  names a lane outright does not obviously trip it, and a session has a reason
  to go looking for a second session first.

**Distinct from `PL-CP74`,** which is about work that carries no id at all.
Here the item existed, was correctly ranked, and was ranked in the other lane.

**Where.** `subprojects/docket/src/docket/cli.py` (`cmd_next`), `CLAUDE.md`,
`.claude/skills/docket/SKILL.md`.

**Done when.** Bare `docket next` names which lane its answer sits in and what
the other lane's own pick is, so a session prompted for a lane sees the
mismatch in the output it is already reading; the resident line names the lane
form of the command; and the skill's rule fires on the prompt naming a lane
rather than on a second session being known to exist.
