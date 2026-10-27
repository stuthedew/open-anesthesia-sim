---
id: PL-876V
title: Until Projects threads load .claude/ again (PL-CR81), a thread does not know it runs with no guard hooks, no session-start digest and no repository skills: have the coordinator open each thread's first message with the hook probe and the skill paths, so the thread says it is unguarded and reads .claude/skills/ by path
priority: P2
effort: S
status: ready
classes: infra
feature: projects-trial
touches: .claude/skills/docket/modes/coordinator.md
added: 2026-10-25
payoff: a Projects thread knows when it runs without guard hooks and skills, and reads the skills by path
verify: grep -qF 'pytest --version' .claude/skills/docket/modes/coordinator.md
---

**Problem.** Until Projects threads load .claude/ again (PL-CR81), a thread does not know it runs with no guard hooks, no session-start digest and no repository skills: have the coordinator open each thread's first message with the hook probe and the skill paths, so the thread says it is unguarded and reads .claude/skills/ by path

**Reproduced 2026-10-26.** `.claude/skills/docket/modes/coordinator.md` §
"What every brief tells its thread" lists four things every thread brief
carries. None of them is the hook probe `uv run pytest --version | head -1`
from `PL-CR81`, and none names the skill paths under `.claude/skills/`.

**Why it matters.** `PL-CR81` found that a Projects thread loads nothing from
`.claude/`. A thread therefore runs with no guard hook and no skill, and
nothing tells it so. It may push a change that a guard would have refused, or
work a queue procedure from memory.

**Done when.** The coordinator mode's list of what every brief tells its thread
includes the hook probe. It also tells a thread to say it is unguarded when the
probe prints a version, and to read `.claude/skills/<name>/SKILL.md` by path.
The list says to drop these lines once `PL-CR81` is fixed.

**Generator check.** One external behaviour that nothing in the repository
models, the same one `PL-CR81` records. It is a one-off.
