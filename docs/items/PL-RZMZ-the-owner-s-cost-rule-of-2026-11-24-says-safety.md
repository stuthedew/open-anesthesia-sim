---
id: PL-RZMZ
title: The owner's cost rule of 2026-11-24 says safety-critical work always gets the strongest effort level and that the stronger level stays until high is shown within the margin, but every session outside the effort trial, safety work included, still opens at high under the owner's choice of 2026-10-19; which level each kind of work outside the trial runs at is the owner's to decide
status: untriaged
feature: effort-trial
touches: docket.toml, docs/maintainer.md, docs/model-review.md
added: 2026-11-24
filed-pr: 2319
---

**Problem.** The owner's cost rule of 2026-11-24 says safety-critical work always gets the strongest effort level and that the stronger level stays until high is shown within the margin, but every session outside the effort trial, safety work included, still opens at high under the owner's choice of 2026-10-19; which level each kind of work outside the trial runs at is the owner's to decide

**The conflict.** `docs/maintainer.md` § "Match model capability to the work"
now says: "Until then the stronger setting stays. For work under the
safety-critical standard the margin is zero, so that work always gets the
strongest setting" (project owner, 2026-11-24, ratified, `PL-1WTY`). The
`[models]` table's default effort is still `high` for every session (project
owner, 2026-10-19, over `max` and `xhigh`, `PL-6XZG`). Cloud sessions draw
`high` or `xhigh` at random. Projects threads open at `high` until `PL-C38D`
brings them into the trial. Nothing sets another level for safety-critical
work, which the model review never randomizes
(`.claude/skills/model-review/SKILL.md`, "Confounding by indication"). Of the
781 items closed from 2026-10-25 to 2026-11-24, 108 (13.8%) carry the `safety`
or `science` class, the classes `Item.model_guidance` already sends to the
strongest model.

**What the research found** (both pages read in full on 2026-11-24).

1. Anthropic's effort page
   (https://platform.claude.com/docs/en/build-with-claude/effort.md) calls
   `max` "Absolute maximum capability with no constraints on token spending".
   For Opus 5.5 it says to "Run an effort sweep on your own evals rather than
   carrying settings over". It says of Fable 5.2 that `max` "runs slower and
   costs more than at `xhigh`, often for only a small gain", and of Opus 4.7
   that `max` can lead to overthinking "on some structured-output or less
   intelligence-sensitive tasks". It says neither of Opus 5.5.
2. Anthropic's cost page
   (https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence.md)
   reports that on 463 problems of its SWE-bench Pro subset, Opus 5.5 solved
   95.5% at `high` for $0.30 per solved task and 96.5% at `xhigh` for $0.75.
   It publishes no Opus 5.5 figure at `max`.

**The options.**

1. Safety-critical work at `max`, and other work outside the trial at `high`.
2. Safety-critical work at `max`, and other work outside the trial at `xhigh`
   until `high` is shown within the margin.
3. Safety-critical work at `xhigh`, and other work outside the trial at
   `high`.
4. Everything outside the trial stays at `high`.

**Recommendation: option 1.** For safety-critical work the margin is zero, and
`max` is the level Anthropic describes as the model's maximum capability. No
measurement shows `xhigh` to be as correct there, so the rule selects `max`.
For other work, the choice of `high` on 2026-10-19 weighed the same published
gap of about one more task solved in 100 for about 2.5 times the cost per
solved task, and the trial is the measurement the rule asks for. Once threads
join the trial, half of them run at `xhigh` in any case. The cost of option 1
is longer and costlier sessions on about one item in seven.

**What the build does under options 1 to 3.** A session that starts a
safety-critical item moves to the chosen level before any work, as a session
on a generator's cause moves to `xhigh`
(`.claude/skills/docket/modes/triage.md`): a cloud session runs `python3
tools/effort_trial.py move --to max --reason "safety-critical work"`, and a
Projects thread sets its own level. A `[[models.rule]]` in `docket.toml`
matching the two classes gives the level, so `bin/docket next` prints it. The
trial's analysis leaves items with either class out of both arms. Triage sets
the class before any session works the item, so leaving them out does not
depend on the arm (`PL-C38D`, point 3). Under option 2, the table's default
becomes `xhigh` and the trial's draw still sets cloud sessions' levels.
Under options 1 and 4, `docs/maintainer.md` says beside "Until then the
stronger setting stays" that the level other work opens at outside the trial
is the owner's own judgement, which the trial is testing.
