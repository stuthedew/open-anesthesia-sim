---
id: PL-D902
title: The pull-request skill lets a session squash-merge a green, current pull request but does not say to merge without asking, so a session asked the owner after a harness permission check refused its next call
priority: P2
effort: S
status: done
classes: infra
touches: .claude/skills/pull-request/SKILL.md
added: 2026-10-26
closed: 2026-10-26
pr: 1868
payoff: a session merges a green, current pull request itself instead of asking the owner a question he has already answered
verify: grep -q 'never a question for the owner' .claude/skills/pull-request/SKILL.md
---

**Problem.** The pull-request skill lets a session squash-merge a green, current pull request but does not say to merge without asking, so a session asked the owner after a harness permission check refused its next call.

**Why it matters.** The skill says a session squash-merges a pull request that GitHub will not arm because it is already green and current (`PL-NXRJ`, 2026-10-03). It does not say the session asks nothing first. On 2026-10-26 a thread merged #1854 that way. The harness's automatic permission check then refused its next tool call, labelled "Merge Without Review". The thread read that as a reason to ask the owner whether direct merges were allowed, and the coordinator paused direct merges in every thread until he answered. The owner had already decided this, and said so: "Direct squash merges are ok if passing checks and you shouldn't be asking me just because it's a squash merge but wouldnt if auto-armed" (project owner, 2026-10-26).

**Done when.** The skill's paragraph on direct merges says that a direct merge needs exactly what an armed auto-merge needs, so the session asks the owner nothing first. It also says that a permission check refusing the call is a blocked tool call, reported as blocked, and never a question for the owner.

**Generator check.** Not a generator. This is one missing sentence in a rule that already exists, found once. The owner asked for the edit ("Should we just update the skill?", 2026-10-26), which lifts the generator pause for this request.

**Done.** Added the sentence to `.claude/skills/pull-request/SKILL.md` § "Bring `main` in only when there is a reason", after the `PL-NXRJ` sentence. A direct merge needs exactly what an armed auto-merge needs, so the session asks nothing first, and a refused permission check is reported as blocked rather than turned into a question for the owner.
