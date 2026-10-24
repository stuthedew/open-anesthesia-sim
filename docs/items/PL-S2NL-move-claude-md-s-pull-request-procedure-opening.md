---
id: PL-S2NL
title: Move CLAUDE.md's pull request procedure (opening, arming, bringing main in, repeated CI failures) into a skill, keeping one always-loaded trigger sentence and a hook on push and pull request creation
priority: P2
effort: M
status: done
classes: session-cost
feature: skill-routing
milestone: v0.6.1
touches: CLAUDE.md, .claude/skills, .claude/hooks/push-check-guard.sh, .claude/hooks/pr-body-email-guard.sh, docs/resident-instructions.md, tests/unit/test_push_check_guard.py, tests/unit/test_pr_body_check.py, subprojects/docket/src/docket/arming.py, docs/items/PL-6VJ3-the-resident-instruction-set-grew-from-about-37.md, docs/items/PL-JRVV-review-claude-md-for-instructions-that-a-script.md
added: 2026-10-24
closed: 2026-10-24
pr: 1714
payoff: every session stops loading about 5,000 characters of pull request procedure that it needs only at a push, and the push and pull request hooks point to that procedure at the moment it applies
verify: grep -q '^name: pull-request' .claude/skills/pull-request/SKILL.md && ! grep -q 'Four failed runs of one check' CLAUDE.md && grep -q 'pull-request/SKILL.md' .claude/hooks/push-check-guard.sh && grep -q 'pull-request/SKILL.md' .claude/hooks/pr-body-email-guard.sh
---

**Problem.** Move CLAUDE.md's pull request procedure (opening, arming, bringing main in, repeated CI failures) into a skill, keeping one always-loaded trigger sentence and a hook on push and pull request creation

**Why it matters.** Two bullets in `CLAUDE.md` § "The queue, and how the project owner works" carry the pull request procedure: "Commit and push as you go" and "Bring `origin/main` into an open pull request once". A rough split on 2026-10-24 measured them at 4,008 and 1,190 characters. Every session loads them, but only a session about to push or open a pull request needs them. Here the trigger is a tool call, so a hook can start the skill reliably instead of relying on the model to remember. `.claude/hooks/push-check-guard.sh` and `.claude/hooks/pr-body-email-guard.sh` already run at those moments.

**What `PL-SN2Z` found, 2026-10-24.** A skill named by a resident trigger started first in 8 of 8 sessions whose request named its moment. It measured no moment that arrives mid-task, which is this procedure's, so keep the hooks on push and on pull request creation. Keep a resident sentence that names the moment, and name it in the skill's description too.

[superseded 2026-10-24] **Waits on** `PL-6VJ3` and `PL-JRVV`. Work this item after `PL-6VJ3` and `PL-JRVV`, which also edit `CLAUDE.md`, so that no paragraph is moved by one item and deleted by another.

**Order changed, 2026-10-24.** The project owner named this item to start, and the session that filed the wait had written it as a sequencing preference, not a dependency. The three items edit different paragraphs of `CLAUDE.md`. Any order works as long as they run one after another, and no session holds `PL-6VJ3` or `PL-JRVV`. Both briefs now say that this item moved the two pull request bullets first, so `PL-JRVV` reviews the skill for rules a check enforces, not `CLAUDE.md`.

**What stays always loaded.** Any rule a session must apply before its first commit or push stays: the item id at the front of every commit subject, and the `Co-authored-by` line. The read-only rule that a session disarms its own armed pull requests also stays, because it applies before any push.

**Done when.** The procedure lives in a skill. `CLAUDE.md` keeps one trigger sentence and a pointer. The hooks on push and on pull request creation name the skill. `docs/resident-instructions.md` records the move, and `make check`'s resident total shows the cut.

**Generator check.** None. The owner asked for this work after the comparison with testdouble/han, and no fact was misread to produce it.

**Done 2026-10-24.** The procedure lives in `.claude/skills/pull-request/SKILL.md`, sorted by the moment each rule applies. One resident bullet keeps "commit and push as you go", the standing request to open the pull request on approved, green work, and a trigger that names the skill. `.claude/hooks/push-check-guard.sh` and `.claude/hooks/pr-body-email-guard.sh` now add a note naming the skill beside the result of a call they let through. The note on pull request creation fired live when this item's own pull request opened. `CLAUDE.md` went from 55,984 to 51,597 characters, and the skill's description adds 441, so the resident set is 3,946 characters smaller. `docs/resident-instructions.md` § "The pull request procedure, routed to a skill 2026-10-24" records what stayed and why.
