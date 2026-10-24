---
id: PL-SN2Z
title: Test whether the docket skill starts on the requests it should and stays out of the ones it should not, running each test prompt in a fresh session with the skill on and again with it off
priority: P2
effort: M
status: done
classes: session-cost
feature: skill-routing
touches: tools/skill_start_eval.py, tools/skill_start_prompts.json, tests/unit/test_skill_start_eval.py, docket.toml, docs/apparatus.md, docs/items/PL-S2NL-move-claude-md-s-pull-request-procedure-opening.md, docs/items/PL-Z90G-move-claude-md-s-context-budget-reset-procedure.md
added: 2026-10-24
closed: 2026-10-24
pr: 1713
payoff: the owner learns from a measurement, not a guess, whether a procedure can leave the always-loaded instructions for a skill and still be followed
verify: grep -q 'def test_counts_a_docket_skill_call_as_a_start' tests/unit/test_skill_start_eval.py && grep -qE '^[*][*]Result, 20' docs/items/PL-SN2Z-*.md
---

**Problem.** Test whether the docket skill starts on the requests it should and stays out of the ones it should not, running each test prompt in a fresh session with the skill on and again with it off

**Why it matters.** About 91,000 characters of instructions load in every session: `CLAUDE.md` plus the three rules with no `paths:`. Anthropic's skills page says a section of `CLAUDE.md` that "has grown into a procedure rather than a fact" belongs in a skill, whose body loads only when it is used. This repository keeps procedures always loaded because a skill may not start when it is needed. `PL-WWDT` recorded the same failure for a path-scoped rule that loaded too late. Nothing measures whether our skills start. Until something does, moving a procedure out of `CLAUDE.md` risks a rule that silently stops applying. `PL-S2NL` and `PL-Z90G` wait on this answer.

**Evidence.**

- The Claude Code skills page, § "Evaluate and iterate on a skill" (https://code.claude.com/docs/en/skills, read 2026-10-24), says: "Seeing a skill trigger tells you Claude found it, not that it did what you intended." For a project skill, it gives the baseline as a second run with the skill set to `"off"` in `skillOverrides`. The `skill-creator` plugin automates this loop with an `evals/evals.json` file, and `claude plugin eval` does it for plugins. Whether `claude plugin eval` accepts `.claude/skills/` directly was not confirmed.
- testdouble/han is a worked example (https://github.com/testdouble/han, `evals/code-review/tests.json`, read 2026-10-24). It has prompts that should start a skill, including one that never says "review". It has prompts that should not, such as "a movie review". A second model grades the output against a written rubric.
- One developer reported that a skill started on its own 55% of the time on Sonnet 4.5 with no hook, and on all 22 test prompts with a hook that forced the check (https://scottspence.com/posts/measuring-claude-code-skill-activation-with-sandboxed-evals). That host refused a CONNECT from the session's container, so these figures come from a search summary and were not read at the source.

**Decision** (project owner, 2026-10-24, ratified, over `PL-LN69`'s refusal of evals on 2026-09-21). `PL-LN69` weighed evals only as a test for retiring rules. This item tests a different thing: whether a skill starts at the moment its procedure is needed. That decides whether a procedure can leave the always-loaded set. The session that recommended it had compared this repository's setup with testdouble/han.

**Scope.** Start with the `docket` skill only. Write a small set of prompts in two groups. The first group should start the skill, including requests that never say "queue" or "docket". The second group should not start it. Run each prompt in a fresh session with the skill on, and again with it off. Record how often the skill starts and on which prompts it does not. Every run is a real model call on the owner's plan, so keep the set small and do not add it to CI in this item.

**Done when.** The prompt set is committed with the method to rerun it. One run's start rate for each group is recorded in this item. The item says whether that rate is good enough to move a procedure into a skill while leaving only a one-sentence trigger always loaded, or whether a hook is needed as well. `PL-S2NL` and `PL-Z90G` read that answer.

**Generator check.** None. The owner asked for this work after the comparison with testdouble/han, and no fact was misread to produce it.

**Result, 2026-10-24.** One run of all 13 prompts, 21 sessions in all. Each session ran Opus 5.5 at the project's `high` effort, in `dontAsk` mode with at most 5 model requests, in a scratch clone of `main` at 6228be8f. The command is the one in `tools/skill_start_eval.py`'s docstring.

| Prompts | Skill | Sessions that called the `docket` skill |
| --- | --- | --- |
| 8 that should start it | on | 8 of 8, each as its first tool call |
| 5 that should not | on | 0 of 5 |
| 8 that should start it | off | 1 of 8, though the skill was hidden |

- Every session that started the skill did so with its first tool call, before any call was refused. So `dontAsk` mode cannot have shaped a start.
- Eight of 8 gives an exact 95% interval of 63% to 100% for the start rate, and 0 of 5 gives 0% to 52% for starts that should not happen (Clopper CJ, Pearson ES, *Biometrika* 1934;26(4):404-413, doi:10.1093/biomet/26.4.404). A set this small shows that misses are uncommon. It cannot show a rate close to 100%.
- With the skill off, 7 of 8 sessions still began the queue workflow. They ran `bin/docket` commands, and 6 of the 8 read the skill's mode files by their paths, which the resident instructions and the session-start digest name. One session, `free-hour`, called the hidden skill anyway. A rerun of `free-hour` saved the raw output. It showed that the off setting removes `docket` from the skill list in the session's `init` event, and that time the session did not call it.
- Three of the 5 sessions that should not start the skill ran `bin/docket branch` before replying, as rule 14 of `.claude/rules/instruction-writing.md` requires. The runner now leaves `branch` out of its `ran_docket` signal and records whether the skill was listed. The first run had neither change. The start counts above depend on neither.
- The 21 sessions cost $13.39 at list price. The pilot and the rerun cost $2.53 more. In a cloud session this is billed to the owner's subscription.

**Answered 2026-10-24.** The start rate is good enough for a procedure whose moment is a request the owner makes. In that case a resident trigger plus the skill's description started the skill first every time. The configuration measured is more than one sentence, though. `CLAUDE.md` names the docket skill in several places, and the skill's description lists every workflow it covers. So a moved procedure keeps a resident sentence that names its moment, and the skill's description names the moment too.

This run did not measure a procedure whose moment arrives in the middle of a task, with no request that names it. Every prompt here put the moment in the request. That case needs a hook as well:

- `PL-S2NL`'s pull request procedure fires when a session is about to push. Its brief already plans hooks on push and on pull request creation, and this result says to keep them.
- `PL-Z90G`'s reset procedure fires when an item starts, which the `start-named` and `pick-next` prompts covered. Its housekeeping rule fires at the first edit to work that no item names. `.claude/hooks/docket-branch-guard.sh` already fires at that moment, through `tools/branch_id_check.py --hint-changed`, so that half has its hook.
