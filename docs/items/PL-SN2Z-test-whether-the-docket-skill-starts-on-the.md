---
id: PL-SN2Z
title: Test whether the docket skill starts on the requests it should and stays out of the ones it should not, running each test prompt in a fresh session with the skill on and again with it off
status: untriaged
feature: skill-routing
added: 2026-10-24
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
