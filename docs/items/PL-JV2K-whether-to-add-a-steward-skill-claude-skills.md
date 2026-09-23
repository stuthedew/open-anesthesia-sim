---
id: PL-JV2K
title: Whether to add a steward skill (.claude/skills/steward/SKILL.md), which the cloud harness reads before acting on a CI or review event on a session's own pull request: decided no on 2026-09-23
priority: P3
effort: S
status: dropped
classes: infra
touches: docs/items
added: 2026-09-23
closed: 2026-09-23
reason: project owner, 2026-09-23, ratified, over adding a steward override list - the harness's PR rules already fit this repo, and the one clash it could settle (porting a red-main fix) is a tooling defect held by PL-GHHW and PL-PXZ3
---

**Problem.** Whether to add a steward skill (.claude/skills/steward/SKILL.md), which the cloud harness reads before acting on a CI or review event on a session's own pull request: decided no on 2026-09-23

**What it is.** The cloud harness tells a session driving its own pull request
to read `.claude/skills/steward/SKILL.md` (and `babysit/`) before acting on a
CI or review event, and treats that file as taking "precedence over these rules
on conventions and on how proactive to be". It cannot override the harness's
"never" rules, nor let a session approve or merge. It is not documented on
code.claude.com as of 2026-09-23.

**Why not, measured 2026-09-23.**

- The events it governs barely occur here: two checks (`checks`, `pr-title`),
  no review bot, no Claude Approvals check. Only 12 pull requests in the
  repository's history ever had a comment, none had changes requested, and the
  ten merged between #933 and #942 merged 3-16 minutes after opening.
- Where the harness and this repository differ, `CLAUDE.md` already governs:
  the standing pull-request ask, auto-merge, id-led titles, no habit merges of
  `main`. A steward file would be a second copy of those rules.
- The one clash, porting another branch's fix while `main` is red, was
  exercised the same day: four branches ported the fix for `a65b440c` (per
  `PL-GHHW`), #935's byte for byte (`155d6fa2`), and #935 merged green. What
  broke was tooling: `PL-GHHW` (`bin/docket stranded`) and `PL-PXZ3`
  (`tools/left_behind_check.py`) read a ported commit as unlanded. Fixing them
  by patch identity is deterministic and covers any cherry-pick; a steward rule
  forbidding ports would leave both tools wrong.
- It is a new workflow mechanism, held by the pause while `PL-1P5V` carried
  `generator: live`.

**Reopen when** a pull-request-driving session is recorded mishandling a CI or
review event because the harness's generic rule differs from this repository's
convention, or Claude Code Review is turned on here. Build it then as an
override list only, with `disable-model-invocation: true` so its description
stays out of every session's skill listing
(https://code.claude.com/docs/en/skills, § "Control who invokes a skill"); the
harness reads the file by path.
