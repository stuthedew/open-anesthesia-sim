---
id: PL-K9XQ
title: pr-title fails on the first head of every draft opened at the claim push with its description, because docs/pr-bodies/N.md cannot exist before the pull request has a number, so each such pull request carries a red run that held nothing (a draft cannot merge) and wakes its session to a CI failure it must investigate; seen on #1106
status: dropped
feature: pr-body-integrity
touches: tools/pr_body_check.py, .github/workflows/pr-title.yml, .claude/skills/docket/modes/start.md
added: 2026-09-26
closed: 2026-09-26
reason: moot under PL-3PH2 (project owner, 2026-09-26, ratified): pr-title no longer checks the body, so a draft's first head has nothing to fail on and no red run to wake its session
---

**Problem.** pr-title fails on the first head of every draft opened at the claim push with its description, because docs/pr-bodies/N.md cannot exist before the pull request has a number, so each such pull request carries a red run that held nothing (a draft cannot merge) and wakes its session to a CI failure it must investigate; seen on #1106

**Evidence, 2026-09-26.** `#1106` (`PL-V2X5`'s close-out) opened as a draft at
its claim push, as `.claude/skills/docket/modes/start.md` has it, with its final
description. `pr-title` ran on `opened` against the claim commit and failed:
"pr-body: #1106's body is not recorded on this branch: docs/pr-bodies/1106.md is
not in the tree at HEAD." The file could not have been there. `python3
tools/pr_body_check.py --record` fetches the body from GitHub, so it runs only
once the pull request exists, which is after the claim commit was pushed. The
closure push carried the recorded body, and `pr-title` passed on it.

**Why it matters.** The red run held nothing: GitHub will not merge a draft,
and the push that makes the pull request mergeable re-runs the check. It stays
in the pull request's check history beside the green run, and it reaches the
session as a CI-failure wake that the drive-to-green rules make it investigate
and answer. On `#1106` that was a turn and a job-log read to establish that the
ordering was the expected one. Every pull request opened at the claim push with
its description pays it, which is the shape `CLAUDE.md` § "Prefer deterministic
tooling over repeated model work" calls a defect in the check: one that fires
without changing a decision.

**Routes, not yet weighed.** `--check` could pass a draft, since a draft cannot
merge. `pr-title.yml` triggers on `opened`, `synchronize`, `reopened` and
`edited` but not `ready_for_review`, so that route needs the trigger added, or a
draft marked ready with no later push would merge on a pass it never earned. Or
the start mode could open the draft with an empty description, which `--check`
already passes, and write the description at the closure push, leaving the
draft without one while it is up.
